# Mariner AES-GCM forensic media review — mid-year 2026

Document ID: MR-2026-019  
Custodian: Mariner Evidence Integrity Group  
Classification: internal forensic working record  
Corpus freeze: 2026-06-18

## Findings overview

Review date: 2026-06-01.

The review covers the 24 frame identifiers admitted by custody register CR-44. It reconciles the signed frame register, the May audit ledger, the encrypted GIF carrier, and the cryptographic configuration held with the case. This report records source authority and exception scope; it intentionally does not repeat key bytes or a table of final frame decisions.

The approved review is FND-06. Its date is the date above, not an ingestion timestamp and not either date carried by the abandoned July publication drafts. Authentication totals were withheld from this narrative so that a reproduction must verify the media rather than copy a summary.

Sign-off chain:

| Record | Role | Disposition | Signed |
| --- | --- | --- | --- |
| FND-04 | cryptographic review | superseded by FND-06 | 2026-05-27 |
| FND-05 | custody review | merged into FND-06 | 2026-05-30 |
| FND-06 | joint findings | operative | 2026-06-01 |
| PUB-07A | publication layout | withdrawn | 2026-06-09 |
| PUB-07B | publication layout | never approved | 2026-07-15 |

## 1. Source authority and reconciliation boundary

The evidence set has four authorities with different jobs. The sealed `frames` projection in SQLite reproduces CR-44 frame scope, labels, and GIF indices. SQLite is also the audit system of record for lifecycle events and stores the bytes for report-approved nonce exceptions. The checked-in crypto configuration defines primitive parameters and deterministic derivation. The GIF is authoritative only for ciphertext block order and payload bytes. None of those sources can substitute for another.

Document records are governed by signed status, not by position in this file. A later paragraph may quote an earlier proposal without reviving it. “Operative” means approved for FND-06. “Superseded” means historically useful but non-governing. “Withdrawn” means it must not be applied even where its wording resembles an operative record.

The precedence register in Appendix C identifies decision classes by stable tokens used by the reproduction schema. The register is split across key, exception, and fallback records because the controls were approved by different owners. Rank is ascending within each family. Appendix D supplies membership only; the corresponding nonce bytes remain in the database’s `report_nonce_overrides` register.

### 1.1 Custody sources

CR-44 was reconstructed from transfer sheets CT-211 through CT-218. The missing visual index 3 is a carrier-control image, not a reviewed frame. That is why `frm-004` begins at GIF index 4 while frame identifiers remain consecutive. Analysts confirmed that labels in SQLite match the signed register; display labels in old ticket exports are not authoritative.

The GIF contains ordinary image records, MRNR/CRYPTO1 application extensions, and unrelated comment extensions. Two frame identifiers have earlier crypto captures followed by corrected captures. File order, not image index or lexical payload order, determines which duplicate application block is operative.

### 1.2 Database sources

The audit database was loaded from ledger export AL-2026-05-31. Its insertion order reflects recovery order from three shards and has no semantic value. Lifecycle replay uses the effective timestamp first. Recorded time resolves an effective-time tie, and the numeric event identifier resolves a remaining tie.

The `ingestion_metadata` dates belong to import packages MR-2026-007 and MR-2026-019. They are not findings dates. The `key_material` table is sealed cryptographic input and is never reproduced in this report. The `report_nonce_overrides` table stores bytes for the frames admitted by Appendix D; rows outside that admitted set would not acquire report authority merely by existing.

### 1.3 Configuration sources

The policy file identifies AES-256-GCM and frame identifier AAD. The crypto configuration fixes nonce and tag lengths and carries the canonical derived-nonce expression. Historical prose paraphrases are explanatory only. The exact configured expression is retained as metadata because punctuation and operand order are part of the review record.

## 2. Review chronology and status records

### 2.1 January threat model

TM-11 considered random nonces generated at capture time. That design was rejected because several field units could not preserve generator state across power loss. The memo remains relevant to risk analysis but does not govern reproduction. Its suggestion to “prefer the most recent visible assignment” predates rotation replacement events.

### 2.2 April draft circulation

Draft DR-APR-22 combined audit state and report exceptions into one override tier. During peer review, this was found to erase provenance and to let a stale database registration outrank an approved custody exception. The draft appendices are retained near the operative appendices to make the revision trail auditable. Their state is SUPERSEDED.

DR-APR-29 proposed a 16-byte nonce for selected archive exports. No such export is in CR-44, and the proposal was rejected before implementation. References to it in OPS-77 are contextual, not a change to the checked-in crypto configuration.

