from typing import List
from .schema import Cluster, Summary

def has_no_key_heuristic(cluster: Cluster) -> bool:
  has_error_or_warnings = False
  has_placeholders = False

  for item in cluster.items:
    if item.level in ['error', 'warning']:
      has_error_or_warnings = True
      break
  
  for placeholder in ['<NUM>', '<SIG>', '<ID>']:
    if placeholder in cluster.key:
      has_placeholders = True
      break
  
  # Check if its recurring which means that it needs summarization (if it has placeholders)
  is_recurring = cluster.count > 1
  
  return has_error_or_warnings and (has_placeholders or is_recurring)

def summarize_clusters(clusters: List[Cluster]) -> List[Summary]:
  summaries = []

  for cluster in clusters:
    if has_no_key_heuristic(cluster):
      print(f"Generating summary for cluster {cluster.id}...")
      summary = generate_summary_with_gemini(cluster)
      if summary:
        summaries.append(summary)
      else:
        print(f"Failed to generate summary for cluster {cluster.id}")

  return summaries


