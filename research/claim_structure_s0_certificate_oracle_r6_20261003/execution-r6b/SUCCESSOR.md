# S0-R6b review-instruction successor

Predecessor freeze: `da6007163bfe96d39ef1026f9efb98e42edbbbeb`

Predecessor tree: `9ef2e145af8e078d71a6da019613740be316d3cb`

Predecessor tag: `freeze/claim-structure-s0-certificate-oracle-r6-decisive-20261003`

This successor changes the review checklist and the review prompt only. It does not edit the predecessor certificates, schema, validator, mutation generator, calibration packet, reviewer profiles, request configuration, or the six scaffold files.

## Why this successor exists

The predecessor calibration ran all four frozen profiles. None was eligible. The compact record is `evidence/r6-calibration-failure.json`.

Observed failure modes, before any r6b reviewer call:

- `gemma4:12b` rejected two known-good certificates because the one-word ledger rows were treated as a mismatch with a multi-word role span, and it accepted a certificate whose subject role had been removed.
- `qwen3:14b` accepted every known-good certificate and also accepted hard copies that removed a subject, an object, a qualifier, a negation binding, a live reading, or that changed the stated modal force.
- `qwen3-coder:30b` accepted every known-good certificate and also accepted hard copies that removed a subject, a qualifier, or a negation binding, plus a span whose text was not the root slice.
- `muse-glimmer:30b` returned empty message content for every item. Empty output is unparsable. It is not a semantic accept and it is not a semantic rejection.

The repeated accept path is that obligation prose still names a role or a token after the role entry or the scope binding has been removed. Completeness flags were true on those copies. Agreement with that prose is not a role or a scope binding.

## What stays frozen from the predecessor

- `CERTIFICATE-SCHEMA.json`
- `execution/s0r6/` validator, builder, mutation generator, and prompt renderer
- `execution/packet/` certificates, requirements, corpus, and calibration controls
- `execution/protocol/REVIEWER-PROFILES.json` request and profile identities
- `execution/protocol/REVIEW-CHECKLIST.md` and `REVIEW-PROMPT.txt` as the predecessor texts

Pinned predecessor hashes are in `tests/test_r6b_prompt.py`.

## What this successor freezes

- `protocol/REVIEW-CHECKLIST.md`
- `protocol/REVIEW-PROMPT.txt`
- `s0r6b/run_review.py` and `s0r6b/eligibility.py`
- the calibration order and the stopping rule in this file
- `evidence/r6-calibration-failure.json`

## Reviewer procedure

Use the same four profiles, the same endpoint, and the same request: `stream` false, `think` false, `format` json, `temperature` 0, `seed` 7, `num_ctx` 16384.

Run one model at a time. For each profile, review `execution/packet/calibration/known-good` and then `execution/packet/calibration/mutations` into one output directory. Skip a file that already has an output. Do not show one profile's output to another.

Eligibility is the predecessor rule: `ACCEPT_COMPLETE` on every known-good item, and no `ACCEPT_COMPLETE` on any hard mutation. Unparsable output is not `ACCEPT_COMPLETE`. `s0r6b.eligibility.score_profile` applies that rule. A stem containing `--` is a hard mutation. The scorer reads executor filenames. Those filenames are not part of the reviewer prompt.

Calibration order, fixed before the first r6b call:

1. `ollama-qwen3-14b-t0-s7`
2. `ollama-qwen3-coder-30b-t0-s7`
3. `ollama-gemma4-12b-t0-s7` only if fewer than two profiles are eligible after steps 1 and 2
4. `ollama-muse-glimmer-30b-t0-s7` only if fewer than two profiles are eligible after step 3

If steps 1 and 2 are both eligible, they are the two decisive reviewers. Do not run steps 3 or 4 after that.

Decisive review uses `execution/packet/decisive` and only eligible profiles. Reviewers still receive the root, the analysis basis, the certificate, the schema, and the r6b checklist and prompt. They do not receive requirements JSON, controls, other reviewer output, or a desired disposition.

After the first r6b reviewer call, do not edit the r6b checklist, prompt, runner request, profiles, certificates, validator, or mutation generator. A further defect needs a new successor identity. The next successor, if fewer than two profiles are eligible, must change the review procedure shape. Another paragraph in this prompt is not that successor.

## Boundary

A supported result from this successor still authorizes only preparation of a fresh targeted S0 packet. It does not authorize S1, a proposer, a verifier, or a production change.
