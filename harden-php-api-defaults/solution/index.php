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
        $verdict = with_token_state_lock($config, function () use (
            $config,
            $token,
            $origin,
            $path,
            $auditOrigin
        ) {
            $record = read_token_state_unlocked($config);
            if (!$record['valid']) {
                return audit_log_then(
                    $config,
                    'health',
                    $path,
                    $auditOrigin,
                    'denied',
                    'invalid_token',
                    static fn() => 'denied'
                );
            }
            $state = $record['state'];
            $stateChanged = false;
            $pendingSecretUsable = true;
            if ($state['pending_digest'] !== null) {
                $liveSecretDigest = bootstrap_secret_fingerprint($config);
                if ($liveSecretDigest === null) {
                    $pendingSecretUsable = false;
                    if ($state['pending_sponsors'] !== [] || $state['pending_origins'] !== []) {
                        $state['pending_sponsors'] = [];
                        $state['pending_origins'] = [];
                        $stateChanged = true;
                    }
                } elseif (!hash_equals($state['pending_secret_digest'], $liveSecretDigest)) {
                    $state['pending_sponsors'] = [];
                    $state['pending_origins'] = [];
                    $state['pending_secret_digest'] = $liveSecretDigest;
                    $stateChanged = true;
                }
            }
            $stateAfterSecretRefresh = $state;
            $finish = function (
                $verdict,
                $decision,
                $reason,
                $nextState,
                $publish
            ) use ($config, $path, $auditOrigin, $origin) {
                if ($decision === 'denied'
                        && $reason === 'invalid_token'
                        && $nextState['pending_digest'] !== null
                        && cors_origin_allowed($config, $origin)) {
                    $sponsorPosition = array_search(
                        $origin,
                        $nextState['pending_sponsors'],
                        true
                    );
                    if ($sponsorPosition !== false) {
                        unset($nextState['pending_sponsors'][$sponsorPosition]);
                        $nextState['pending_sponsors'] = array_values(
                            $nextState['pending_sponsors']
                        );
                        $publish = true;
                    }
                }
                return audit_log_then(
                    $config,
                    'health',
                    $path,
                    $auditOrigin,
                    $decision,
                    $reason,
                    function () use ($config, $nextState, $publish, $verdict) {
                        if ($publish) {
                            write_token_state_unlocked($config, $nextState);
                        }
                        return $verdict;
                    }
                );
            };
            $digest = hash('sha256', $token);
            if (hash_equals($state['current_digest'], $digest)) {
                $publishedGeneration = read_credential_generation($config);
                if ($state['pending_digest'] !== null
                        && $pendingSecretUsable
                        && $publishedGeneration !== null
                        && $publishedGeneration === $state['pending_generation']
                        && cors_origin_allowed($config, $origin)
                        && !in_array($origin, $state['pending_sponsors'], true)) {
                    $state['pending_sponsors'][] = $origin;
                    $stateChanged = true;
                }
                return $finish('current', 'accepted', null, $state, $stateChanged);
            }
            if ($state['previous_digest'] !== null
                    && hash_equals($state['previous_digest'], $digest)
                    && cors_origin_allowed($config, $origin)) {
                $position = array_search(
                    $origin,
                    $state['previous_origins_remaining'],
                    true
                );
                $publishedGeneration = read_credential_generation($config);
                if ($position !== false
                        && $state['pending_digest'] !== null
                        && $publishedGeneration !== null
                        && $publishedGeneration === $state['pending_generation']) {
                    return $finish(
                        'denied',
                        'denied',
                        'overlap_frozen',
                        $state,
                        $stateChanged
                    );
                }
                if ($position === false) {
                    return $finish(
                        'denied',
                        'denied',
                        'invalid_token',
                        $state,
                        $stateChanged
                    );
                }
                unset($state['previous_origins_remaining'][$position]);
                $state['previous_origins_remaining'] = array_values(
                    $state['previous_origins_remaining']
                );
                return $finish(
                    'predecessor',
                    'accepted',
                    'predecessor_overlap',
                    $state,
                    true
                );
            }
            if ($state['pending_digest'] !== null
                    && cors_origin_allowed($config, $origin)
                    && hash_equals($state['pending_digest'], $digest)) {
                $publishedGeneration = read_credential_generation($config);
                if ($publishedGeneration !== null
                        && $state['pending_generation'] !== null
                        && $publishedGeneration > $state['pending_generation']) {
                    return $finish(
                        'denied',
                        'denied',
                        'invalid_token',
                        $state,
                        $stateChanged
                    );
                }
                if (!$pendingSecretUsable
                        || !in_array($origin, $state['pending_sponsors'], true)) {
                    return $finish(
                        'denied',
                        'denied',
                        'invalid_token',
                        $state,
                        $stateChanged
                    );
                }
                if (!in_array($origin, $state['pending_origins'], true)) {
                    $state['pending_origins'][] = $origin;
                    if (count($state['pending_origins']) === 1) {
                        $state['pending_sponsors'] = array_values(array_intersect(
                            $state['pending_sponsors'],
                            $state['pending_origins']
                        ));
                    }
                }
                if (count($state['pending_origins']) === count($config['allowed_origins'])) {
                    $activationGeneration = read_credential_generation($config);
                    if ($activationGeneration === null
                            || $activationGeneration > $state['pending_generation']) {
                        return $finish(
                            'denied',
                            'denied',
                            'invalid_token',
                            $stateAfterSecretRefresh,
                            $stateChanged
                        );
                    }
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
                        'pending_secret_digest' => null,
                    ];
                    return $finish(
                        'activated',
                        'accepted',
                        'cutover_activated',
                        $state,
                        true
                    );
                }
                return $finish(
                    'confirmation',
                    'accepted',
                    'cutover_confirmation',
                    $state,
                    true
                );
            }
            return $finish(
                'denied',
                'denied',
                'invalid_token',
                $state,
                $stateChanged
            );
        });
    } catch (Throwable $error) {
        fail($config, 500, 'internal error');
        exit;
    }

    if (in_array($verdict, ['current', 'predecessor', 'confirmation', 'activated'], true)) {
        send_json($config, 200, ['status' => 'ok']);
    } else {
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
            $liveSecret = read_bootstrap_secret($config);
            if (!secret_matches($liveSecret, $presentedSecret)) {
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
                    'pending_secret_digest' => null,
                ];
            } else {
                $state = $record['state'];
                $state['pending_generation'] = $generation;
                $state['pending_digest'] = hash('sha256', $token);
                $state['pending_origins'] = [];
                $state['pending_sponsors'] = [];
                $state['pending_secret_digest'] = hash(
                    'sha256',
                    strtolower(ascii_trim($liveSecret))
                );
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
