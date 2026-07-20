-- Canonical ledger produced by the ingester. One row per surviving entry.

CREATE TABLE canonical_ledger (
  seq          BIGINT       NOT NULL,
  account      VARCHAR(64)  NOT NULL,
  counterparty VARCHAR(128) NOT NULL,
  amount       DECIMAL(18,2) NOT NULL,
  memo         VARCHAR(512) NOT NULL,
  source_file  VARCHAR(128) NOT NULL,
  source_line  INT          NOT NULL
);
