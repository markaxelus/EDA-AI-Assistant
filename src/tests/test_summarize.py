import io
import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_logs.summarize import has_no_key_heuristic, summarize_clusters
from ai_logs.schema import LogItem, Cluster

