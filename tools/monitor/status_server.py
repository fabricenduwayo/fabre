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
<title>Terminus pipeline</title>
<style>
:root{
  --bg:#0d0d0c; --surface:#1a1a19; --raise:#222220; --raise2:#2a2a27;
  --line:#302f2b; --line2:#3c3b36;
  --ink:#ffffff; --ink2:#c3c2b7; --muted:#87867a; --faint:#61605a;
  /* validated status palette on the dark surface */
  --good:#0ca30c; --warn:#fab219; --review:#b18cf2; --info:#3987e5; --neutral:#8a8a80;
}
*{box-sizing:border-box}
html,body{margin:0}
body{
  background:
    radial-gradient(1100px 520px at 78% -8%, rgba(57,135,229,.10), transparent 60%),
    radial-gradient(900px 480px at 8% 0%, rgba(250,178,25,.06), transparent 55%),
    var(--bg);
  color:var(--ink); min-height:100vh; padding-bottom:44px;
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:900px;margin:0 auto;padding:0 16px}

header{position:sticky;top:0;z-index:20;
  background:linear-gradient(180deg,rgba(13,13,12,.94),rgba(13,13,12,.72));
  backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
.hin{max-width:900px;margin:0 auto;padding:15px 16px 0;
  display:flex;align-items:flex-start;justify-content:space-between;gap:14px}
.brand{display:flex;align-items:center;gap:11px}
.spark{width:30px;height:30px;border-radius:9px;flex:0 0 auto;position:relative;
  background:linear-gradient(150deg,#3987e5,#0ca30c);box-shadow:0 0 0 1px rgba(255,255,255,.06) inset}
.spark::after{content:"";position:absolute;inset:8px;border-radius:4px;
  background:var(--bg);box-shadow:0 0 12px rgba(57,135,229,.5)}
h1{margin:0;font-size:16px;font-weight:680;letter-spacing:-.02em}
.tag{color:var(--faint);font-size:12px;margin-top:1px;letter-spacing:.01em}
.right{text-align:right;flex:0 0 auto}
button{font:inherit;cursor:pointer;border-radius:10px;border:1px solid var(--line2);
  background:var(--raise);color:var(--ink);padding:7px 13px;font-size:13px;font-weight:520;
  display:inline-flex;align-items:center;gap:8px;transition:.15s}
button:hover{background:var(--raise2);border-color:#494840}
button:active{transform:scale(.97)}
button[disabled]{opacity:.55;cursor:default}
.spin{width:12px;height:12px;border:2px solid var(--faint);border-top-color:var(--ink);
  border-radius:50%;animation:sp .7s linear infinite;display:none}
button.busy .spin{display:block}
@keyframes sp{to{transform:rotate(360deg)}}
.stamp{color:var(--muted);font-size:11.5px;margin-top:6px;font-variant-numeric:tabular-nums}
.stamp b{color:var(--ink2);font-weight:600}

.bar{height:2px;margin-top:14px;background:transparent;overflow:hidden}
.bar.on{background:rgba(57,135,229,.16)}
.bar.on::after{content:"";display:block;height:100%;width:32%;
  background:linear-gradient(90deg,transparent,var(--info),transparent);
  animation:slide 1.1s ease-in-out infinite}
@keyframes slide{0%{margin-left:-40%}100%{margin-left:100%}}

/* pipeline funnel */
.flow{display:flex;align-items:stretch;gap:6px;margin:18px 0 6px;overflow-x:auto;
  scrollbar-width:none;padding-bottom:2px}
.flow::-webkit-scrollbar{display:none}
.stage{flex:1 1 0;min-width:112px;position:relative;text-align:left;
  background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:12px 13px 13px;cursor:pointer;transition:.16s;color:inherit;overflow:hidden}
.stage:hover{border-color:var(--line2);transform:translateY(-1px)}
.stage::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:var(--c);opacity:.9}
.stage.off{opacity:.4}
.stage.off .num{color:var(--muted)}
.stage.on{box-shadow:0 0 0 1px var(--c) inset, 0 6px 18px -12px var(--c)}
.srow{display:flex;align-items:center;gap:7px;color:var(--c)}
.glyph{font-size:13px;line-height:1;width:16px;text-align:center}
.slabel{font-size:11px;font-weight:640;letter-spacing:.05em;text-transform:uppercase;color:var(--ink2)}
.num{font-size:30px;font-weight:720;letter-spacing:-.03em;margin-top:6px;
  font-variant-numeric:tabular-nums;line-height:1}
.snote{color:var(--faint);font-size:11px;margin-top:3px}
.chev{flex:0 0 auto;align-self:center;color:var(--line2);font-size:15px;user-select:none}
.pulse::after{content:"";position:absolute;top:9px;right:10px;width:7px;height:7px;border-radius:50%;
  background:var(--warn);box-shadow:0 0 0 0 rgba(250,178,25,.6);animation:pulse 1.8s ease-out infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(250,178,25,.5)}70%{box-shadow:0 0 0 8px rgba(250,178,25,0)}100%{box-shadow:0 0 0 0 rgba(250,178,25,0)}}

.hint{color:var(--faint);font-size:11.5px;margin:2px 2px 14px}

/* cards */
.err{background:rgba(250,178,25,.10);border:1px solid rgba(250,178,25,.32);
  color:var(--warn);border-radius:12px;padding:10px 13px;margin-bottom:12px;font-size:13px}
.list.busy{opacity:.5;transition:.2s}
.card{position:relative;background:var(--surface);border:1px solid var(--line);
  border-radius:14px;padding:14px 15px 13px 18px;margin-bottom:10px;overflow:hidden;transition:.16s}
.card:hover{border-color:var(--line2);transform:translateY(-1px)}
.card::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--c)}
.ctop{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.folder{font-weight:640;font-size:15px;letter-spacing:-.01em;word-break:break-word;line-height:1.35}
.folder.none{color:var(--faint);font-weight:400;font-style:italic}
.pill{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;padding:4px 9px 4px 8px;
  border-radius:999px;font-size:11px;font-weight:640;letter-spacing:.03em;
  color:var(--c);background:color-mix(in srgb, var(--c) 15%, transparent);
  border:1px solid color-mix(in srgb, var(--c) 34%, transparent);white-space:nowrap}
.meta{display:flex;flex-wrap:wrap;gap:6px 13px;margin-top:10px;color:var(--muted);font-size:12px;align-items:center}
.meta .id{color:var(--faint);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}
.pay{border:1px solid var(--line2);border-radius:6px;padding:1px 7px;font-size:11px;color:var(--ink2)}
.pay.win{color:var(--good);border-color:color-mix(in srgb,var(--good) 40%,transparent);
  background:color-mix(in srgb,var(--good) 12%,transparent)}
.empty{color:var(--faint);text-align:center;padding:38px 0;font-size:13.5px}

.sk{height:78px;border-radius:14px;margin-bottom:10px;border:1px solid var(--line);
  background:linear-gradient(90deg,var(--surface) 25%,var(--raise) 37%,var(--surface) 63%);
  background-size:400% 100%;animation:sh 1.3s ease infinite}
@keyframes sh{0%{background-position:100% 50%}100%{background-position:0 50%}}

@media (max-width:600px){
  .chev{display:none}
  .flow{flex-wrap:wrap}
  .stage{flex:1 1 44%;min-width:0}
  .num{font-size:26px}
}
</style></head><body>

<header>
  <div class="hin">
    <div class="brand">
      <div class="spark"></div>
      <div>
        <h1>Terminus</h1>
        <div class="tag">submission pipeline</div>
      </div>
    </div>
    <div class="right">
      <button id="rf"><span class="spin"></span><span id="rfl">Refresh</span></button>
      <div class="stamp">updated <b id="up">-</b></div>
    </div>
  </div>
  <div class="bar" id="bar"></div>
</header>

<div class="wrap">
  <div class="flow" id="flow"></div>
  <div class="hint" id="hint"></div>
  <div id="err"></div>
  <div class="list" id="list"></div>
</div>

<script>
const STATES = {
  OFFERED:            {label:"Offered",    note:"unclaimed",        color:"var(--neutral)", glyph:"\\u25CB"},
  EVALUATION_PENDING: {label:"Evaluating", note:"autoeval running", color:"var(--info)",    glyph:"\\u25D0"},
  NEEDS_REVISION:     {label:"Needs you",  note:"your move",        color:"var(--warn)",    glyph:"\\u25C6"},
  REVIEW_PENDING:     {label:"In review",  note:"with a reviewer",  color:"var(--review)",  glyph:"\\u25D1"},
  ACCEPTED:           {label:"Accepted",   note:"done",             color:"var(--good)",    glyph:"\\u2713"},
};
const PIPELINE = ["OFFERED","EVALUATION_PENDING","NEEDS_REVISION","REVIEW_PENDING","ACCEPTED"];
const KEY = "tsb-hidden-v2";
let data = null, busy = false;
let hidden = new Set(JSON.parse(localStorage.getItem(KEY) || '["OFFERED"]'));

const esc = s => (s||"").replace(/[&<>"]/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const meta = s => STATES[s] || {label:s, note:"", color:"var(--neutral)", glyph:"\\u25CB"};
const save = () => localStorage.setItem(KEY, JSON.stringify([...hidden]));

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
    document.getElementById("flow").innerHTML = "";
    list.innerHTML = busy ? '<div class="sk"></div>'.repeat(4) : "";
    return;
  }
  document.getElementById("up").textContent = data.updated;
  document.getElementById("err").innerHTML = data.error
    ? '<div class="err">' + esc(data.error) + ' &middot; showing last good data</div>' : '';

  const cnt = {}; (data.counts||[]).forEach(c => cnt[c.state] = c.n);

  document.getElementById("flow").innerHTML = PIPELINE.map((s, i) => {
    const m = meta(s), n = cnt[s] || 0, on = !hidden.has(s);
    const attn = s === "NEEDS_REVISION" && n > 0 ? " pulse" : "";
    const tile =
      '<button class="stage ' + (on ? 'on' : 'off') + attn + '" data-s="' + s +
        '" style="--c:' + m.color + '">' +
        '<div class="srow"><span class="glyph">' + m.glyph + '</span>' +
        '<span class="slabel">' + esc(m.label) + '</span></div>' +
        '<div class="num">' + n + '</div>' +
        '<div class="snote">' + esc(m.note) + '</div>' +
      '</button>';
    const chev = i < PIPELINE.length - 1 ? '<span class="chev">\\u203A</span>' : '';
    return tile + chev;
  }).join("");

  const shown = data.rows.filter(r => !hidden.has(r.state));
  document.getElementById("hint").textContent =
    shown.length + " of " + data.total + " shown \\u00B7 tap a stage to filter";

  list.innerHTML = shown.length ? shown.map(r => {
    const m = meta(r.state);
    const win = /PAYOUT/i.test(r.payment);
    return '<div class="card" style="--c:' + m.color + '">' +
      '<div class="ctop">' +
        '<span class="folder' + (r.folder ? '' : ' none') + '">' +
          esc(r.folder || "unclaimed slot") + '</span>' +
        '<span class="pill"><span class="glyph">' + m.glyph + '</span>' + esc(m.label) + '</span>' +
      '</div>' +
      '<div class="meta">' +
        '<span>' + esc(r.note) + '</span>' +
        '<span>' + esc(r.created) + '</span>' +
        (r.payment ? '<span class="pay' + (win ? ' win' : '') + '">' +
           esc(r.payment.replace(/_/g," ").toLowerCase()) + '</span>' : '') +
        '<span class="id">' + esc(r.id.slice(0,8)) + '</span>' +
      '</div></div>';
  }).join("") : '<div class="empty">Nothing here \\u00B7 every stage is filtered out</div>';
}

document.getElementById("flow").onclick = e => {
  const st = e.target.closest(".stage");
  if(!st) return;
  const s = st.dataset.s;
  hidden.has(s) ? hidden.delete(s) : hidden.add(s);
  save(); render();
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
