Milestone 2: read `/app/out/rules.json` from milestone 1 and correlate each in-scope frame from SQLite against it. Voiding, ordering, and scoping semantics in the forensic report's normative appendix govern which audit events count.

Load each in-scope row from the SQLite `frames` table and copy `label` and `gif_index` into every correlation record. Replace the broken correlate stage and write `/app/out/correlation.json` per `/app/schema/correlation.schema.json`. Keep `com.mariner.forensic.Main correlate` callable from compiled classes.
