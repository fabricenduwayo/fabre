# Snorkel submission monitor (every 2 hours)

Polls Terminus submissions **every 90 minutes**. Each run sends a status text
first (all states, changes since last run, what will be fixed, what needs
manual UI edits), then auto-fixes up to `MAX_FIXES_PER_RUN` (default 8)
`NEEDS_REVISION` tasks using Composer 2.5 via the Cursor SDK.

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
- **Not** green on the eval gates (difficulty ✅, solvable ✅, instruction
  sufficiency ✅, quality checks ✅ — see `feedback_gates.py`). Green tasks only
  need manual UI edits (explanations / rubric / paragraph nits); the monitor
  reports them in the status text as "finish in UI" and never touches the task
  content.
- Feedback hash not already fixed in `state.json`
- Fewer than `MAX_ATTEMPTS_PER_FEEDBACK` (default 2) agent attempts on the
  same unchanged feedback — prevents retry loops on a stuck task

Skipped states: `EVALUATION_PENDING`, `REVIEW_PENDING`, `OFFERED`, `ACCEPTED`.

## Run flow (every 90 minutes)

1. Status text to your phone before any work: state counts, state changes since
   the last run, the auto-fix queue, and the "finish in UI" list.
2. If Docker Desktop is down and fixes are queued, you get a "waiting for
   Docker" text and nothing runs (the oracle needs Docker).
3. Per task: "fix started" text → Composer 2.5 agent (fix, oracle to 1.0,
   revision bump, resubmit without reviewer) → "resubmitted" or "verify" text
   with oracle/static-check results and a diff stat.
4. "Run complete" text with the fixed count.

To re-enable auto-fix for a task you reviewed manually, delete its entry from
`review_exclusions.json`. To retry a task that hit the attempt cap, delete its
entry from `.review-scratch/monitor/state.json` `runs`.

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

# Live fix (max 8 tasks per run by default)
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
| Status (every run, before work) | State counts, changes since last run, fix queue, finish-in-UI list |
| Fix started | Task name + platform issue |
| Resubmitted | State, oracle, static checks, change summary |
| Waiting for Docker | Queue blocked until Docker Desktop is running |
| Error | Failure reason |
| Run complete | Fixed count + next check time |

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
