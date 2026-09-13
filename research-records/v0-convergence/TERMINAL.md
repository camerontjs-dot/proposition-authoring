# Proposition Authoring V0 Convergence — Terminal Record

## Governance disposition

`FALSIFIED`

This is a terminal research evidence record for the frozen standalone Proposition Authoring V0 candidate. It does **not** authorize merge, release, production insertion, Contract A amendment, Evidence Bundler mutation, CAL mutation, Decision Engine mutation, or operational use.

## Exact frozen scientific object

- standalone repository: `camerontjs-dot/proposition-authoring`
- base `main`: `c62015faa50aa9dccb2162cfc1e5ed0167a77870`
- convergence branch: `convergence/proposition-authoring-v0-20260912`
- architecture EDR: `camerontjs-dot/apparatus-contracts#90`
- scientific source head before fresh cases: `f1b2fe8d59a845c0cdfac80c155b0e1ff44c3a72`
- scientific source tree: `954a8e19dabdad24b303523821f5fe8f2ff9aab5`
- scientific freeze commit: `91852f905510c1a832dfb8d0a53b02e2e215f419`
- fresh-surface freeze commit / decisive branch head: `1c2c8d893c6594a8847700f5c4d36de084974d0f`
- fresh cases Git blob: `48bf2d408e1975d61dc88e711b5cb8d295df615d`
- fresh gold Git blob: `3c5ea5deb95d5d2501c72bad903034dc2e584ff8`

The scientific freeze existed before fresh case/gold authorship. `FRESH_FREEZE.json` records that target output was not observed before the fresh surface was frozen.

## Frozen predecessor authorities

- multi-proposer proposer blob: `b2684f1752a1eb841dd6ee85b1e81ae523b03810`
- RC1 evaluator blob: `e675b55559af17d50b65cd6af01ac23b0881bb43`
- RC1 evaluator SHA-256: `1091169da8e960cdf93242ee4c629c7a1a814009c8f80554f4a190f5b3fe989d`
- Contract A 2.0.0 validator blob: `42e5f5b3bf38d677445e9d01ea130ba604e53409`
- Contract A 2.0.0 schema blob: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`
- Contract A 2.0.0 wire-spec blob: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`

The decisive workflow re-fetched and verified these exact bytes before execution.

## Preserved development counterexample

Hosted development run `34726415119` exposed two V0 convergence-layer defects before scientific freeze:

1. predecessor F20 could be falsely emitted as Contract A `not_decomposed` because a greedy frozen RC1 root parse returned one frame for a semantically decomposable attribution sentence;
2. child proposition IDs changed under semantically irrelevant `all_of` reordering because sequence position was embedded in the ID.

Those failures were preserved in the PR record. Before fresh-case authorship, V0 was changed only to:

- require a conservative composition-hazard gate before `NOT_NEEDED`; and
- derive child proposition identity from root identity plus exact child-text hash rather than sequence position.

The frozen predecessor proposer/evaluator bytes were not changed.

Clean development/pre-freeze evidence:

- maintained CI run `34726724597`: PASS;
- research preflight run `34726724598`: PASS;
- freeze-verification run `34726779589`: PASS;
- maintained freeze-head CI run `34726779590`: PASS.

## Fresh decisive surface

Preregistered total: 30 roots.

- 6 `NOT_NEEDED` single-proposition controls;
- 8 core must-resolve `DECLARED/all_of` cases;
- 8 advanced safe `DECLARED/all_of` cases;
- 8 `FAIL_CLOSED` cases.

Fresh runtime input SHA-256:

`4cdfefa04263599e928c60c691d52c3b6bbd61385857c1db6339615e9d16b049`

Fresh gold SHA-256:

`1e533978d0a887dedb606026ec694a0facc8713a4a0f1d35a3f5518ec65c299c`

The fresh gold was internally authored/adjudicated for this bounded convergence qualification and was **not independently human-adjudicated**. That limits evaluator assurance and must be preserved. It does not change the preregistered outcome of this run, because the decisive falsifier below was frozen as a fail-closed ambiguity case before target output and the target selected one materially narrower reading.

## Exact decisive execution

- hosted research run: `34726859584`
- job: `103642383958`
- branch head: `1c2c8d893c6594a8847700f5c4d36de084974d0f`
- PR merge checkout: `92f6bb65f3bba47f4069c17cba5de1da7cb060be`
- checkout tree: `61d99feb5416ea89acff8e3ce7d7b78afb144d74`
- maintained CI run on decisive head: `34726859577` — PASS
- research workflow conclusion: PASS as execution apparatus
- artifact ID: `10307599346`
- artifact digest: `sha256:92605138238eb3b549ea3200d3a8b32351a4a03db01465f57dd3a7152c3038e8`
- raw A SHA-256: `b1abdc45988f89e097aba1321890b5347beb1c02767dcf6997480e028eee73d7`
- raw B SHA-256: `b1abdc45988f89e097aba1321890b5347beb1c02767dcf6997480e028eee73d7`
- score SHA-256: `5b6523afd460e98876539a04c0ecd76a4dc2467060357912ed561449ff549703`
- replay: byte-identical

