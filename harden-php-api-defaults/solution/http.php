<?php
// HTTP helpers: CORS, JSON responses, and error replies.

function apply_cors($config)
{
    // Only the allowlisted internal origin is granted access, and because we
    // support credentialed requests we must echo the exact origin (never '*')
    // and vary on it. Every other origin gets no CORS grant at all.
    $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : null;
    if ($origin !== null && hash_equals($config['allowed_origin'], $origin)) {
        header('Access-Control-Allow-Origin: ' . $origin);
        header('Access-Control-Allow-Credentials: true');
        header('Vary: Origin');
        header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
        header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Bootstrap-Secret');
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
