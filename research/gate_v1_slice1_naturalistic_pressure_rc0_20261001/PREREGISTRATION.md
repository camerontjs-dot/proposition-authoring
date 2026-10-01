# Gate V1 Slice 1 naturalistic pressure RC0 preregistration

## Decision

Determine whether the exact frozen Gate V1 Slice 1 remains safe and internally consistent on a small naturalistic cohort of real claims and source bytes without changing Gate semantics, the sample after outcomes, or the released Contract A boundary.

This is pressure evidence, not a release or promotion decision.

## Exact subject

Repository: `camerontjs-dot/proposition-authoring`

Frozen operator subject:

- commit: `89ca88c7f0a661601f7eb798b6759667fa20ab3f`
- tree: `50a4a2f9bc694aa71f1943637e63afad1e6ee883`
- freeze ref: `freeze/gate-v1-slice-1-cli-20260919`
- PR: #54

Protected runtime identities:

- `src/proposition_authoring/production_slice.py`: `22fc914868cb9da36cfbba77e1c43cd557df46a1`
- `src/proposition_authoring/production_cli.py`: `cd660576db899e86aa9fe6766428ffab2acdbdf0`
- `scripts/run_gate_production_slice_v1.py`: `f7f2e48ffc61ba676ac1ed7629c5dcbc9e41e1e8`
- `src/proposition_authoring/gate_v1_rc3.py`: `00918633bd83e2b69e083d20c2d4578b797ed9e4`
- `src/proposition_authoring/gate_v1.py`: `d5120bd09050f7566b15ddd6347a6fdfbfc01450`
- `src/proposition_authoring/contract_a.py`: `c7997d91146a1a7b3e888c98a9ed5f9610ce3f6e`

Released Contract A authority:

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `529c92b49a34d5c610618551a8737f019f9fa332`
- version: 2.0.0

Do not mutate, rebase, rebuild, cherry-pick, or repair the Gate subject. Any runtime identity mismatch is a stop condition.

## Scope

In scope:

- real claim texts already present in local material before Gate execution;
- the exact source bytes associated with those claims where available;
- ClaimGate decomposition / abstention behavior;
- EvidenceGate source identity, representation, provenance, and claim-independence properties;
- Contract A emission / fail-closed behavior;
- deterministic replay;
- bounded metamorphic and mutation controls.

Out of scope:

- adding or tuning decomposition rules;
- changing ClaimGate/EvidenceGate schemas;
- widening Contract A;
- representation transformation;
- changing Evidence Bundler, CAL, Contract C, Decision, or Authorization;
- release/version changes;
- rerolling the cohort after observing Gate output.

## Naturalistic pool and frozen selection

Use only real claims that existed in local project/research material before this run. Do not invent claims merely to help the Gate.

Build a local private `POOL.jsonl` with at least 16 eligible claims. Each row must contain:

- stable `claim_id`;
- exact claim text;
- claim-text SHA-256;
- source IDs;
- exact source-byte SHA-256 values;
- actual source media types;
- source locator or local provenance pointer;
- one pre-output structural stratum.

Use these strata, assigned from surface structure before Gate execution:

1. `plain` — no obvious coordination or attribution structure;
2. `coordination` — conjunction / multiple proposition-like clauses;
3. `attribution` — reporting, saying, finding, concluding, or similar attribution;
4. `qualified` — quantitative, temporal, jurisdictional, compliance, or other material qualifiers.

If a claim matches several, use precedence:
`attribution > coordination > qualified > plain`.

Require at least three eligible claims in every stratum before selection. If a stratum cannot supply three genuine claims, stop as `BLOCKED_INSUFFICIENT_NATURALISTIC_POOL`; do not backfill with invented examples.

### Frozen selection seed

`gate-v1-naturalistic-pressure-rc0::89ca88c7::20261001`

Selection algorithm for each stratum:

`score = sha256(seed + NUL + claim_id)`

Sort ascending by the lowercase hexadecimal digest and take the first three claims from each stratum.

This yields exactly 12 selected claims. Freeze `POOL.jsonl`, `SELECTED.json`, the seed, algorithm, and their SHA-256 identities before executing Gate. Do not change the seed, pool membership, strata, or selected cohort after observing any Gate output.

## Pre-run structural review

Before Gate execution, create `PRE-RUN-STRUCTURAL-REVIEW.json` for the 12 selected claims.

For each claim, record one of:

- `SINGLE`
- `DECOMPOSABLE_ALL_OF`
- `MATERIALLY_AMBIGUOUS_ABSTAIN`
- `NOT_JUDGED`

For `DECOMPOSABLE_ALL_OF`, record the expected child proposition texts or the exact semantic obligations the children must jointly preserve.

Review specifically for:

