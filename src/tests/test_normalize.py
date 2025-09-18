import io
import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_logs.normalize import fingerprint, cluster_logs
from ai_logs.schema import LogItem, Cluster


class TestFingerprint:    
    def test_fingerprint_basic_number_replacement(self):
        """Test that numbers are replaced with <NUM>"""
        msg1 = "signal 'clk' has value 123"
        msg2 = "signal 'clk' has value 456"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 == fp2
        assert len(fp1) == 32  # MD5 hash length
    
    def test_fingerprint_quoted_string_replacement(self):
        """Test that quoted strings are replaced with '<SIG>'"""
        msg1 = "signal 'clk' is not connected"
        msg2 = "signal 'reset' is not connected"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 == fp2
    
    def test_fingerprint_identifier_replacement(self):
        """Test that identifiers are replaced with <ID>"""
        msg1 = "variable my_var has no driver"
        msg2 = "variable other_var has no driver"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 == fp2
    
    def test_fingerprint_preserves_keywords(self):
        """Test that keywords are preserved and not replaced"""
        msg1 = "signal port module net driver assignment"
        msg2 = "signal port module net driver assignment"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 == fp2
    
    def test_fingerprint_mixed_normalization(self):
        """Test fingerprint with mixed types of normalization"""
        msg1 = "signal 'clk' in module counter_123 has value 456"
        msg2 = "signal 'reset' in module timer_789 has value 999"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 == fp2
    
    def test_fingerprint_different_messages(self):
        """Test that genuinely different messages have different fingerprints"""
        msg1 = "signal 'clk' is not connected"
        msg2 = "syntax error near 'endmodule'"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 != fp2
    
    def test_fingerprint_empty_string(self):
        """Test fingerprint with empty string"""
        msg = ""
        fp = fingerprint(msg)
        
        assert len(fp) == 32  
        assert isinstance(fp, str)
    
    def test_fingerprint_special_characters(self):
        """Test fingerprint with special characters"""
        msg1 = "error: unexpected token ';' at line 123"
        msg2 = "error: unexpected token ':' at line 456"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 == fp2
    
    def test_fingerprint_case_sensitivity(self):
        """Test that fingerprint is case sensitive for non-normalized parts"""
        msg1 = "Signal 'clk' is not connected"
        msg2 = "signal 'clk' is not connected"
        
        fp1 = fingerprint(msg1)
        fp2 = fingerprint(msg2)
        
        assert fp1 != fp2


class TestClusterLogs:
    def test_cluster_logs_basic_clustering(self):
        """Test basic clustering of similar log items"""
        items = [
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' has value 123", raw="raw1"),
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'reset' has value 456", raw="raw2"),
            LogItem(tool="iverilog", level="error", code=None, 
                   msg="syntax error near 'endmodule'", raw="raw3"),
        ]
        
        clusters = cluster_logs(items)
        
        assert len(clusters) == 2  
        
        signal_cluster = next(c for c in clusters if c.count == 2)
        error_cluster = next(c for c in clusters if c.count == 1)
        
        assert signal_cluster.count == 2
        assert error_cluster.count == 1
        assert signal_cluster.id.startswith("cluster_")
        assert error_cluster.id.startswith("cluster_")
    
    def test_cluster_logs_identical_messages(self):
        """Test clustering with identical messages"""
        items = [
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' is not connected", raw="raw1"),
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' is not connected", raw="raw2"),
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' is not connected", raw="raw3"),
        ]
        
        clusters = cluster_logs(items)
        
        assert len(clusters) == 1
        assert clusters[0].count == 3
        assert len(clusters[0].items) == 3
        assert clusters[0].id == "cluster_0"
    
    def test_cluster_logs_empty_input(self):
        """Test clustering with empty input"""
        items = []
        clusters = cluster_logs(items)
        
        assert len(clusters) == 0
    
    def test_cluster_logs_single_item(self):
        """Test clustering with single item"""
        items = [
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' is not connected", raw="raw1"),
        ]
        
        clusters = cluster_logs(items)
        
        assert len(clusters) == 1
        assert clusters[0].count == 1
        assert clusters[0].id == "cluster_0"
        assert clusters[0].items[0] == items[0]
    
    def test_cluster_logs_key_template_generation(self):
        """Test that cluster keys are properly templated"""
        items = [
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' has value 123", raw="raw1"),
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'reset' has value 456", raw="raw2"),
        ]
        
        clusters = cluster_logs(items)
        
        assert len(clusters) == 1
        cluster = clusters[0]
        
        assert "<NUM>" in cluster.key
        assert "'<SIG>'" in cluster.key
        assert "signal" in cluster.key
    
    def test_cluster_logs_preserves_original_items(self):
        """Test that original LogItem objects are preserved in clusters"""
        items = [
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' is not connected", raw="raw1"),
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'reset' is not connected", raw="raw2"),
        ]
        
        clusters = cluster_logs(items)
        
        assert len(clusters) == 1
        cluster = clusters[0]
        
        assert cluster.items[0] == items[0]
        assert cluster.items[1] == items[1]
        assert cluster.items[0].raw == "raw1"
        assert cluster.items[1].raw == "raw2"
    
    def test_cluster_logs_multiple_different_patterns(self):
        """Test clustering with multiple different message patterns"""
        items = [
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'clk' has value 123", raw="raw1"),
            LogItem(tool="iverilog", level="warning", code=None, 
                   msg="signal 'reset' has value 456", raw="raw2"),
            LogItem(tool="iverilog", level="error", code=None, 
                   msg="syntax error near 'endmodule'", raw="raw3"),
            LogItem(tool="iverilog", level="error", code=None, 
                   msg="syntax error near 'begin'", raw="raw4"),
            LogItem(tool="yosys", level="info", code="step:1", 
                   msg="Executing Verilog-2005 frontend.", raw="raw5"),
        ]
        
        clusters = cluster_logs(items)
        
        assert len(clusters) == 3  
        
        total_items = sum(cluster.count for cluster in clusters)
        assert total_items == 5
        
        cluster_ids = [cluster.id for cluster in clusters]
        assert len(set(cluster_ids)) == len(cluster_ids)
