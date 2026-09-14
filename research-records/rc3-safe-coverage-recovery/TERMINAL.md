# RC3 Safe Coverage Recovery — Terminal Record

## Disposition

Canonical governance disposition: **SUPPORTED FOR PROMOTION**.

Experiment-specific classification: **SUPPORTED_FOR_RC4_INDEPENDENT_REPRODUCTION**.

“Promotion” here means only freezing this integrated bounded research candidate for the next qualification stage, RC4 context-free independent reproduction. It is not production authorization, merge authorization, release authorization, or pipeline insertion.

## Research question

With the RC2 fail-closed semantic authority boundary frozen, can bounded proposal generation recover useful end-to-end Proposition Authoring coverage without introducing unsafe authoritative outcomes?

## Exact lineage

- base `main`: `a4f018285ffc6d2c5755b2cc02a751799f1511a1`
- RC2 target freeze: `c7565f5e40ef73bef3807fbef724e4a32ac6460f`
- RC2 terminal evidence: `3743ba831194108f9413aa57ba33d48970a87b76`
- RC3 scientific source head: `825ec2a4f590ca9c61431d5d88953825c8f1ea5a`
- RC3 target freeze: `50a943c401f8a09d5bb940472bdad43b54dca5d0`
- fresh seal / decisive head: `71adeacdaea4c10e061161f64bffb06abbf79e36`
- fresh cases Git blob: `69d055cdac7b7b8ba332932415e22af8ebfff374`
- fresh gold Git blob: `4f0abc07abde271bd3b87443167d46e83a9e3ec8`
- fresh-freeze Git blob: `51afe6c8e026dbabb6a03b8879cd6e12830fc74b`

Target freeze explicitly recorded `fresh_cases_present_at_freeze=false` and `fresh_gold_present_at_freeze=false`. Cases, gold, and the fresh-freeze receipt were then committed atomically after freeze with `target_output_observed_before_fresh_freeze=false`.

## Target

RC3 preserved the exact RC2 authority composition:

1. RC1 root-scope ambiguity veto;
2. frozen RC1 binding evaluator;
3. RC2 `surface-scope-conservation-v1` instrument;
4. fail-closed AND composition;
5. no vote, count, reranker score, proposer identity, or downstream outcome can override a veto.

RC3 changed only proposal generation with two bounded lanes:

- **P4**: affirmative shared-subject fallback for the predicate-looking-subject lexical collision family exposed by V0 Q09.
- **P5**: explicit **`reported that A and B`** shared-attribution expander. The broader pre-freeze `stated that` attempt was rejected because the frozen authority profile does not support it; P5 was contracted before freeze.

## Fresh decisive surface

36 unseen end-to-end roots:

- 6 P4 target roots;
- 8 P5 target roots;
- 8 baseline-safe decomposition controls;
- 4 single-proposition controls;
- 10 fail-closed adversaries.

## Decisive execution

- research run: `34798048858` — SUCCESS
- maintained CI: `34798048877` — SUCCESS on Python 3.11 and 3.12
- artifact: `10329619593`
- artifact digest: `sha256:1e42505a05045c4e88cc83ea5af4ef7723ea2b2fe6fd14617e463bdba3b12797`
- fresh cases content SHA-256: `5223e4ed7eb45ff178f3d5c5e4f1840b3d0c9546c109e51725fdd31280c1749a`
- fresh gold content SHA-256: `946c838d263ee9368636937cdb25f53dc5681aacb3f6dbe1a21fedbf46a81f53`
- raw A/B SHA-256: `bfaf87efea77fd7e46322dd9c207ec239dbf2bc2ed74e4120742059c897dc123`
- score SHA-256: `d54f086418f120466b866d565a7eee237e63eaa003c28fba6931466a70783481`
- replay: byte-identical

## Fresh result

### Original baseline P1/P2/P3

- 12/26 safe roots correct;
- 10/10 fail-closed roots correct;
- 22/36 total exact;
- zero unsafe authoritative outcomes.

### Pooled P1/P2/P3 + P4 + P5 under frozen RC2 authority

- **26/26 safe roots correct**;
- **10/10 fail-closed roots correctly abstained**;
- **36/36 total exact**;
- **0 unsafe authoritative outcomes**;
- **0 materially wrong safe authoritative decompositions**;
- **14 safe gains over baseline**;
- gains in both preregistered families:
  - `p4_subject_predicate_collision`: R01–R06;
  - `p5_reported_that_shared_attribution`: R07–R14;
- **100% preservation** of baseline-safe finalizations;
- **26/26 authoritative pooled Contract A emissions validated** with the exact released Contract A validator.

All preregistered positive gates passed.

## Weak control

The weak `first_pooled_proposal` control incorrectly declared six fail-closed roots: R27, R28, R29, R30, R34, R35.

Examples included unmarked attribution scope, connective scope, sentential negation, unresolved reference, and trailing-adjunct scope. The pooled target correctly abstained on all six. This demonstrates that coverage gains came from adding proposal hypotheses while the semantic authority boundary still contributed essential discrimination.

## Preserved pre-freeze deviations

1. Hosted run `34797383568` stopped at Ruff lint before semantic execution. The repair was maintenance-only (`ClassVar` and test iteration formatting).
2. Hosted run `34797801333` reached semantic development and showed that `stated that` exceeded frozen evaluator competence. P5 was contracted to `reported that` only. No RC2 authority code changed and no fresh RC3 surface existed.
3. The apparent V0 Q09 contradiction was resolved by the actual decisive receipt: Q09 had an empty candidate ledger. P1 treated subject-initial `Archive` as a predicate token, so subject extraction failed. P4 addresses this bounded parser-coupling failure without changing authority.

## Limitations

- The fresh cohort and gold were internally authored/adjudicated, not independently human-adjudicated.
- P4 evidence is bounded to the tested predicate-looking-subject collision family; it is not a general parser replacement.
- P5 evidence is bounded to explicit `reported that` coordination under the frozen authority profile; no claim is made for `stated`, `confirmed`, `noted`, `claimed`, or arbitrary embeddings.
- RC3 does not establish context-free reproducibility by an independent executor.
- RC3 does not establish independent Evidence Bundler consumption.
- RC3 does not establish naturalistic real-claim performance.

## Nonclaims

This result does not authorize merge of research semantics to `main`, release/tagging, Contract A changes, Evidence Bundler integration, CAL changes, Decision Engine changes, production defaults, or production use.

## Next authorized action

Freeze the integrated bounded RC3 candidate and hand it to **RC4 context-free independent reproduction**. RC4 must consume pinned artifacts and a context-free execution packet without relying on this conversation or hidden experiment knowledge.
