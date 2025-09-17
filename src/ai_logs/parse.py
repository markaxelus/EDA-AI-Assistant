import re
from typing import Iterable, List
from .schema import LogItem

IVERILOG_PTRN = re.compile(r"^(?:iverilog:\s+)?(?P<level>warning|error):(?P<msg>.*?)$", re.I)
YOSYS_STEP_PTRN = re.compile(r"^(?P<step>\d+)\.\s+(?P<msg>.*)$")
YOSYS_LEVELED_PTRN = re.compile(r"^(?P<level>warning|error):\s*(?P<msg>.*?)$", re.I)

def parse_lines(tool:str, lines: Iterable[str]) -> List[LogItem]:
  items: List[LogItem] = []
  
  for raw in lines:
    s = raw.rstrip("\n")
    if not s:
      continue

    if tool == "iverilog":
      m = IVERILOG_PTRN.match(s)
      if not m:
        continue

      data = m.groupdict()
      level = data['level'].lower()
      msg = data['msg'].strip()
      
      items.append(
        LogItem(
          tool=tool,
          level=level,
          code=None,
          msg=msg,
          raw=s
        )
      )

    elif tool == "yosys":
      ys = YOSYS_STEP_PTRN.match(s)
      if ys:
        step = int(ys.group("step"))
        msg = ys.group("msg").strip()
        items.append(
          LogItem(
            tool=tool,
            level="info",
            code=f"step:{step}",
            msg=msg,
            raw=s
          )
        )
      
      yl = YOSYS_LEVELED_PTRN.match(s)
      if yl:
        data = yl.groupdict()
        level = data["level"].lower()
        msg = data["msg"].strip()
        items.append(
          LogItem(
            tool=tool,
            level=level,
            code=None,
            msg=msg,
            raw=s
          )
        )

  return items