-- generated store seed; do not edit by hand

INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0001', 'prod', '7c96d9c62f996a8a7a13bbb3a159b8e31865fecedcd582079d8bcbf1212f24e3', 'sha256', 'blobs/obj-0001.bin', 211, '2026-01-10 00:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0002', 'prod', '3d537591896c8cc685a99e51775c2018f14eb0f7e058450f751e21fb09748bb1', 'sha256', 'blobs/obj-0002.bin', 222, '2026-02-11 01:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0003', 'prod', 'df5a75aa2d09bd2ef48caac9928af65c78e862cea92cc2207f4045a8b9b9dfcb', 'sha256', 'blobs/obj-0003.bin', 233, '2026-03-12 02:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0004', 'prod', '0c8381aa85cd7620e3381e2f907614bdb207da9c624d09d443abd3d262bbe1e6', 'sha256', 'blobs/obj-0004.bin', 244, '2026-04-13 03:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0005', 'prod', 'c97a5b3e80aae333ceea1a83cf002003aa108f1615da09b1e266c8ff2fb019b9', 'sha256', 'blobs/obj-0005.bin', 250, '2026-05-14 04:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0006', 'prod', 'cfd0fc9d11a8d849d6e809f2bc42d0509a0ea6d5d431a73d87c245e83773f064', 'sha256', 'blobs/obj-0006.bin', 250, '2026-06-15 05:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0007', 'prod', 'f32b99dd75077c4cb79fa83aff932e04960932500e99d4a9424013aed4fc1891', 'sha256', 'blobs/obj-0007.bin', 277, '2026-07-16 06:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0008', 'prod', '70f6897c267ad4740fd71792d8b628514acfbae23ad9e9eb37d78e511d04e209', 'sha256', 'blobs/obj-0008.bin', 288, '2026-08-17 07:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0009', 'prod', '0000000000000000000000000000000000000000000000000000000000000000', 'sha256', 'blobs/obj-0009.bin', 300, '2026-09-18 08:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0010', 'prod', '1111111111111111111111111111111111111111111111111111111111111111', 'sha256', 'blobs/obj-0010.bin', 180, '2026-01-10 00:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0011', 'archive', '3a21b0be8ce8b9bc1e2afe102467f25508c7ee795caac0f844a56a602452e6c8', 'sha256', 'blobs/obj-0011.bin', 260, '2026-02-11 01:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0012', 'archive', '06a35f3364c2c51957db8fe8d38917bdff2b671555f102ac25dc20cff5173c7f', 'sha256', 'blobs/obj-0012.bin', 150, '2026-03-12 02:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0013', 'archive', 'b99d4c8c3609548e626b1bdf5cbf4d2e4420dab8b9dba734e1a74e10df603bcc', 'sha256', 'blobs/obj-0013.bin', 210, '2026-04-13 03:15:00');
INSERT INTO objects (object_id, bucket, declared_digest, digest_algo, blob_path, size_bytes, created_at) VALUES ('obj-0014', 'prod', '874f21907e7f3af381eae92f2f32f43ee605b42e277782f4a5b5366e7559e737', 'sha256', 'blobs/obj-0014.bin', 200, '2026-05-14 04:15:00');

INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0001', 0, 0, 'chunks/obj-0001.g0.000', 211);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0002', 0, 0, 'chunks/obj-0002.g0.000', 222);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0003', 0, 0, 'chunks/obj-0003.g0.000', 233);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0004', 0, 0, 'chunks/obj-0004.g0.000', 244);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0005', 0, 0, 'chunks/obj-0005.g0.000', 120);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0005', 0, 1, 'chunks/obj-0005.g0.001', 130);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0006', 0, 0, 'chunks/obj-0006.g0.000', 120);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0006', 0, 1, 'chunks/obj-0006.g0.001', 130);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0007', 0, 0, 'chunks/obj-0007.g0.000', 277);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0008', 0, 0, 'chunks/obj-0008.g0.000', 288);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0009', 0, 0, 'chunks/obj-0009.g0.000', 300);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0010', 0, 0, 'chunks/obj-0010.g0.000', 180);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0013', 0, 0, 'chunks/obj-0013.g0.000', 210);
INSERT INTO object_chunks (object_id, generation, ordinal, chunk_path, size_bytes) VALUES ('obj-0014', 0, 0, 'chunks/obj-0014.g0.000', 200);

INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0001', 'verified', '7c96d9c62f996a8a7a13bbb3a159b8e31865fecedcd582079d8bcbf1212f24e3', '2026-01-10 00:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0002', 'verified', '3d537591896c8cc685a99e51775c2018f14eb0f7e058450f751e21fb09748bb1', '2026-02-11 01:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0003', 'verified', 'df5a75aa2d09bd2ef48caac9928af65c78e862cea92cc2207f4045a8b9b9dfcb', '2026-03-12 02:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0004', 'verified', '0c8381aa85cd7620e3381e2f907614bdb207da9c624d09d443abd3d262bbe1e6', '2026-04-13 03:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0005', 'verified', 'c97a5b3e80aae333ceea1a83cf002003aa108f1615da09b1e266c8ff2fb019b9', '2026-05-14 04:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0006', 'verified', 'cfd0fc9d11a8d849d6e809f2bc42d0509a0ea6d5d431a73d87c245e83773f064', '2026-06-15 05:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0007', 'verified', 'f32b99dd75077c4cb79fa83aff932e04960932500e99d4a9424013aed4fc1891', '2026-07-16 06:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0008', 'verified', '70f6897c267ad4740fd71792d8b628514acfbae23ad9e9eb37d78e511d04e209', '2026-08-17 07:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0009', 'verified', '0000000000000000000000000000000000000000000000000000000000000000', '2026-09-18 08:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0010', 'failed', NULL, '2026-01-10 00:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0011', 'verified', '3a21b0be8ce8b9bc1e2afe102467f25508c7ee795caac0f844a56a602452e6c8', '2026-02-11 01:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0012', 'verified', '06a35f3364c2c51957db8fe8d38917bdff2b671555f102ac25dc20cff5173c7f', '2026-03-12 02:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0013', 'verified', 'b99d4c8c3609548e626b1bdf5cbf4d2e4420dab8b9dba734e1a74e10df603bcc', '2026-04-13 03:15:00');
INSERT INTO attestation_cache (object_id, status, digest, verified_at) VALUES ('obj-0014', 'failed', NULL, '2026-05-14 04:15:00');
