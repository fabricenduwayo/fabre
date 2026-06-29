package com.mariner.forensic;

/**
 * Mariner AES-GCM forensic pipeline (starter scaffold).
 *
 * Usage: java com.mariner.forensic.Main &lt;rules|correlate|decrypt&gt;
 *
 *   rules      extract the report's exception rules  -&gt; /app/out/rules.json
 *   correlate  resolve per-frame key/nonce from audit -&gt; /app/out/correlation.json
 *   decrypt    AES-GCM decrypt the frames             -&gt; /app/out/findings.json
 *
 * Each stage is a no-argument subcommand. The three stage classes below are
 * stubbed out — implement them as described in the milestone briefs.
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
