from pathlib import Path
from typing import Dict, List
from .schema import Cluster, Summary

def make_markdown(clusters: List[Cluster], summaries: Dict[str, Summary], feedback_url: str) -> str:
  lines = ["# Engineering Log Analysis Report", ""]
  lines += [f"- Total clusters: **{len(clusters)}**",
            f"- Feedback: [{feedback_url}]({feedback_url})", ""]

  for element in clusters:
    s = summaries.get(element.id)
    severity_levels = [item.level for item in element.items] if element.items else ['unknown']
    severity_order = {'error': 3, 'warning': 2, 'info': 1}
    most_severe = max(severity_levels, key=lambda x: severity_order.get(x, 0))

    lines += [f"## Cluster {element.id} — {element.key}",
              f"- Count: **{element.count}** | Tool: `{element.items[0].tool if element.items else 'n/a'}`",
              f"- Severity: `{most_severe}`",
              "",
              "**Explanation**",
              s.explanation if s else "_(no summary)_",
              "",
              "**Suggested fixes**"]
    if s and s.suggested_fixes:
        lines += [f"- {fx}" for fx in s.suggested_fixes]
    else:
        lines += ["- (none)"]
    lines.append("")
    
  return "\n".join(lines)

def generate_summary_stats(clusters: List[Cluster], summaries: Dict[str, Summary]) -> Dict[str, int]:
  return 

def make_markdown_with_stats(clusters: List[Cluster], summaries: Dict[str, Summary], feedback_url: str, stats: Dict[str, int] = None) -> str:
  return

def write_report(md: str, out_md: Path) -> None:
  out_md.write_text(md, encoding="utf-8")
  print(f"Markdown report written to {out_md}")