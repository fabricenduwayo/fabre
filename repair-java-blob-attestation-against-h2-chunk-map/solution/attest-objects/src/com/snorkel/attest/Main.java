package com.snorkel.attest;

public final class Main {
    private static final String DEFAULT_DB_URL = "jdbc:h2:file:/app/store/objects";
    private static final String DEFAULT_OUTPUT = "/app/build/attestation-report.json";

    public static void main(String[] args) throws Exception {
        String jdbcUrl = args.length > 0 ? args[0] : DEFAULT_DB_URL;
        String outputPath = args.length > 1 ? args[1] : DEFAULT_OUTPUT;
        Auditor.run(jdbcUrl, outputPath);
    }

    private Main() {}
}
