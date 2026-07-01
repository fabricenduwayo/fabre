# Hourly Snorkel submission monitor

Polls Terminus submissions every hour. **One task auto-fixed per hour** when
eligible; scans every run but respects a 1-hour cooldown between fixes.

Every agent run injects the current rules and docs:

- `.cursor/rules/terminus.mdc`
- `.cursor/rules/final-check.mdc`
- `.cursor/rules/terminus-submission-hardening.mdc`
- `docs/terminus-lessons-learned.md`
- `docs/New submission requirements.txt`

## What gets auto-fixed

Only `NEEDS_REVISION` tasks that pass all of:

- Local folder exists on disk
- **Not** in `tools/monitor/review_exclusions.json` (manual review queue)
- **Not** currently or previously `REVIEW_PENDING` (those IDs are added to exclusions automatically each run)
- **Not** a green eval with only AutoEval boilerplate failure (difficulty, instruction sufficiency, solvability, quality checks all pass — see `feedback_gates.py`)
- Feedback hash not already fixed in `state.json`

Skipped states: `EVALUATION_PENDING`, `REVIEW_PENDING`, `OFFERED`, `ACCEPTED`.

## One fix per hour

Each successful fix (or error during fix) sets `next_fix_allowed_after` in
`.review-scratch/monitor/state.json` (default 3600s via `FIX_COOLDOWN_SEC`).
The next hourly trigger scans the queue but waits until cooldown expires before
starting another agent. Use `--force` to bypass cooldown (exclusions still apply).

To re-enable auto-fix for a task you reviewed manually, delete its entry from
`review_exclusions.json`.

## One-time setup

```bash
cd /Users/fabrice-mac-mini/Documents/snorkel-ai/tools/monitor
chmod +x install-hourly-launchd.sh run-hourly.sh
./install-hourly-launchd.sh
```

Then edit `tools/monitor/.env` and set `CURSOR_API_KEY` from
[Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations).

Verify `stb login` already works (Snorkel auth persists on disk).

## Manual test

```bash
# Check submissions, write prompt preview, no agent call
./run-hourly.sh --dry-run

# Live fix (max 1 task per run by default)
./run-hourly.sh
```

## Notifications

**Mac banners alone do not sync to iPhone** — script notifications stay on the Mac.
For your phone, use one of these:

### Option A: iMessage yourself (same iCloud — easiest if Messages is set up)

In `tools/monitor/.env`:

```bash
NOTIFY_IMESSAGE=1
IMESSAGE_TO=+15551234567    # or your @icloud.com / @me.com email
```

Messages must be signed in on this Mac with the same Apple ID as your iPhone.
The first run may prompt: **System Settings → Privacy → Automation** — allow
`osascript` or `run-hourly.sh` to control Messages.

Test:

```bash
./test-phone-notify.sh
```

### Option B: ntfy (most reliable for overnight launchd runs)

1. Install [ntfy](https://ntfy.sh) on your iPhone (App Store)
2. Subscribe to a secret topic name
3. In `.env`:

```bash
NOTIFY_NTFY=1
NTFY_TOPIC=your-secret-topic-name
```

### Option C: Slack on your phone

```bash
NOTIFY_SLACK=1
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### What gets sent

| Event | Phone message includes |
|-------|------------------------|
| Fix started | Task name + platform issue |
| Resubmitted | State, oracle, static checks, change summary |
| Error | Failure reason |

Full JSON: `.review-scratch/monitor/last-run-report.json`

Set `NOTIFY_ON_IDLE=1` for a ping when nothing needs fixing (off by default).

## Unattended tomorrow

The Mac must be **on** and your user **logged in** (screen lock is fine; full
logout stops LaunchAgents). Keep **Docker Desktop** running for oracle builds.

Recommended: System Settings → Lock Screen / Battery → prevent sleep while
plugged in, or leave the machine on power.

## Logs

- `/.review-scratch/monitor/monitor.log` — check/fix actions
- `/.review-scratch/monitor/state.json` — dedupe by feedback hash
- `/.review-scratch/monitor/launchd-stderr.log` — launchd errors

## iMessage start / stop (optional)

Text yourself from your iPhone to control the monitor (same Apple ID as this Mac):

| Message | Action |
|---------|--------|
| `start-terminus` | Enable hourly monitor + kick one run |
| `stop-terminus` | Disable hourly monitor |
| `status-terminus` | Reply with running/stopped + queue |
| `run-terminus` | One fix cycle now |

Install the listener (separate from the hourly job):

```bash
cd /Users/fabrice-mac-mini/Documents/snorkel-ai/tools/monitor
chmod +x install-imessage-control.sh terminus-control.sh
./install-imessage-control.sh
```

**One-time:** System Settings → Privacy & Security → **Full Disk Access** → add
`tools/monitor/run-imessage-listener.sh` (Messages database read). Restart the
listener after granting:

```bash
launchctl kickstart -k gui/$(id -u)/com.snorkel.terminus-imessage-control
```

The listener ignores old messages on first start — send a **new** text after install.

Manual control without iMessage:

```bash
./terminus-control.sh status
./terminus-control.sh stop
./terminus-control.sh start
./terminus-control.sh run
```

Logs: `.review-scratch/monitor/control.log` and `imessage-listener-stderr.log`

## Uninstall

```bash
launchctl bootout gui/$(id -u)/com.snorkel.submission-monitor
launchctl bootout gui/$(id -u)/com.snorkel.terminus-imessage-control
rm ~/Library/LaunchAgents/com.snorkel.submission-monitor.plist
rm ~/Library/LaunchAgents/com.snorkel.terminus-imessage-control.plist
```

## Task → resubmit mapping

Edit `tools/monitor/tasks.json` when you add new submissions.
