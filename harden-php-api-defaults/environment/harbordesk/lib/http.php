<?php
// HTTP helpers: CORS, JSON responses, and error replies.

function apply_cors($config)
{
    // Staging default: hand the configured origin to everyone, with credentials
    // turned on for the frontend.
    header('Access-Control-Allow-Origin: ' . $config['cors_allow_origin']);
    header('Access-Control-Allow-Credentials: true');
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Bootstrap-Secret');
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
    // Staging default: surface internals to make debugging easier.
    if (!empty($config['debug'])) {
        $extra['X-Debug-Mode'] = 'on';
        if ($detail !== null) {
            $body['trace'] = $detail;
        }
    }
    send_json($config, $status, $body, $extra);
}
