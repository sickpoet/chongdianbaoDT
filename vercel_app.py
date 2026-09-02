from __future__ import annotations

import io
import json
import os
import time
from functools import lru_cache
from html import escape
from urllib.parse import quote

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

import charger_cabinet_planner as planner
import requests


app = FastAPI()

def env_has(name: str) -> bool:
    return bool((os.getenv(name) or "").strip())


def kv_env_probe() -> dict[str, bool]:
    names = [
        "KV_REST_API_URL",
        "KV_REST_API_TOKEN",
        "KV_REST_API_READ_ONLY_TOKEN",
        "REDIS_URL",
        "UPSTASH_REDIS_URL",
        "REDIS_REST_URL",
        "REDIS_REST_TOKEN",
        "REDIS_REST_READ_ONLY_TOKEN",
        "UPSTASH_REDIS_REST_URL",
        "UPSTASH_REDIS_REST_TOKEN",
        "UPSTASH_REDIS_REST_READ_ONLY_TOKEN",
    ]
    return {n: env_has(n) for n in names}


# 宋瓷水墨：两个 Python 渲染页面共用的一套样式。
# 用普通字符串而不是 f-string，避免 CSS 花括号被格式化吞掉。
SITE_CSS = """
:root {
  --paper: #edeae3;
  --leaf: #f7f5f0;
  --leaf-2: #f2efe9;
  --ink: #23262b;
  --ink-2: #3d4349;
  --ink-3: #4e5358;
  --ink-4: #6b7075;
  --rule: #d8d3c9;
  --rule-2: #e5e1d9;
  --celadon: #7e9c99;
  --celadon-deep: #4f6e6b;
  --celadon-wash: #dbe3df;
  --cinnabar: #a93226;
  --plum: #3f6b54;
  --song: "Source Han Serif SC", "Noto Serif CJK SC", "Noto Serif SC",
    "Songti SC", "STSong", "SimSun", serif;
  --hei: "Source Han Sans SC", "Noto Sans CJK SC", -apple-system,
    BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
    Roboto, Helvetica, Arial, sans-serif;
  --mono: "SFMono-Regular", "JetBrains Mono", Consolas, "Liberation Mono", Menlo, monospace;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: var(--hei);
  font-size: 15px; line-height: 1.7;
  background: var(--paper); color: var(--ink);
  -webkit-font-smoothing: antialiased;
}
b, strong { font-weight: 500; }
a { color: var(--celadon-deep); text-decoration: none; }
a:hover { color: var(--ink); }

.wrap { max-width: 1140px; margin: 0 auto; padding: 0 28px; }

.seal {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; flex: 0 0 26px;
  border-radius: 2px;
  background: var(--cinnabar); color: var(--leaf);
  font-family: var(--song); font-size: 15px; line-height: 1; font-weight: 400;
}
.ico { width: 15px; height: 15px; flex: 0 0 15px; stroke: currentColor; fill: none; stroke-width: 1.4; }
/* ---------- 页头 ---------- */
.pagehead {
  background:
    radial-gradient(120% 88% at 14% 118%, rgba(96, 136, 127, .34), rgba(96, 136, 127, 0) 66%),
    linear-gradient(172deg, #e7ece7 0%, #d9e2dd 60%, #cbd8d2 100%);
  border-bottom: 1px solid var(--rule);
  padding: 40px 0 34px;
}
.pagehead.home { padding: 78px 0 66px; }
.pagehead-inner {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 24px;
}
.pagetitle-row { display: flex; align-items: center; gap: 12px; }
.pagetitle {
  margin: 0;
  font-family: var(--song); font-size: 30px; font-weight: 400;
  letter-spacing: 2.5px; color: #1b1f22;
}
.pagelede { margin: 10px 0 0; font-size: 14.5px; color: #2c3634; max-width: 42em; }
.backlink {
  display: inline-flex; align-items: center; gap: 6px;
  color: #35443f; font-size: 14px; white-space: nowrap;
  padding-top: 6px;
}
.backlink:hover { color: var(--cinnabar); }

/* ---------- 运行状态：默认收起 ---------- */
.status { margin: 22px 0 0; font-size: 13px; }
.status > summary {
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; list-style: none;
  color: var(--ink-3);
  padding: 7px 0; border-bottom: 1px solid var(--rule-2);
}
.status > summary::-webkit-details-marker { display: none; }
.status > summary:hover { color: var(--ink); }
.status .dot { width: 7px; height: 7px; border-radius: 50%; flex: 0 0 7px; background: var(--celadon); }
.status .dot-off { background: transparent; border: 1px solid var(--ink-4); }
.status .more { margin-left: auto; color: var(--ink-4); font-size: 12.5px; }
.status[open] .more::after { content: "，收起"; }
.status-body { padding: 12px 0 2px; }
.status-body .kv { display: flex; gap: 12px; padding: 4px 0; }
.status-body .kv > span:first-child { color: var(--ink-4); min-width: 12em; }
.status-body p { margin: 8px 0 0; color: var(--ink-4); font-size: 12.5px; }
/* ---------- 册页 ---------- */
main { padding-bottom: 60px; }
.row { display: flex; gap: 22px; flex-wrap: wrap; align-items: flex-start; }
.row > * { flex: 1; min-width: 320px; }

.card {
  background: var(--leaf);
  border: 1px solid var(--rule);
  border-radius: 3px;
  padding: 20px 22px;
  margin: 0 0 22px;
}
.card.error { border-color: #d9b8b2; background: #f7ece9; color: #8b2b21; }
.card.muted { color: var(--ink-4); }

/* 步骤：一、二、三 是真的顺序，所以保留编号 */
.step {
  display: flex; align-items: center; gap: 2px;
  margin: 0 0 14px;
  font-family: var(--song); font-size: 18px; font-weight: 400; letter-spacing: 1.5px;
}
.step-n {
  color: var(--cinnabar);
  font-family: var(--song); font-size: 18px; line-height: 1;
}
.card-title {
  display: flex; align-items: center; gap: 10px;
  margin: 0 0 14px;
  font-family: var(--song); font-size: 18px; font-weight: 400; letter-spacing: 1.5px;
}
.card-title::before { content: ""; width: 2px; height: 17px; flex: 0 0 2px; background: var(--cinnabar); }

/* ---------- 表单 ---------- */
input[type="text"] {
  width: 100%;
  border: 0; border-bottom: 1.5px solid var(--rule);
  background: transparent; color: var(--ink);
  font-family: var(--hei); font-size: 15px;
  padding: 8px 0; outline: none;
}
input[type="text"]:focus { border-bottom-color: var(--ink); }
input[type="text"]::placeholder { color: var(--ink-4); }

button {
  border: 1px solid var(--ink); border-radius: 2px;
  background: var(--ink); color: var(--leaf);
  font-family: var(--hei); font-size: 14px;
  padding: 8px 20px; cursor: pointer;
}
button:hover { background: #14171a; }
button.secondary { background: transparent; color: var(--ink); }
button.secondary:hover { background: var(--leaf-2); color: var(--ink); }

.card label { display: block; padding: 5px 0; font-size: 14.5px; cursor: pointer; }
.card label:hover { color: var(--celadon-deep); }
input[type="radio"], input[type="checkbox"] { accent-color: #8f2a20; margin-right: 4px; }
/* ---------- 测算结果三联 ---------- */
.result-grid { display: flex; gap: 0; margin: 4px 0 4px; flex-wrap: wrap; }
.result-grid > div {
  flex: 1; min-width: 140px;
  padding: 4px 0 4px 20px;
  border-left: 1px solid var(--rule-2);
}
.result-grid > div:first-child { padding-left: 0; border-left: 0; }
.result-grid .k { font-size: 12.5px; color: var(--ink-4); }
.result-grid .v {
  font-family: var(--song); font-size: 30px; line-height: 1.3; color: var(--ink);
  font-variant-numeric: tabular-nums;
}

/* ---------- 表格 ---------- */
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { padding: 9px 14px; text-align: left; }
th:first-child, td:first-child { padding-left: 0; }
th {
  background: transparent; color: var(--ink-3);
  font-weight: 400; font-size: 12.5px;
  border-bottom: 1px solid var(--ink-4);
}
td { border-bottom: 1px solid var(--rule-2); font-variant-numeric: tabular-nums; }
tbody tr:last-child td { border-bottom: 0; }

.muted { color: var(--ink-4); }
.error { color: #8b2b21; }
.ok { color: var(--celadon-deep); }

code, pre {
  background: var(--leaf-2);
  border: 1px solid var(--rule-2);
  border-radius: 2px;
  font-family: var(--mono);
  overflow: auto; white-space: pre-wrap; word-break: break-word;
}
code { padding: 1px 6px; font-size: 12.5px; }
pre {
  padding: 16px 18px; margin: 0;
  font-size: 13px; line-height: 1.85; color: var(--ink-2);
}

/* ---------- 首页条目 ---------- */
.entry-list { border-top: 1px solid var(--rule); margin: 30px 0 70px; max-width: 780px; }
.entry {
  display: flex; align-items: flex-start; gap: 16px;
  padding: 26px 4px;
  border-bottom: 1px solid var(--rule);
  color: var(--ink);
}
.entry:hover { background: var(--leaf); color: var(--ink); }
.entry-body { flex: 1; min-width: 0; }
.entry-title {
  display: block;
  margin: 0 0 4px;
  font-family: var(--song); font-size: 23px; font-weight: 400; letter-spacing: 2px;
}
.entry-desc { display: block; margin: 0; color: var(--ink-3); font-size: 14.5px; }
.entry-go {
  display: inline-flex; align-items: center; gap: 6px;
  color: var(--celadon-deep); font-size: 14px; white-space: nowrap;
  padding-top: 8px;
}
.entry:hover .entry-go { color: var(--cinnabar); }
/* ---------- 焦点与动效 ---------- */
a:focus-visible, button:focus-visible, input:focus-visible, summary:focus-visible {
  outline: 2px solid var(--celadon-deep);
  outline-offset: 2px;
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}

/* ---------- 响应式 ---------- */
@media (max-width: 720px) {
  .wrap { padding: 0 18px; }
  .pagehead { padding: 24px 0 22px; }
  .pagetitle { font-size: 23px; letter-spacing: 1.5px; }
  .pagehead-inner { flex-direction: column; gap: 10px; }
  .backlink { padding-top: 0; order: -1; }
  .row { gap: 0; }
  /* 内联 style="flex:1" 会盖掉 flex-basis，用 min-width 强制换行 */
  .row > * { min-width: 100%; }
  .card { padding: 16px 16px; }
  .result-grid > div { padding-left: 0; border-left: 0; flex-basis: 100%; }
  .entry { padding: 20px 2px; flex-wrap: wrap; }
  .entry-title { font-size: 20px; }
  th, td { padding: 8px 10px; }
  pre { padding: 12px 12px; font-size: 12.5px; }
}
"""



