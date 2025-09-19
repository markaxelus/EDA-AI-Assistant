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

    Please provide:
    1. A clear explanation of what this error/warning means
    2. 2-3 specific, actionable suggested fixes

    Format your response as:
    EXPLANATION: [your explanation here]
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

  explanation = ""
  suggested_fixes = []
  lines = response_text.split('\n')
  current_section = None

  for line in lines:
    line = line.strip()
    if line.startswith('EXPLANATION:'):
      explanation = line.replace('EXPLANATION:', '').strip()
      current_section = explanation
    elif line.startswith('FIXES:'):
      current_section = 'fixes'
    elif current_section == 'fixes' and line.startswith('- '):
      fix = line.replace('- ', '').strip()
      if fix:
        suggested_fixes.append(fix)

  if not explanation:
    explanation = "Unable to parse explanation from AI response"
  if not suggested_fixes:
    suggested_fixes = ["Review the log messages for specific detail"]
  
  return Summary(
    cluster_id=cluster_id,
    explanation=explanation,
    suggested_fixes=suggested_fixes
  )

def generate_summary_with_gemini(cluster: Cluster) -> Optional[Summary]:
  if not GEMINI_AVAILABLE:
    print("Gemini API not available; google-genai package not installed")
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

def generate_gemini_summary():
    return

def create_fallback_summary(): 
    return