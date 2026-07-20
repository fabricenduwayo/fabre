package com.snorkel.attest;

/**
 * Release attestation worker CLI.
 *
 * Usage:
 *   java -cp '/app/attest-worker/classes:/app/lib/*' com.snorkel.attest.Main [jdbc-url]
 */
public final class Main {
    private static final String DEFAULT_DB_URL = "jdbc:h2:file:/app/attestation-db/attestation";

    public static void main(String[] args) throws Exception {
        String jdbcUrl = args.length > 0 ? args[0] : DEFAULT_DB_URL;
        Worker.run(jdbcUrl);
    }

    private Main() {}
}
