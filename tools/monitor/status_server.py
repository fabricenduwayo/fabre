#!/Users/fabrice-mac-mini/.local/share/uv/tools/snorkelai-stb/bin/python3
"""One page submission status board, reachable from the phone on the LAN.

    python3 tools/monitor/status_server.py [--port 8787] [--ttl 120]

Binds 0.0.0.0 and prints the URL to open. Results are cached so refreshing on a
phone does not hammer the platform API; hit /?refresh=1 to force a fetch.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from snorkelai_stb.submission_utils import fetch_folder_names, list_submission_ids

PROJECT_ID = os.environ.get(
    "TERMINUS_PROJECT_ID", "bfe79c33-8ab0-4061-9849-08d3207c9927"
)

# Ordered worst-first so anything needing attention floats to the top.
STATE_ORDER = [
    "NEEDS_REVISION",
    "EVALUATION_PENDING",
    "REVIEW_PENDING",
    "OFFERED",
    "ACCEPTED",
]
STATE_NOTE = {
    "NEEDS_REVISION": "your move",
    "EVALUATION_PENDING": "autoeval running",
    "REVIEW_PENDING": "with a reviewer",
    "OFFERED": "unclaimed slot",
    "ACCEPTED": "done",
}

_lock = threading.Lock()
_cache: dict = {"at": 0.0, "subs": [], "error": ""}


def fetch(ttl: float, force: bool = False) -> dict:
    """Return cached submissions, refetching when the cache is older than ttl."""
    with _lock:
        fresh = time.time() - _cache["at"] < ttl
        if fresh and not force and _cache["subs"]:
            return dict(_cache)
        try:
            subs = list_submission_ids(project_id=PROJECT_ID)
            fetch_folder_names(subs, fetch_all=True)
            _cache.update(at=time.time(), subs=subs, error="")
        except Exception as exc:  # keep serving the last good snapshot
            _cache["error"] = f"{type(exc).__name__}: {exc}"
        return dict(_cache)


def shape(snapshot: dict) -> dict:
    """Flatten a snapshot into what the page renders."""
    rows = []
    for sub in snapshot["subs"]:
        state = sub.get("assignment_state") or "UNKNOWN"
        rows.append(
            {
                "id": sub.get("submission_id", ""),
                "folder": (sub.get("folder_name") or "").strip(),
                "state": state,
                "payment": sub.get("payment_status") or "",
                "created": sub.get("created_at") or "",
                "note": STATE_NOTE.get(state, ""),
            }
        )
    rank = {name: i for i, name in enumerate(STATE_ORDER)}
    rows.sort(key=lambda r: (rank.get(r["state"], 99), r["created"]), reverse=False)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1

    stamp = snapshot["at"]
    return {
        "rows": rows,
        "counts": [
            {"state": s, "n": counts[s]} for s in STATE_ORDER if s in counts
        ],
        "total": len(rows),
        "error": snapshot.get("error", ""),
        "updated": datetime.fromtimestamp(stamp, timezone.utc)
        .astimezone()
        .strftime("%H:%M:%S")
        if stamp
        else "never",
    }


PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Terminus submissions</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#14161a;--dim:#666e7a;--line:#e3e6ea}
@media (prefers-color-scheme:dark){
  :root{--bg:#0f1115;--card:#171a20;--ink:#e8eaed;--dim:#98a1ad;--line:#252a33}
}
*{box-sizing:border-box}
body{margin:0;padding:16px;background:var(--bg);color:var(--ink);
  font:16px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
header{display:flex;justify-content:space-between;align-items:baseline;gap:12px;
  margin-bottom:14px;flex-wrap:wrap}
h1{font-size:19px;margin:0;letter-spacing:-.01em}
.meta{color:var(--dim);font-size:13px}
.counts{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.pill{background:var(--card);border:1px solid var(--line);border-radius:999px;
  padding:5px 11px;font-size:13px;display:flex;gap:6px;align-items:center}
.pill b{font-variant-numeric:tabular-nums}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:13px 14px;margin-bottom:10px}
.top{display:flex;justify-content:space-between;align-items:center;gap:10px}
.folder{font-weight:600;word-break:break-word}
.folder.empty{color:var(--dim);font-weight:400;font-style:italic}
.badge{font-size:11px;font-weight:700;letter-spacing:.04em;padding:4px 9px;
  border-radius:6px;white-space:nowrap}
.NEEDS_REVISION{background:#fdecec;color:#a11}
.EVALUATION_PENDING{background:#e8f0fe;color:#14509a}
.REVIEW_PENDING{background:#f0e9fb;color:#5b2ea6}
.ACCEPTED{background:#e6f6ec;color:#186a3b}
.OFFERED{background:#eef0f3;color:#5a6472}
@media (prefers-color-scheme:dark){
  .NEEDS_REVISION{background:#3a1a1c;color:#ff9c9c}
  .EVALUATION_PENDING{background:#122a49;color:#8fbaff}
  .REVIEW_PENDING{background:#2a1f45;color:#c3a8ff}
  .ACCEPTED{background:#11331f;color:#7fd7a0}
  .OFFERED{background:#22262e;color:#9aa4b1}
}
.sub{color:var(--dim);font-size:12.5px;margin-top:7px;
  display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.sid{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11.5px}
.pay{border:1px solid var(--line);border-radius:5px;padding:1px 6px}
.err{background:#fdecec;color:#a11;border-radius:10px;padding:11px 13px;
  margin-bottom:14px;font-size:14px}
button{font:inherit;background:var(--card);color:var(--ink);cursor:pointer;
  border:1px solid var(--line);border-radius:8px;padding:6px 13px}
</style></head><body>
<header>
  <h1>Terminus submissions</h1>
  <div class="meta">updated <span id="up">-</span> - <button id="rf">Refresh</button></div>
</header>
<div id="err"></div>
<div class="counts" id="counts"></div>
<div id="list"></div>
<script>
const esc = s => (s||"").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function render(d){
  document.getElementById("up").textContent = d.updated;
  document.getElementById("err").innerHTML = d.error
    ? '<div class="err">' + esc(d.error) + ' (showing last good data)</div>' : '';
  document.getElementById("counts").innerHTML = d.counts.map(c =>
    '<span class="pill"><b>' + c.n + '</b> ' + esc(c.state.replace(/_/g," ").toLowerCase()) + '</span>'
  ).join("") + '<span class="pill"><b>' + d.total + '</b> total</span>';
  document.getElementById("list").innerHTML = d.rows.map(r =>
    '<div class="card"><div class="top">' +
      '<span class="folder' + (r.folder ? '' : ' empty') + '">' +
        esc(r.folder || "unclaimed") + '</span>' +
      '<span class="badge ' + esc(r.state) + '">' + esc(r.state.replace(/_/g," ")) + '</span>' +
    '</div><div class="sub">' +
      '<span>' + esc(r.note) + '</span>' +
      '<span>' + esc(r.created) + '</span>' +
      '<span class="pay">' + esc(r.payment.replace(/_/g," ").toLowerCase()) + '</span>' +
      '<span class="sid">' + esc(r.id.slice(0,8)) + '</span>' +
    '</div></div>'
  ).join("");
}
async function load(force){
  try{
    const r = await fetch("/api/status" + (force ? "?refresh=1" : ""), {cache:"no-store"});
    render(await r.json());
  }catch(e){ /* keep showing what we have */ }
}
document.getElementById("rf").onclick = () => load(true);
load(false);
setInterval(() => load(false), 60000);
</script></body></html>
"""


class Handler(BaseHTTPRequestHandler):
    ttl = 120.0

    def _send(self, body: bytes, ctype: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        force = "refresh=1" in self.path
        if path == "/api/status":
            data = shape(fetch(self.ttl, force=force))
            self._send(json.dumps(data).encode(), "application/json; charset=utf-8")
        elif path == "/":
            if force:
                fetch(self.ttl, force=True)
            self._send(PAGE.encode(), "text/html; charset=utf-8")
        else:
            self.send_error(404)

    def log_message(self, *args) -> None:
        pass


def lan_ip() -> str:
    """Best guess at the address the phone should use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--ttl", type=float, default=120.0, help="cache seconds")
    args = ap.parse_args()

    Handler.ttl = args.ttl
    snapshot = fetch(args.ttl, force=True)
    if snapshot["error"]:
        print(f"warning: first fetch failed - {snapshot['error']}")
    else:
        print(f"loaded {len(snapshot['subs'])} submissions")

    print(f"  this mac : http://localhost:{args.port}")
    print(f"  phone    : http://{lan_ip()}:{args.port}")
    print("ctrl-c to stop", flush=True)
    ThreadingHTTPServer(("0.0.0.0", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
