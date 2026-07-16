<?php

$config = require __DIR__ . '/config.php';
require __DIR__ . '/lib/audit.php';
require __DIR__ . '/lib/http.php';

ini_set('display_errors', '0');
ini_set('default_mimetype', '');
header_remove('X-Powered-By');

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$origin = $_SERVER['HTTP_ORIGIN'] ?? null;

apply_cors($config, $origin);

if ($method === 'OPTIONS') {
    apply_preflight($config, $origin);
    header_remove('Content-Type');
    http_response_code(204);
    exit;
}

if ($path === '/health' && $method === 'GET') {
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    $token = null;
    if (preg_match('/^Bearer[ \t]+(.+\S|[^ \t])$/', $auth, $match)) {
        $token = ascii_trim($match[1]);
        if ($token === '') {
            $token = null;
        }
    }

    if ($token === null) {
        audit_log($config, 'health', $path, $origin, 'denied', 'missing_credentials');
        fail($config, 401, 'unauthorized');
        exit;
    }

    try {
        $accepted = with_token_state_lock($config, function () use ($config, $token) {
            $record = read_token_state_unlocked($config);
            if (!$record['valid']) {
                return false;
            }
            $state = $record['state'];
            $digest = hash('sha256', $token);
            if (hash_equals($state['current_digest'], $digest)) {
                return true;
            }
            if ($state['previous_digest'] !== null
                    && $state['previous_uses_remaining'] > 0
                    && hash_equals($state['previous_digest'], $digest)) {
                $state['previous_uses_remaining']--;
                write_token_state_unlocked($config, $state);
                return true;
            }
            return false;
        });
    } catch (Throwable $error) {
        fail($config, 500, 'internal error');
        exit;
    }

    if ($accepted) {
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
    json_decode($raw, true);
    if ($raw !== '' && json_last_error() !== JSON_ERROR_NONE) {
        audit_log($config, 'bootstrap', $path, $origin, 'denied', 'malformed_request');
        fail($config, 400, 'bad request');
        exit;
    }

    $presentedSecret = $_SERVER['HTTP_X_BOOTSTRAP_SECRET'] ?? null;
    try {
        $result = with_token_state_lock($config, function () use ($config, $presentedSecret) {
            $generation = read_credential_generation($config);
            $record = read_token_state_unlocked($config);
            if ($generation === null) {
                return ['status' => 500, 'message' => 'internal error', 'reason' => null, 'token' => null];
            }
            if ($record['exists']
                    && (!$record['valid'] || $generation <= $record['state']['generation'])) {
                return [
                    'status' => 409,
                    'message' => 'conflict',
                    'reason' => 'already_bootstrapped',
                    'token' => null,
                ];
            }
            if (!secret_matches(read_bootstrap_secret($config), $presentedSecret)) {
                return [
                    'status' => 403,
                    'message' => 'forbidden',
                    'reason' => 'invalid_secret',
                    'token' => null,
                ];
            }

            $token = bin2hex(random_bytes(24));
            $previous = $record['valid'] ? $record['state'] : null;
            $state = [
                'version' => 1,
                'generation' => $generation,
                'current_digest' => hash('sha256', $token),
                'previous_generation' => $previous['generation'] ?? null,
                'previous_digest' => $previous['current_digest'] ?? null,
                'previous_uses_remaining' => $previous === null ? 0 : $config['predecessor_uses'],
            ];
            write_token_state_unlocked($config, $state);
            return ['status' => 201, 'message' => null, 'reason' => null, 'token' => $token];
        });
    } catch (Throwable $error) {
        fail($config, 500, 'internal error');
        exit;
    }

    if ($result['status'] === 201) {
        audit_log($config, 'bootstrap', $path, $origin, 'accepted', null);
        send_json($config, 201, ['token' => $result['token']]);
    } elseif ($result['reason'] !== null) {
        audit_log($config, 'bootstrap', $path, $origin, 'denied', $result['reason']);
        fail($config, $result['status'], $result['message']);
    } else {
        fail($config, $result['status'], $result['message']);
    }
    exit;
}

fail($config, 404, 'not found');
