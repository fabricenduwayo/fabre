<?php
// HarborDesk Edge API configuration, hardened and reconciled with the Hardening
// Standard as amended by Appendix G:
//   - G-2026-01: origin allowlist extended with the ops console origin.
//   - G-2026-02: preflight cache lifetime lowered 600 -> 300.
return [
    'debug' => false,
    'allow_plaintext_bootstrap' => false,
    'allowed_origins' => [
        'https://harbordesk.internal',
        'https://ops.harbordesk.internal',
    ],
    'preflight_max_age' => 300,
    'token_file' => '/app/harbordesk/data/admin_token',
    'bootstrap_secret_file' => '/app/harbordesk/data/bootstrap_secret',
    'audit_db' => '/app/harbordesk/data/audit.db',
];
