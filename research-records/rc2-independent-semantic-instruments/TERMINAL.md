# Proposition Authoring RC2 Independent Semantic Instruments — Terminal Record

## Governance disposition

`SUPPORTED_FOR_RC3_COVERAGE_TESTING`

RC2 is terminal. This disposition supports only carrying the fail-closed composed candidate-authority rule into the separate RC3 coverage experiment. It does not authorize merge of semantic runtime to `main`, release, Contract A amendment, Evidence Bundler/CAL/Decision mutation, or pipeline insertion.

## Exact lineage

- repository: `camerontjs-dot/proposition-authoring`
- programme: issue #4
- experiment: issue #6
- Draft Research PR: #16
- base `main`: `a4f018285ffc6d2c5755b2cc02a751799f1511a1`
- RC1 target freeze: `bd4fca4494b1ffce4a13118fad5a1268990e42db`
- RC1 terminal evidence: `b3d2b429d21b2d52125492b1f14cadab83e1e84f`
- RC2 scientific source head before fresh authoring: `e4a2333f8996358e2bb6f205a15ece856c749707`
- RC2 scientific source tree: `f91aed747ff71c26486efcbdf5718eead2ddddd0`
- target freeze commit: `c7565f5e40ef73bef3807fbef724e4a32ac6460f`
- fresh seal / decisive head: `9af7ebc590d8ba317607efd8a9bf8eef5d416bc3`
- fresh surface tree: `44fa5fe9a193f0b09402dc1da40bf08c2aac5e94`
- fresh cases Git blob: `8b8481c8f8b1538813a4ee63a251e2d5460be81b`
- fresh gold Git blob: `d58a38b7913076795a6654de79fc42aa2214cce9`

The exact target/harness freeze was verified in hosted CI before the fresh candidate surface existed.

## Target architecture

RC2 kept the frozen RC1 root-ambiguity veto and frozen RC1 candidate evaluator. It added a separately implemented `surface-scope-conservation-v1` instrument that reads only root/candidate surface strings and has no import or call dependency on the frozen evaluator/parser/backend.

Candidate authority is fail-closed AND-composition:

1. root ambiguity finding blocks;
2. frozen evaluator must return `ACCEPTABLE_WITHIN_PROFILE`;
3. independent conservation must return `PASS`;
4. any rejection, failure, or indeterminate result blocks;
5. vote/count/score never grants authority.

The conservation instrument can veto only. It cannot generate children, repair a candidate, override the frozen evaluator, or use downstream outcomes.

## Pre-freeze development evidence

Development used only revealed predecessor evidence Q18, Q29, and RC1 R22.

The exact frozen P2 proposer regenerated the R22 bad candidate:

- `Committee Pine reported both Unit Amber passed.`
- `Unit Cobalt failed.`

The frozen evaluator returned `ACCEPTABLE_WITHIN_PROFILE`; the independent conservation instrument returned `FAIL`; composed authority returned `BLOCK / CONSERVATION_FAIL`.

Development research run `34790355139`: PASS.
Maintained CI run `34790355150`: PASS on Python 3.11 and 3.12.

## Fresh decisive surface

36 candidate-level cases, authored only after target freeze:

- 20 semantically conservative `SAFE` candidates expected `ALLOW`;
- 16 ambiguous or non-conservative candidates expected `BLOCK`.

Candidate-level testing was deliberate. RC2 tests authority measurement independently of proposer coverage; end-to-end proposal coverage is reserved for RC3.

Fresh surface identities:

- cases Git blob `8b8481c8f8b1538813a4ee63a251e2d5460be81b`
- gold Git blob `d58a38b7913076795a6654de79fc42aa2214cce9`
- cases SHA-256 `bcfeb92eef7512b1779ca433459ce7a43f5fe43644e1605529728fc05b83a67a`
- gold SHA-256 `f6d71532be180e33dc9760945ef9aed7672fa18b09cdf0c0419ee920e9602d0c`

Gold was internally adjudicated, not independent human consensus.

## Decisive execution

