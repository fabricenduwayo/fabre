<?php

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
    apply_preflight($config);
    http_response_code(204);
    exit;
}

if ($path === '/health' && $method === 'GET') {
    $auth = isset($_SERVER['HTTP_AUTHORIZATION']) ? $_SERVER['HTTP_AUTHORIZATION'] : '';
    $token = null;
    if (preg_match('/^Bearer\s+(.*)$/', $auth, $m)) {
        $token = $m[1];
    }
    $stored = read_admin_token($config);
    if ($token !== null && $token !== '' && $stored !== null && hash_equals($stored, $token)) {
        audit_log($config, 'health', $path, $origin, 'accepted', null);
        send_json($config, 200, ['status' => 'ok']);
    } elseif ($token === null) {
        audit_log($config, 'health', $path, $origin, 'denied', 'missing_token');
        fail($config, 401, 'unauthorized');
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
        fail($config, 400, 'bad request', 'json error: ' . json_last_error_msg());
        exit;
    }

    $secret = isset($_SERVER['HTTP_X_BOOTSTRAP_SECRET']) ? $_SERVER['HTTP_X_BOOTSTRAP_SECRET'] : null;
    $expected = read_bootstrap_secret($config);

    $allowed = false;
    if ($expected !== null && $secret !== null && hash_equals($expected, $secret)) {
        $allowed = true;
    }

    if (!$allowed) {
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'invalid_secret');
        fail($config, 403, 'forbidden');
        exit;
    }

    if (admin_token_exists($config)) {
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'already_bootstrapped');
        fail($config, 403, 'forbidden');
        exit;
    }

    $token = bin2hex(random_bytes(24));
    file_put_contents($config['token_file'], $token);
    chmod($config['token_file'], 0644);
    audit_log($config, 'bootstrap', $path, $origin, 'accepted', null);
    send_json($config, 201, ['token' => $token]);
    exit;
}

fail($config, 404, 'not found');
