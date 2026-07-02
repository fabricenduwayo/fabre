<?php

function audit_db($config)
{
    $db = new SQLite3($config['audit_db']);
    $db->enableExceptions(true);
    $db->busyTimeout(2000);
    $db->exec('CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        event TEXT NOT NULL,
        route TEXT NOT NULL,
        actor TEXT NOT NULL,
        decision TEXT NOT NULL,
        reason TEXT
    )');
    return $db;
}

function audit_log($config, $event, $route, $origin, $decision, $reason)
{
    try {
        $db = audit_db($config);
        $stmt = $db->prepare(
            'INSERT INTO audit_log (ts, event, route, origin, decision, reason)
             VALUES (:ts, :event, :route, :origin, :decision, :reason)'
        );
        $stmt->bindValue(':ts', gmdate('c'));
        $stmt->bindValue(':event', $event);
        $stmt->bindValue(':route', $route);
        $stmt->bindValue(':origin', $origin);
        $stmt->bindValue(':decision', $decision);
        $stmt->bindValue(':reason', $reason);
        $stmt->execute();
        $db->close();
    } catch (Throwable $e) {
        if (!empty($config['debug'])) {
            error_log('audit: ' . $e->getMessage());
        }
    }
}
