<?php
// HarborDesk configuration, hardened from the staging defaults.
return [
    'debug' => false,
    'cors_allow_origin' => '*',
    'allow_plaintext_bootstrap' => false,
    'allowed_origin' => 'https://harbordesk.internal',
    'token_file' => '/app/harbordesk/data/admin_token',
    'bootstrap_secret_file' => '/app/harbordesk/data/bootstrap_secret',
    'audit_db' => '/app/harbordesk/data/audit.db',
];
