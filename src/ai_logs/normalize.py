import hashlib
from collections import defaultdict
import re
from typing import List
from .schema import LogItem, Cluster



def fingerprint(msg: str) -> str:
  template = NUM.