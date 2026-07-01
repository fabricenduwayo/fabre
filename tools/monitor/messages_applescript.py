"""Read recent iMessages via AppleScript (no Full Disk Access needed)."""

from __future__ import annotations

import subprocess


def _run_applescript(script: str) -> str:
    proc = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "AppleScript failed")
    return proc.stdout


def fetch_recent_messages_lines(limit_per_chat: int = 3) -> list[tuple[str, str]]:
    """Return (message_id, text) for recent messages (any direction).

    Texts from your iPhone to yourself often arrive as *incoming* on the Mac.
    """
    sep_rec = chr(30)
    sep_field = chr(31)
    script = f"""
tell application "Messages"
    set outText to ""
    repeat with aChat in chats
        try
            set chatMessages to messages of aChat
            set msgCount to count of chatMessages
            if msgCount > 0 then
                set endIdx to msgCount - {max(0, limit_per_chat - 1)}
                if endIdx < 1 then set endIdx to 1
                repeat with i from msgCount to endIdx by -1
                    try
                        set aMessage to item i of chatMessages
                        set mid to id of aMessage as text
                        set body to ""
                        try
                            set body to text of aMessage
                        end try
                        if body is not missing value and body is not "" then
                            set outText to outText & mid & (ASCII character {ord(sep_field)}) & body & (ASCII character {ord(sep_rec)})
                        end if
                    end try
                end repeat
            end if
        end try
    end repeat
    return outText
end tell
"""
    raw = _run_applescript(script)
    if not raw.strip():
        return []
    out: list[tuple[str, str]] = []
    for rec in raw.split(sep_rec):
        rec = rec.strip()
        if not rec or sep_field not in rec:
            continue
        mid, _, body = rec.partition(sep_field)
        out.append((mid.strip(), body.strip()))
    return out