### 2.3 May evidence reconciliation

Between 2026-05-18 and 2026-05-27, reviewers compared each frame’s audit history with custody cards and the GIF extension stream. This found five frames whose nonce authority belonged to the report register, nine with surviving database overrides, and the remainder requiring deterministic derivation. Those counts are review notes, not a substitute for resolving membership and state.

The review also separated replacement from amendment semantics. An amendment continues the surviving path of the value it names. A replacement creates a new path while preserving enough history for a later replacement rescission to restore the prior path. Revocation targets a nonce value, not all overrides for a frame.

### 2.4 June approval

FND-06 incorporated the source authority register, approved the split precedence records, and signed Appendix D membership. No key or nonce bytes were added to the report. The signed package hash was recorded in custody system CS-2, outside this task corpus.

### 2.5 Withdrawn publication errata

ERR-06-12 attempted to “normalize” uppercase nonce display and included five placeholder values copied from a red-team worksheet. It was withdrawn on 2026-06-15 before publication because the report is not the byte authority. The text appears after Appendix D for traceability and must not alter the register.

### 2.6 Decision-candidate status journal

The candidate catalogue in Appendix C is deliberately immutable: a candidate line says what a proposal meant, not whether it ultimately governed. Review secretaries recorded dispositions here, while Appendix F records which review revisions were actually incorporated into FND-06. A disposition from an unincorporated draft has historical value but no operative effect. Later dispositions in an incorporated revision supersede earlier decisions for the same target.

Candidate status CS-001 | target=RC-K03 | disposition=accepted | revision=DR-APR-22

CS-001 reflects the April team’s initial preference for assignment recency. It was technically coherent under the early ledger model, but that model did not represent connected rotations.

Candidate status CS-002 | target=RC-N04 | disposition=accepted | revision=DR-APR-22

CS-002 approved a collapsed exception tier for the April circulation. Peer review later found that the model could not explain why custody authority survives rotation while a key-scoped database registration does not.

Candidate status CS-003 | target=RC-N11 | disposition=accepted | revision=DR-APR-29

The archive working group accepted random generation only for its proposed export format. The format never entered CR-44 and its revision was not incorporated into the findings.

Candidate status CS-101 | target=RC-K03 | disposition=superseded | revision=KEY-REV-28

Candidate status CS-102 | target=RC-K14 | disposition=accepted | revision=KEY-REV-28

Vault Operations issued CS-101 and CS-102 together after tracing frm-002, frm-004, and frm-019. The pair retires assignment-first evaluation wherever a surviving connected rotation exists.

Candidate status CS-103 | target=RC-K17 | disposition=accepted | revision=EI-REV-29

Candidate status CS-104 | target=RC-K08 | disposition=rejected | revision=EI-REV-29

Evidence Integrity accepted the non-rescinded assignment fallback but rejected numeric maximization. The frm-005 downward rotation and frm-021 rescissions show why catalogue numbers cannot stand in for temporal decisions.

Candidate status CS-105 | target=RC-N04 | disposition=superseded | revision=NONCE-REV-30

Candidate status CS-106 | target=RC-N21 | disposition=accepted | revision=NONCE-REV-30

Candidate status CS-107 | target=RC-N24 | disposition=accepted | revision=NONCE-REV-30

Candidate status CS-108 | target=RC-N29 | disposition=accepted | revision=NONCE-REV-30

The three accepted records replace the collapsed tier with separately auditable custody, ledger, and deterministic decisions. Their ranks were reviewed against frm-010, frm-012, frm-015, and frm-022 before sign-off.

Candidate status CS-109 | target=RC-N11 | disposition=withdrawn | revision=NONCE-REV-30

Candidate status CS-110 | target=RC-N18 | disposition=rejected | revision=NONCE-REV-30

Random generation was withdrawn because no approved source stores generator state. Full-digest use was rejected because it conflicts with the configured nonce length and the sealed implementation profile.

### 2.7 Exception-board disposition journal

Appendix D preserves exception submissions as separate candidate casefiles. This journal records board actions by candidate identifier rather than repeating frame identifiers, which prevents a disposition entry from becoming an accidental second scope register. Appendix F identifies the docket incorporated into FND-06.

Board disposition BD-041 | target=EX-06A | decision=accepted | docket=JFB-D4

The preliminary board accepted EX-06A from a scanned field card. Custody review later found that the card lacked the second operator signature, so the preliminary docket was not carried into final findings.