def get_api_connection_status() -> str:
    amap_status = "已配置" if amap_is_configured() else "未配置"
    probe = kv_env_probe()
    probe_text = " / ".join(
        [
            f"KV_URL={'是' if probe['KV_REST_API_URL'] else '否'}",
            f"KV_TOKEN={'是' if probe['KV_REST_API_TOKEN'] else '否'}",
            f"KV_RO={'是' if probe['KV_REST_API_READ_ONLY_TOKEN'] else '否'}",
            f"REDIS_URL={'是' if probe['REDIS_URL'] else '否'}",
            f"REDIS_REST_URL={'是' if probe['REDIS_REST_URL'] else '否'}",
            f"REDIS_REST_TOKEN={'是' if probe['REDIS_REST_TOKEN'] else '否'}",
            f"UP_URL={'是' if probe['UPSTASH_REDIS_REST_URL'] else '否'}",
            f"UP_TOKEN={'是' if probe['UPSTASH_REDIS_REST_TOKEN'] else '否'}",
            f"UP_RO={'是' if probe['UPSTASH_REDIS_REST_READ_ONLY_TOKEN'] else '否'}",
        ]
    )
    kv_mode = kv_mode_text()
    amap_ok = amap_is_configured()
    kv_ok = kv_can_read()
    summary_bits = [
        ("高德行政区划" + ("已接通" if amap_ok else "未配置")),
        ("缓存" + ("已启用" if kv_ok else "未配置")),
    ]
    dot_cls = "dot" if (amap_ok and kv_ok) else "dot dot-off"
    return f"""
    <details class="status">
      <summary>
        <span class="{dot_cls}" aria-hidden="true"></span>
        <span>运行状态：{escape('，'.join(summary_bits))}</span>
        <span class="more">详情</span>
      </summary>
      <div class="status-body">
        <div class="kv"><span>高德行政区划</span><span class="{'ok' if amap_ok else 'error'}">{amap_status}</span></div>
        <div class="kv"><span>缓存（Vercel KV / Upstash）</span><span class="{kv_mode['class']}">{kv_mode['text']}</span></div>
        <p>运行时环境变量：<code>{escape(probe_text)}</code></p>
        <p>在 Vercel 控制台启用 Storage → Upstash → Redis 并绑定项目后，会自动注入 UPSTASH_REDIS_REST_URL 与 UPSTASH_REDIS_REST_TOKEN。</p>
      </div>
    </details>
    """


