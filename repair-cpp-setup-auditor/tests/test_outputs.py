"""Verifies the C++ setup auditor against the resolved Lab Access Hardening Standard.

The auditor parses a raw host snapshot and proposes remediation patches. Its
output must match the Standard as it stands *after* the authoritative amendments
in Appendix G. The reference implementation used to compute expectations lives
only in the test image; the agent must derive the resolved policy from the
dossier in /app/docs.
"""

import json
import os
import random

from helpers import canon, cpp_audit, expected_patches, load_fixture, make_snapshot

RANDOM_CASES = 60
LEDGER_PATH = os.environ.get("AUDITOR_LEDGER", "/app/cpp-auditor/state/ledger.json")


def test_health_endpoint_responds():
    """The auditor is reachable and /v1/setup/audit returns a JSON patch list."""
    snap = load_fixture("compliant.json")
    assert isinstance(cpp_audit(snap), list)


def test_matches_resolved_policy_on_random_hosts():
    """Across randomized host snapshots the auditor agrees with the resolved policy."""
    rng = random.Random(20260625)
    failures = []
    for i in range(RANDOM_CASES):
        snap = make_snapshot(rng)
        got = canon(cpp_audit(snap))
        want = canon(expected_patches(snap))
        if got != want:
            failures.append(f"case {i}: got {got}, want {want}")
    assert not failures, (
        f"{len(failures)}/{RANDOM_CASES} snapshots disagreed with policy:\n"
        + "\n".join(failures[:5])
    )


def test_primary_group_membership_grants_sudo():
    """Sudo granted via the primary GID (not only supplementary groups) is detected."""
    snap = load_fixture("primary_gid.json")
    assert canon(cpp_audit(snap)) == canon(
        [{"action": "sudoers.require_password", "target": "alice"}]
    )


def test_locked_and_extended_shells_lose_keys():
    """Disabled via *LK*, git-shell, and a bare '!' lock all trigger revocation."""
    snap = load_fixture("locked_keys.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "ssh.revoke_keys", "target": "carol"},
            {"action": "ssh.revoke_keys", "target": "dan"},
            {"action": "ssh.revoke_keys", "target": "erin"},
        ]
    )


def test_nopasswd_all_and_negation():
    """Only NOPASSWD applied to ALL counts, and negated principals are excluded."""
    snap = load_fixture("sudo_nopasswd.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "sudoers.require_password", "target": "alice"},
            {"action": "sudoers.require_password", "target": "dan"},
        ]
    )


def test_sshd_precedence_and_context_match():
    """A non-applicable Match (User deploy) is skipped; an applicable Address/CIDR
    Match supplies the effective value (G-2026-17)."""
    snap = load_fixture("sshd_precedence.json")
    assert canon(cpp_audit(snap)) == canon(
        [{"action": "systemd.set_dropin", "unit": "sshd", "key": "PasswordAuthentication", "value": "no"}]
    )


def test_exempt_ceiling_and_roster():
    """uid ceiling 499 and the extended roster (svc_backup) are honored."""
    snap = load_fixture("exempt.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "sudoers.require_password", "target": "alice"},
            {"action": "sudoers.require_password", "target": "midrange"},
        ]
    )


def test_sudo_defaults_authenticate_grants_passwordless():
    """`Defaults:<binder> !authenticate` grants passwordless sudo (user and group)."""
    snap = load_fixture("sudo_defaults.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "sudoers.require_password", "target": "alice"},
            {"action": "sudoers.require_password", "target": "carol"},
        ]
    )


def test_sshd_kbdinteractive_alias_first_match():
    """ChallengeResponseAuthentication aliases KbdInteractiveAuthentication, first wins."""
    snap = load_fixture("sshd_kbdint.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {
                "action": "systemd.set_dropin",
                "unit": "sshd",
                "key": "KbdInteractiveAuthentication",
                "value": "no",
            }
        ]
    )


def test_sudo_last_match_wins():
    """A later spec supersedes earlier grants for the same principal (G-2026-07)."""
    snap = load_fixture("sudo_last_match.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "sudoers.require_password", "target": "bob"},
            {"action": "sudoers.require_password", "target": "carol"},
        ]
    )


