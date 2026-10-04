# S0-R7 preregistration — new reviewer pool

## Frozen scientific subject

Certificate packet commit:

`da6007163bfe96d39ef1026f9efb98e42edbbbeb`

Packet tree:

`9ef2e145af8e078d71a6da019613740be316d3cb`

Do not modify any packet object.

## Frozen review interface

Use the exact R6c review interface from predecessor head `fb3e907d1b1e94f69eb8ccbf1f92e01bc7fed9e5`.

Pinned blobs:

- review checklist: `bef3ed02e738ab3c508d219ca2d13ef7d2756339`
- review prompt: `5656ffa07f40a6be13e2133b53c8af1c2b03b4a2`
- eligibility implementation: `8a2ac7ae23456bb9bd78ed2126b7fe8d17a8c273`
- inspection implementation: `ee0ebcc3444692eacfba527df8604ff3ea820089`
- review runner reference implementation: `433c7613149ea7619dd964246a8b2e310cf0b4a3`

A provider-specific transport wrapper may differ only as necessary to deliver the exact frozen semantic review task and capture the required structured response. Any semantic prompt/checklist change is a different experiment.

## Excluded profiles

Do not reuse these profiles as R7 candidates:

- `gemma3:12b`
- `qwen3.5:9b`
- `qwen3:14b`
- `qwen3-coder:30b`
- `gemma4:12b`
- `muse-glimmer:30b`

The unused local `qwen2.5-coder:14b` may be one candidate only.

A second run, different seed, temperature, prompt wrapper, or context length on one model does not create a second reviewer.

## Candidate-pool freeze

Before calibration, create `REVIEWER-POOL.json` containing every candidate reviewer profile you intend to test.

For every profile record:

- reviewer ID;
- reviewer type: `model` or `human` or other explicit type;
- provider/runtime;
- exact model/version/digest where applicable;
- endpoint/tool/runtime version;
- prompt/checklist blob pins;
- generation settings;
- whether the reviewer shares provider/model family/runtime with another candidate;
- availability/reproducibility limitations;
- reason it is materially new relative to the excluded pool.

Freeze and hash this pool before observing any calibration outcome.

Do not add replacement profiles after calibration results begin.

If fewer than two genuinely new profiles can be preregistered, stop `BLOCKED_NEW_REVIEWER_POOL`.

## Calibration

Run each preregistered profile against the unchanged R6c calibration packet.

Eligibility is exactly the predecessor rule:

1. required field copy matches on every calibration item;
2. every known-good certificate is `ACCEPT_COMPLETE`;
3. no hard mutation is `ACCEPT_COMPLETE`.

No partial credit.

Do not tune a failed reviewer and rerun it inside R7.

Preserve raw output, transport failures and every failed item.

## Correlation / independence accounting

Passing calibration does not prove reviewer independence.

Before a positive disposition, record for each eligible pair:

- provider relationship;
- model-family relationship;
- shared serving stack/runtime;
- prompt/checklist identity;
- whether either reviewer is human;
- any known common dependency.

Do not call the pair independent unless the evidence supports that claim.

R7 requires two **eligible genuinely new profiles**; it does not claim statistical independence by default.

## Packet-falsifier routing

If a new eligible reviewer identifies a material semantic defect in the frozen certificate packet, do not edit the packet.

Record the exact objection against source/analysis evidence.

If the objection is independently supported strongly enough to falsify a certificate assumption, terminate:

`FALSIFIED_CERTIFICATE_PACKET_BY_NEW_REVIEWER_EVIDENCE`

This is distinct from reviewer ineligibility.

## Stopping rule

- at least two eligible profiles -> `SUPPORTED_NEW_REVIEWER_POOL_FOR_DECISIVE_REVIEW`
- fewer than two eligible profiles -> `BLOCKED_NEW_REVIEWER_POOL`
- apparatus/transport evidence cannot determine eligibility -> `INCONCLUSIVE_NEW_REVIEWER_POOL`
- new review evidence falsifies the frozen certificate packet -> `FALSIFIED_CERTIFICATE_PACKET_BY_NEW_REVIEWER_EVIDENCE`

Do not run decisive certificate review inside R7. Freeze the eligible pool first; decisive review is a separately frozen successor execution.
