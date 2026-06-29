-- Mariner forensic audit store. Loaded into SQLite at image build.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS audit_events;
DROP TABLE IF EXISTS key_material;
DROP TABLE IF EXISTS frames;

CREATE TABLE frames (
    frame_id   TEXT PRIMARY KEY,
    label      TEXT NOT NULL,
    gif_index  INTEGER NOT NULL
);

CREATE TABLE key_material (
    key_version INTEGER PRIMARY KEY,
    key_hex     TEXT NOT NULL
);

CREATE TABLE audit_events (
    event_id                INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id                TEXT NOT NULL,
    event_type              TEXT NOT NULL,
    key_version             INTEGER,
    replacement_key_version INTEGER,
    nonce_override_hex      TEXT,
    recorded_at             TEXT NOT NULL,
    FOREIGN KEY (frame_id) REFERENCES frames(frame_id)
);

INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-001', 'alpha-channel', 0);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-002', 'bravo-channel', 1);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-003', 'charlie-channel', 2);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-004', 'delta-channel', 4);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-005', 'echo-channel', 5);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-006', 'foxtrot-channel', 6);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-007', 'golf-channel', 7);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-008', 'hotel-channel', 8);

INSERT INTO key_material (key_version, key_hex) VALUES (1, '4220382C46144233B13842B212FA655E1F9477D0BBA6F521E229591187E20F7B');
INSERT INTO key_material (key_version, key_hex) VALUES (2, '6FA99B5FC8E7410562BB1454106D847F8854FAA824D305EE211BB9CFF5B8C5DF');
INSERT INTO key_material (key_version, key_hex) VALUES (3, '99B142A5C05D78B67EAC363D4282B87EE17F18BD96905A64A2CA0D20B7BBDDA7');
INSERT INTO key_material (key_version, key_hex) VALUES (4, 'A50910B673AEAD384BC3B016996AD899490D6854EA406A68194E42ADBCBD4E39');

INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-008', 'nonce_override_registered', 2, NULL, 'C1D2E3F4029384758690A1B2', '2026-05-24 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-008', 'nonce_override_registered', 2, NULL, 'FFFFFFFFFFFFFFFFFFFFFFFF', '2026-05-21 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-008', 'key_assigned', 2, NULL, NULL, '2026-05-13 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-007', 'nonce_override_registered', 2, NULL, 'B4E19A7305C2D8F61E0A4B9C', '2026-05-23 15:30:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-007', 'nonce_override_registered', 2, NULL, 'DEADBEEF0000000000000000', '2026-05-20 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-007', 'key_assigned', 2, NULL, NULL, '2026-05-11 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-006', 'key_assigned', 2, NULL, NULL, '2026-05-08 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-005', 'key_rotated', 3, 2, NULL, '2026-05-19 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-005', 'key_assigned', 3, NULL, NULL, '2026-05-06 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-004', 'key_assigned', 2, NULL, NULL, '2026-05-25 12:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-004', 'key_rotated', 2, 4, NULL, '2026-05-21 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-004', 'key_rotated', 1, 2, NULL, '2026-05-09 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-004', 'key_assigned', 1, NULL, NULL, '2026-05-02 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-003', 'nonce_override_registered', 2, NULL, 'A7C3E91B4D2F8065E1B9C0A3', '2026-05-22 16:45:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-003', 'key_assigned', 2, NULL, NULL, '2026-05-12 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-002', 'key_assigned', 2, NULL, NULL, '2026-05-20 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-002', 'key_rotated', 1, 3, NULL, '2026-05-18 14:30:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-002', 'key_assigned', 1, NULL, NULL, '2026-05-04 08:15:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, recorded_at) VALUES ('frm-001', 'key_assigned', 2, NULL, NULL, '2026-05-10 09:00:00');

