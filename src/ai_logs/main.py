import json
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from .parse import parse_lines
from .normalize import cluster_logs
from .summarize import summarize_clusters
from .report import make_markdown, write_report

app = typer.Typer(add_completion=False, help="EDA log analysis pipeline: parse → cluster → summarize → report")

def _read_lines_if_exists(path_str: Optional[str], tool: str) -> list[str]:
  if not path_str:
    return []
  p = Path(path_str)
  if not p.exists():
    return []
  try:
    return p.read_text(encoding="utf-8", errors="ignore").splitlines()
  except Exception:
    return []


@app.command()
def run(
  iverilog_log: str = typer.Option("data/verilog_small.log", help="Path to Icarus Verilog log"),
  yosys_log: str = typer.Option("data/yosys_small.log", help="Path to Yosys log"),
  feedback_url: str = typer.Option("https://example.com/feedback", help="Feedback form URL to embed in the report"),
  out_json: str = typer.Option("data/processed/results.json", help="Path to write structured JSON results"),
  out_md: str = typer.Option("data/reports/report.md", help="Path to write Markdown report"),
):
  """Run the full pipeline on the provided logs and generate a report."""
  load_dotenv()

  items = []

  iv_lines = _read_lines_if_exists(iverilog_log, "iverilog")
  if iv_lines:
    items += parse_lines("iverilog", iv_lines)

  ys_lines = _read_lines_if_exists(yosys_log, "yosys")
  if ys_lines:
    items += parse_lines("yosys", ys_lines)

  clusters = cluster_logs(items)

  summaries = summarize_clusters(clusters)

  Path(out_json).parent.mkdir(parents=True, exist_ok=True)
  Path(out_md).parent.mkdir(parents=True, exist_ok=True)

  Path(out_json).write_text(
    json.dumps(
      {
        "clusters": [c.model_dump() for c in clusters],
        "summaries": {k: v.model_dump() for k, v in summaries.items()},
      },
      indent=2,
    ),
    encoding="utf-8",
  )

  md = make_markdown(clusters, summaries, feedback_url)
  write_report(md, Path(out_md))

  typer.echo(f"Parsed items: {len(items)} | Clusters: {len(clusters)} | Summaries: {len(summaries)}")
  typer.echo(f"Wrote JSON: {out_json}")
  typer.echo(f"Wrote Markdown: {out_md}")


if __name__ == "__main__":
  app()