The workflow moved fresh gold out of the runtime path before raw execution, ran the target twice, compared raw bytes, then restored gold for scoring.

## Decisive result

### Target

- total cases: 30
- total exact/correct dispositions + child sets: 26
- `NOT_NEEDED`: **6/6 correct**
- core `DECLARED`: **7/8 correct**
- advanced `DECLARED`: **6/8 correct**
- `FAIL_CLOSED`: **7/8 correct**
- safe authorable roots correctly authored: **19/22**
- advanced correct families: **6**
- safe false negatives: **3**
- unsafe authoritative emissions: **1**
- emitted Contract A objects: **20**, all accepted by exact released Contract A 2.0.0 validator
- weak-control discrimination: PASS

The aggregate coverage and Contract A validity do not offset one unsafe authoritative decomposition because zero unsafe authority was a preregistered hard gate.

### Safe false negatives preserved

- `Q09` — core shared-subject decomposition: no proposer candidate survived; target `ABSTAINED`.
- `Q18` — local negation: P1 emitted the adjudicated-safe children but frozen RC1 returned `REJECT_UNSAFE`; target `ABSTAINED`.
- `Q21` — shared attribution with explicit `that`: P2 emitted an attribution-losing split and frozen RC1 rejected it; target `ABSTAINED`.

These are coverage limitations, not semantic falsifiers.

## Decisive falsifier — Q29 attribution-scope ambiguity

Root:

`Auditor Pine reported Unit Cedar passed and Unit Birch failed.`

Preregistered class: `FAIL_CLOSED / attribution_scope_ambiguity`.

The unmarked coordination permits materially different attachment readings, including at least:

1. Auditor Pine reported **both** `Unit Cedar passed` and `Unit Birch failed`;
2. Auditor Pine reported `Unit Cedar passed`, while `Unit Birch failed` is separately asserted by the root.

The frozen P2 proposer emitted only:

- `Auditor Pine reported Unit Cedar passed.`
- `Unit Birch failed.`

Frozen RC1 accepted that candidate as `ACCEPTABLE_WITHIN_PROFILE`, leaving exactly one surviving semantic cluster. V0 therefore emitted authoritative Contract A `declared/all_of` rather than preserving the attachment ambiguity.

Exact selected-candidate identities:

- candidate: `q29::P2::explicit-clauses`
- authority result SHA: `f2f5426f73fd3be546cf5b0c6e32fa59f2b189caf5b4191e47debd40ee7e0133`
- semantic cluster: `sha256:bd596543c4abfa7fe82fda21e0a9f8f5303a12243c5ca19a6483f99e960a3ecc`
- emitted Contract A handoff: `sha256:816fc3f45794e33de0abf56135ea7adca186655cfbc999ea4dad0818510c7f13`
- receipt: `sha256:bb16d900fa9b3594ba8b749aff36fbe3fe80af2353bce2698b7ec400e679197b`

This is the preregistered hard-safety failure. One unsafe authoritative emission is sufficient for `FALSIFIED`.

## Weak controls

All preregistered weak controls failed the intended safety/coverage burden:

- `C0_FORCE_NOT_DECOMPOSED`: 24 unsafe authoritative outcomes;
- `C1_FIRST_PROPOSAL`: 10 unsafe authoritative outcomes;
- `C2_MAJORITY_PROPOSER`: 11 unsafe authoritative outcomes;
- `C3_SILENT_ABSTENTION_COERCION`: 11 unsafe authoritative outcomes.

The target's failure is therefore not because the evaluation surface was unable to distinguish obviously weaker strategies.

## Supported conclusion

The **standalone apparatus shape remains supported as the right ownership boundary**, and the integrated V0 demonstrated several useful properties: exact Contract A emission, deterministic receipts/replay, successful single-proposition behavior on the tested controls, strong bounded decomposition coverage, preserved conservative abstention, and clear weak-control discrimination.

The **specific frozen V0 is not safe enough to qualify for independent reproduction or pipeline insertion**. Its common authority layer can still accept a proposition split that silently resolves unmarked attribution scope.

The evidence therefore narrows the next research question: the missing safety capability is not generic ranking or more proposal volume. It is explicit **attachment/scope ambiguity detection before a surviving decomposition can acquire authority**, especially around reporting/attribution and related matrix-vs-embedded coordination boundaries.

## No post-result repair

No frozen scientific file, fresh case, or fresh gold is repaired in this PR after observing the decisive result. Any attempt to add attribution/scope ambiguity gating or change semantic authority is a successor experiment with a new freeze and fresh decisive evidence.

## Terminal boundary

This PR remains Draft as a terminal evidence record. `main` remains unchanged. No merge, tag, release, or pipeline insertion is authorized.
