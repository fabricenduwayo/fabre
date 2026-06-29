package com.mariner.audit;

/**
 * Mariner TLS waiver reconciliation pipeline.
 *
 * Usage: java com.mariner.audit.Main &lt;decode|join|validate&gt;
 *
 *   decode    parse the narrative report  -> /app/out/waivers.json
 *   join      join the H2 probe evidence  -> /app/out/evidence.json
 *   validate  reconcile config + decide   -> /app/out/findings.json
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
