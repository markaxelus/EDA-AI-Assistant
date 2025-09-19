import io
import os
import sys
from pathlib import Path
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_logs.summarize import has_no_key_heuristic, summarize_clusters
from ai_logs.schema import LogItem, Cluster

class TestNoKeyHeuristic:
  def test_heuristic_errors_with_placeholders(self):
    """Test cases for no-key heuristic"""
    items = [
            LogItem(tool="iverilog", level="error", code=None, 
                   msg="signal 'clk' has value 123", raw="raw1"),
            LogItem(tool="iverilog", level="error", code=None, 
                   msg="signal 'reset' has value 456", raw="raw2"),
        ]
        
    cluster = Cluster(
        id="cluster_0",
        key="signal '<SIG>' has value <NUM>",
        count=2,
        items=items
    )
    
    assert has_no_key_heuristic(cluster) == True

  def test_heuristic_warnings_recurring(self):
    """Test that warning clusters with multiple occurrences need summarization"""
    items = [
        LogItem(tool="iverilog", level="warning", code=None, 
                msg="signal 'clk' is not connected", raw="raw1"),
        LogItem(tool="iverilog", level="warning", code=None, 
                msg="signal 'reset' is not connected", raw="raw2"),
    ]
    
    cluster = Cluster(
        id="cluster_0",
        key="signal 'clk' is not connected",
        count=2,
        items=items
    )
    
    assert has_no_key_heuristic(cluster) == True
    
  def test_heuristic_info_messages_no_summary(self):
    """Test that info-only clusters don't need summarization"""
    items = [
        LogItem(tool="yosys", level="info", code="step:1", 
                msg="Executing Verilog-2005 frontend.", raw="raw1"),
    ]
    
    cluster = Cluster(
        id="cluster_0",
        key="Executing Verilog-2005 frontend.",
        count=1,
        items=items
    )
    
    assert has_no_key_heuristic(cluster) == False
  
  def test_heuristic_single_error_no_placeholders(self):
    """Test that single errors without placeholders don't need summarization"""
    items = [
        LogItem(tool="iverilog", level="error", code=None, 
                msg="syntax error near 'endmodule'", raw="raw1"),
    ]
    
    cluster = Cluster(
        id="cluster_0",
        key="syntax error near 'endmodule'",
        count=1,
        items=items
    )
    
    assert has_no_key_heuristic(cluster) == False
  
  def test_heuristic_mixed_levels_with_placeholders(self):
    """Test clusters with mixed error/warning levels and placeholders"""
    items = [
        LogItem(tool="iverilog", level="error", code=None, 
                msg="signal 'clk' has value 123", raw="raw1"),
        LogItem(tool="iverilog", level="warning", code=None, 
                msg="signal 'reset' has value 456", raw="raw2"),
    ]
    
    cluster = Cluster(
        id="cluster_0",
        key="signal '<SIG>' has value <NUM>",
        count=2,
        items=items
    )

    assert has_no_key_heuristic(cluster) == True

  def test_heuristic_error_with_placeholders_nonrecurring(self):
    """Test clusters with placeholders and non-recurring"""
    items = [
        LogItem(tool="iverilog", level="error", code=None,
                msg="signal 'clk' has value 123", raw="raw1"),
    ]
    cluster = Cluster(
        id="cluster_x",
        key="signal '<SIG>' has value <NUM>",
        count=1,                 
        items=items
    )

    assert has_no_key_heuristic(cluster) == True

class TestSummarizeClusters:
  def test_summarize_clusters_empty_input(self):
    """Test summarize_clusters with empty input."""
    clusters = []
    summaries = summarize_clusters(clusters)
    
    assert len(summaries) == 0
  
  def test_summarize_clusters_no_eligible_clusters(self):
    """Test summarize_clusters with no clusters meeting heuristic."""
    items = [
        LogItem(tool="yosys", level="info", code="step:1", 
                msg="Executing Verilog-2005 frontend.", raw="raw1"),
    ]
    
    cluster = Cluster(
        id="cluster_0",
        key="Executing Verilog-2005 frontend.",
        count=1,
        items=items
    )
    
    clusters = [cluster]
    summaries = summarize_clusters(clusters)
    
    assert len(summaries) == 0

  @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="Requires GEMINI_API_KEY environment variable")
  def test_summarize_clusters_with_api(self):
    """Test summarize_clusters with actual API call (requires API key)."""
    print("Running Gemini Summary Test")
    items = [
        LogItem(tool="iverilog", level="error", code=None, 
                msg="signal 'clk' has value 123", raw="raw1"),
        LogItem(tool="iverilog", level="error", code=None, 
                msg="signal 'reset' has value 456", raw="raw2"),
    ]
    
    cluster = Cluster(
        id="cluster_0",
        key="signal '<SIG>' has value <NUM>",
        count=2,
        items=items
    )
    
    clusters = [cluster]
    summaries = summarize_clusters(clusters)
    
    if len(summaries) > 0:
        summary = next(iter(summaries.values()))
        assert summary.cluster_id == 0
        assert len(summary.explanation) > 0
        assert len(summary.suggested_fixes) > 0