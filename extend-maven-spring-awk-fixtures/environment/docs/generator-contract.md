# Dependency seed generator contract

The Maven `generate-resources` phase must run `/app/dependency-audit/tools/flatten-deps.awk` against `/app/dependency-audit/fixtures/resolution-tree.json` and write SQL to:

`target/classes/data/seed-dependencies.sql`

That file is loaded by Spring Boot after `classpath:schema.sql`.

## Input JSON

- Top-level `buildId` string identifies the build row.
- `root` is a nested node object with `groupId`, `artifactId`, `version`, `scope`, and `children` (array of nodes).
- Child arrays may be empty. Every node uses those five fields.

## Output SQL

1. One `INSERT INTO builds (id, root_coordinate)` using `buildId` and the root GAV (`groupId:artifactId:version`).
2. One `INSERT INTO dependency_nodes` per node (root included) with columns:
   `node_key`, `build_id`, `parent_key`, `group_id`, `artifact_id`, `version`, `scope`, `ordinal`
3. Root row uses `node_key = 'root'`, `parent_key = NULL`, `ordinal = 0`.
4. Direct children of root use keys `root/0`, `root/1`, … in array order; deeper descendants extend the path (`root/0/1`, etc.).
5. Escape single quotes in SQL string literals by doubling them.

No other tables or columns. Do not hand-edit generated SQL in source control.
