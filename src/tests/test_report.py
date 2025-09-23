import types
from pathlib import Path
import sys

import pytest

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
  sys.path.insert(0, str(SRC_DIR))

from ai_logs.report import make_markdown, write_report
from ai_logs.schema import LogItem, Cluster, Summary


def _sample_cluster_and_summaries():
  items = [
    LogItem(tool="iverilog", level="warning", code=None, msg="unused signal foo", raw="raw-1"),
    LogItem(tool="iverilog", level="error", code=None, msg="signal 'clk' has value 123", raw="raw-2"),
  ]
  cluster = Cluster(id="cluster_0", key="signal '<SIG>' has value <NUM>", count=len(items), items=items)
  summaries = {
    "cluster_0": Summary(
      cluster_id=0,
      explanation="Clock value mismatch due to uninitialized signal.",
      suggested_fixes=[
        "Initialize 'clk' in the testbench",
        "Verify reset sequencing",
      ],
    )
  }
  return cluster, summaries

def test_make_markdown_basic_contents():
  cluster, summaries = _sample_cluster_and_summaries()

  md = make_markdown([cluster], summaries, "https://feedback.example")

  assert "# Engineering Log Analysis Report" in md
  assert "Total clusters:" in md
  assert "Feedback:" in md

  assert "Cluster cluster_0" in md
  # Check for escaped version of cluster key (with backticks around placeholders)
  escaped_key = cluster.key.replace('<', '`<').replace('>', '>`')
  assert escaped_key in md
  assert "Count: **2**" in md
  assert "Tool: `iverilog`" in md

  assert "Severity: `error`" in md

  assert "**Explanation**" in md
  assert "Clock value mismatch" in md
  assert "**Suggested fixes**" in md
  assert "Initialize 'clk'" in md


def test_write_report_md_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
  cluster, summaries = _sample_cluster_and_summaries()
  md = make_markdown([cluster], summaries, "https://feedback.example")

  out_md = tmp_path / "report.md"
  write_report(md, out_md)

  assert out_md.exists()
  assert out_md.read_text(encoding="utf-8") == md

  out = capsys.readouterr().out
  assert "Markdown report written to" in out




def test_preview_markdown_stdout():
  """python -m pytest src/tests/test_report.py::test_preview_markdown_stdout -s -q"""
  cluster, summaries = _sample_cluster_and_summaries()
  md = make_markdown([cluster], summaries, "https://feedback.example")
  print("\n===== GENERATED MARKDOWN PREVIEW =====\n")
  print(md)
  print("\n===== END MARKDOWN PREVIEW =====\n")
  assert "# Engineering Log Analysis Report" in md
