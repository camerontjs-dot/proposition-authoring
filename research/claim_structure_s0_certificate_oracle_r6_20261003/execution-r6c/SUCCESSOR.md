# S0-R6c inspection-first review

Predecessor commit: `9be357a6fd345a34a8245b34b80f624f0530ff6c`

Predecessor tag: `freeze/claim-structure-s0-certificate-oracle-r6b-20261003`

Certificate packet: `da6007163bfe96d39ef1026f9efb98e42edbbbeb`

Tag `freeze/claim-structure-s0-certificate-oracle-r6-decisive-20261003` stays on that packet.

This successor changes the review response procedure. It does not edit the certificates, schema, validator, mutation generator, reviewer profiles, sampling options, or the r6b checklist and prompt.

## R6b result

The item-level record is `evidence/r6b-calibration.json`.

- `qwen3:14b` was ineligible. It accepted hard copies that removed a subject, an object, a qualifier, or a negation binding. Several of those accepts were 12-token verdicts.
- `qwen3-coder:30b` was ineligible. It accepted hard copies that removed a subject, a qualifier, or a negation binding.
- `gemma4:12b` was ineligible. It rejected the known-good Kim certificate because the ledger splits the object span, and it accepted the disjunction copied as conjunction.
- `muse-glimmer:30b` was eligible. It accepted every known-good certificate and rejected every hard mutation.

One eligible profile is below the frozen minimum of two. Repeating that profile is not a second reviewer. Decisive review did not start.

## Procedure

The reviewer copies these fields from the certificate before the verdict:

- every predicate role;
- every scope binding on a `MATERIALLY_LIVE` reading;
- the live reading ids and their operators;
- every `MODALITY` obligation description;
- `spans_exact`, true only when each recorded source span equals its root slice.

`s0r6c.inspection.inspection_match` compares that copy with the certificate. Order does not matter. A copy that adds a role the certificate does not contain is a mismatch. A matching copy is not semantic authority.

Eligibility requires all three:

- the copy matches on every calibration item;
- every known-good verdict is `ACCEPT_COMPLETE`;
- every hard mutation has a parsed verdict other than `ACCEPT_COMPLETE`.

A mismatch makes the profile ineligible even when the verdict would otherwise pass. Unparsable output is not `ACCEPT_COMPLETE`.

Sampling stays `temperature` 0, `seed` 7, `num_ctx` 16384, and `think` false. The response format is the inspection schema in `s0r6c/run_review.py`, not the string `json`. That format change is part of this procedure.

## Order

Run one model at a time. Review known-good certificates, then hard mutations, into one output directory.

1. `ollama-qwen3-14b-t0-s7`
2. `ollama-qwen3-coder-30b-t0-s7`
3. `ollama-gemma4-12b-t0-s7` only if fewer than two profiles are eligible
4. `ollama-muse-glimmer-30b-t0-s7` only if fewer than two profiles are eligible after step 3

If two profiles are eligible, they are the decisive reviewers. Do not run later profiles after that.

If fewer than two profiles are eligible after this order, do not add a model and do not add another prompt paragraph. Record `BLOCKED_CERTIFICATE_SURFACE`. Decisive review does not start.

## Boundary

A supported result still authorizes only preparation of a fresh targeted S0 packet. It does not authorize S1, a proposer, a verifier, or a production change.
