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
$auditOrigin = cors_origin_allowed($config, $origin) ? $origin : null;

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
        audit_log($config, 'health', $path, $auditOrigin, 'denied', 'missing_credentials');
        fail($config, 401, 'unauthorized');
        exit;
    }

    try {
        $verdict = with_token_state_lock($config, function () use ($config, $token, $origin) {
            $record = read_token_state_unlocked($config);
            if (!$record['valid']) {
                return 'denied';
            }
            $state = $record['state'];
            $digest = hash('sha256', $token);
            if (hash_equals($state['current_digest'], $digest)) {
                $publishedGeneration = read_credential_generation($config);
                if ($state['pending_digest'] !== null
                        && $publishedGeneration !== null
                        && $publishedGeneration === $state['pending_generation']
                        && cors_origin_allowed($config, $origin)
                        && !in_array($origin, $state['pending_sponsors'], true)) {
                    $state['pending_sponsors'][] = $origin;
                    write_token_state_unlocked($config, $state);
                }
                return 'current';
            }
            if ($state['previous_digest'] !== null
                    && hash_equals($state['previous_digest'], $digest)
                    && cors_origin_allowed($config, $origin)) {
                $position = array_search(
                    $origin,
                    $state['previous_origins_remaining'],
                    true
                );
                if ($position === false) {
                    return 'denied';
                }
                unset($state['previous_origins_remaining'][$position]);
                $state['previous_origins_remaining'] = array_values(
                    $state['previous_origins_remaining']
                );
                write_token_state_unlocked($config, $state);
                return 'predecessor';
            }
            if ($state['pending_digest'] !== null
                    && cors_origin_allowed($config, $origin)
                    && hash_equals($state['pending_digest'], $digest)) {
                $publishedGeneration = read_credential_generation($config);
                if ($publishedGeneration !== null
                        && $state['pending_generation'] !== null
                        && $publishedGeneration > $state['pending_generation']) {
                    return 'denied';
                }
                if (!in_array($origin, $state['pending_sponsors'], true)) {
                    return 'denied';
                }
                if (!in_array($origin, $state['pending_origins'], true)) {
                    $state['pending_origins'][] = $origin;
                }
                if (count($state['pending_origins']) === count($config['allowed_origins'])) {
                    $state = [
                        'version' => 2,
                        'generation' => $state['pending_generation'],
                        'current_digest' => $state['pending_digest'],
                        'previous_generation' => $state['generation'],
                        'previous_digest' => $state['current_digest'],
                        'previous_origins_remaining' => $config['allowed_origins'],
                        'pending_generation' => null,
                        'pending_digest' => null,
                        'pending_origins' => [],
                        'pending_sponsors' => [],
                    ];
                    write_token_state_unlocked($config, $state);
                    return 'activated';
                }
                write_token_state_unlocked($config, $state);
                return 'confirmation';
            }
            return 'denied';
        });
    } catch (Throwable $error) {
        fail($config, 500, 'internal error');
        exit;
    }

    if (in_array($verdict, ['current', 'predecessor', 'confirmation', 'activated'], true)) {
        $reason = match ($verdict) {
            'predecessor' => 'predecessor_overlap',
            'confirmation' => 'cutover_confirmation',
            'activated' => 'cutover_activated',
            default => null,
        };
        audit_log($config, 'health', $path, $auditOrigin, 'accepted', $reason);
        send_json($config, 200, ['status' => 'ok']);
    } else {
        audit_log($config, 'health', $path, $auditOrigin, 'denied', 'invalid_token');
        fail($config, 401, 'unauthorized');
    }
    exit;
}

if ($path === '/admin/bootstrap' && $method === 'POST') {
    $raw = file_get_contents('php://input');
    json_decode($raw, true);
    if ($raw !== '' && json_last_error() !== JSON_ERROR_NONE) {
        audit_log($config, 'bootstrap', $path, $auditOrigin, 'denied', 'malformed_request');
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
            if ($record['exists']) {
                if (!$record['valid']) {
                    return [
                        'status' => 409,
                        'message' => 'conflict',
                        'reason' => 'already_bootstrapped',
                        'token' => null,
                    ];
                }
                $state = $record['state'];
                $highestGeneration = $state['pending_generation'] ?? $state['generation'];
                if ($generation <= $highestGeneration) {
                    return [
                        'status' => 409,
                        'message' => 'conflict',
                        'reason' => 'already_bootstrapped',
                        'token' => null,
                    ];
                }
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
            if (!$record['exists']) {
                $state = [
                    'version' => 2,
                    'generation' => $generation,
                    'current_digest' => hash('sha256', $token),
                    'previous_generation' => null,
                    'previous_digest' => null,
                    'previous_origins_remaining' => [],
                    'pending_generation' => null,
                    'pending_digest' => null,
                    'pending_origins' => [],
                    'pending_sponsors' => [],
                ];
            } else {
                $state = $record['state'];
                $state['pending_generation'] = $generation;
                $state['pending_digest'] = hash('sha256', $token);
                $state['pending_origins'] = [];
                $state['pending_sponsors'] = [];
            }
            write_token_state_unlocked($config, $state);
            return ['status' => 201, 'message' => null, 'reason' => null, 'token' => $token];
        });
    } catch (Throwable $error) {
        fail($config, 500, 'internal error');
        exit;
    }

    if ($result['status'] === 201) {
        audit_log($config, 'bootstrap', $path, $auditOrigin, 'accepted', null);
        send_json($config, 201, ['token' => $result['token']]);
    } elseif ($result['reason'] !== null) {
        audit_log($config, 'bootstrap', $path, $auditOrigin, 'denied', $result['reason']);
        fail($config, $result['status'], $result['message']);
    } else {
        fail($config, $result['status'], $result['message']);
    }
    exit;
}

fail($config, 404, 'not found');
