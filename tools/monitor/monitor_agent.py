"""Cursor SDK agent — cloud (default) or local runtime for the submission monitor."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

DEFAULT_CURSOR_MODEL = "composer-2.5"
DEFAULT_RUNTIME = "cloud"

KNOWN_COMPOSER_MODELS = frozenset(
    {
        "composer-2.5",
        "composer-2.5-fast",
    }
)

CLOUD_PROMPT_SUFFIX = """
## Cloud agent runtime (mandatory)
You are a Cursor Cloud Agent working on a GitHub clone (not the user's Mac).
1. Apply all code fixes under the task folder in this repository.
2. Bump `# platform-revision:` in the task's environment/Dockerfile.
3. `git add` your changes, `git commit`, and `git push` to the configured branch.
4. Do NOT run harbor, docker, stb, or platform resubmit — the local monitor runs
   oracle and resubmit after your push.
5. Do NOT add Co-authored-by, Made-with, or any Cursor attribution to commits.
6. End with a short summary of files changed and what you fixed.
"""


def resolve_cursor_model() -> str:
    """Return the Cursor Composer model slug; reject non-Cursor models."""
    raw = (
        os.environ.get("CURSOR_COMPOSER_MODEL", "").strip()
        or os.environ.get("MONITOR_MODEL", "").strip()
        or DEFAULT_CURSOR_MODEL
    )
    model = raw.lower()
    if not model.startswith("composer-"):
        known = ", ".join(sorted(KNOWN_COMPOSER_MODELS))
        raise RuntimeError(
            "Monitor only uses Cursor Composer via cursor_sdk "
            f"(model must start with composer-). Got {raw!r}. "
            f"Examples: {known}. "
            "Set CURSOR_COMPOSER_MODEL=composer-2.5 in tools/monitor/.env"
        )
    return model


def resolve_agent_runtime() -> str:
    """Return `cloud` (no macOS popup) or `local` (needs Cursor.app)."""
    runtime = os.environ.get("MONITOR_AGENT_RUNTIME", DEFAULT_RUNTIME).strip().lower()
    if runtime in {"cloud", "local"}:
        return runtime
    raise RuntimeError(
        f"MONITOR_AGENT_RUNTIME must be cloud or local, got {runtime!r}"
    )


def agent_runtime_label() -> str:
    return f"cursor-{resolve_agent_runtime()}"


def assert_cursor_sdk_only() -> str:
    """Validate config and return the resolved Composer model."""
    resolve_agent_runtime()
    return resolve_cursor_model()


def resolve_github_repo_url(repo_root: Path) -> str:
    """HTTPS GitHub repo URL for cloud agents."""
    url = os.environ.get("GITHUB_REPO_URL", "").strip().rstrip("/")
    if url:
        return url
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Set GITHUB_REPO_URL in tools/monitor/.env "
            "(e.g. https://github.com/fabricenduwayo/fabre)"
        )
    raw = proc.stdout.strip()
    if raw.startswith("git@github.com:"):
        return "https://github.com/" + raw.removeprefix("git@github.com:").removesuffix(".git")
    return raw.removesuffix(".git")


def resolve_github_branch(repo_root: Path) -> str:
    branch = os.environ.get("GITHUB_BRANCH", "").strip()
    if branch:
        return branch
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return "main"
    return proc.stdout.strip()


def resolve_github_starting_ref(repo_root: Path) -> str:
    """Branch name or commit SHA for CloudRepository.starting_ref."""
    override = os.environ.get("CLOUD_STARTING_REF", "").strip()
    if override:
        return override
    use_sha = os.environ.get("CLOUD_USE_COMMIT_SHA", "1").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    branch = resolve_github_branch(repo_root)
    if not use_sha:
        return branch
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", branch],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return branch


def _cloud_branch_validation_hint(repo_url: str, ref: str) -> str:
    slug = repo_url.rstrip("/").removeprefix("https://github.com/")
    return (
        f"Cursor Cloud could not verify ref {ref!r} on {slug}. "
        "Cloud agents use Cursor's GitHub App (not GITHUB_TOKEN in .env). "
        "In Cursor: Dashboard → Integrations → GitHub → connect and grant "
        f"access to {slug.split('/')[-1]}. Then retry. "
        "See tools/monitor/README.md#cursor-github-for-cloud-agents."
    )


def _is_branch_validation_error(message: str) -> bool:
    lower = message.lower()
    return (
        "failed to verify existence of branch" in lower
        or "failed to determine repository default branch" in lower
    )


def cloud_prompt(prompt: str, *, branch: str) -> str:
    return (
        prompt.rstrip()
        + "\n"
        + CLOUD_PROMPT_SUFFIX.replace("the configured branch", f"branch `{branch}`")
    )


def run_agent(
    prompt: str,
    *,
    repo_root: Path,
    dry_run: bool,
    log_fn: Callable[[str], None] | None = None,
) -> tuple[str, str]:
    """Run a fix via Cursor SDK (cloud by default — no local bridge / macOS popup)."""
    model = resolve_cursor_model()
    runtime = resolve_agent_runtime()

    if dry_run:
        if log_fn:
            log_fn(
                f"DRY RUN — would call cursor_sdk Agent.prompt "
                f"runtime={runtime} model={model}"
            )
        return "dry_run", "skipped"

    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key or api_key.startswith("cursor_your"):
        raise RuntimeError(
            "CURSOR_API_KEY not set — copy tools/monitor/.env.example to tools/monitor/.env"
        )

    if runtime == "local":
        from monitor_health import local_agent_ready

        ready, reason = local_agent_ready()
        if not ready:
            raise RuntimeError(reason)
        return _run_local_agent(prompt, api_key=api_key, model=model, repo_root=repo_root)

    return _run_cloud_agent(prompt, api_key=api_key, model=model, repo_root=repo_root)


def _run_local_agent(
    prompt: str,
    *,
    api_key: str,
    model: str,
    repo_root: Path,
) -> tuple[str, str]:
    from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions

    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model=model,
                local=LocalAgentOptions(cwd=str(repo_root)),
            ),
        )
    except CursorAgentError as exc:
        raise RuntimeError(f"Cursor agent startup failed: {exc.message}") from exc
    finally:
        _cleanup_local_bridges(repo_root)

    if result.status == "error":
        raise RuntimeError(f"Cursor agent run failed: {getattr(result, 'result', '')}")
    return str(result.status), str(getattr(result, "result", ""))[:4000]


def _run_cloud_agent(
    prompt: str,
    *,
    api_key: str,
    model: str,
    repo_root: Path,
) -> tuple[str, str]:
    from cursor_sdk import Agent, AgentOptions, CloudAgentOptions, CloudRepository, CursorAgentError

    repo_url = resolve_github_repo_url(repo_root)
    branch = resolve_github_branch(repo_root)
    starting_ref = resolve_github_starting_ref(repo_root)
    work_on_branch = os.environ.get("CLOUD_WORK_ON_BRANCH", "1").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    max_retries = int(os.environ.get("CLOUD_AGENT_RETRIES", "3"))
    retry_sec = int(os.environ.get("CLOUD_AGENT_RETRY_SEC", "45"))

    last_exc: CursorAgentError | None = None
    refs_to_try = [starting_ref]
    if starting_ref != branch:
        refs_to_try.append(branch)

    for attempt in range(1, max_retries + 1):
        for ref in refs_to_try:
            try:
                result = Agent.prompt(
                    cloud_prompt(prompt, branch=branch),
                    AgentOptions(
                        api_key=api_key,
                        model=model,
                        cloud=CloudAgentOptions(
                            repos=[CloudRepository(url=repo_url, starting_ref=ref)],
                            work_on_current_branch=work_on_branch,
                            auto_create_pr=False,
                            skip_reviewer_request=True,
                        ),
                    ),
                )
            except CursorAgentError as exc:
                last_exc = exc
                if _is_branch_validation_error(exc.message) and attempt < max_retries:
                    time.sleep(retry_sec)
                    continue
                if _is_branch_validation_error(exc.message):
                    raise RuntimeError(
                        _cloud_branch_validation_hint(repo_url, ref)
                    ) from exc
                raise RuntimeError(f"Cursor cloud agent failed: {exc.message}") from exc
            else:
                if result.status == "error":
                    raise RuntimeError(
                        f"Cursor cloud agent run failed: {getattr(result, 'result', '')}"
                    )
                return str(result.status), str(getattr(result, "result", ""))[:4000]

    if last_exc is not None:
        if _is_branch_validation_error(last_exc.message):
            raise RuntimeError(_cloud_branch_validation_hint(repo_url, starting_ref)) from last_exc
        raise RuntimeError(f"Cursor cloud agent failed: {last_exc.message}") from last_exc
    raise RuntimeError("Cursor cloud agent failed after retries")


def _cleanup_local_bridges(repo_root: Path) -> None:
    pattern = f"cursor-sdk-bridge.js.*{repo_root}"
    subprocess.run(["pkill", "-f", pattern], capture_output=True, check=False)
