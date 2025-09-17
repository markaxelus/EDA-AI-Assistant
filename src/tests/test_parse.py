import io
import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_logs.parse import parse_lines

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def read_lines(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return f.readlines()

def test_parse_iverilog_small_log():
    lines = read_lines("verilog_small.log")
    items = parse_lines("iverilog", lines)

    assert len(items) == 3

    assert items[0].tool == "iverilog"
    assert items[0].level == "warning"
    assert items[0].code is None
    assert items[0].msg == "signal 'clk' is not connected to any module ports."
    assert items[0].raw == lines[0].rstrip("\n")

    assert items[1].tool == "iverilog"
    assert items[1].level == "error"
    assert items[1].code is None
    assert items[1].msg == 'syntax error near "endmodule"'
    assert items[1].raw == lines[1].rstrip("\n")

    assert items[2].tool == "iverilog"
    assert items[2].level == "error"
    assert items[2].code is None
    assert items[2].msg == 'Unable to elaborate module "counter_tb".'
    assert items[2].raw == lines[2].rstrip("\n")

def test_parse_yosys_small_log():
    lines = read_lines("yosys_small.log")
    items = parse_lines("yosys", lines)

    assert len(items) == 3
  
    assert items[0].tool == "yosys"
    assert items[0].level == "info"
    assert items[0].code == "step:1"
    assert items[0].msg == "Executing Verilog-2005 frontend."
    assert items[0].raw == lines[0].rstrip("\n")

    assert items[1].tool == "yosys"
    assert items[1].level == "warning"
    assert items[1].code is None
    assert items[1].msg == "signal top.clk has no driver."
    assert items[1].raw == lines[1].rstrip("\n")

    assert items[2].tool == "yosys"
    assert items[2].level == "error"
    assert items[2].code is None
    assert items[2].msg == "Parser error in line 12: syntax error, unexpected END."
    assert items[2].raw == lines[2].rstrip("\n")


def test_parse_yosys_large_log_counts_and_order():
    lines = read_lines("yosys_large.log")
    items = parse_lines("yosys", lines)

    assert len(items) == 11

    assert items[0].code == "step:2"
    assert items[0].level == "info"
    assert items[0].msg == "Executing Verilog-2005 frontend."

    levels = [it.level for it in items[1:]]
    assert levels.count("warning") == 6
    assert levels.count("error") == 4


