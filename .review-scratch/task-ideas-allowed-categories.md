I read the Maven task, the reconcile harness (`tests/helpers.py`, the variant tests), the trailswitch and harden-php instructions for voice, the authoring rules, and the abandoned `rebuild-java-ledger-ingest-parity` task. Two things from that reading change the analysis, and I've built the ranking around them.

**The abandoned task declared `category = "security"` in its `task.toml` and still classified data-processing at 0.95.** Its tags were `audit-trail`, `tamper-evidence`, `duplicate-claims`, `text-encoding`. So it wasn't a labelling failure. Comparing it to the seven that cleared gives a sharper rule than "reframe the prose":

> **Programs that emit judgments clear as security. Programs that emit records get read as data-processing.** The killed task's deliverable was a populated `canonical_ledger` table plus per-file counts — a transformed dataset. Every task that cleared emits verdicts: promoted/rejected, allow/deny, compliant/violating. Use that as the go/no-go filter on any new mechanic, before writing a line.

**Second: two of the Maven concepts took fatals for the same structural reason, and it generalises further than the scorer noted.** I'll cover that in the straight answer at the end.

---

# 1. `repair-java-blob-attestation-against-h2-chunk-map`

**Category** security · **Subcategories** `api_integration`, `db_interaction` · **Languages** java, sql, bash
**Stack** Java 17, bundled in-process HTTP API + H2 2.2.224 from `/app/lib/`, plain `javac` via `build.sh`, no Spring needed, no network.

**Premise**

> The blob store at `/app/blob-store` serves objects over a local HTTP API backed by H2 at `jdbc:h2:file:/app/store/objects`, and its attestation endpoint reports every object as verified, which we know is wrong because customers have pulled back content that does not match what they uploaded. Finish the auditor at `/app/attest-objects` and build it with `/app/attest-objects/build.sh` so it writes `/app/build/attestation-report.json` partitioning every object into intact, corrupt or unattestable, and recording every disagreement between the attestation cache and what the object actually hashes to under `conflicts`. The store keeps more than one copy of an object's bytes and they do not always agree, so work out which one it actually treats as durable rather than assuming. Optional positional arguments are the JDBC URL then the output path; pointing it at another compatible store has to give that store's answer, not this one's.

**Classifier safety.** Verbs are hash, attest, verify, reject, distrust. Output is three verdict buckets plus a conflict list — judgments, not records. Nearest neighbours are `reproduce-java-tls-waiver-findings` (PAYOUT_SUBMITTED) and `reconcile-spring-boot-model-registry` (accepted), both security. The one adjacency worth naming honestly: concatenating ordered chunk rows to reconstruct content is *assembly*, and assembly is data-processing-adjacent. Kill that risk in wording and in code — the program never writes reconstructed bytes anywhere, it streams them into a digest and discards them. No output artifact contains object content. Keep `chunk` out of the tags; use `content-integrity`, `attestation`, `digest-trust`, `fail-closed`, `h2`.

**Where difficulty lives.** Not in the policy. In one unstated fact with a strongly-endorsed wrong default: `blob_path` looks like the content and is not. The shipped corpus is deliberately degenerate — every object with a chunk map has exactly one chunk byte-identical to `blob_path`, and all but one row declares sha256. So "hash `blob_path`, trust the declared algorithm" reproduces the correct report on **everything the agent can see**, with zero remaining local signal. That is the exact sample-fitting mode he already measured at 34/49 divergent rows. Source reading doesn't settle it either, because the compat reader genuinely exists and is genuinely wired to another endpoint, so its presence is not evidence it's wrong. The only way to establish authority is to POST a fresh object and observe which artifact the store reads back — an experiment, not a transcription. Second miss is bucket discipline: a missing chunk file is `unattestable`, not `corrupt`; bytes matching a declared **sha1** are `unattestable`, not `intact`. Models routinely collapse both into the two-bucket intuition.