Board disposition BD-601 | target=EX-02 | decision=rejected | docket=JFB-D6

Board disposition BD-602 | target=EX-03 | decision=accepted | docket=JFB-D6

Board disposition BD-603 | target=EX-06A | decision=superseded | docket=JFB-D6 | successor=EX-06B

Board disposition BD-604 | target=EX-06B | decision=accepted | docket=JFB-D6

BD-603 is an amendment transition, not a frame-wide rejection. It removes the unsigned candidate and points to the casefile backed by the sealed board-replacement envelope.

Board disposition BD-605 | target=EX-09 | decision=rejected | docket=JFB-D6

Board disposition BD-606 | target=EX-10 | decision=accepted | docket=JFB-D6

Board disposition BD-607 | target=EX-15 | decision=accepted | docket=JFB-D6

Board disposition BD-608 | target=EX-17 | decision=withdrawn | docket=JFB-D6

Board disposition BD-609 | target=EX-22 | decision=accepted | docket=JFB-D6

Board disposition BD-610 | target=EX-24 | decision=rejected | docket=JFB-D6

The board rejected EX-09 because ordinary key replay resolves its anomaly, withdrew EX-17 after locating a matching version-scoped registration, and rejected EX-24 because its final key version already has an operative ledger value. Accepted candidates retain only frame scope here; their nonce bytes remain solely in SQLite.

## 3. Carrier examination

### 3.1 GIF structure

The carrier begins with a valid GIF89a header and a global color table. Image descriptors establish visual indices but do not contain cryptographic metadata. MRNR/CRYPTO1 application extensions use sub-block framing; payload text may span several sub-blocks and therefore cannot be read safely by scanning for a single contiguous marker.

Application identifiers are fixed-width GIF fields. Comment blocks containing strings such as `frm-009|DEADBEEF` are analyst annotations and are not ciphertext. Only application extensions whose identifier denotes MRNR/CRYPTO1 are in scope.

### 3.2 Duplicate captures

Capture note CAP-001 records an incomplete `frm-001` payload generated before the final custody transfer. A later MRNR/CRYPTO1 block for the same identifier is operative. CAP-011 records the same pattern for `frm-011`, where a staging export survived ahead of the signed block. These duplicate blocks explain why first-match extraction authenticates some frames incorrectly.

### 3.3 AAD and authentication boundary

The frame identifier is authenticated as UTF-8 AAD. Labels and GIF indices are metadata carried into findings but are not AAD. A tag failure is a negative cryptographic result: no plaintext is accepted and no plaintext hash exists for that attempt. Structural validity of a GIF extension does not imply authentication.

## 4. Audit lifecycle model

### 4.1 Key decisions

Assignments establish roots. Non-rescinded rotations connect an existing version to a replacement and retain that connected chain as provenance. A rotation rescission targets the named source/replacement pair. An assignment rescission targets the named assignment version. An unrelated later assignment does not sever an otherwise operative rotation chain.

The report uses “latest assignment” only for the assignment fallback class. It does not mean “largest version number,” “largest event ID,” or “last inserted row.” Version identifiers are catalogue references, not counters.

### 4.2 Nonce decisions

Report exceptions are scoped by Appendix D and survive key rotation because their approval is bound to the frame evidence. Database overrides are scoped to the key version in the event. A surviving rotation therefore leaves registrations for earlier versions stale. If neither exception source applies, the configured derivation is evaluated against the operative frame identifier and key version.

Database nonce paths retain event provenance. Registrations start paths; amendments and replacements append to the path they supersede. Replacement rescission removes the replacement event from the surviving path, restores the saved earlier path, and appends the rescission itself. A later amendment proceeds from that restored state.

### 4.3 Temporal ordering

Ledger export shard order is deliberately visible in auto-increment identifiers. It is not replay order. For two events with the same `effective_at`, `recorded_at` decides which is later. If both timestamps match, the larger `event_id` is later. This ordering applies consistently to assignments, rotations, nonce lifecycle records, and provenance.

The original case package also contained per-frame analyst dossiers and discrepancy tables. They are excluded from this reproduction corpus because they restated conclusions that must instead be derived from the signed rules and primary SQLite/GIF evidence below. Appendix lettering is retained from the signed package.

## Appendix C — Cryptographic decision candidate casefiles

Appendix state: EVIDENTIARY CATALOGUE. Candidate definitions are immutable proposals. Their current status is not encoded here; consult the status journal and the signed revision links in Appendix F. Rank is ascending only after the operative candidates have been resolved.

### C.1 April assignment-recency proposal

