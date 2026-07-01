-- Mariner forensic audit store. Loaded into SQLite at image build.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS audit_events;
DROP TABLE IF EXISTS ingestion_metadata;
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
    supersedes_nonce_hex    TEXT,
    recorded_at             TEXT NOT NULL,
    FOREIGN KEY (frame_id) REFERENCES frames(frame_id)
);

CREATE TABLE ingestion_metadata (
    report_id   TEXT PRIMARY KEY,
    review_date TEXT NOT NULL
);

INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-001', 'alpha-channel', 0);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-002', 'bravo-channel', 1);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-003', 'charlie-channel', 2);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-004', 'delta-channel', 4);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-005', 'echo-channel', 5);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-006', 'foxtrot-channel', 6);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-007', 'golf-channel', 7);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-008', 'hotel-channel', 8);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-009', 'india-channel', 9);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-010', 'juliet-channel', 10);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-011', 'kilo-channel', 11);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-012', 'lima-channel', 12);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-013', 'mike-channel', 13);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-014', 'november-channel', 14);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-015', 'oscar-channel', 15);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-016', 'papa-channel', 16);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-017', 'quebec-channel', 17);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-018', 'sierra-channel', 18);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-019', 'tango-channel', 19);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-020', 'uniform-channel', 20);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-021', 'victor-channel', 21);
INSERT INTO frames (frame_id, label, gif_index) VALUES ('frm-022', 'whiskey-channel', 22);

INSERT INTO key_material (key_version, key_hex) VALUES (1, '4220382C46144233B13842B212FA655E1F9477D0BBA6F521E229591187E20F7B');
INSERT INTO key_material (key_version, key_hex) VALUES (2, '6FA99B5FC8E7410562BB1454106D847F8854FAA824D305EE211BB9CFF5B8C5DF');
INSERT INTO key_material (key_version, key_hex) VALUES (3, '99B142A5C05D78B67EAC363D4282B87EE17F18BD96905A64A2CA0D20B7BBDDA7');
INSERT INTO key_material (key_version, key_hex) VALUES (4, 'A50910B673AEAD384BC3B016996AD899490D6854EA406A68194E42ADBCBD4E39');
INSERT INTO key_material (key_version, key_hex) VALUES (5, 'CED0E4593CCF957B392EF6EBA154EE7479D7792AEF80E05FBC4AEA98CB6284E4');
INSERT INTO key_material (key_version, key_hex) VALUES (6, '9C0C1826C45E36F2643A7692DCD84C70F45EF2996C5296A0F4CA13D65CC51DB2');

INSERT INTO ingestion_metadata (report_id, review_date) VALUES
    ('MR-2026-007', '2026-07-15'),
    ('MR-2026-019', '2026-07-15');

INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-022', 'key_rotated', 2, 4, NULL, NULL, '2026-05-20 12:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-022', 'nonce_override_registered', 2, NULL, 'FACEFACEFACEFACEFACEFACE', NULL, '2026-05-18 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-022', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-08 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-021', 'key_rotation_rescinded', 2, 5, NULL, NULL, '2026-05-25 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-021', 'key_rotated', 2, 5, NULL, NULL, '2026-05-24 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-021', 'key_assignment_rescinded', 6, NULL, NULL, NULL, '2026-05-22 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-021', 'key_assigned', 6, NULL, NULL, NULL, '2026-05-20 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-021', 'key_rotation_rescinded', 2, 4, NULL, NULL, '2026-05-16 13:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-021', 'key_rotated', 2, 4, NULL, NULL, '2026-05-15 12:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-021', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-08 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-020', 'nonce_override_amended', 2, NULL, 'D4E5F60718293A4B5C6D7E8F', 'C3D4E5F60718293A4B5C6D7E', '2026-05-24 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-020', 'nonce_override_amended', 2, NULL, 'C3D4E5F60718293A4B5C6D7E', 'B2C3D4E5F60718293A4B5C6D', '2026-05-20 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-020', 'nonce_override_registered', 2, NULL, 'B2C3D4E5F60718293A4B5C6D', NULL, '2026-05-16 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-020', 'nonce_override_registered', 2, NULL, 'A1B2C3D4E5F60718293A4B5C', NULL, '2026-05-14 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-020', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-09 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-019', 'key_rotation_rescinded', 3, 5, NULL, NULL, '2026-05-19 15:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-019', 'key_rotated', 3, 5, NULL, NULL, '2026-05-18 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-019', 'key_rotated', 1, 3, NULL, NULL, '2026-05-12 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-019', 'key_assigned', 1, NULL, NULL, NULL, '2026-05-05 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-018', 'key_assignment_rescinded', 6, NULL, NULL, NULL, '2026-05-22 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-018', 'key_assigned', 6, NULL, NULL, NULL, '2026-05-20 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-018', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-08 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-017', 'nonce_override_registered', 2, NULL, '5566778899AABBCCDDEEFF00', NULL, '2026-05-26 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-017', 'nonce_override_registered', 4, NULL, '66778899AABBCCDDEEFF0011', NULL, '2026-05-25 18:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-017', 'nonce_override_amended', 4, NULL, '778899AABBCCDDEEFF001122', '66778899AABBCCDDEEFF0011', '2026-05-23 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-017', 'nonce_override_registered', 4, NULL, '66778899AABBCCDDEEFF0011', NULL, '2026-05-21 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-017', 'nonce_override_registered', 4, NULL, '5566778899AABBCCDDEEFF00', NULL, '2026-05-19 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-017', 'key_rotated', 2, 4, NULL, NULL, '2026-05-15 12:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-017', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-07 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-016', 'nonce_override_amended', 2, NULL, '33445566778899AABBCCDDEE', '112233445566778899AABBCC', '2026-05-22 15:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-016', 'nonce_override_registered', 2, NULL, '112233445566778899AABBCC', NULL, '2026-05-18 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-016', 'nonce_override_registered', 2, NULL, 'AABBCCDDEEFF001122334455', NULL, '2026-05-14 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-016', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-09 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-015', 'key_rotated', 2, 4, NULL, NULL, '2026-05-16 12:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-015', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-08 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-014', 'nonce_override_registered', 4, NULL, 'ABCDEF0123456789ABCDEF01', NULL, '2026-05-22 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-014', 'nonce_override_registered', 2, NULL, '998877665544332211009988', NULL, '2026-05-20 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-014', 'key_rotated', 2, 4, NULL, NULL, '2026-05-18 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-014', 'nonce_override_registered', 2, NULL, '000102030405060708090A0B', NULL, '2026-05-12 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-014', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-10 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-013', 'key_rotated', 2, 4, NULL, NULL, '2026-05-25 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-013', 'nonce_override_revoked', 2, NULL, 'FFEEDDCCBBAA998877665544', NULL, '2026-05-22 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-013', 'nonce_override_registered', 2, NULL, 'FFEEDDCCBBAA998877665544', NULL, '2026-05-20 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-013', 'nonce_override_registered', 2, NULL, '112233445566778899AABBCC', NULL, '2026-05-15 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-013', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-10 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-012', 'key_rotated', 2, 4, NULL, NULL, '2026-05-24 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-012', 'nonce_override_registered', 2, NULL, 'D0E1F2A3B4C5D6E7F8091A2B', NULL, '2026-05-18 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-012', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-09 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-011', 'key_assigned', 6, NULL, NULL, NULL, '2026-05-28 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-011', 'key_rotated', 2, 4, NULL, NULL, '2026-05-22 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-011', 'key_rotated', 6, 2, NULL, NULL, '2026-05-15 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-011', 'key_rotated', 1, 6, NULL, NULL, '2026-05-08 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-011', 'key_assigned', 1, NULL, NULL, NULL, '2026-05-01 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-010', 'nonce_override_registered', 2, NULL, 'FEEDFACECAFE000000000001', NULL, '2026-05-27 17:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-010', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-14 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-009', 'key_assigned', 3, NULL, NULL, NULL, '2026-05-26 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-009', 'key_rotation_rescinded', 2, 4, NULL, NULL, '2026-05-21 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-009', 'key_rotated', 2, 4, NULL, NULL, '2026-05-20 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-009', 'key_rotated', 2, 5, NULL, NULL, '2026-05-17 12:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-009', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-07 08:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-008', 'nonce_override_revoked', 2, NULL, 'AABBCCDDEEFF001122334455', NULL, '2026-05-27 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-008', 'nonce_override_registered', 2, NULL, 'AABBCCDDEEFF001122334455', NULL, '2026-05-26 18:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-008', 'nonce_override_registered', 2, NULL, 'C1D2E3F4029384758690A1B2', NULL, '2026-05-24 16:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-008', 'nonce_override_registered', 2, NULL, 'FFFFFFFFFFFFFFFFFFFFFFFF', NULL, '2026-05-21 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-008', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-13 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-007', 'nonce_override_registered', 2, NULL, 'B4E19A7305C2D8F61E0A4B9C', NULL, '2026-05-23 15:30:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-007', 'nonce_override_registered', 2, NULL, 'DEADBEEF0000000000000000', NULL, '2026-05-20 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-007', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-11 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-006', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-08 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-005', 'key_rotated', 3, 2, NULL, NULL, '2026-05-19 14:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-005', 'key_assigned', 3, NULL, NULL, NULL, '2026-05-06 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-004', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-25 12:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-004', 'key_rotated', 2, 4, NULL, NULL, '2026-05-21 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-004', 'key_rotated', 1, 2, NULL, NULL, '2026-05-09 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-004', 'key_assigned', 1, NULL, NULL, NULL, '2026-05-02 09:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-003', 'nonce_override_registered', 2, NULL, 'A7C3E91B4D2F8065E1B9C0A3', NULL, '2026-05-22 16:45:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-003', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-12 10:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-002', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-20 11:00:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-002', 'key_rotated', 1, 3, NULL, NULL, '2026-05-18 14:30:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-002', 'key_assigned', 1, NULL, NULL, NULL, '2026-05-04 08:15:00');
INSERT INTO audit_events (frame_id, event_type, key_version, replacement_key_version, nonce_override_hex, supersedes_nonce_hex, recorded_at) VALUES ('frm-001', 'key_assigned', 2, NULL, NULL, NULL, '2026-05-10 09:00:00');

