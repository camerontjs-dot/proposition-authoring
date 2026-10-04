# Local agent brief — S0-R7 new reviewer pool

Act as the local ClaimGate S0 reviewer-pool qualification owner.

## Live authority

Inspect live GitHub first.

Repository:

`camerontjs-dot/proposition-authoring`

Successor issue:

`#65 — S0-R7: qualify a genuinely new reviewer pool against the frozen certificate packet`

Predecessor evidence:

- issue #63: terminal `BLOCKED_CERTIFICATE_SURFACE`
- Draft PR #64
- terminal head `fb3e907d1b1e94f69eb8ccbf1f92e01bc7fed9e5`

Frozen certificate packet:

`da6007163bfe96d39ef1026f9efb98e42edbbbeb`

Do not modify it.

Read this R7 directory and the predecessor R6c result/protocol before any reviewer call.

## Objective

Find and preregister a genuinely new reviewer pool, then determine whether at least two profiles pass the unchanged R6c calibration.

Do not perform decisive certificate review unless a later separately frozen successor authorizes it.

## Reviewer discovery

Inspect what reviewer-capable runtimes/providers are actually available from this machine/project.

Possible candidates include:

- unused local instruction models;
- remote model providers already legitimately available to the environment;
- Claude/Gemini/Grok/OpenAI or other agent/model surfaces if exact active model/provider identity can be established and the review can be run without hidden conversation context;
- qualified human review if available.

Do not claim a reviewer is available until you can execute it and preserve an identity/receipt.

Do not install or purchase a production dependency merely to satisfy this research task.

If a provider requires operator credentials/approval that are genuinely unavailable, record that and move on.

## Exclusions

Never reuse as R7 candidates:

- gemma3:12b
- qwen3.5:9b
- qwen3:14b
- qwen3-coder:30b
- gemma4:12b
- muse-glimmer:30b

`qwen2.5-coder:14b` may be at most one candidate.

Different settings on the same model are not different reviewers.

## Freeze candidate pool first

Before calibration, create the exact candidate-pool manifest required by the preregistration.

Freeze:

- candidate identities;
- provider/runtime identities;
- model digests/versions;
- semantic prompt/checklist pins;
- transport wrapper code;
- settings;
- eligibility implementation;
- stopping rule.

Do not add a new candidate after seeing another candidate fail.

If you cannot identify at least two genuinely new candidate profiles before execution, stop:

`BLOCKED_NEW_REVIEWER_POOL`

## Calibration

Use the unchanged R6c packet and eligibility rule.

Every candidate must:

- copy required fields correctly on every item;
- accept every known-good certificate;
- reject every hard mutation.

Preserve exact raw responses.

No retries that alter semantics.

Transport retry may be used only if preregistered and the original failure remains visible.

Do not tune a reviewer after a failed calibration.

## Reviewer-pair interpretation

If two profiles pass:

- freeze the exact eligible pool;
- record correlation/independence limitations;
- do not run decisive review yet;
- return `SUPPORTED_NEW_REVIEWER_POOL_FOR_DECISIVE_REVIEW`.

The next experiment should perform decisive certificate review with the frozen eligible profiles.

If fewer than two pass:

`BLOCKED_NEW_REVIEWER_POOL`

Do not solve that by adding another model after results.

## Packet objections

A new reviewer may discover a real semantic defect in the frozen packet.

Do not treat that automatically as reviewer failure.

Trace the objection to the exact source/certificate/analysis basis.

If the evidence supports a packet defect, preserve it and terminate under:

`FALSIFIED_CERTIFICATE_PACKET_BY_NEW_REVIEWER_EVIDENCE`

Do not repair the packet in R7.

## Continue-until rule

Continue autonomously through routine reviewer discovery, provider preflight, identity capture, candidate-pool freeze, calibration execution, evidence preservation and Draft Research publication.

Stop for an operator only if:

- a required provider needs unavailable credentials/paid authorization;
- a human reviewer must be recruited;
- satisfying the task would require changing the frozen packet, V1, Contract A or product responsibility.

## Return

Return:

- branch/commit/tree;
- R7 disposition;
- frozen reviewer-pool hash;
- all candidate reviewer identities;
- excluded-profile check;
- exact prompt/checklist/eligibility pins;
- per-reviewer calibration outcome;
- raw response/artifact hashes;
- transport deviations;
- eligible reviewer IDs;
- reviewer-correlation assessment;
- any packet objections and their disposition;
- evidence PR/comment;
- observed evidence;
- bounded inference;
- smallest justified next action.

Do not proceed to S1.