CHEVRON_LEFT = (
    '<svg class="ico" viewBox="0 0 20 20" aria-hidden="true">'
    '<path d="M11.5 5.5 L7 10 l4.5 4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
CHEVRON_RIGHT = (
    '<svg class="ico" viewBox="0 0 20 20" aria-hidden="true">'
    '<path d="M8.5 5.5 L13 10 l-4.5 4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def html_page(title: str, body: str, main_content_style: str = "") -> str:
    safe_title = escape(title)
    api_status = get_api_connection_status()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title}</title>
  <style>{SITE_CSS}</style>
</head>
<body>
  <header class="pagehead">
    <div class="wrap pagehead-inner">
      <div>
        <div class="pagetitle-row">
          <span class="seal" aria-hidden="true">宝</span>
          <h1 class="pagetitle">{safe_title}</h1>
        </div>
        <p class="pagelede">按常住人口测算柜机数与代理名额，并生成一份可直接用的投放简报。</p>
      </div>
      <a class="backlink" href="/">{CHEVRON_LEFT} 返回首页</a>
    </div>
  </header>
  <div class="wrap">
    {api_status}
    <main style="padding-top: 26px; {main_content_style}">
      {body}
    </main>
  </div>
</body>
</html>"""


def render_table(rows: list[dict]) -> str:
    if not rows:
        return "<div class='muted'>无数据</div>"
    headers = [k for k in rows[0].keys() if not k.startswith("_")]
    thead = "<tr>" + "".join(f"<th>{escape(str(h))}</th>" for h in headers) + "</tr>"
    tbody_rows = []
    for r in rows:
        tds = "".join(f"<td>{escape(str(r.get(h, '')))}</td>" for h in headers)
        tbody_rows.append(f"<tr>{tds}</tr>")
    tbody = "".join(tbody_rows)
    return f"<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>"


def kv_is_configured() -> bool:
    return kv_can_read()


def kv_rest_url() -> str:
    for k in ("KV_REST_API_URL", "REDIS_REST_URL", "UPSTASH_REDIS_REST_URL"):
        v = (os.getenv(k) or "").strip()
        if v:
            return v.rstrip("/")
    return ""


def kv_rest_write_token() -> str:
    for k in ("KV_REST_API_TOKEN", "REDIS_REST_TOKEN", "UPSTASH_REDIS_REST_TOKEN"):
        v = (os.getenv(k) or "").strip()
        if v:
            return v
    return ""


def kv_rest_read_token() -> str:
    for k in (
        "KV_REST_API_READ_ONLY_TOKEN",
        "REDIS_REST_READ_ONLY_TOKEN",
        "UPSTASH_REDIS_REST_READ_ONLY_TOKEN",
        "KV_REST_API_TOKEN",
        "REDIS_REST_TOKEN",
        "UPSTASH_REDIS_REST_TOKEN",
    ):
        v = (os.getenv(k) or "").strip()
        if v:
            return v
    return ""


def kv_can_read() -> bool:
    return (bool(kv_rest_url()) and bool(kv_rest_read_token())) or bool(kv_redis_url())


def kv_can_write() -> bool:
    return (bool(kv_rest_url()) and bool(kv_rest_write_token())) or bool(kv_redis_url())


def kv_mode_text() -> dict[str, str]:
    if kv_redis_url():
        return {"text": "已配置(Redis URL)", "class": "ok"}
    if kv_can_write():
        return {"text": "已配置(读写)", "class": "ok"}
    if kv_can_read():
        return {"text": "已配置(只读)", "class": "muted"}
    return {"text": "未配置(可选)", "class": "muted"}


def kv_redis_url() -> str:
    for k in ("REDIS_URL", "UPSTASH_REDIS_URL"):
        v = (os.getenv(k) or "").strip()
        if v:
            return v
    return ""


@lru_cache(maxsize=1)
def kv_redis_client():
    url = kv_redis_url()
    if not url:
        return None
    try:
        import redis  # type: ignore
    except Exception:
        return None
    try:
        return redis.Redis.from_url(url, socket_timeout=3, socket_connect_timeout=3, retry_on_timeout=True)
    except Exception:
        return None



def kv_call(command: str, *args: str, body: bytes | None = None, params: dict[str, str] | None = None) -> object | None:
    url = kv_rest_url()
    token = kv_rest_read_token()
    if not url or not token:
        client = kv_redis_client()
        if client is None:
            return None
        cmd = command.strip().lower()
        try:
            if cmd == "get" and len(args) >= 1:
                v = client.get(str(args[0]))
                if v is None:
                    return None
                if isinstance(v, bytes):
                    return v.decode("utf-8", errors="ignore")
                return str(v)
            if cmd == "set" and len(args) >= 1 and body is not None:
                ex = None
                if params and isinstance(params.get("EX"), str) and params["EX"].strip().isdigit():
                    ex = int(params["EX"].strip())
                ok = client.set(str(args[0]), body, ex=ex)
                return "OK" if ok else None
            if cmd == "lpush" and len(args) >= 1 and body is not None:
                client.lpush(str(args[0]), body)
                return 1
            if cmd == "ltrim" and len(args) >= 3:
                client.ltrim(str(args[0]), int(args[1]), int(args[2]))
                return 1
            if cmd == "lrange" and len(args) >= 3:
                items = client.lrange(str(args[0]), int(args[1]), int(args[2]))
                out: list[str] = []
                for it in items:
                    if isinstance(it, bytes):
                        out.append(it.decode("utf-8", errors="ignore"))
                    else:
                        out.append(str(it))
                return out
        except Exception:
            return None
        return None

    path = "/".join([quote(command.strip().lower(), safe=""), *(quote(str(a), safe="") for a in args)])
    full_url = f"{url}/{path}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        if body is None:
            resp = requests.get(full_url, headers=headers, params=params, timeout=6)
        else:
            resp = requests.post(full_url, headers=headers, params=params, data=body, timeout=6)
    except Exception:
        return None

    try:
        payload = resp.json()
    except Exception:
        return None

    if isinstance(payload, dict) and "error" in payload:
        return None
    if isinstance(payload, dict) and "result" in payload:
        return payload.get("result")
    return None


def kv_set_json(key: str, value: object, ex_seconds: int | None = None) -> None:
    if not kv_can_write():
        return
    body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    params = {"EX": str(int(ex_seconds))} if ex_seconds else None
    kv_call("set", key, body=body, params=params)


def kv_get_json(key: str) -> object | None:
    if not kv_can_read():
        return None
    raw = kv_call("get", key)
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def kv_set_text(key: str, value: str, ex_seconds: int | None = None) -> None:
    if not kv_can_write():
        return
    body = value.encode("utf-8")
    params = {"EX": str(int(ex_seconds))} if ex_seconds else None
    kv_call("set", key, body=body, params=params)


def kv_get_text(key: str) -> str | None:
    if not kv_can_read():
        return None
    raw = kv_call("get", key)
    if isinstance(raw, str) and raw:
        return raw
    return None


def kv_lpush_json(list_key: str, value: object, max_len: int = 50) -> None:
    if not kv_can_write():
        return
    body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    kv_call("lpush", list_key, body=body)
    kv_call("ltrim", list_key, "0", str(max_len - 1))


def kv_lrange_json(list_key: str, start: int, stop: int) -> list[object]:
    if not kv_can_read():
        return []
    raw = kv_call("lrange", list_key, str(start), str(stop))
    if not isinstance(raw, list):
        return []
    out: list[object] = []
    for item in raw:
        if not isinstance(item, str) or not item:
            continue
        try:
            out.append(json.loads(item))
        except Exception:
            continue
    return out


def amap_key() -> str | None:
    for k in ("AMAP_KEY", "GAODE_KEY", "AMAP_WEB_KEY"):
        v = (os.getenv(k) or "").strip()
        if v:
            return v
    return None


def amap_is_configured() -> bool:
    return bool(amap_key())


def amap_get_json(params: dict[str, str]) -> dict | None:
    key = amap_key()
    if not key:
        return None
    merged = dict(params)
    merged["key"] = key
    try:
        resp = requests.get("https://restapi.amap.com/v3/config/district", params=merged, timeout=6)
    except Exception:
        return None
    try:
        payload = resp.json()
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("status") != "1":
        return None
    return payload


def amap_get_poi_json(params: dict[str, str]) -> dict | None:
    key = amap_key()
    if not key:
        return None
    merged = dict(params)
    merged["key"] = key
    try:
        resp = requests.get("https://restapi.amap.com/v3/place/text", params=merged, timeout=6)
    except Exception:
        return None
    try:
        payload = resp.json()
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("status") != "1":
        return None
    return payload


def amap_poi_count(city: str, keyword: str) -> int | None:
    city_val = city.strip()
    kw_val = keyword.strip()
    if not city_val or not kw_val:
        return None

    cache_key = f"amap:poi:count:{city_val}:{kw_val}"
    if kv_is_configured():
        cached = kv_get_json(cache_key)
        if isinstance(cached, dict) and isinstance(cached.get("count"), int):
            return int(cached["count"])

    payload = amap_get_poi_json(
        {
            "keywords": kw_val,
            "city": city_val,
            "citylimit": "true",
            "children": "0",
            "offset": "1",
            "page": "1",
            "extensions": "base",
        }
    )
    if not payload:
        return None
    count_raw = payload.get("count")
    try:
        count = int(str(count_raw or "0").strip())
    except Exception:
        count = 0
    if kv_is_configured():
        kv_set_json(cache_key, {"count": count}, ex_seconds=60 * 60 * 24 * 14)
    return count


def amap_poi_samples(city: str, keyword: str, limit: int = 3) -> list[str]:
    city_val = city.strip()
    kw_val = keyword.strip()
    limit = max(1, min(int(limit), 10))
    if not city_val or not kw_val:
        return []

    cache_key = f"amap:poi:samples:{city_val}:{kw_val}:{limit}"
    if kv_is_configured():
        cached = kv_get_json(cache_key)
        if isinstance(cached, list):
            out: list[str] = []
            for it in cached:
                s = str(it or "").strip()
                if s:
                    out.append(s)
            if out:
                return out[:limit]

    payload = amap_get_poi_json(
        {
            "keywords": kw_val,
            "city": city_val,
            "citylimit": "true",
            "children": "0",
            "offset": str(limit),
            "page": "1",
            "extensions": "base",
        }
    )
    if not payload:
        return []
    pois = payload.get("pois")
    if not isinstance(pois, list) or not pois:
        return []

    out: list[str] = []
    for p in pois:
        if not isinstance(p, dict):
            continue
        name = str(p.get("name") or "").strip()
        if name:
            out.append(name)
        if len(out) >= limit:
            break

    if kv_is_configured() and out:
        kv_set_json(cache_key, out, ex_seconds=60 * 60 * 24 * 14)
    return out


def amap_build_poi_section(city: str) -> str:
    if not amap_is_configured():
        return ""
    city_val = city.strip()
    if not city_val:
        return ""

    items = [
        ("商场/购物中心", "商场"),
        ("餐饮", "餐厅"),
        ("医院", "医院"),
        ("学校", "学校"),
        ("地铁站", "地铁站"),
        ("景点", "景区"),
        ("写字楼", "写字楼"),
    ]
    lines: list[str] = []
    lines.append("（高德）POI 概览")
    ok_any = False
    for label, kw in items:
        cnt = amap_poi_count(city_val, kw)
        if cnt is None:
            continue
        ok_any = True
        samples = amap_poi_samples(city_val, kw, limit=3)
        if samples:
            lines.append(f"- {label}：{cnt:,}（例如：{'、'.join(samples)}）")
        else:
            lines.append(f"- {label}：{cnt:,}")
    if not ok_any:
        return ""
    lines.append("")
    return "\n".join(lines)


def insert_poi_after_section3(report: str, poi_section: str) -> str:
    base = (report or "").strip()
    poi = (poi_section or "").strip()
    if not poi:
        return report
    if not base:
        return poi + "\n"

    marker = "\n四、投放建议"
    idx = base.find(marker)
    if idx == -1:
        marker = "\n五、核心板块拆解"
        idx = base.find(marker)
    if idx == -1:
        return base.rstrip() + "\n\n" + poi + "\n"

    before = base[:idx].rstrip()
    after = base[idx:].lstrip()
    return before + "\n\n" + poi + "\n\n" + after + "\n"


def amap_district_search(keyword: str, limit: int = 10) -> list[dict[str, str]]:
    kw = keyword.strip()
    if not kw:
        return []

    cache_key = f"amap:district:search:{kw}:{limit}"
    if kv_is_configured():
        cached = kv_get_json(cache_key)
        if isinstance(cached, list):
            out: list[dict[str, str]] = []
            for item in cached:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()
                adcode = str(item.get("adcode") or "").strip()
                level = str(item.get("level") or "").strip()
                if name and adcode:
                    out.append({"name": name, "adcode": adcode, "level": level})
            if out:
                return out

    payload = amap_get_json(
        {
            "keywords": kw,
            "subdistrict": "0",
            "extensions": "base",
            "page": "1",
            "offset": str(max(1, min(limit, 50))),
        }
    )
    if not payload:
        return []
    districts = payload.get("districts")
    if not isinstance(districts, list):
        return []

    out: list[dict[str, str]] = []
    for d in districts:
        if not isinstance(d, dict):
            continue
        name = str(d.get("name") or "").strip()
        adcode = str(d.get("adcode") or "").strip()
        level = str(d.get("level") or "").strip()
        if name and adcode:
            out.append({"name": name, "adcode": adcode, "level": level})
        if len(out) >= limit:
            break

    if kv_is_configured() and out:
        kv_set_json(cache_key, out, ex_seconds=60 * 60 * 24 * 7)
    return out


def amap_district_detail(adcode_or_keyword: str, subdistrict: int = 0) -> dict | None:
    key = adcode_or_keyword.strip()
    if not key:
        return None

    cache_key = f"amap:district:detail:{key}:{int(bool(subdistrict))}"
    if kv_is_configured():
        cached = kv_get_json(cache_key)
        if isinstance(cached, dict) and str(cached.get("adcode") or "").strip():
            return cached

    payload = amap_get_json(
        {
            "keywords": key,
            "subdistrict": "1" if subdistrict else "0",
            "extensions": "base",
            "page": "1",
            "offset": "1",
        }
    )
    if not payload:
        return None
    districts = payload.get("districts")
    if not isinstance(districts, list) or not districts:
        return None
    d0 = districts[0]
    if not isinstance(d0, dict):
        return None
    if kv_is_configured():
        kv_set_json(cache_key, d0, ex_seconds=60 * 60 * 24 * 30)
    return d0


def pick_best_wikidata_qid(name: str, candidates: list[planner.WikidataCandidate]) -> str | None:
    target = name.strip()
    if not target or not candidates:
        return None

    best_qid: str | None = None
    best_score = -1
    for c in candidates:
        label = (c.label or "").strip()
        desc = (c.description or "").strip()
        score = 0
        if label == target:
            score += 50
        if "中国" in desc or "中华人民共和国" in desc:
            score += 12
        if any(k in desc for k in ("省", "市", "县", "区", "自治州", "地区", "乡", "镇", "街道")):
            score += 8
        if any(k in label for k in ("省", "市", "县", "区", "自治州", "地区", "乡", "镇", "街道")):
            score += 4
        if c.qid and c.qid.startswith("Q"):
            score += 1
        if score > best_score:
            best_score = score
            best_qid = c.qid
    return best_qid


def resolve_wikidata_qid_for_name(name: str) -> str | None:
    target = name.strip()
    if not target:
        return None

    cache_key = f"wikidata:resolve:{target}"
    if kv_is_configured():
        cached = kv_get_text(cache_key)
        if isinstance(cached, str) and cached.startswith("Q"):
            return cached

    try:
        candidates = planner.wikidata_search(target, limit=12, language="zh")
    except Exception:
        candidates = []

    qid = pick_best_wikidata_qid(target, candidates)
    if kv_is_configured() and qid and qid.startswith("Q"):
        kv_set_text(cache_key, qid, ex_seconds=60 * 60 * 24 * 30)
    return qid


def is_county_level_amap(level: str) -> bool:
    lv = (level or "").strip().lower()
    return lv in {"district", "street"}


def is_county_level_wikidata(label: str, description: str) -> bool:
    text = f"{label} {description}".strip()
    if not text:
        return False
    markers = ["自治县", "县级市", "市辖区", "旗", "自治旗", "林区", "县", "区"]
    return any(m in text for m in markers)


@app.get("/", response_class=HTMLResponse)
def site_home():
    entries = [
        ("榜", "国庆旅游热度榜", "去年人气、今年预测、机票紧张度、县域黑马，四张榜单一起看。", "/travel/", "进入榜单"),
        ("宝", "共享充电宝投放分析", "搜地区、按人口测算柜机数与代理名额、导出投放简报。", "/charger", "进入工具"),
    ]
    rows = "".join(
        f"""
      <a class="entry" href="{href}">
        <span class="seal" aria-hidden="true">{mark}</span>
        <span class="entry-body">
          <span class="entry-title">{escape(name)}</span>
          <span class="entry-desc">{escape(desc)}</span>
        </span>
        <span class="entry-go">{cta} {CHEVRON_RIGHT}</span>
      </a>"""
        for mark, name, desc, href, cta in entries
    )
    return HTMLResponse(content=f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>两件小工具 · 国庆旅游热度榜与充电宝投放分析</title>
  <style>{SITE_CSS}</style>
</head>
<body>
  <header class="pagehead home">
    <div class="wrap">
      <h1 class="pagetitle">两件小工具</h1>
      <p class="pagelede">一个查国庆旅游热度，一个算共享充电宝投放。都是轻量版，数据口径写在各自页面里。</p>
    </div>
  </header>
  <div class="wrap">
    <nav class="entry-list">{rows}
    </nav>
  </div>
</body>
</html>""")


