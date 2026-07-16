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

    $cols = [];
    $res = $db->query('PRAGMA table_info(audit_log)');
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $cols[] = $row['name'];
    }

    if (in_array('actor', $cols, true) && !in_array('origin', $cols, true)) {
        $db->exec('ALTER TABLE audit_log RENAME TO audit_log_legacy');
        $db->exec('CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            event TEXT NOT NULL,
            route TEXT NOT NULL,
            origin TEXT,
            decision TEXT NOT NULL,
            reason TEXT
        )');
        $db->exec(
            'INSERT INTO audit_log (id, ts, event, route, origin, decision, reason)
             SELECT id, ts, event, route, actor, decision, reason FROM audit_log_legacy'
        );
        $db->exec('DROP TABLE audit_log_legacy');
    }

    return $db;
}

function audit_log($config, $event, $route, $origin, $decision, $reason)
{
    try {
        $db = audit_db($config);
        $db->exec('CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            event TEXT NOT NULL,
            route TEXT NOT NULL,
            origin TEXT,
            decision TEXT NOT NULL,
            reason TEXT
        )');
        $stmt = $db->prepare(
            'INSERT INTO audit (ts, event, route, origin, decision, reason)
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
