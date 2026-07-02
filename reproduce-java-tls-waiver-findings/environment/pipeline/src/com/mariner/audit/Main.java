package com.mariner.audit;

/**
 * Mariner TLS waiver reconciliation pipeline (broken starter scaffold).
 *
 * Usage: java com.mariner.audit.Main &lt;decode|join|validate&gt;
 *
 *   decode    parse the narrative report  -&gt; /app/out/waivers.json
 *   join      join the H2 probe evidence  -&gt; /app/out/evidence.json
 *   validate  reconcile config + decide   -&gt; /app/out/findings.json
 *
 * Each stage is a no-argument subcommand. Repair the stage classes below per
 * the milestone briefs and /app/reports/mariner-tls-waiver-review.md.
 */
public final class Main {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("usage: Main <decode|join|validate>");
            System.exit(2);
        }
        switch (args[0]) {
            case "decode" -> WaiverDecoder.run();
            case "join" -> EvidenceJoiner.run();
            case "validate" -> FindingsEngine.run();
            default -> {
                System.err.println("unknown command: " + args[0]);
                System.exit(2);
            }
        }
    }

    private Main() {}
}