def test_sshd_match_all_applies():
    """`Match all` always applies, so a keyword set only after it is effective; a
    keyword inside a non-applicable block is skipped (G-2026-17)."""
    snap = load_fixture("sshd_match_all.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {
                "action": "systemd.set_dropin",
                "unit": "sshd",
                "key": "PasswordAuthentication",
                "value": "no",
            }
        ]
    )


def test_sshd_match_context_user_group_address():
    """Negated User excludes root, an out-of-range CIDR is skipped, and a combined
    User+Address block applies (G-2026-17)."""
    snap = load_fixture("sshd_context.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {
                "action": "systemd.set_dropin",
                "unit": "sshd",
                "key": "PasswordAuthentication",
                "value": "no",
            }
        ]
    )


def test_sudo_includedir_splices_in_order():
    """`#includedir` files splice in sorted order and obey last-match (G-2026-09).

    PermitRootLogin without-password is also accepted (G-2026-10), so the only
    patches are the passwordless grants surviving last-match resolution.
    """
    snap = load_fixture("sudo_includedir.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "sudoers.require_password", "target": "bob"},
            {"action": "sudoers.require_password", "target": "carol"},
        ]
    )


def test_sudo_runas_nonroot_not_passwordless():
    """A NOPASSWD: ALL grant whose runas target is non-root does not count (G-2026-15)."""
    snap = load_fixture("sudo_runas.json")
    assert canon(cpp_audit(snap)) == canon(
        [{"action": "sudoers.require_password", "target": "alice"}]
    )


def test_sudo_sticky_tags_and_key_markers():
    """Sticky sudo command tags and inactive key-marker lines are resolved correctly."""
    snap = load_fixture("sudo_tags_and_key_markers.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "sudoers.require_password", "target": "alice"},
            {"action": "ssh.revoke_keys", "target": "dan"},
        ]
    )


def test_account_expiry_disables_account():
    """An expired account (shadow field 8 below the reference day) is disabled (G-2026-16).

    The expired account with keys is revoked and the expired account with
    passwordless sudo is exempted from a password requirement, while a future
    expiry still requires a password.
    """
    snap = load_fixture("expiry.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "ssh.revoke_keys", "target": "carol"},
            {"action": "sudoers.require_password", "target": "erin"},
        ]
    )


def test_sudo_host_scoping_and_alias():
    """A spec applies only when its host field includes the audit host (G-2026-18).

    A grant scoped to another host is ignored, a Host_Alias that resolves to the
    audit host applies, and a later non-applicable spec does not revoke an earlier
    applicable grant.
    """
    snap = load_fixture("sudo_host.json")
    assert canon(cpp_audit(snap)) == canon(
        [
            {"action": "sudoers.require_password", "target": "alice"},
            {"action": "sudoers.require_password", "target": "carol"},
        ]
    )


def test_audit_ledger_migrated_and_records_patches():
    """Audits are appended to the ledger, which is migrated from the legacy schema.

    The on-disk ledger starts in schema 1 (records under "audits"). A correct
    auditor migrates it to schema 2 ("entries"), preserves the pre-existing
    record, and appends every patch it emits.
    """
    snap = load_fixture("sudo_nopasswd.json")
    patches = cpp_audit(snap)
    assert patches, "fixture should produce patches to record"

    with open(LEDGER_PATH) as fh:
        ledger = json.load(fh)

    assert ledger.get("schema") == 2, "ledger must be migrated to schema 2"
    entries = ledger.get("entries")
    assert isinstance(entries, list) and entries, "ledger must keep an entries list"

    recorded = {json.dumps(e, sort_keys=True) for e in entries}
    legacy = json.dumps({"action": "audit.bootstrap", "target": "legacy-seed"}, sort_keys=True)
    assert legacy in recorded, "migration must preserve existing legacy records"
    for patch in patches:
        assert json.dumps(patch, sort_keys=True) in recorded, "each emitted patch must be logged"


def test_compliant_host_needs_no_patches():
    """An already-compliant host produces an empty, idempotent patch set."""
    snap = load_fixture("compliant.json")
    assert cpp_audit(snap) == []
