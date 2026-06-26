<?php
// HarborDesk front controller. Routes:
//   GET  /health           -> authenticated health check
//   POST /admin/bootstrap  -> one-time admin token bootstrap
// Both are recorded in the SQLite audit ledger.

$config = require __DIR__ . '/config.php';
require __DIR__ . '/lib/audit.php';
require __DIR__ . '/lib/http.php';

if (!empty($config['debug'])) {
    ini_set('display_errors', '1');
    error_reporting(E_ALL);
} else {
    ini_set('display_errors', '0');
}

apply_cors($config);

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : null;

if ($method === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($path === '/health' && $method === 'GET') {
    $auth = isset($_SERVER['HTTP_AUTHORIZATION']) ? $_SERVER['HTTP_AUTHORIZATION'] : '';
    $token = null;
    if (preg_match('/^Bearer\s+(.+)$/', $auth, $m)) {
        $token = $m[1];
    }
    $stored = is_file($config['token_file']) ? trim(file_get_contents($config['token_file'])) : null;
    $presented = $token !== null ? hash('sha256', $token) : null;
    if ($presented !== null && $stored !== null && hash_equals($stored, $presented)) {
        audit_log($config, 'health', $path, $origin, 'accepted', null);
        send_json($config, 200, ['status' => 'ok']);
    } else {
        audit_log($config, 'health', $path, $origin, 'denied', 'invalid_token');
        fail($config, 401, 'unauthorized');
    }
    exit;
}

if ($path === '/admin/bootstrap' && $method === 'POST') {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    if ($raw !== '' && $data === null) {
        fail($config, 400, 'bad request', 'json error: ' . json_last_error_msg());
        exit;
    }

    $secret = isset($_SERVER['HTTP_X_BOOTSTRAP_SECRET']) ? $_SERVER['HTTP_X_BOOTSTRAP_SECRET'] : null;
    $expected = is_file($config['bootstrap_secret_file'])
        ? trim(file_get_contents($config['bootstrap_secret_file']))
        : null;

    if (is_file($config['token_file'])) {
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'already_bootstrapped');
        fail($config, 403, 'forbidden');
        exit;
    }

    if ($expected === null || $secret === null || !hash_equals($expected, $secret)) {
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'invalid_secret');
        fail($config, 403, 'forbidden');
        exit;
    }

    $token = bin2hex(random_bytes(24));
    // Store only a digest so a leaked token file cannot be replayed; the raw
    // token is handed back to the caller this one time.
    if (file_put_contents($config['token_file'], hash('sha256', $token)) === false) {
        fail($config, 500, 'internal error');
        exit;
    }
    chmod($config['token_file'], 0600);
    audit_log($config, 'bootstrap', $path, $origin, 'accepted', null);
    send_json($config, 201, ['token' => $token]);
    exit;
}

fail($config, 404, 'not found');
