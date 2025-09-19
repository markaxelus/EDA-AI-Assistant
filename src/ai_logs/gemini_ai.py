import os
from typing import List, Optional
from .schema import Cluster, Summary

try:
  from google import genai
  GEMINI_AVAILABLE = True
except ImportError:
  GEMINI_AVAILABLE = False

def create_summary_prompt(cluster: Cluster) -> str:
  # Use the first 3 msgs in the cluster as example for now (future_work-validate performance & quality under different sample sizes)
  sample_messages = [item.msg for item in cluster.items[:3]]  
  tool_types = list(set(item.tool for item in cluster.items))
  levels = list(set(item.level for item in cluster.items))
  prompt = f"""
    You are an expert in Electronic Design Automation (EDA) tools. Analyze the following log messages and provide a clear explanation and suggested fixes.
    Tool(s): {', '.join(tool_types)}
    Severity: {', '.join(levels)}
    Occurrences: {cluster.count}
    Message template: {cluster.key}

    Sample messages:
    {chr(10).join(f"- {msg}" for msg in sample_messages)}

    Write ONLY in this exact format (no extra prose, no code fences, no markdown headings):
    EXPLANATION: <one concise paragraph>
    FIXES:
    - <fix 1>
    - <fix 2>
    - <fix 3>
  """
  return prompt

def parse_summary_response(response_text: str, cluster_id: int) -> Summary:
  """
    Goal: 
      EXPLANATION: <some explanation text>
      FIXES:
      - <fix 1>
      - <fix 2> 
  """
  text = response_text.strip()
  if text.startswith("```") and text.endswith("```"):
    text = text.strip('`')  # crude fence strip
  lines = [ln.strip() for ln in text.split('\n') if ln.strip()]

  explanation = ""
  suggested_fixes: list[str] = []

  current_section = None
  for line in lines:
    upper = line.upper()
    if upper.startswith('EXPLANATION:'):
      explanation = line.split(':', 1)[1].strip()
      current_section = 'explanation'
      continue
    if upper.startswith('FIXES:'):
      current_section = 'fixes'
      continue
    if current_section == 'fixes':
      # Accept bullets "- ", "* ", or numbered lists "1. "
      if line.startswith('- ') or line.startswith('* '):
        fix = line[2:].strip()
        if fix:
          suggested_fixes.append(fix)
        continue
      if any(line[:2].isdigit() for _ in [0]) and '.' in line[:4]:
        # naive numbered list like "1. fix"
        fix = line.split('.', 1)[1].strip()
        if fix:
          suggested_fixes.append(fix)

  # Fallbacks if the model ignored headers
  if not explanation and lines:
    explanation = lines[0]
  if not suggested_fixes:
    # Heuristic: collect any bullet-like lines anywhere
    for line in lines[1:]:
      if line.startswith('- ') or line.startswith('* '):
        suggested_fixes.append(line[2:].strip())
      elif any(line[:2].isdigit() for _ in [0]) and '.' in line[:4]:
        suggested_fixes.append(line.split('.', 1)[1].strip())
      if len(suggested_fixes) >= 3:
        break
  if not suggested_fixes:
    suggested_fixes = [
      "Review the log messages for specific details",
      "Consult the tool documentation for this error type",
      "Check design/testbench for common syntax and connectivity issues",
    ]
  
  return Summary(
    cluster_id=cluster_id,
    explanation=explanation,
    suggested_fixes=suggested_fixes
  )

def generate_summary_with_gemini(cluster: Cluster) -> Optional[Summary]:
  if not GEMINI_AVAILABLE:
    print("Gemini API not available; google-genai package not installed")
    return None
  try:
    client = genai.Client()

    prompt = create_summary_prompt(cluster)

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    
    response_text = response.text.strip()
    cluster_id = int(cluster.id.split('_')[1])

    return parse_summary_response(response_text, cluster_id)
  
  except Exception as e:
    print(f"Error generating summary for cluster: {cluster.id}: {e}")
    return None

def create_fallback_summary(cluster: Cluster) -> Summary:
  cluster_id = int(cluster.id.split('_')[1])
  return Summary(
    cluster_id=cluster_id,
    explanation=(
      f"This cluster contains {cluster.count} {cluster.items[0].level}(s) "
      f"matching: {cluster.key}"
    ),
    suggested_fixes=[
      "Review the specific log messages for details",
      "Check tool documentation for this error/warning type",
      "Verify design files and testbench for common issues",
    ],
  )