- attribution scope;
- negation scope;
- temporal qualifiers;
- quantitative values and units;
- jurisdiction;
- modality / uncertainty;
- shared trailing modifiers;
- causal/comparative relations;
- subject/object identity;
- conjunction/disjunction meaning.

Freeze the review before Gate output is revealed.

A separate reviewer/agent that cannot see Gate outputs is preferred. If the same executor authors this review, record `review_independence: same-agent-pre-run`; do not later describe it as independent adjudication.

## Execution

Install and execute the exact frozen subject in an isolated worktree/environment.

Use the installed operator surface:

`proposition-authoring-v1 PACKET.json --out-dir RUN_DIR --implementation-identity gate-v1-naturalistic-pressure-rc0`

For each of the 12 selected claims:

1. construct the packet from the frozen claim/source bytes without paraphrasing;
2. run Gate twice into fresh directories;
3. preserve all Gate inputs, ClaimGate, EvidenceGate, standardization receipt, authoring receipt, Contract A when emitted, stdout/stderr, and exit code;
4. compare the two output trees byte-for-byte;
5. externally validate every emitted Contract A object with the exact released Contract A 2.0 validator.

Do not invoke a downstream consumer when no Contract A is emitted.

## Required pressure controls

In addition to the 12 untouched naturalistic cases, run these controls on copies. Never mutate the frozen originals.

### EvidenceGate invariance / sensitivity

On at least three selected multi-source cases where possible:

- reverse source order and corresponding metadata order: EvidenceGate must remain invariant;
- change only root claim identity/text while holding evidence fixed: EvidenceGate must remain invariant;
- change one source byte: evidence-world identity must change;
- change one source media type while holding source content fixed: representation identity must change and the evidence-world identity must respond according to V1 representation semantics.

### Contract A boundary

For at least three cases that otherwise emit Contract A:

- substitute an unsupported source representation such as `text/html` without relabeling it as plain/Markdown;
- Gate must fail closed with `CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED`;
- EvidenceGate must retain the actual unsupported representation;
- no `CONTRACT-A.json` may exist.

For genuine local source representations already outside released Contract A 2.0, use the actual representation and treat the same fail-closed behavior as the expected boundary.

### Output tamper controls

On copies of at least two emitted Contract A objects:

- mutate root text without recomputing its binding;
- mutate one child text where decomposition exists;
- alter the top-level handoff hash/binding.

The exact released Contract A validator must reject the tampered copies.

## Hard falsifiers

Any of the following is a hard falsifier for the bounded pressure claim:

1. an authoritative `DECLARED` decomposition that the frozen pre-run review identifies as materially ambiguous or non-conservative;
2. a declared child set that drops or invents a material negation, attribution, temporal, quantitative, jurisdictional, modal, causal, comparative, subject, or object constraint;
3. exact replay produces different authoritative output bytes;
4. EvidenceGate changes under a claim-only mutation with identical evidence;
5. EvidenceGate fails to respond to an actual source-content mutation;
6. unsupported source representation produces Contract A instead of failing closed;
7. emitted Contract A fails the exact released Contract A 2.0 validator;
8. a prohibited downstream authority is acquired by ClaimGate or EvidenceGate;
9. the exact frozen subject/runtime identities do not match before or after execution.

Safe abstention and safe false negatives are not hard falsifiers. Preserve and report them.

## Allowed dispositions

- `SUPPORTED_FOR_BOUNDED_NATURALISTIC_PRESSURE_RC0` — zero hard falsifiers, all emitted decompositions survive frozen structural review, required invariants/controls pass, and replay is deterministic.
- `FALSIFIED` — at least one hard falsifier is observed.
- `INCONCLUSIVE` — evidence cannot determine whether a material decomposition/output is conservative, or the review/control apparatus is insufficient.
- `BLOCKED` — required real claims, sources, exact subject, validator authority, or environment cannot be established.

Do not repair the Gate, modify the frozen review, reseed, reroll, drop inconvenient cases, or change the cohort after a result.

## Required return receipt

Return:

- exact repository/worktree and subject SHA;
- runtime blob verification;
- seed and selection algorithm;
- pool count and per-stratum counts;
- SHA-256 of `POOL.jsonl`, `SELECTED.json`, and `PRE-RUN-STRUCTURAL-REVIEW.json`;
- 12 selected claim IDs;
- review-independence classification;
- per-case Gate state/reason;
- exact decomposition children where emitted;
- replay result;
- Contract A validation result;
- mutation/metamorphic results;
- failures and deviations;
- observed evidence;
- bounded inference;
- disposition;
- explicit non-claims;
- paths/hashes of preserved local receipts.

Do not publish private source bytes or sensitive local paths to GitHub. Hashes and privacy-safe summaries are sufficient for a later public evidence record.