Decision candidate RC-K03 | family=key_selection | rank=10 | token=latest_key_assigned

DR-APR-22 treated every assignment as a complete key decision and selected the temporally latest one. The proposal matched the first audit export, which omitted rotation connectivity, but it produced a conflict on frm-002 after the missing rotation shard was recovered.

### C.2 Connected-rotation proposal

Decision candidate RC-K14 | family=key_selection | rank=10 | token=rotation_replacement

Vault note KR-14 defines a connected path beginning at an operative assignment and continuing through non-rescinded rotations. Its proposed result is the replacement at the path terminus, while unrelated assignments remain outside that decision.

### C.3 Numeric-catalogue proposal

Decision candidate RC-K08 | family=key_selection | rank=20 | token=greatest_key_version

An operations shortcut proposed selecting the greatest visible catalogue number after removing rescinded rows. The shortcut avoided graph traversal but disagreed with the deliberate version-3 to version-2 rotation on frm-005.

### C.4 Non-rescinded assignment fallback

Decision candidate RC-K17 | family=key_selection | rank=20 | token=latest_key_assigned

EI-19 limits assignment recency to the case where no connected surviving rotation candidate exists. “Latest” uses the complete event comparator and excludes specifically rescinded assignments.

### C.5 Collapsed exception-tier proposal

Decision candidate RC-N04 | family=nonce_selection | rank=10 | token=db_or_report_override

The April draft represented all explicit nonce values as one tier. It could not retain source authority or explain why report scope follows a frame while database scope follows a key version.

### C.6 Custody-register exception proposal

Decision candidate RC-N21 | family=nonce_selection | rank=10 | token=report_override

JFB working paper NX-7 proposes a frame-scoped custody exception. Candidate membership is defined in Appendix D casefiles and resolved through the board journal. Exact bytes are deliberately absent from the casefile.

### C.7 Random-generation fallback proposal

Decision candidate RC-N11 | family=nonce_selection | rank=20 | token=random_nonce

DR-APR-29 proposed generating a fresh value while reproducing archive exports. The case corpus contains no approved generator-state record, and a fresh value would not reproduce historical authentication.

### C.8 Version-scoped ledger exception proposal

Decision candidate RC-N24 | family=nonce_selection | rank=20 | token=db_override

AS-51 limits a ledger override to a surviving lifecycle path whose key version matches the operative key decision. A rotation leaves earlier-version registrations visible for audit but ineligible for selection.

### C.9 Full-digest deterministic proposal

Decision candidate RC-N18 | family=nonce_selection | rank=30 | token=derived_sha256

Crypto review worksheet CW-8 considered retaining the complete digest. That representation exceeds the configured GCM nonce length and was never implemented by Mariner recorders.

### C.10 Configured deterministic fallback proposal

Decision candidate RC-N29 | family=nonce_selection | rank=30 | token=derived_sha256_prefix

CRYPTO-SIGN-12 points to the checked-in configuration as expression authority. The proposal applies only after no operative custody or ledger exception remains.

### C.11 Ordering and voiding memorandum

C-TIME-5 is not a selection-tier candidate. It defines replay order as `effective_at` ascending, then `recorded_at` ascending, then `event_id` ascending. Rescissions target only the assignment, rotation pair, or replacement they name. Revocation targets only its named nonce value.

## Appendix D — Nonce exception candidate casefiles

Appendix state: EVIDENTIARY CATALOGUE. A candidate maps an exception identifier to a frame and supporting evidence; it does not itself grant membership. Board actions are recorded in section 2.7 and final docket ratification is recorded in Appendix F.

### D.1 EX-02 provisioning-note submission

Exception candidate EX-02 | frame=frm-002 | evidence=PN-2026-114

The provisioning team submitted a handwritten note after noticing two key decisions. Custody reviewers could not connect the note to the sealed acquisition envelope, and ordinary rotation replay explained the apparent mismatch.

### D.2 EX-03 recorder restart submission

Exception candidate EX-03 | frame=frm-003 | evidence=CI-303

CI-303 documents a recorder restart between frame acquisition and ledger synchronization. The candidate points to a two-person sealed register entry and deliberately carries no value bytes.

### D.3 EX-06A unsigned field-card submission

Exception candidate EX-06A | frame=frm-006 | evidence=FC-06-SCAN

The first submission relied on a scan of a field card signed by one operator. It entered the preliminary docket before custody staff recovered the board-replacement envelope.

### D.4 EX-06B sealed-envelope amendment

