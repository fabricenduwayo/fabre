# Mariner forensic pipeline (starter scaffold)

A minimal Java command-line scaffold for the AES-GCM media-evidence review.
`com.mariner.forensic.Main` dispatches three stages — `rules`, `correlate`, and
`decrypt`. The shipped `rules` and `correlate` stages compile but are not
normative; repair them per the milestone briefs. `decrypt` is still a stub.
Each stage reads its inputs and writes JSON under `/app/out`.

Build with:

    bash build.sh                 # compiles src/ to ./classes against /app/lib/*

Run a stage (after building):

    java -cp classes:/app/lib/* com.mariner.forensic.Main rules
