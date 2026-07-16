<?php

function audit_log($config, $event, $route, $origin, $decision, $reason)
{
    $db = new SQLite3($config['audit_db']);
    $db->enableExceptions(true);
    $db->busyTimeout(5000);
    $db->exec('BEGIN IMMEDIATE');
    try {
        $db->exec('CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            event TEXT NOT NULL,
            route TEXT NOT NULL,
            origin TEXT,
            decision TEXT NOT NULL,
            reason TEXT
        )');
        $columns = [];
        $result = $db->query('PRAGMA table_info(audit_log)');
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $columns[] = $row['name'];
        }
        if (in_array('actor', $columns, true) || !in_array('origin', $columns, true)) {
            $db->exec('DROP TABLE IF EXISTS audit_log_reconciled');
            $db->exec('CREATE TABLE audit_log_reconciled (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event TEXT NOT NULL,
                route TEXT NOT NULL,
                origin TEXT,
                decision TEXT NOT NULL,
                reason TEXT
            )');
            $db->exec(
                'INSERT INTO audit_log_reconciled
                    (id, ts, event, route, origin, decision, reason)
                 SELECT id, ts, event, route, NULL, decision, reason
                 FROM audit_log ORDER BY id'
            );
            $db->exec('DROP TABLE audit_log');
            $db->exec('ALTER TABLE audit_log_reconciled RENAME TO audit_log');
        }

        $stmt = $db->prepare(
            'INSERT INTO audit_log (ts, event, route, origin, decision, reason)
             VALUES (:ts, :event, :route, :origin, :decision, :reason)'
        );
        $stmt->bindValue(':ts', gmdate('c'), SQLITE3_TEXT);
        $stmt->bindValue(':event', $event, SQLITE3_TEXT);
        $stmt->bindValue(':route', $route, SQLITE3_TEXT);
        $stmt->bindValue(':origin', $origin, $origin === null ? SQLITE3_NULL : SQLITE3_TEXT);
        $stmt->bindValue(':decision', $decision, SQLITE3_TEXT);
        $stmt->bindValue(':reason', $reason, $reason === null ? SQLITE3_NULL : SQLITE3_TEXT);
        $stmt->execute();
        $db->exec('COMMIT');
    } catch (Throwable $error) {
        $db->exec('ROLLBACK');
        $db->close();
        throw $error;
    }
    $db->close();
}
