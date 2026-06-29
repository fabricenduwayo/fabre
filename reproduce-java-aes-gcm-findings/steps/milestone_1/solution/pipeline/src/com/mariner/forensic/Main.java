package com.mariner.forensic;

/**
 * Mariner AES-GCM forensic reproduction pipeline.
 *
 * Usage: java com.mariner.forensic.Main &lt;rules|correlate|decrypt&gt;
 */
public final class Main {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("usage: Main <rules|correlate|decrypt>");
            System.exit(2);
        }
        switch (args[0]) {
            case "rules" -> RuleExtractor.run();
            case "correlate" -> AuditCorrelator.run();
            case "decrypt" -> MediaDecryptor.run();
            default -> {
                System.err.println("unknown command: " + args[0]);
                System.exit(2);
            }
        }
    }

    private Main() {}
}