@app.get("/charger", response_class=HTMLResponse)
def home(
    request: Request,
    query: str | None = None,
    code: str | None = None,
    qid: str | None = None,
    pop: str | None = None,
    include_subdiv: int = 0,
):
    query_val = (query or "").strip()
    code_val = (code or "").strip()
    qid_val = (qid or "").strip()
    pop_val = (pop or "").strip()
    include_subdiv_raw = 1 if include_subdiv else 0
    include_subdiv_provided = "include_subdiv" in request.query_params

    left_panel_content = """
<div class="card">
  <form method="get" action="/charger">
    <div class="step"><span class="step-n">一、</span>搜索地区</div>
    <input type="text" name="query" placeholder="例如：永康、北京、杭州西湖区" value="{query}" />
    <div style="margin-top:18px;"><button type="submit">搜索</button></div>
  </form>
</div>
""".format(query=escape(query_val))
    right_panel_content = ""

    if not query_val:
        if kv_is_configured():
            items = kv_lrange_json("history:queries", 0, 9)
            if items:
                links: list[str] = []
                seen: set[tuple[str, str]] = set()
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    item_qid = str(it.get("qid") or "").strip()
                    item_code = str(it.get("code") or "").strip()
                    item_name = str(it.get("name") or "").strip()
                    item_pop = it.get("population")
                    if not item_name or (not item_qid and not item_code):
                        continue
                    identity = item_code or item_qid
                    dedup_key = (identity, item_name)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)
                    if isinstance(item_pop, int) and item_pop > 0:
                        pop_param = f"&pop={quote(str(item_pop), safe='')}"
                    else:
                        pop_param = ""
                    if item_code:
                        id_param = f"&code={quote(item_code, safe='')}"
                    else:
                        id_param = f"&qid={quote(item_qid, safe='')}"
                    links.append(
                        f"<div><a href='/?query={quote(item_name, safe='')}{id_param}{pop_param}'>"
                        f"{escape(item_name)} <span class='muted'>({escape(item_code or item_qid)})</span>"
                        f"</a></div>"
                    )
                if links:
                    left_panel_content += "<div class='card'><div class='card-title'>最近查询</div><div>" + "".join(links) + "</div></div>"
        body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
        return html_page("共享充电宝投放分析工具", body)

    amap_candidates: list[dict[str, str]] = []
    wikidata_candidates: list[planner.WikidataCandidate] = []
    error = ""
    prefer_wikidata = bool(qid_val.startswith("Q") and not code_val)
    if amap_is_configured() and not prefer_wikidata:
        try:
            amap_candidates = amap_district_search(query_val, limit=10)
        except Exception:
            amap_candidates = []
    if not amap_candidates:
        try:
            wikidata_candidates = planner.wikidata_search(query_val, limit=10, language="zh")
        except Exception as e:
            error = str(e)

    if error:
        left_panel_content += f"<div class='card error'>联网搜索失败：{escape(error)}</div>"
        body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
        return html_page("共享充电宝投放分析工具", body)

    if not amap_candidates and not wikidata_candidates:
        left_panel_content += "<div class='card muted'>未找到匹配项，请换个关键词再试。</div>"
        body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
        return html_page("共享充电宝投放分析工具", body)

    left_panel_content += """
<div class="card">
  <form method="get" action="/charger">
    <div class="step"><span class="step-n">二、</span>选择最匹配项</div>
    <input type="hidden" name="query" value="{query}" />
""".format(query=escape(query_val))

    selection_mode = "wikidata" if prefer_wikidata else ("amap" if amap_candidates else "wikidata")
    default_include_subdiv = 1
    if selection_mode == "amap":
        selected = None
        if code_val:
            selected = next((c for c in amap_candidates if str(c.get("adcode") or "").strip() == code_val), None)
        if selected is None and amap_candidates:
            selected = amap_candidates[0]
        level = str((selected or {}).get("level") or "").strip()
        default_include_subdiv = 0 if is_county_level_amap(level) else 1
    else:
        selected = None
        if qid_val:
            selected = next((c for c in wikidata_candidates if c.qid == qid_val), None)
        if selected is None and wikidata_candidates:
            selected = wikidata_candidates[0]
        label = (selected.label if selected else "").strip()
        desc = (selected.description if selected else "").strip()
        default_include_subdiv = 0 if is_county_level_wikidata(label, desc) else 1

    include_subdiv_effective = include_subdiv_raw if include_subdiv_provided else default_include_subdiv
    if selection_mode == "amap":
        for idx, c in enumerate(amap_candidates):
            adcode = str(c.get("adcode") or "").strip()
            name = str(c.get("name") or "").strip()
            level = str(c.get("level") or "").strip()
            if not adcode or not name:
                continue
            checked = "checked" if (code_val and adcode == code_val) or (not code_val and idx == 0) else ""
            level_text = f"{escape(level)} / " if level else ""
            left_panel_content += (
                f"<label>"
                f"<input type='radio' name='code' value='{escape(adcode)}' {checked} /> "
                f"{escape(name)} <span class='muted'>({level_text}{escape(adcode)})</span>"
                f"</label>"
            )
    else:
        for idx, c in enumerate(wikidata_candidates):
            checked = "checked" if (qid_val and c.qid == qid_val) or (not qid_val and idx == 0) else ""
            desc = f" - {c.description}" if c.description else ""
            left_panel_content += (
                f"<label>"
                f"<input type='radio' name='qid' value='{escape(c.qid)}' {checked} /> "
                f"{escape(c.label)}{escape(desc)} <span class='muted'>({escape(c.qid)})</span>"
                f"</label>"
            )

    checked = "checked" if include_subdiv_effective else ""
    left_panel_content += """
    <div class="step" style="margin-top:24px;"><span class="step-n">三、</span>人口（可留空自动查）</div>
    <input type="text" name="pop" placeholder="例如：100万、350000、0.35亿（留空自动查询）" value="{pop}" />
    <div style="margin-top:14px;">
      <input type="hidden" name="include_subdiv" value="0" />
      <label><input type="checkbox" name="include_subdiv" value="1" {checked} /> 拉取下一级行政区划（可能较慢）</label>
    </div>
    <div style="margin-top:18px;"><button type="submit">开始测算</button></div>
  </form>
</div>
""".format(pop=escape(pop_val), checked=checked)

    selected_code = ""
    selected_qid = ""
    selected_name = query_val
    resolved_qid: str | None = None
    if selection_mode == "amap":
        selected_code = code_val or str(amap_candidates[0].get("adcode") or "").strip()
        if not selected_code:
            body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
            return html_page("共享充电宝投放分析工具", body)
        detail = amap_district_detail(selected_code, subdistrict=1 if include_subdiv_effective else 0) or {}
        selected_name = str(detail.get("name") or query_val).strip() or query_val
        if qid_val.startswith("Q"):
            resolved_qid = qid_val
        else:
            resolved_qid = resolve_wikidata_qid_for_name(selected_name)
        if resolved_qid:
            selected_qid = resolved_qid
    else:
        selected_qid = qid_val or wikidata_candidates[0].qid
        resolved_qid = selected_qid if selected_qid.startswith("Q") else None
        selected_name = query_val

    population: int | None = None
    if pop_val:
        try:
            population = planner.parse_population(pop_val)
        except Exception as e:
            left_panel_content += f"<div class='card error'>人口解析失败：{escape(str(e))}</div>"
            body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
            return html_page("共享充电宝投放分析工具", body)
    else:
        if resolved_qid:
            try:
                population = planner.wikidata_population(resolved_qid)
            except Exception as e:
                left_panel_content += f"<div class='card error'>自动获取人口失败：{escape(str(e))}</div>"
                body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
                return html_page("共享充电宝投放分析工具", body)

    if population is None:
        if selection_mode == "amap" and not resolved_qid:
            left_panel_content += "<div class='card error'>已从高德获取行政区划，但未匹配到可用的人口来源，请手动输入人口数。</div>"
        else:
            left_panel_content += "<div class='card error'>无法自动获取该地区人口，请手动输入人口数。</div>"
        body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
        return html_page("共享充电宝投放分析工具", body)

    population_int = int(population)
    calc_id = selected_qid if selected_qid else f"code:{selected_code}"
    cache_key = f"calc:{calc_id}:{population_int}:{planner.PEOPLE_PER_CABINET}:{planner.CABINETS_PER_AGENT}"
    cached = kv_get_json(cache_key) if kv_is_configured() else None
    if isinstance(cached, dict) and cached.get("id") == calc_id and cached.get("population") == population_int:
        plan = planner.plan_for_area(str(cached.get("name") or selected_name), population_int)
    else:
        plan = planner.plan_for_area(selected_name, population_int)
    rows = [
        {
            "地区": plan.name,
            "人口(万)": f"{plan.population / 10_000:.2f}",
            "柜机数": f"{plan.cabinets_needed}",
            "代理名额": f"{plan.agent_slots}",
            "_qid": selected_qid or selected_code,
        }
    ]

    entity = None
    if resolved_qid:
        try:
            entity = planner.wikidata_first_entity(resolved_qid, language=planner.WIKIDATA_LANG)
        except Exception:
            entity = None

    if include_subdiv_effective and entity:
        try:
            children = planner.wikidata_entity_list_qids_labels(entity, "P150", limit=40)
        except Exception:
            children = []

        for child_qid, child_label in children:
            try:
                child_pop = planner.wikidata_population(child_qid)
            except Exception:
                child_pop = None
            if child_pop is None:
                continue
            child_plan = planner.plan_for_area(child_label, int(child_pop))
            rows.append(
                {
                    "地区": child_plan.name,
                    "人口(万)": f"{child_plan.population / 10_000:.2f}",
                    "柜机数": f"{child_plan.cabinets_needed}",
                    "代理名额": f"{child_plan.agent_slots}",
                    "_qid": child_qid,
                }
            )

    if kv_is_configured():
        ts = int(time.time())
        kv_set_json(
            cache_key,
            {
                "id": calc_id,
                "qid": selected_qid,
                "code": selected_code,
                "name": plan.name,
                "population": plan.population,
                "cabinets": plan.cabinets_needed,
                "agents": plan.agent_slots,
                "people_per_cabinet": planner.PEOPLE_PER_CABINET,
                "cabinets_per_agent": planner.CABINETS_PER_AGENT,
                "include_subdiv": include_subdiv_effective,
                "ts": ts,
            },
            ex_seconds=60 * 60 * 24 * 30,
        )
        newest = kv_lrange_json("history:queries", 0, 0)
        should_push = True
        if newest and isinstance(newest[0], dict):
            prev = newest[0]
            prev_qid = str(prev.get("qid") or "").strip()
            prev_code = str(prev.get("code") or "").strip()
            prev_name = str(prev.get("name") or "").strip()
            prev_pop = prev.get("population")
            if (
                prev_qid == str(selected_qid or "").strip()
                and prev_code == str(selected_code or "").strip()
                and prev_name == str(plan.name or "").strip()
                and isinstance(prev_pop, int)
                and prev_pop == int(plan.population)
            ):
                should_push = False
        if should_push:
            kv_lpush_json(
                "history:queries",
                {"qid": selected_qid, "code": selected_code, "name": plan.name, "population": plan.population, "ts": ts},
                max_len=60,
            )

    left_panel_content += f"""
<div class="card">
  <div class="card-title">测算结果</div>
  <div class="result-grid">
    <div><div class="k">人口（万）</div><div class="v">{escape(f"{plan.population / 10_000:,.2f}")}</div></div>
    <div><div class="k">建议柜机数</div><div class="v">{escape(f"{plan.cabinets_needed:,}")}</div></div>
    <div><div class="k">代理名额</div><div class="v">{escape(f"{plan.agent_slots:,}")}</div></div>
  </div>
  <div style="margin-top:20px;">{render_table(rows)}</div>
</div>
"""
    report_content = ""
    report_qid = selected_qid or None
    poi_city = selected_code or selected_name
    poi_section = amap_build_poi_section(poi_city) if poi_city else ""

    if report_qid and plan.name and plan.population:
        report_key = f"report:v2:{report_qid}:{selected_code}:{plan.population}:{planner.PEOPLE_PER_CABINET}:{planner.CABINETS_PER_AGENT}"
        if kv_is_configured():
            cached = kv_get_text(report_key)
            if cached:
                report_content = cached
        if not report_content:
            report_content = planner.build_area_report(plan=plan, qid=report_qid, entity=entity)
            if poi_section:
                report_content = insert_poi_after_section3(report_content, poi_section)
            if kv_is_configured() and report_content:
                kv_set_text(report_key, report_content, ex_seconds=60 * 60 * 24 * 30)
    else:
        if poi_section:
            report_content = poi_section

    right_panel_content = f"""
<div class="card">
  <div class="card-title">投放简报</div>
  <pre>{escape(report_content)}</pre>
</div>
"""
    body = f"""
<div class="row">
  <div style="flex:1;">{left_panel_content}</div>
  <div style="flex:1;">{right_panel_content}</div>
</div>
"""
    return html_page("共享充电宝投放分析工具", body)
