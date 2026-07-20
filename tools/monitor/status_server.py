#!/Users/fabrice-mac-mini/.local/share/uv/tools/snorkelai-stb/bin/python3
"""One page submission status board, reachable from the phone on the LAN.

    python3 tools/monitor/status_server.py [--port 8787] [--ttl 120]

Binds 0.0.0.0 and prints the URL to open. Results are cached so refreshing on a
phone does not hammer the platform API; the Refresh button forces a live fetch.
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
    rows.sort(key=lambda r: (rank.get(r["state"], 99), r["created"]))

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1

    stamp = snapshot["at"]
    return {
        "rows": rows,
        "counts": [{"state": s, "n": counts[s]} for s in STATE_ORDER if s in counts],
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
<meta name="color-scheme" content="dark">
<title>Terminus submissions</title>
<style>
:root{
  --bg:#0a0c10; --surface:#12161d; --raise:#1a2029; --line:#232b36;
  --ink:#e9edf4; --dim:#8b96a7; --faint:#5b6675;
  --needs:#ffa63d; --eval:#4d9cff; --review:#b08cff; --accept:#3ddc97; --offer:#6b7789;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased;padding-bottom:40px}

header{position:sticky;top:0;z-index:10;background:rgba(10,12,16,.86);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:14px 18px 0}
.hrow{display:flex;align-items:center;justify-content:space-between;gap:12px}
h1{margin:0;font-size:16px;font-weight:650;letter-spacing:-.01em}
.sub{color:var(--faint);font-size:12px;margin-top:2px}
.stamp{color:var(--dim);font-size:12px;font-variant-numeric:tabular-nums}

button{font:inherit;cursor:pointer;border-radius:9px;border:1px solid var(--line);
  background:var(--raise);color:var(--ink);padding:7px 13px;font-size:13px;
  display:inline-flex;align-items:center;gap:7px;transition:.15s}
button:active{transform:scale(.97)}
button[disabled]{opacity:.6;cursor:default}
.spin{width:12px;height:12px;border:2px solid var(--faint);border-top-color:var(--ink);
  border-radius:50%;animation:sp .7s linear infinite;display:none}
button.busy .spin{display:block}
@keyframes sp{to{transform:rotate(360deg)}}

.bar{height:2px;margin:12px -18px 0;background:transparent;overflow:hidden}
.bar.on{background:rgba(77,156,255,.18)}
.bar.on::after{content:"";display:block;height:100%;width:35%;background:var(--eval);
  animation:slide 1.1s ease-in-out infinite}
@keyframes slide{0%{margin-left:-35%}100%{margin-left:100%}}

.chips{display:flex;gap:7px;overflow-x:auto;padding:12px 18px 13px;
  scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;border:1px solid var(--line);background:var(--surface);
  color:var(--dim);border-radius:999px;padding:5px 11px;font-size:12.5px;
  display:flex;align-items:center;gap:6px;cursor:pointer;user-select:none;
  transition:.15s;white-space:nowrap}
.chip .dot{width:7px;height:7px;border-radius:50%;background:var(--c);opacity:.35}
.chip.on{color:var(--ink);border-color:var(--c);background:var(--raise)}
.chip.on .dot{opacity:1}
.chip b{font-variant-numeric:tabular-nums;font-weight:600}

main{padding:4px 18px 0;max-width:720px;margin:0 auto}
.card{position:relative;background:var(--surface);border:1px solid var(--line);
  border-radius:12px;padding:14px 15px 13px 18px;margin-bottom:9px;overflow:hidden}
.card::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--c)}
.ctop{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.folder{font-weight:600;font-size:14.5px;letter-spacing:-.01em;word-break:break-word;line-height:1.35}
.folder.none{color:var(--faint);font-weight:400;font-style:italic}
.state{flex:0 0 auto;font-size:10.5px;font-weight:700;letter-spacing:.07em;
  color:var(--c);display:flex;align-items:center;gap:5px;padding-top:2px}
.state .dot{width:6px;height:6px;border-radius:50%;background:var(--c)}
.meta{display:flex;flex-wrap:wrap;gap:5px 12px;margin-top:9px;
  color:var(--dim);font-size:12px}
.meta .id{color:var(--faint);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}
.note{color:var(--c);opacity:.85}

.sk{height:74px;border-radius:12px;margin-bottom:9px;border:1px solid var(--line);
  background:linear-gradient(90deg,var(--surface) 25%,var(--raise) 37%,var(--surface) 63%);
  background-size:400% 100%;animation:sh 1.3s ease infinite}
@keyframes sh{0%{background-position:100% 50%}100%{background-position:0 50%}}
.list.busy{opacity:.45;transition:.2s}
.err{background:rgba(255,166,61,.1);border:1px solid rgba(255,166,61,.3);
  color:var(--needs);border-radius:10px;padding:10px 13px;margin-bottom:12px;font-size:13px}
.empty{color:var(--faint);text-align:center;padding:34px 0;font-size:13.5px}
</style></head><body>

<header>
  <div class="hrow">
    <div>
      <h1>Terminus submissions</h1>
      <div class="sub">Terminus-2nd-Edition</div>
    </div>
    <div style="text-align:right">
      <button id="rf"><span class="spin"></span><span id="rfl">Refresh</span></button>
      <div class="stamp" id="up" style="margin-top:5px">-</div>
    </div>
  </div>
  <div class="bar" id="bar"></div>
  <div class="chips" id="chips"></div>
</header>

<main>
  <div id="err"></div>
  <div class="list" id="list"></div>
</main>

<script>
const COLOR = {NEEDS_REVISION:"var(--needs)",EVALUATION_PENDING:"var(--eval)",
  REVIEW_PENDING:"var(--review)",ACCEPTED:"var(--accept)",OFFERED:"var(--offer)"};
const KEY = "tsb-hidden";
let data = null, busy = false;
let hidden = new Set(JSON.parse(localStorage.getItem(KEY) || '["OFFERED"]'));

const esc = s => (s||"").replace(/[&<>"]/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const pretty = s => esc((s||"").replace(/_/g," ").toLowerCase());
const col = s => COLOR[s] || "var(--offer)";

function paintBusy(){
  document.getElementById("bar").className = "bar" + (busy ? " on" : "");
  const b = document.getElementById("rf");
  b.className = busy ? "busy" : "";
  b.disabled = busy;
  document.getElementById("rfl").textContent = busy ? "Loading" : "Refresh";
  document.getElementById("list").className = "list" + (busy && data ? " busy" : "");
}

function render(){
  paintBusy();
  const list = document.getElementById("list");
  if(!data){
    list.innerHTML = busy ? '<div class="sk"></div>'.repeat(4) : '';
    return;
  }
  document.getElementById("up").textContent = data.updated;
  document.getElementById("err").innerHTML = data.error
    ? '<div class="err">' + esc(data.error) + ' &middot; showing last good data</div>' : '';

  document.getElementById("chips").innerHTML = data.counts.map(c =>
    '<div class="chip ' + (hidden.has(c.state) ? '' : 'on') + '" data-s="' + c.state +
    '" style="--c:' + col(c.state) + '"><span class="dot"></span>' +
    pretty(c.state) + ' <b>' + c.n + '</b></div>').join("");

  const rows = data.rows.filter(r => !hidden.has(r.state));
  list.innerHTML = rows.length ? rows.map(r =>
    '<div class="card" style="--c:' + col(r.state) + '">' +
      '<div class="ctop">' +
        '<span class="folder' + (r.folder ? '' : ' none') + '">' +
          esc(r.folder || "unclaimed slot") + '</span>' +
        '<span class="state"><span class="dot"></span>' + pretty(r.state) + '</span>' +
      '</div>' +
      '<div class="meta">' +
        '<span class="note">' + esc(r.note) + '</span>' +
        '<span>' + esc(r.created) + '</span>' +
        '<span>' + pretty(r.payment) + '</span>' +
        '<span class="id">' + esc(r.id.slice(0,8)) + '</span>' +
      '</div></div>').join("")
    : '<div class="empty">Nothing to show &middot; every state is filtered out</div>';
}

document.getElementById("chips").onclick = e => {
  const chip = e.target.closest(".chip");
  if(!chip) return;
  const s = chip.dataset.s;
  hidden.has(s) ? hidden.delete(s) : hidden.add(s);
  localStorage.setItem(KEY, JSON.stringify([...hidden]));
  render();
};

async function load(force){
  if(busy) return;
  busy = true; render();
  try{
    const r = await fetch("/api/status" + (force ? "?refresh=1" : ""), {cache:"no-store"});
    data = await r.json();
  }catch(e){ /* keep whatever we had */ }
  busy = false; render();
}

document.getElementById("rf").onclick = () => load(true);
load(false);
setInterval(() => { if(!busy) load(false); }, 60000);
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
