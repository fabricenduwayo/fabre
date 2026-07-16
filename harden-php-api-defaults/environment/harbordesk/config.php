<?php

$origins_file = __DIR__ . '/data/allowed_origins';
$allowed_origins = ['https://harbordesk.internal'];
if (is_readable($origins_file)) {
    $allowed_origins = array_values(
        array_filter(
            array_map('trim', file($origins_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES))
        )
    );
}

return [
    'debug' => true,
    'allowed_origins' => $allowed_origins,
    'preflight_max_age' => 600,
    'token_file' => '/app/harbordesk/data/admin_token',
    'bootstrap_secret_file' => '/app/harbordesk/data/bootstrap_secret',
    'audit_db' => '/app/harbordesk/data/audit.db',
];
