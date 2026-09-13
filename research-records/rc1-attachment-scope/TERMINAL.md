# Proposition Authoring RC1 Attachment/Scope Ambiguity Gate — Terminal Record

## Governance disposition

`FALSIFIED`

RC1 is terminal. This record does not authorize merge of semantic runtime to `main`, release, Contract A amendment, Evidence Bundler mutation, CAL mutation, Decision Engine mutation, or pipeline insertion.

## Exact lineage

- repository: `camerontjs-dot/proposition-authoring`
- programme: issue #4
- experiment: issue #5
- Draft Research PR: #13
- base `main`: `a4f018285ffc6d2c5755b2cc02a751799f1511a1`
- predecessor V0 source commit: `f1b2fe8d59a845c0cdfac80c155b0e1ff44c3a72`
- predecessor V0 source tree: `954a8e19dabdad24b303523821f5fe8f2ff9aab5`
- RC1 scientific source head before fresh authoring: `f83709f469269475a6d5fe918a30780bf9bcf580`
- RC1 scientific source tree: `c22d6e5bc32b88e7e7aa888a137800a18e9b1d0b`
- target freeze commit: `bd4fca4494b1ffce4a13118fad5a1268990e42db`
- fresh-surface seal / decisive head: `be0eb5257aa932be1c3755a34a16a547227d7ddb`
- fresh-surface tree: `9df720dfffec942a160171ccb11cdfb957c43750`
- fresh cases Git blob: `d8f8b9bbb94b278bb3d68b8e3f6d684ec766c186`
- fresh gold Git blob: `bb0d9d1e8c9ac27861ae3f9f40f9f1dd97dd3d32`

The target and qualification harness were frozen before fresh cases/gold existed. `FRESH_FREEZE.json` records that target output had not been observed before the fresh surface was sealed.

## Frozen target architecture

RC1 retained the exact V0 P1/P2/P3 proposer logic and exact frozen RC1 candidate evaluator. It added only a veto-only bounded root-scope analyzer plus receipt instrumentation.

The gate covered preregistered structural families:

- matrix attribution/evidential scope over coordinated clause-like material;
- trailing temporal/location/condition-like adjunct attachment;
- explicit sentential negation over coordinated propositions.

A root-scope finding could only block authority. It could not generate children, repair candidates, select between candidates, rescue evaluator rejections, or use downstream outcomes.

## Hosted pre-freeze evidence

- development research run `34784339888`: PASS
- development maintained CI run `34784339892`: PASS on Python 3.11 and 3.12
- target-freeze research run `34784393257`: PASS
- target-freeze maintained CI run `34784393247`: PASS

Development included the already-revealed V0 Q29 failure and clear counterparts only. Q29 was converted from unsafe `DECLARED` to `ABSTAINED / MATERIAL_ROOT_SCOPE_AMBIGUITY` before freeze.

## Fresh decisive surface

24 fresh roots, authored after target freeze:

- 9 `AMBIGUOUS`
- 7 `CLEAR_REQUIRED`
- 4 `CLEAR_DIAGNOSTIC`
- 4 `NOT_NEEDED`

Fresh cases SHA-256:

`206bf287ed617ab5a46674af2ae7de506b18497ba8f4a2975c75b3f5ab4bf755`

Fresh gold SHA-256:

`61b31baf37ba604850ee231b186f584f11ed38a8fac68bd0d6eea40b83903d21`

The fresh gold was internally bounded/adjudicated and was not independent human consensus. That evaluator-assurance limitation is preserved.

## Decisive execution

- research run: `34784510353` — execution PASS
- maintained CI: `34784510352` — PASS on Python 3.11 and 3.12
- decisive head: `be0eb5257aa932be1c3755a34a16a547227d7ddb`
- artifact ID: `10326630127`
- artifact digest: `sha256:ade3ca0d165c8246dfa82339487e5f89703f2595999a7bb5a36f100d05c3ee51`
- raw A SHA-256: `6a139f3f0032219ef887fb9941248cf97441a300b88fd7199c06a007affb3af2`
- raw B SHA-256: `6a139f3f0032219ef887fb9941248cf97441a300b88fd7199c06a007affb3af2`
- exact replay: byte-identical
- score SHA-256: `164bf0b1d2fbbff1deee7a1d8941563d18537897799560ab9982fa96a4d559cd`

The workflow removed gold from the runtime path before both raw executions and restored it only for scoring.

## Decisive result

Target totals:

