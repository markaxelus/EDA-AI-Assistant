from pydantic import BaseModel
from typing import List, Optional, Dict

class LogItem(BaseModel):
  tool: str             # iverilog, yosys, or generic
  level: str            # error, warning, info
  code: Optional[str]   # tool-specific
  message: str
  raw: str

class Cluster(BaseModel):
  id: str
  key: str              # fingerprint key (msg template)
  count: int
  items: List[LogItem]

class Summary(BaseModel):
  cluster_id: int
  explanation: str
  suggested_fixes: List[str]

class Results(BaseModel):
  clusters: List[Cluster]
  summaries: List[Summary]