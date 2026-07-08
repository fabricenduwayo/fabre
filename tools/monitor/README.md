# Snorkel submission monitor

Polls Terminus submissions **every 90 minutes**. Sends Telegram alerts, then
optionally auto-fixes `NEEDS_REVISION` tasks via Composer (only when enabled).

All config: **`tools/monitor/.env`**. State: **`.review-scratch/monitor/`**.

## Quick start

```bash
cd /Users/fabrice-mac-mini/Documents/snorkel-ai/tools/monitor
cp .env.example .env    # if needed — fill CURSOR_API_KEY + Telegram
./install-hourly-launchd.sh
./install-command-listener.sh
./test-notify.sh
```

## Token savings (recommended defaults)

```bash
AUTO_AGENT_FIX=0          # scheduled runs = scan + notify only
ORACLE_PRECHECK=1         # run harbor oracle before Cursor; skip agent if already 1.0
MAX_FIXES_PER_RUN=1
MAX_FIXES_PER_DAY=8
MAX_AGENT_MINUTES_PER_DAY=180
```

Trigger Cursor only when you want it:

- Telegram: `run` or `run repair-flask-signalbox-configs`
- CLI: `./terminus-control.sh run`

Set `AUTO_AGENT_FIX=1` for fully unattended agent fixes on schedule.

## Telegram commands

| Command | Action |
|---------|--------|
| `status` | Monitor + health + queue |
| `queue` | Fix queue + skip reasons |
| `health` / `docker` | Docker, stb, git, bridges |
| `summary` | Today's daily summary |
| `start` / `stop` | Enable/disable scheduled monitor |
| `pause 6h` / `pause 30m` | Pause fixes (hours or minutes) |
| `resume` | Clear pause |
| `run` | One fix cycle (uses Cursor) |
| `run <task-folder>` | Fix one task only |
| `dry-run` | Scan only, no agent |
| `exclude <task>` | Add to review_exclusions |
| `unexclude <task>` | Remove exclusion |
| `reset <task>` | Clear state.json entry for retry |
| `skip <task>` | Skip one task next scheduled run |
| `ui <task>` | Finish-in-UI checklist |
| `draft <task>` | Draft platform explanation text |
| `help` | Command list |

## Notifications

- **Digest mode** (`NOTIFY_DIGEST=1`) — one Telegram message per run
- **Quiet hours** (`NOTIFY_QUIET_HOURS=1`) — suppress routine alerts overnight
- **Priority only** (`NOTIFY_PRIORITY_ONLY=1`) — errors/resubmits only
- **Daily summary** — once per UTC day at `NOTIFY_DAILY_SUMMARY_HOUR_UTC` (default 23)

## What gets auto-fixed

Only `NEEDS_REVISION` with failing eval gates, local folder on disk, not excluded,
under attempt cap, not green-gate UI-only, oracle precheck not already passing.

## Manual

```bash
./run-hourly.sh --dry-run
./run-hourly.sh --force
./run-hourly.sh --folder repair-express-trivia-worker
./terminus-control.sh status
./stop-all.sh
./status-all.sh
```

## Logs

- `.review-scratch/monitor/monitor.log`
- `.review-scratch/monitor/state.json`
- `.review-scratch/monitor/last-run-report.json`

## Uninstall

```bash
./stop-all.sh
rm ~/Library/LaunchAgents/com.snorkel.submission-monitor.plist
rm ~/Library/LaunchAgents/com.snorkel.terminus-command-listener.plist
```
