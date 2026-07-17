<?php

function cors_origin_allowed($config, $origin)
{
    return $origin !== null && in_array($origin, $config['allowed_origins'], true);
}

function apply_cors($config, $origin)
{
    if (cors_origin_allowed($config, $origin)) {
        header('Access-Control-Allow-Origin: ' . $origin);
        header('Access-Control-Allow-Credentials: true');
        header('Vary: Origin');
    }
}

function apply_preflight($config, $origin)
{
    if (cors_origin_allowed($config, $origin)) {
        header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
        header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Bootstrap-Secret');
        header('Access-Control-Max-Age: ' . $config['preflight_max_age']);
    }
}

function send_json($config, $status, $payload)
{
    http_response_code($status);
    header('Content-Type: application/json');
    echo json_encode($payload);
}

function fail($config, $status, $message)
{
    send_json($config, $status, ['error' => $message]);
}

function ascii_trim($value)
{
    return trim($value, " \t\n\r\0\x0B");
}

function read_bootstrap_secret($config)
{
    if (!is_file($config['bootstrap_secret_file'])) {
        return null;
    }
    return ascii_trim((string) file_get_contents($config['bootstrap_secret_file']));
}

function secret_matches($expected, $presented)
{
    if ($expected === null || $presented === null) {
        return false;
    }
    $left = hash('sha256', strtolower(ascii_trim($expected)));
    $right = hash('sha256', strtolower(ascii_trim($presented)));
    return hash_equals($left, $right);
}

function read_credential_generation($config)
{
    if (!is_file($config['credential_generation_file'])) {
        return null;
    }
    $raw = ascii_trim((string) file_get_contents($config['credential_generation_file']));
    if (!preg_match('/^(0|[1-9][0-9]*)$/', $raw)) {
        return null;
    }
    $generation = filter_var($raw, FILTER_VALIDATE_INT, ['options' => ['min_range' => 0]]);
    return $generation === false ? null : $generation;
}

function digest_valid($value)
{
    return is_string($value) && preg_match('/^[0-9a-f]{64}$/', $value) === 1;
}

function read_token_state_unlocked($config)
{
    if (!is_file($config['token_file'])) {
        return ['exists' => false, 'valid' => false, 'state' => null];
    }
    $decoded = json_decode((string) file_get_contents($config['token_file']), true);
    $valid = is_array($decoded)
        && ($decoded['version'] ?? null) === 2
        && is_int($decoded['generation'] ?? null)
        && $decoded['generation'] >= 0
        && digest_valid($decoded['current_digest'] ?? null)
        && is_int($decoded['previous_uses_remaining'] ?? null)
        && $decoded['previous_uses_remaining'] >= 0
        && is_array($decoded['pending_origins'] ?? null);
    if (!$valid) {
        return ['exists' => true, 'valid' => false, 'state' => null];
    }
    $previousDigest = $decoded['previous_digest'] ?? null;
    $previousGeneration = $decoded['previous_generation'] ?? null;
    $valid = $valid && (
        ($previousDigest === null && $previousGeneration === null)
        || (digest_valid($previousDigest)
            && is_int($previousGeneration)
            && $previousGeneration >= 0
            && $previousGeneration < $decoded['generation'])
    );
    $pendingDigest = $decoded['pending_digest'] ?? null;
    $pendingGeneration = $decoded['pending_generation'] ?? null;
    $pendingOrigins = $decoded['pending_origins'] ?? null;
    $validPending = is_array($pendingOrigins) && ((
        $pendingDigest === null
        && $pendingGeneration === null
        && $pendingOrigins === []
    ) || (
        digest_valid($pendingDigest)
        && is_int($pendingGeneration)
        && $pendingGeneration > $decoded['generation']
        && count($pendingOrigins) === count(array_unique($pendingOrigins))
        && count(array_diff($pendingOrigins, $config['allowed_origins'])) === 0
    ));
    $valid = $valid && $validPending;
    return ['exists' => true, 'valid' => $valid, 'state' => $valid ? $decoded : null];
}

function write_token_state_unlocked($config, $state)
{
    $path = $config['token_file'];
    $tmp = $path . '.tmp.' . getmypid() . '.' . bin2hex(random_bytes(4));
    $encoded = json_encode($state, JSON_UNESCAPED_SLASHES);
    if ($encoded === false || file_put_contents($tmp, $encoded . "\n", LOCK_EX) === false) {
        @unlink($tmp);
        throw new RuntimeException('credential state write failed');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('credential state publish failed');
    }
    chmod($path, 0600);
}

function with_token_state_lock($config, $callback)
{
    $lock = fopen($config['token_lock_file'], 'c+');
    if ($lock === false) {
        throw new RuntimeException('credential lock open failed');
    }
    chmod($config['token_lock_file'], 0600);
    if (!flock($lock, LOCK_EX)) {
        fclose($lock);
        throw new RuntimeException('credential lock failed');
    }
    try {
        return $callback();
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}