- research run `34790568335`: execution PASS
- maintained CI `34790568330`: PASS on Python 3.11 and 3.12
- decisive head `9af7ebc590d8ba317607efd8a9bf8eef5d416bc3`
- artifact ID `10327647140`
- artifact digest `sha256:fae9841b1b082819afda8733edb8a4f01d4806c4417a464034c8cebf568e801f`
- raw A SHA-256 `6f7e2e75068aee650cd9da9e7fe01858cc3bfa4ed7efe9feaef1922f578ff469`
- raw B SHA-256 `6f7e2e75068aee650cd9da9e7fe01858cc3bfa4ed7efe9feaef1922f578ff469`
- exact replay: byte-identical
- score SHA-256 `860f8675ee4622939bbfac0de4d620a84af6a8a943ac2076c99707db7837bb52`

Gold was removed from the runtime path before both raw executions and restored only for scoring.

## Decisive result

Target:

- 36 cases total
- **0 unsafe `ALLOW` decisions**
- **18/20 safe candidates `ALLOW`** (90%)
- safe accepts across **9 semantic families**
- 34/36 exact decisions
- 18 Contract A projections emitted and **18/18 validated** under the exact released Contract A validator
- hard safety gate: PASS
- coverage gate: PASS
- weak-control discrimination: PASS
- disposition: `SUPPORTED_FOR_RC3_COVERAGE_TESTING`

The two safe false negatives were:

- A17 local negation: independent conservation `PASS`, frozen evaluator `REJECT_UNSAFE`;
- A20 correlative `both`: independent conservation `PASS`, frozen evaluator `REJECT_UNSAFE`.

These remain authority-layer coverage limits. They were not repaired after fresh output.

## Complementarity evidence

The controls demonstrate non-duplicative failure coverage.

### C0 evaluator-only

- 18/20 safe allows
- **2 unsafe allows: B01, B02**

Both were fresh shared-attribution-loss candidates. The frozen evaluator alone would grant authority; the independent conservation instrument vetoed both.

### C1 conservation-only

- 20/20 safe allows
- **4 unsafe allows: B09, B10, B11, B12**

These were object swap, agent swap, comparison-direction swap, and modal swap candidates. Surface conservation alone missed them; the frozen evaluator rejected them.

### C2 permissive any-pass

- 20/20 safe allows
- **6 unsafe allows: B01, B02, B09, B10, B11, B12**

This directly falsifies permissive voting/OR composition on the fresh surface.

### C3 lexical coverage

- 20/20 safe allows
- **12 unsafe allows**

Lexical conservation remains inadequate as semantic authority.

The AND-composed target is therefore doing more than blanket conservatism: each semantic instrument catches a fresh unsafe family the other misses.

## What this supports

RC2 supports the following bounded claim:

> Within the tested candidate-level profile, fail-closed composition of the frozen binding evaluator, the RC1 root-ambiguity veto, and an independently implemented surface-scope conservation instrument reduced complementary unsafe-authority failures to zero while retaining 90% safe-candidate coverage.

This is sufficient to carry the composed authority boundary into RC3, where proposer coverage can be tested separately.

## What this does not support

- not production readiness;
- not universal semantic conservation;
- not proof that the surface instrument is independently correct outside tested families;
- not end-to-end proposition-authoring coverage;
- not independent-human evaluator assurance;
- not permission to relax fail-closed AND composition;
- not Contract A, EB, CAL, or Decision Engine promotion.

Both semantic instruments were authored within the same research programme and operate on the same textual inputs even though they use separate implementation/representation paths. Their fresh complementary errors provide evidence of useful independence, but stronger assurance still requires later context-free reproduction and naturalistic qualification.

## Preserved deviations

Before target freeze there were three non-scientific/development deviations:

1. hosted lint rejected `re.I`; changed only to `re.IGNORECASE`;
2. hosted lint rejected runner import grouping; formatting only;
3. the first hand-built R22 fixture returned `INVALID_INPUT` because it omitted the exact frozen proposer schema. The test was changed to regenerate R22 through the exact frozen P2 proposer; conservation logic was unchanged.

No fresh target output existed during any of these repairs. No scientific code, fresh cases, or fresh gold changed after the target/fresh freezes.

A duplicate bookkeeping issue #15 was also created by repeated connector invocation and immediately closed as duplicate of #14; it carries no research authority.

## Terminal boundary

RC2 is `SUPPORTED_FOR_RC3_COVERAGE_TESTING`. PR #16 remains a Draft Research evidence record and must not be interpreted as production authorization. RC3 issue #7 is the next separate experiment boundary.