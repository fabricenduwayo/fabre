<?php
// HarborDesk staging configuration.
// These are the loose staging defaults that shipped with the image.
return [
    'debug' => true,
    'cors_allow_origin' => '*',
    'allow_plaintext_bootstrap' => true,
    'allowed_origin' => 'https://harbordesk.internal',
    'token_file' => '/app/harbordesk/data/admin_token',
    'bootstrap_secret_file' => '/app/harbordesk/data/bootstrap_secret',
    'audit_db' => '/app/harbordesk/data/audit.db',
];
