from pathlib import Path
import re, sys

p = Path(r"metatime\core\clock.py")
s = p.read_text(encoding="utf-8")

mc = re.search(r"class\s+RelationalClock\b.*?:", s)
if not mc:
    print("ERROR: class RelationalClock not found")
    sys.exit(1)

start = mc.start()
tail = s[start:]

mi = re.search(r"\n\s+def\s+__init__\s*\([^\)]*\)\s*:\s*\n", tail)
if not mi:
    print("ERROR: __init__ not found inside RelationalClock")
    sys.exit(1)

init_pos = start + mi.end()

after = s[init_pos:]
m_indent = re.search(r"(\s+)\S", after)
if not m_indent:
    print("ERROR: Could not detect indentation after __init__")
    sys.exit(1)

indent = m_indent.group(1)

# لا نكرر إذا كانت موجودة في بداية __init__
init_block = after[:600]
if "self.step_counter" in init_block:
    print("OK: self.step_counter already in __init__ (no change)")
    sys.exit(0)

injection = f"{indent}self.step_counter = 0\n{indent}self.relational_age = 0.0\n"
s2 = s[:init_pos] + injection + s[init_pos:]

p.write_text(s2, encoding="utf-8")
print("PATCHED: inserted step_counter & relational_age into RelationalClock.__init__")
print("File:", p)
