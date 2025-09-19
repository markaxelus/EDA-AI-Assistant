import os
from typing import List, Optional
from .schema import Cluster, Summary

try:
  from google import genai
  GEMINI_AVAILABLE = True
except ImportError:
  GEMINI_AVAILABLE = False

def create_summary_prompt(cluster: Cluster) -> str:
  return

def parse_summary_response(response_text: str, cluster_id: int) -> Summary:
  return

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