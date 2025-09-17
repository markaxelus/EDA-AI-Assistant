import re
import typing from Iterable, List
from .schema import LogItem

IVERILOG_PTRN = re.compile(r"^(?:iverilog:\s+)?(?P<level>warning|error):(?P<msg>.*?)$")
YOSYS_PTRN = re.compile(r"^$")
GENERIC_PTRN = re.compile(r"^$")