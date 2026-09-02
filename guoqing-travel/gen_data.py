"""由上级目录的 travel_data.py 重新生成前端 data.js。

用法（在 guoqing-travel 目录下执行）：
    python gen_data.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import travel_data as td  # noqa: E402

snap = td.data_snapshot()
out = "// 自动生成：源数据来自 ../travel_data.py（data_snapshot()）\n"
out += "// 更新数据请改 ../travel_data.py 后重新运行：python gen_data.py\n"
out += "window.TRAVEL_DATA = " + json.dumps(snap, ensure_ascii=False, separators=(",", ":")) + ";\n"

dest = os.path.join(HERE, "data.js")
with open(dest, "w", encoding="utf-8") as f:
    f.write(out)
print("已写入 %s ｜ cities=%d counties=%d provinces=%d" % (
    dest, len(snap["cities"]), len(snap["counties"]), len(snap["provinces_2025"])))
