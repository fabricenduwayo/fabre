# Mariner TLS waiver pipeline (starter scaffold)

A minimal Java command-line scaffold for the TLS waiver reconciliation review.
`com.mariner.audit.Main` dispatches three stages — `decode`, `join`, and
`validate` — each currently an unimplemented stub. Implement them per the
milestone briefs so each stage reads its inputs and writes its JSON output under
`/app/out`.

Build with:

    bash build.sh                 # compiles src/ to ./classes against /app/lib/*

Run a stage (after building):

    java -cp classes:/app/lib/* com.mariner.audit.Main decode
