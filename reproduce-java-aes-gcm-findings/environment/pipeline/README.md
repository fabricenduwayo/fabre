# Mariner forensic pipeline (starter scaffold)

`com.mariner.forensic.Main` dispatches `rules`, `correlate`, and `decrypt`.
Build with `bash build.sh` (output under `./classes`). Run a stage after building:

    java -cp classes:/app/lib/* com.mariner.forensic.Main rules

Each stage reads inputs and writes JSON under `/app/out`.
