"""Verifies the C++ setup auditor against the resolved Lab Access Hardening Standard.

The auditor parses a raw host snapshot and proposes remediation patches. Its
output must match the Standard as it stands *after* the authoritative amendments
in Appendix G. The reference implementation used to compute expectations lives
only in the test image; the agent must derive the resolved policy from the
dossier in /app/docs.
"""

import random

from helpers import canon, cpp_audit, expected_patches, load_fixture, make_snapshot

RANDOM_CASES = 60


def test_health_endpoint_responds():
    """The auditor is reachable and /v1/setup/audit returns a JSON patch list."""
    snap = load_fixture("compliant.json")
    assert isinstance(cpp_audit(snap), list)


def test_matches_resolved_policy_on_random_hosts():
    """Across randomized host snapshots the auditor agrees with the resolved policy."""
    rng = random.Random(20260625)
    mismatches = 0
    for _ in range(RANDOM_CASES):
        snap = make_snapshot(rng)
        if canon(cpp_audit(snap)) != canon(expected_patches(snap)):
            mismatches += 1
    assert mismatches == 0, f"{mismatches}/{RANDOM_CASES} snapshots disagreed with policy"


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


def test_sshd_precedence_and_prohibit_password():
    """First global value wins, Match blocks ignored, prohibit-password accepted."""
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


def test_sshd_match_all_resumes_global():
    """`Match all` returns to global scope so later keywords are evaluated (G-2026-08)."""
    snap = load_fixture("sshd_match_all.json")
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


def test_compliant_host_needs_no_patches():
    """An already-compliant host produces an empty, idempotent patch set."""
    snap = load_fixture("compliant.json")
    assert cpp_audit(snap) == []
