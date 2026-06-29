# Mariner forensic pipeline (starter scaffold)

A minimal Java command-line scaffold for the AES-GCM media-evidence review.
`com.mariner.forensic.Main` dispatches three stages — `rules`, `correlate`, and
`decrypt` — each currently an unimplemented stub. Implement them per the
milestone briefs so each stage reads its inputs and writes its JSON output under
`/app/out`.

Build with:

    bash build.sh                 # compiles src/ to ./classes against /app/lib/*

Run a stage (after building):

    java -cp classes:/app/lib/* com.mariner.forensic.Main rules
