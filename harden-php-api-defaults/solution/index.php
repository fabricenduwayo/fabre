<?php
// HarborDesk Edge API front controller, reconciled with the Hardening Standard
// (body controls + Appendix G amendments). Routes:
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

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : null;

apply_cors($config, $origin);

if ($method === 'OPTIONS') {
    // CO-PREFLIGHT: 204, hints only for an allowed origin; not audited.
    apply_preflight($config, $origin);
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

    if ($token === null) {
        // AC-HEALTH + G-2026-04: missing-credential reason renamed.
        audit_log($config, 'health', $path, $origin, 'denied', 'missing_credentials');
        fail($config, 401, 'unauthorized');
        exit;
    }

    $presented = hash('sha256', $token);
    if ($stored !== null && hash_equals($stored, $presented)) {
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
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'malformed_request');
        fail($config, 400, 'bad request');
        exit;
    }

    // AC-BOOTSTRAP + G-2026-05: already-bootstrapped takes precedence over the
    // secret check, so a repeat is refused even with a wrong/absent secret.
    if (is_file($config['token_file'])) {
        // G-2026-03: refusal status for an existing token is 409.
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'already_bootstrapped');
        fail($config, 409, 'conflict');
        exit;
    }

    $secret = isset($_SERVER['HTTP_X_BOOTSTRAP_SECRET'])
        ? trim($_SERVER['HTTP_X_BOOTSTRAP_SECRET'])
        : null;
    $expected = is_file($config['bootstrap_secret_file'])
        ? trim(file_get_contents($config['bootstrap_secret_file']))
        : null;

    if ($expected === null || $secret === null
            || !hash_equals(strtolower($expected), strtolower($secret))) {
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'invalid_secret');
        fail($config, 403, 'forbidden');
        exit;
    }

    $token = bin2hex(random_bytes(24));
    // AC-TOKEN-STORE: store a non-recoverable digest, return the raw token once,
    // and write the file owner-only (0600).
    if (file_put_contents($config['token_file'], hash('sha256', $token)) === false) {
        fail($config, 500, 'internal error');
        exit;
    }
    chmod($config['token_file'], 0600);
    audit_log($config, 'bootstrap', $path, $origin, 'accepted', null);
    send_json($config, 201, ['token' => $token]);
    exit;
}

// EH-NO-DISCLOSE: unknown routes/methods are a generic 404 and not audited.
fail($config, 404, 'not found');