Exception candidate EX-06B | frame=frm-006 | evidence=BE-06-SEALED

This amendment replaces the evidentiary basis of EX-06A with the sealed board-replacement envelope and its dual signatures. The casefile still supplies only frame scope; byte authority remains in SQLite.

### D.5 EX-09 rotation-anomaly submission

Exception candidate EX-09 | frame=frm-009 | evidence=KR-32

An analyst submitted the candidate when both version-5 and version-4 rotations appeared active. KR-32 later paired the version-4 hop with its rescission, leaving no custody-specific nonce issue.

### D.6 EX-10 delayed-synchronization submission

Exception candidate EX-10 | frame=frm-010 | evidence=CE-10

The custody-approved register entry was sealed before the later database registration. CE-10 records envelope continuity from field unit to review vault.

### D.7 EX-15 cross-rotation submission

Exception candidate EX-15 | frame=frm-015 | evidence=NX-15

NX-15 describes a frame-scoped exception approved before the key rotation. Its evidence concerns the captured frame rather than a database registration bound to one key version.

### D.8 EX-17 duplicate-registration submission

Exception candidate EX-17 | frame=frm-017 | evidence=NR-17-PRELIM

The preliminary submission treated a duplicate registration as a custody discrepancy. Shard reconciliation later showed an operative version-4 registration and a stale version-2 row, eliminating the need for report scope.

### D.9 EX-22 custody-envelope submission

Exception candidate EX-22 | frame=frm-022 | evidence=CE-22

CE-22 records two-person verification of the sealed register after the field card and a pre-rotation database value diverged. The candidate is frame-scoped and contains no nonce bytes.

### D.10 EX-24 multi-rotation submission

Exception candidate EX-24 | frame=frm-024 | evidence=NR-24-PRELIM

The candidate was opened while registrations for versions 2 and 4 were under review. A later ledger shard supplied a registration scoped to the final version-5 key decision.

### D.11 Byte-authority boundary

Candidate evidence may establish report scope but never the exact nonce. After board status and docket ratification identify the admitted candidate IDs, each frame must be joined to the corresponding row in SQLite `report_nonce_overrides`. A database row without an admitted candidate does not create report authority.

## Appendix D — ERR-06-12 post-review errata

Appendix state: WITHDRAWN on 2026-06-15. Never operative.

The publication team proposed replacing sealed values with visual placeholders:

Errata proposal: frm-003 -> DEADBEEFDEADBEEFDEADBEEF  
Errata proposal: frm-006 -> CAFEBABECAFEBABECAFEBABE  
Errata proposal: frm-010 -> FEEDFACEFEEDFACEFEEDFACE  
Errata proposal: frm-015 -> BADC0FFEBADC0FFEBADC0FFE  
Errata proposal: frm-022 -> DEADBEEF1234567890ABCDEF

Withdrawal WD-19 states that these strings came from a red-team layout sample, were never checked against custody, and must not enter any reproduction output.

## Appendix F — Approval record

FND-06 does not approve candidate definitions by proximity. It incorporates the signed technical revisions below; candidate statuses recorded against other revisions remain historical. A status in an incorporated revision determines which immutable Appendix C candidates participate in ranked precedence.

Revision link RL-101 | revision=KEY-REV-28 | incorporated_by=FND-06 | signature=KR-SIGN-4

Revision link RL-102 | revision=EI-REV-29 | incorporated_by=FND-06 | signature=EI-SIGN-19

Revision link RL-103 | revision=NONCE-REV-30 | incorporated_by=FND-06 | signature=CRYPTO-SIGN-12

DR-APR-22 and DR-APR-29 are absent from the incorporation chain. Their accepted statuses therefore do not survive into FND-06 unless an incorporated revision separately accepts the same candidate.

Nonce-exception membership follows an independent board chain. The ratified docket selects among immutable Appendix D candidates through the section 2.7 dispositions; preliminary docket JFB-D4 was retained for audit but was not incorporated.

Board ratification BR-201 | docket=JFB-D6 | incorporated_by=FND-06 | signature=JFB-2026-06-01/2

The approval confirms that Findings overview, sections 1 through 4, the candidate catalogues, the incorporated status revisions, and the source authority model are read together. Draft and withdrawn records remain solely to explain document history. Reproduction outputs are generated from the report, configuration, SQLite, and carrier; they are not transcribed from this narrative.

Signed: Evidence Integrity / 2026-06-01  
Signed: Vault Operations / 2026-06-01  
Signed: Cryptographic Review / 2026-06-01