- 24 cases
- 23 exact/correct against frozen gold
- 9/9 ambiguous roots correctly `ABSTAINED`
- 7/7 required clear counterparts correct
- 4/4 `NOT_NEEDED` controls correct
- 3/4 clear diagnostic cases correct
- 12 emitted Contract A objects, all valid under the exact released validator
- 0 processing failures
- 1 unsafe authoritative emission
- weak-control discrimination: PASS
- positive required gate: PASS
- diagnostic safety gate: FAIL
- hard safety gate: FAIL

Weak controls were discriminating:

- unchanged V0: 8 unsafe authoritative outcomes;
- blanket reporting+coordination abstention: 4 unsafe and only 5/7 required clear cases correct;
- punctuation-only detector: 7 unsafe;
- first-proposal selection: 13 unsafe;
- proposer-majority selection: 14 unsafe.

## Decisive falsifier — R22 shared attribution with `both`

Root:

`Committee Pine reported both Unit Amber passed and Unit Cobalt failed.`

RC1 correctly treated `both` as an explicit disambiguator for the Q29-style root attachment ambiguity, so the new root-scope gate did not fire. The unchanged proposer/evaluator path then emitted authoritative `DECLARED/all_of` children:

1. `Committee Pine reported both Unit Amber passed.`
2. `Unit Cobalt failed.`

This child set is semantically non-conservative. The root's reporting relation and correlative `both` jointly scope over the two coordinated reported propositions. The emitted second child loses the reporting attribution entirely, while `both` is stranded on the first child.

This is a preregistered hard falsifier: a clear counterpart received a materially wrong authoritative decomposition.

Exact decisive identities from the raw receipt:

- selected candidate: `r22::P2::explicit-clauses`
- candidate authority disposition: `ACCEPTABLE_WITHIN_PROFILE`
- candidate authority SHA: `45aca50bea0dc7f1fa7fbb8192792913a7982a3488386e2a41179e201de8a144`
- semantic cluster: `sha256:b9bbc6d97bb3aa2db488d4781cdab6a0b0ebf5617911d2d554d9dccab4231f63`
- Contract A handoff SHA: `sha256:769aa7359c4af8ebebcc37b63f08812fb22d72a80bd7429bf2d87e41f9284ce6`
- receipt SHA: `sha256:d9a6a8653ee2fd5dc3ef60c745c677d527ed7001edcd4af07ce93ac19d44e2fe`

The terminal falsifier does not depend solely on the conservative frozen gold label `ABSTAINED`: even if R22 were later considered authorable within a broader profile, this exact emitted child set would still be semantically invalid because shared attribution is lost.

## What RC1 did establish

The bounded ambiguity veto has positive fresh evidence within its tested families:

- all 9/9 fresh ambiguous cases failed closed;
- matrix attribution ambiguity was caught across reporting/stating, punctuation, and disjunction variants;
- trailing location/temporal/condition scope cases failed closed;
- explicit sentential-negation scope cases failed closed;
- all 7/7 preregistered required clear counterparts remained resolvable;
- all 4/4 simple single-proposition controls remained correct;
- exact replay and order/determinism regressions passed.

This supports the ambiguity gate as a useful measurement layer. It does **not** support the integrated RC1 apparatus for successor qualification because a surviving candidate can still violate scope conservation when an explicit disambiguator is present.

## Competing explanation and inference

The decisive failure is not evidence that root ambiguity detection is useless. R22 is structurally clear enough for the root ambiguity gate to stand down. The failure occurs downstream: the unchanged proposal/candidate-authority path accepts a decomposition that does not preserve the clear shared matrix scope.

The strongest current inference is therefore that the next bottleneck is evaluator/authority assurance on candidate-vs-root scope conservation, not additional root ambiguity heuristics. This aligns with programme RC2 issue #6, but RC2 is a separate experiment and is not executed by this terminal record.

## Deviations / limitations

- Fresh gold was internally adjudicated, not independently human-adjudicated.
- A contents-API write of the fresh JSONL was blocked by the connector before reaching GitHub. The fresh cases/gold were instead created as Git blobs and committed atomically. No target output existed before that atomic fresh freeze.
- A post-freeze `.fresh-authoring-marker` commit was a non-semantic breadcrumb and changed no frozen scientific file.
- No frozen target, fresh case, or fresh gold was repaired after decisive output.

## Terminal boundary

RC1 is `FALSIFIED`. PR #13 remains a research evidence record and must not be merged as semantic runtime. `main` remains the neutral programme/governance surface. Any change to candidate scope-conservation authority is a successor experiment with new frozen identities and fresh evidence.