**Variants** (six verifier-built stores, expected recomputed by `helpers.py` from each store, agent's own compiled CLI re-run against all six):
A multi-chunk object whose `blob_path` is a stale earlier materialisation — chunk authority. B chunk ordinals stored out of insertion order — ordering authority. C object whose bytes match a declared sha1 — must land `unattestable`. D chunk row pointing at a missing file — `unattestable`, not `corrupt`. E `attestation_cache` asserting verified for an object that recomputes wrong — must appear in `conflicts` **and** `corrupt`. **F combines A+C+E**: multi-chunk with stale `blob_path`, declared under sha1, carrying a verified cache row — and the `blob_path` hash *matches* the declared sha1, so the wrong answer looks right. F is the analogue of the variant that measured 6/10.

**Build cost: 4-5 author-days.** Reuses `reconcile-spring-boot-model-registry` almost wholesale — `variant_schema.sql` + per-variant seed SQL, `run_h2_script`, `h2_select` (the CSVWRITE trick), the `expected_decision` recompute-from-store shape, `run_*_cli`, `environment/lib/` jars verbatim, the canonical `test.sh` reward block. New work is the ingest/attest HTTP endpoints and the chunk fixture generator.

**Honest bet: worst-model 0.35-0.50. I would bet on this one.** It is the closest possible neighbour to the only configuration he has *measured* at 0.40, in the category with seven clears. The one build-time risk to watch: if a reviewer or a model can conclude `blob_path` is stale purely by reading source, difficulty collapses to transcription. Keep the compat reader load-bearing for a real endpoint.

---

# 2. `repair-java-classpath-shadow-auditor`

**Category** build-and-dependency-management · **Subcategories** `[]` · **Languages** java, bash
**Stack** Java 17, `javac` + `jar`, tiny purpose-built stub jars generated at image build, no DB, no service, no Spring.

**Premise**

> The service classpath at `/app/shadow-audit/classpath.txt` pulls in a dozen jars and at least two of them ship the same fully-qualified classes at different versions, so which implementation we actually run depends on ordering nobody has audited. Finish the auditor at `/app/shadow-audit` and build it with `/app/shadow-audit/build.sh` so that for a given classpath file it writes `/app/build/shadow-report.json` with the effective load order, every class name that appears in more than one entry, which entry wins it, and every entry that is shadowed for it. The order in the file is not always the order that ends up on the classpath and the winning copy is not always at the top level of its jar, so derive the order the JVM would really use. It takes the classpath file then the output path as positional arguments and has to work on any classpath it is handed.

**Classifier safety.** Content is jars, manifests, classpath ordering, artifact conflict. Primary prediction build-and-dependency-management; likely secondary security (classpath shadowing is a supply-chain surface). **Both allowed — this is the only concept here that is safe whichever way the classifier leans**, which matters a lot given he just lost a finished task to it. No records, no normalisation, no transformation pipeline; the deliverable is an audit of build output, not a feature, so it isn't software engineering either.

**Where difficulty lives.** A naive first-jar-wins scan passes the entire shipped sample and is wrong on three things the sample never contains: (1) a jar whose `MANIFEST.MF` carries `Class-Path` injects entries into the effective order right after that jar, moving the winner; (2) a multi-release jar's `META-INF/versions/N/` copy outranks its own root copy when N ≤ the runtime feature version, and every sample jar is single-release; (3) the report demands the full inventory of shadowed **losers**.

**The mitigation you must build in — I checked this and the original concept overstates the closure.** `URLClassLoader.getResources(name)` returns *all* matching URLs in classpath order, winner first, and `URLClassLoader` honours `Class-Path` manifest expansion natively. So a probe-based agent gets variant A and the loser inventory for free. It does *not* get MR-jar versioning (that needs `JarFile` opened with runtime versioning). Close the gap by requiring the report to carry things no probe emits: for each winner, **which release directory it came from** (`root` or `versions/N`), and the rule that a jar listed twice registers once. Then the probe route still fails B and F, and an agent that builds the probe and gets expansion right has legitimately earned that part.

**Variants** (six held-out classpaths, jars built by `tests/`, agent's compiled auditor re-run): A `Class-Path` expansion changing a winner. B MR-jar where the versioned copy wins. C jar listed twice at different positions — second occurrence must not re-register. D directory entries and signed-jar `META-INF` entries excluded from the duplicate report. E `Class-Path` entry pointing at a nonexistent jar — skipped, not fatal. **F combines A+B**: an MR-jar reachable only through another jar's `Class-Path` expansion, so the winner is neither first nor last listed.

**Build cost: 2-3 author-days — the cheapest strong idea here.** Reuses the `javac`/`jar`-at-image-build pattern and digest-pinned base from `extend-maven-spring-awk-fixtures`, the compiled-CLI + pytest harness, the held-out grading loop. No H2, no HTTP, no Postgres. `environment/` stays tiny.

**Honest bet: 0.45-0.60 unhardened, 0.35-0.50 with the release-provenance requirement added. I'd bet on it, with that mitigation non-optional.** The residual risk is the opposite of #1's: `Class-Path` and MR-jars are standard JVM knowledge, so a model doing careful "what else could differ" reasoning can reach them unprompted. That is why F and the provenance field are load-bearing. Note: subcategories comes out empty here; if the platform prefers non-empty, add a small H2 table holding the declared inventory the report is compared against and take `db_interaction` — about half a day.

---

# 3. `reconcile-java-gateway-and-service-acls`

**Category** security · **Subcategories** `api_integration`, `db_interaction` · **Languages** java, sql, bash
**Stack** Java 17 + Spring Boot + PostgreSQL, same container trio (`init_db.sh`/`build.sh`/`start.sh`) as trailswitch, offline Maven repo.

**Premise**

> The edge gateway in `/app/edgegate` and the per-service enforcement point disagree about who can reach what, and right now the gateway is the one letting requests through that the service then refuses. Finish `AuthorizationDecider` and `AclRepository` under `/app/edgegate/src/main/java/com/edgegate/` so `POST /v1/authorize` returns a fail-closed allow or deny with its reason for any principal, method and path, computed from live PostgreSQL rows including verifier-added ones, and reports every gateway-versus-service disagreement it resolved. The service-side enforcer at `/app/edgegate/lib/service-enforcer.jar` is what production actually does, and it is the tie-breaker wherever `/app/docs/acl-contract.md` is silent — you can call it, you cannot change it. Keep principal lookups safe for arbitrary ids and make sure delegated grants terminate.

**Classifier safety.** Highest of the five. Every noun is access control: principals, roles, route patterns, method grants, deny-overrides, delegation, revocation epochs, fail-closed decision with reason code. Same mechanical shape as `repair-java-trailswitch-graph-rules`, which cleared. Nothing parses, aggregates or cleans anything.

**Where difficulty lives.** The contract is **true but deliberately incomplete**, and it says so: it doesn't state how ties between equally-specific patterns break, whether a deny inherited through a delegated role outranks a direct allow, or that a grant survives its grantor's demotion until the revocation epoch advances. Ground truth for all three lives in the shipped read-only enforcer's *behaviour*. The seeded corpus never puts two equal-specificity patterns on one path, never routes a deny through a delegation, never demotes a grantor. So a model that transcribes the contract passes everything it can run locally with no signal left, and the only route to the corners is probing the existing binary with synthesised inputs. This is precisely the axis on which `enforce-java-release-signature-trust` failed to be hard — there the whole answer was on the page; here the page is a subset of the answer, and the instruction tells the agent that plainly, which keeps it solvable.

**Variants** (six held-out ACL stores, `/v1/authorize` re-run against each): A equal-specificity tie on one path. B deny on a role reachable only through delegation. C grantor demoted after issuing, revocation epoch not yet advanced. D delegation cycle A→B→A — must terminate, must not manufacture authority. E method-level grant narrower than the route-level grant on the same pattern. **F combines A+B+C**: an equal-specificity tie where one tied pattern carries a delegated deny and its grantor was demoted. Plus the arbitrary-principal-id parameterisation test in the style of trailswitch's SQL-injection test.

**Build cost: 5-6 author-days — the most expensive of the five.** Reuses the trailswitch container, Dockerfile, script trio and live-DB-mutation helpers nearly verbatim, the offline Maven repo, the variant-seed harness, the reward block. The new cost is real: you have to author the read-only enforcer, ship it compiled-only, and guarantee its behaviour is deterministic and probeable, because it *is* the spec.

**Honest bet: 0.30-0.45 — the best difficulty mechanism of the five.** I'd bet on the difficulty and hesitate on the calendar. Build it third, when #1 has banked and the pattern is proven.

---

# 4. `reconcile-maven-mediation-with-metadata-only-repo`

**Category** build-and-dependency-management · **Subcategories** `[]` · **Languages** java, bash
**Stack** Java 17, `javac`, offline local Maven repo from the AWK task, no Spring, no H2, no service.

**Premise**

> We mirror our internal Maven repo at `/app/mirror` but the mirror only carries poms, no jars, so `mvn dependency:list` will not run against it and nobody can tell what a module's compile classpath actually resolves to. Finish the resolver at `/app/mediation` and build it with `/app/mediation/build.sh` so that given a project pom and that repository root it writes `/app/build/mediated-deps.json` with each surviving coordinate, its effective version, its effective scope, and the order Maven itself would put them in. There are worked examples under `/app/mediation/samples` with the output we expect for each, but they are examples and not the contract, so match Maven's real mediation and not just those. It takes the pom path then the repository root as positional arguments.

**Classifier safety.** The strongest in the batch — poms, GAV coordinates, `dependencyManagement`, exclusions, optional flags, scopes, `~/.m2` layout, output is literally a resolved classpath. Same shape as `extend-maven-spring-awk-fixtures` minus the AWK layer, which is his one *confirmed positive* on this category.

**Where difficulty lives.** Not in knowing Maven's rules individually — in composing them, with the sample hiding the composition. Ship ~12 sample projects with correct expected outputs so the agent can iterate to a locally-perfect implementation, and keep the sample free of: transitive scope narrowing under a `provided`/`test` parent (they drop entirely rather than narrow), exclusion inheritance to grandchildren rather than the direct child, `optional=true` honoured transitively but ignored when declared directly, `dependencyManagement` applying to transitives but losing to a direct declaration, and equal-depth ties broken by declaration order rather than higher version.

**The hole you must plug, and it is not the one the scorer flagged.** Metadata-only closes `mvn -o dependency:list` — but nothing stops the agent copying the held-out repo to a temp dir, `touch`-ing an empty `.jar` beside every `.pom`, and running real Maven against it. Maven does not inspect jar contents for `dependency:list`. That single trick passes all seven variants with zero mediation implemented. Plug it or the concept is worth nothing: **make the graded output something Maven does not emit.** Require per-coordinate *provenance* — the depth at which the winner was found and the coordinate of the losing occurrence it beat. `dependency:list` gives neither; `dependency:tree` gives depth but not the mediation loser in parseable form. That also makes the variants sharper. Do this before you build fixtures, not after.

**Variants** (seven held-out project sets, agent's compiled CLI re-run): A transitive scope narrowing under `provided`. B exclusion inherited two levels down. C optional direct vs optional transitive on one coordinate. D `dependencyManagement` overridden by a direct declaration. E nearest-wins tie broken by declaration order where the losing branch carries the higher version. F cycle that must terminate without duplicating a node. **G combines B+A**: an exclusion inherited down a branch that is itself scope-narrowed, so the excluded coordinate re-enters via a second path at a different depth and mediation must choose. Ground truth computed offline by Fabrice with a jar-complete repo and real Maven, then frozen under `tests/` — the oracle is Maven's own answer, so it cannot be subtly wrong.

**Build cost: 4-5 author-days, and it is fixture-heavy** — 12 sample projects plus 7 held-out sets plus offline ground-truth generation. Reuses the offline repo population at image build, `build.sh` + compiled-CLI + pytest, and the variant-harness shape (swap H2 seeds for pom trees).

**Honest bet: 0.40-0.55 with the provenance requirement, 0.80+ without it.** Conditional bet. This is the best *pure Maven dependency-management* task available to him, and it is entirely contingent on closing the jar-fabrication route.

---

# 5. `repair-local-maven-repo-metadata-drift`

**Category** build-and-dependency-management · **Subcategories** `[]` · **Languages** java, bash
**Stack** Java 17, `javac`, offline local Maven repo, no service, no DB.

**Premise**

> Our offline local Maven repo at `/root/.m2/repository` has drifted and builds now fail with errors that do not say what is actually wrong: some `maven-metadata-local.xml` advertise versions with nothing on disk, some poms declare coordinates that disagree with the directory they sit in, a few sidecar checksums no longer match their artifact, and some coordinates are relocation-only poms now. Finish the auditor at `/app/repo-audit` and build it with `/app/repo-audit/build.sh` so it writes `/app/build/repo-audit.json` saying which coordinates actually resolve, which only resolve after following a relocation and to what final coordinate, and which do not resolve and why. Take the repository root as a positional argument so it can be pointed at another repo.

**Classifier safety.** Repository and dependency management vocabulary throughout. Checksum verification pulls slightly toward security — which is his strongest confirmed-allowed category, so both plausible landings are fine. Keep the framing on *resolvability* rather than tampering so the likelier landing is build-and-dependency-management.

**Where difficulty lives.** Resolvability is a fixpoint over interacting rules the shipped repo only partly exercises. Relocations chain, and a chain may terminate at a coordinate that is itself missing its jar, so a one-hop follow reports resolvable when the truth is unresolvable. **A relocation pom may omit `groupId` or `artifactId`, in which case the omitted part is inherited from the source coordinate — models almost always assume the target is fully specified.** That one is a genuine, specific, verifiable blind spot and it is the best thing in this concept. A SNAPSHOT directory resolves through `maven-metadata-local.xml` to the baseline `-SNAPSHOT` file, and a metadata entry naming a timestamp with no matching file is unresolvable even though the baseline exists. An absent `.sha1` is not a failure; a present-and-wrong one is. Shipped repo has relocations but no chains, snapshots but no timestamp drift.

**Variants** (seven verifier-built repository roots generated by `tests/`): A metadata advertising a version with no artifact. B pom GAV disagreeing with its path. C present-but-wrong `.sha1` vs absent. D two-hop relocation chain. E relocation pom omitting `groupId`, inherited from source. F SNAPSHOT metadata naming a missing timestamped file. **G combines D+F**: a relocation chain whose final target is a SNAPSHOT whose metadata points at a missing timestamped artifact — verdict unresolvable, with the failure attributed to the **final** coordinate, not the source.

**Build cost: 3-4 author-days.** Reuses the offline repo construction from the AWK task, the fixture-generator + held-out grading pattern, and the positional-argument CLI + variant-rerun harness.

**Honest bet: 0.50-0.65 — marginal, right at the gate.** Partial delegation leak: `mvn dependency:get -o` per coordinate approximates the resolvable/unresolvable split, though not the failure attribution or relocation target. This is the fallback, not the lead. If he builds it, the graded output must lean hard on *attribution* and *final coordinate*, which is where Maven gives nothing usable.

---

# Ranking — build order

**1. `repair-java-blob-attestation-against-h2-chunk-map`.** Build this first. It is the closest possible neighbour to the only configuration he has *measured* at 0.40 worst-model: security category, H2 variant-store harness, expected recomputed from whatever store the CLI is pointed at, one variant combining two mechanics. Seven security clears including a PAYOUT_SUBMITTED. No delegation hole exists because no tool computes the answer. Highest probability of a banked pass per day spent.

**2. `repair-java-classpath-shadow-auditor`.** Cheapest of the strong ideas at 2-3 days, safe under both plausible classifier predictions, and it is his stated Maven/build interest. **If he wants to start on the build side rather than security, start here, not on #4 or #5** — and add the release-provenance field on day one.

**3. `reconcile-java-gateway-and-service-acls`.** Best difficulty mechanism of the five (probe the binary, not read the page), safest classifier, but 5-6 days and requires authoring a read-only enforcer that *is* the spec. Build it once #1 has cleared and the pattern is confirmed.

**4. `reconcile-maven-mediation-with-metadata-only-repo`.** Best pure-Maven concept, conditional on plugging jar-fabrication.

**5. `repair-local-maven-repo-metadata-drift`.** Fallback. Real blind spot in the relocation-inheritance rule, but it sits at the gate boundary.

# The weak one — skip it

**`repair-java-delegated-token-scope-broker` is the one to drop, despite scoring 29.** Its own difficulty argument concedes that frontier models "reliably implement chain intersection and reliably implement revocation" — the entire task then rests on one composition corner, the order of revocation against key-generation grace. One corner means one discriminating variant, and models coin-flip it. That is the shape of `enforce-java-release-signature-trust`, which measured both models 5/5 across 22 tests and 10 runs. Its low build cost is a trap: cheap to build, then bounces as TRIVIAL, and the days are gone. **Predicted worst-model 0.60-0.80.** `repair-java-authz-filter-precedence` (score 23, discrimination 4) is weak for the same reason. The two flagged fatals are correctly flagged — `harden-java-attestation-index-ingest` runs content-addressed deduplication, which is the exact mechanic that classified at 0.95 twice, and `rebuild-java-audit-chain-verifier`'s canonical encoding is genuinely unobservable if every shipped record is canonical. Don't build either.

# Straight answer on Maven / Spring Boot

**Yes, it can carry a MEDIUM — but not in the shape he is most likely to reach for, and there is a real cost to choosing it.** Two qualifications, both concrete.

**The shape that does not work is "compute what Maven computes."** Reactor ordering and mediated classpath resolution both define ground truth as Maven's own answer, and Maven must be in the image because the whole stack builds with it. The agent's CLI can shell out on whatever root it is handed. That is what killed `reconcile-maven-classpath-mediation-offline` and `repair-maven-reactor-order-resolver`, and metadata-only mirroring does not fully fix it either — empty jars beside the poms re-open it. You cannot strip Maven from the image without breaking the build. **The shape that works is "compute something Maven does not compute":** classpath shadowing (JVM classloader semantics, manifest expansion, MR-jar precedence — no Maven goal emits any of it), repository drift *attribution*, mediation *provenance*. Maven-adjacent, not Maven-reimplemented. Every Maven idea he considers should be tested against one question first: *what command already prints this answer?* If one exists, the concept is dead.

**And the category itself is thinner evidence than security.** He has one confirmed positive on build-and-dependency-management against seven on security. One positive is a data point, not a base rate. So the honest trade is: security is the higher-probability pass, Maven is the interest — and `repair-java-classpath-shadow-auditor` is the one idea that gets him a Maven-flavoured task while landing safely whichever way the classifier leans. That is why it is #2 and not #4.