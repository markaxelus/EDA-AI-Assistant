from typing import List
from .schema import Cluster, Summary

def has_no_key_heuristic(cluster: Cluster) -> bool:
  has_error_or_warnings = False
  has_placeholders = False

  for item in cluster.items:
    if item.level in ['error', 'warning']:
      has_error_or_warnings = True
      break
  
  for placeholder in cluster.key:
    if placeholder in ['<NUM>', '<SIG>', '<ID>']:
      has_placeholders = True
      break
  
  # Check if its recurring which means that it needs summarization (if it has placeholders)
  is_recurring = cluster.count > 1
  
  return has_error_or_warnings and (has_placeholders or is_recurring)

