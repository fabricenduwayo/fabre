package com.snorkel.ingest;

import java.nio.file.Path;

public final class Main {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("usage: <corpus-dir> <jdbc-url> <summary-json>");
            System.exit(2);
        }
        Normaliser.ingest(Path.of(args[0]), args[1], Path.of(args[2]));
    }

    private Main() {}
}
