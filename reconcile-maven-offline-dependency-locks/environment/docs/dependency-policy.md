# MeterHub dependency policy

This policy governs which artifact versions the MeterHub build may bind. The
local Maven repository on this machine is the complete universe of allowed
artifacts: every version you may choose already sits in it, and nothing may be
fetched from anywhere else.

## Security floors

Versions below these floors carry known defects and must not appear anywhere in
the resolved dependency tree, including transitively:

| artifact | minimum version |
|----------|-----------------|
| io.meterhub:wire-format | 2.2.0 |
| io.meterhub:telemetry-client | 1.3.0 |

A floor applies to what the build actually resolves, not to what a pom happens
to declare. If a dependency declares an older transitive, the build must
override it.

## Compatibility matrix

Wire compatibility is a runtime property, not a compile-time one. A binding
that compiles but fails at runtime violates this policy.

| artifact | compatible wire-format |
|----------|------------------------|
| telemetry-client 1.2.x | 2.x only |
| telemetry-client 1.4.x | 2.x only |
| format-legacy 0.9.x | 2.x only |
| format-legacy 1.1.x | 3.x only |

The whole build binds exactly one wire-format version. Modules must not
diverge from each other.

## Repository discipline

Builds run fully offline against the local repository. No pom in the project
may declare `<repositories>` or `<pluginRepositories>`; a build that needs a
remote repository to resolve is non-compliant even if that repository is
unreachable.

## Reproducibility

Two consecutive clean builds must produce byte-identical module jars. Maven
supports this natively; a build whose artifacts embed wall-clock timestamps is
non-compliant.

## Change discipline

Reconcile the build by choosing versions, overriding transitives, and removing
non-compliant configuration. Application source code under the modules is
correct as written and is not part of the reconciliation.
