<?php

function read_admin_token($config)
{
    static $cached = null;
    static $loaded = false;
    if (!$loaded) {
        $cached = is_file($config['token_file']) ? trim(file_get_contents($config['token_file'])) : null;
        $loaded = true;
    }
    return $cached;
}

function admin_token_exists($config)
{
    static $exists = null;
    if ($exists === null) {
        $exists = is_file($config['token_file']);
    }
    return $exists;
}

function read_bootstrap_secret($config)
{
    static $cached = null;
    static $loaded = false;
    if (!$loaded) {
        $cached = is_file($config['bootstrap_secret_file'])
            ? trim(file_get_contents($config['bootstrap_secret_file']))
            : null;
        $loaded = true;
    }
    return $cached;
}

function apply_cors($config)
{
    static $sticky_origin = null;
    $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : null;
    if ($origin !== null && in_array($origin, $config['allowed_origins'], true)) {
        $sticky_origin = $origin;
    }

    if ($sticky_origin !== null) {
        header('Access-Control-Allow-Origin: ' . $sticky_origin);
        header('Access-Control-Allow-Credentials: true');
    } elseif (!empty($config['cors_allow_origin'])) {
        header('Access-Control-Allow-Origin: ' . $config['cors_allow_origin']);
        header('Access-Control-Allow-Credentials: true');
    }
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Bootstrap-Secret');
}

function apply_preflight($config)
{
    header('Access-Control-Max-Age: ' . $config['preflight_max_age']);
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
