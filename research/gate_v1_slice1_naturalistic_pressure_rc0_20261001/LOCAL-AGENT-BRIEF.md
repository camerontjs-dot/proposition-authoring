# Local agent brief — Gate V1 Slice 1 naturalistic pressure RC0

Act as the local execution and evidence owner for one bounded naturalistic pressure run of the already-frozen ClaimGate + EvidenceGate V1 Slice 1.

## Authority

Inspect live GitHub first.

Execution subject:

- repository: `camerontjs-dot/proposition-authoring`
- exact Gate subject: `89ca88c7f0a661601f7eb798b6759667fa20ab3f`
- exact tree: `50a4a2f9bc694aa71f1943637e63afad1e6ee883`
- freeze ref: `freeze/gate-v1-slice-1-cli-20260919`
- promotion/local-pipeline record: PR #54

Experiment protocol:

- PR #56
- `research/gate_v1_slice1_naturalistic_pressure_rc0_20261001/PREREGISTRATION.md`
- `research/gate_v1_slice1_naturalistic_pressure_rc0_20261001/select_cohort.py`

Released Contract A 2.0 authority:

- `camerontjs-dot/apparatus-contracts@529c92b49a34d5c610618551a8737f019f9fa332`

GitHub and the exact immutable commits/files above outrank this summary if anything conflicts.

## Objective

Pressure-test the exact frozen V1 Slice 1 with real claims and real source bytes already present locally.

Do not develop or repair the Gate. Do not create a new Gate candidate. This task is allowed to end negative.

## First phase: freeze the real-claim cohort before Gate execution

1. Find at least 16 genuine claims in existing local project/research material, each with the source bytes used to ground or motivate the claim where available.
2. Build the private local `POOL.jsonl` exactly as required by the preregistration.
3. Assign the four pre-output structural strata without running Gate.
4. Run the checked-in `select_cohort.py`; do not manually choose replacements.
5. Freeze `POOL.jsonl`, `SELECTED.json`, the exact seed, and SHA-256 identities.
6. Do not reroll or change the sample afterward.

Frozen seed:

`gate-v1-naturalistic-pressure-rc0::89ca88c7::20261001`

## Second phase: pre-run structural review

Before exposing the 12 selected claims to Gate output, freeze `PRE-RUN-STRUCTURAL-REVIEW.json` under the preregistered vocabulary:

- `SINGLE`
- `DECOMPOSABLE_ALL_OF`
- `MATERIALLY_AMBIGUOUS_ABSTAIN`
- `NOT_JUDGED`

For decomposable claims, record the expected child texts or exact semantic obligations that must be conserved.

Use a separate reviewer/agent blind to Gate output if practical. If not, do the review yourself before execution and record it as `same-agent-pre-run`, not independent review.

## Third phase: execute the frozen Gate

Use an isolated worktree/environment at exactly `89ca88c7f0a661601f7eb798b6759667fa20ab3f`.

Verify the protected runtime blobs from the preregistration before running.

Install the exact subject and run each selected claim twice through:

`proposition-authoring-v1 PACKET.json --out-dir RUN_DIR --implementation-identity gate-v1-naturalistic-pressure-rc0`

Preserve the complete outputs and compare replay trees byte-for-byte.

Externally validate every emitted Contract A object against exact released Contract A 2.0 at `529c92b49a34d5c610618551a8737f019f9fa332`.

## Fourth phase: pressure controls

Run all required controls in the preregistration on copies of the frozen inputs/outputs:

- claim-only EvidenceGate invariance;
- source-order invariance;
- source-content mutation sensitivity;
- representation mutation sensitivity;
- unsupported-representation fail-closed behavior;
- Contract A tamper rejection.

Do not mutate originals.

## Hard rules

- Never change Gate runtime or tests to obtain green.
- Never change the seed, pool, strata, selected cohort, or pre-run structural review after Gate output.
- Never silently drop a difficult claim.
- Preserve safe false negatives and abstentions.
- An unsafe authoritative decomposition is a hard falsifier.
- A representation/provenance/invariance failure is a hard falsifier.
- If required identities do not match, stop.
- If a failure needs a new semantic mechanism, stop and return it as evidence for a successor research question rather than implementing the mechanism here.

## Return

Return the exact receipt required by the preregistration, including:

- subject and blob identities;
- selection seed and pool/selection hashes;
- selected claim IDs;
- pre-run review and independence classification;
- per-case Gate state/reason and child texts;
- replay comparison;
- Contract A validation;
- all metamorphic/mutation controls;
- preserved failures/deviations;
- observed evidence;
- inference;
- remaining unknowns;
- final allowed disposition.

Do not publish private source bytes or sensitive local paths. Keep them local and return hashes plus privacy-safe summaries.
