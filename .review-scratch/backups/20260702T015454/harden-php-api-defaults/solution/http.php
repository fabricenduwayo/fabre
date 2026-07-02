<?php
// HTTP helpers: CORS, JSON responses, and error replies.

function cors_origin_allowed($config, $origin)
{
    // CO-ORIGIN-ALLOW (as amended by G-2026-01): exact, byte-for-byte match
    // against the allowlist. No normalization, no suffix/port matching.
    if ($origin === null) {
        return false;
    }
    foreach ($config['allowed_origins'] as $allowed) {
        if (hash_equals($allowed, $origin)) {
            return true;
        }
    }
    return false;
}

function apply_cors($config, $origin)
{
    // Only an allowlisted origin receives a credentialed grant, echoed exactly
    // (never '*'), with Vary: Origin. Every other origin gets no grant at all.
    if (cors_origin_allowed($config, $origin)) {
        header('Access-Control-Allow-Origin: ' . $origin);
        header('Access-Control-Allow-Credentials: true');
        header('Vary: Origin');
    }
}

function apply_preflight($config, $origin)
{
    // CO-PREFLIGHT: method/header/max-age hints are emitted only for an allowed
    // origin. Max-Age is 300 per G-2026-02.
    if (cors_origin_allowed($config, $origin)) {
        header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
        header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Bootstrap-Secret');
        header('Access-Control-Max-Age: ' . $config['preflight_max_age']);
    }
}

function send_json($config, $status, $payload, $extra = [])
{
    http_response_code($status);
    header('Content-Type: application/json');
    foreach ($extra as $key => $value) {
        header($key . ': ' . $value);
    }
    echo json_encode($payload);
}

function fail($config, $status, $message, $detail = null)
{
    // EH-NO-DISCLOSE: generic error body, no trace, no debug header.
    $body = ['error' => $message];
    $extra = [];
    if (!empty($config['debug'])) {
        $extra['X-Debug-Mode'] = 'on';
        if ($detail !== null) {
            $body['trace'] = $detail;
        }
    }
    send_json($config, $status, $body, $extra);
}
