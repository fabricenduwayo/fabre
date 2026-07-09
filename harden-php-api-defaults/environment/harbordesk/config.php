<?php

return [
    'debug' => true,
    'allowed_origins' => ['https://harbordesk.internal'],
    'preflight_max_age' => 600,
    'token_file' => '/app/harbordesk/data/admin_token',
    'bootstrap_secret_file' => '/app/harbordesk/data/bootstrap_secret',
    'audit_db' => '/app/harbordesk/data/audit.db',
];
