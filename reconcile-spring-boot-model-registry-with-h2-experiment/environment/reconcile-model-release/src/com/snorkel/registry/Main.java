package com.snorkel.registry;

/**
 * Reconcile registry API candidates with H2 experiment evidence.
 *
 * Usage:
 *   java -cp '/app/reconcile-model-release/classes:/app/lib/*' com.snorkel.registry.Main [jdbc-url] [output-path]
 */
public final class Main {
    private static final String DEFAULT_DB_URL = "jdbc:h2:file:/app/experiment-db/experiments";
    private static final String DEFAULT_OUTPUT = "/app/build/release-decision.json";

    public static void main(String[] args) throws Exception {
        String jdbcUrl = args.length > 0 ? args[0] : DEFAULT_DB_URL;
        String outputPath = args.length > 1 ? args[1] : DEFAULT_OUTPUT;
        Reconciler.reconcile(jdbcUrl, outputPath);
    }

    private Main() {}
}
