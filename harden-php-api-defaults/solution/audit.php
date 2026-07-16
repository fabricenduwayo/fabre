<?php
// Audit logging into the SQLite ledger. The shipped ledger predates the current
// schema (it carries a non-null legacy "actor" column and no "origin"), which is
// why inserts were failing and being swallowed. audit_db() migrates the ledger
// in place (AU-LEDGER-SCOPE + G-2026-06) while preserving historical rows, so
// writes succeed and every audited request records its origin.

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
        origin TEXT,
        decision TEXT NOT NULL,
        reason TEXT
    )');

    $cols = [];
    $res = $db->query('PRAGMA table_info(audit_log)');
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $cols[] = $row['name'];
    }

    // Legacy layout: an "actor" column and/or a missing "origin" column. Migrate
    // to the current schema, carrying every existing row forward (origin NULL for
    // rows that predate the column).
    if (!in_array('origin', $cols, true) || in_array('actor', $cols, true)) {
        $db->exec('DROP TABLE IF EXISTS audit_log_legacy');
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
        $db->exec('INSERT INTO audit_log (id, ts, event, route, origin, decision, reason)
                   SELECT id, ts, event, route, NULL, decision, reason FROM audit_log_legacy');
        $db->exec('DROP TABLE audit_log_legacy');
    }
    return $db;
}

function audit_log($config, $event, $route, $origin, $decision, $reason)
{
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
}
