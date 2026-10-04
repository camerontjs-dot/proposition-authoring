# S0-R6c result

Disposition: `BLOCKED_CERTIFICATE_SURFACE`

This is a certificate-surface disposition. It is not `SUPPORTED FOR PROMOTION`.

Decisive review did not start. No decisive certificate was admitted. S1 is not authorized.

## Identities

Branch: `research/claim-structure-s0-certificate-oracle-r6-20261003`

| Freeze | Commit | Tree | Tag |
| --- | --- | --- | --- |
| Packet, schema, validator, mutations | `da6007163bfe96d39ef1026f9efb98e42edbbbeb` | `9ef2e145af8e078d71a6da019613740be316d3cb` | `freeze/claim-structure-s0-certificate-oracle-r6-decisive-20261003` |
| R6b review instructions | `9be357a6fd345a34a8245b34b80f624f0530ff6c` | `f8070c345b8fd73d1d4175adaf65bda3f17a5330` | `freeze/claim-structure-s0-certificate-oracle-r6b-20261003` |
| R6c inspection procedure | `e29dad1d710a89a7e462f33ee40ea256cb015ad7` | `56c6c9f8171bce861830e7af7c20d74dbcfd7463` | `freeze/claim-structure-s0-certificate-oracle-r6c-20261003` |

Scaffold parent of the packet: `4ccd9b7a5dd5c461b589e8e3eae1831d8b3dca1d`.

The ref named in the opening PR note, `freeze/claim-structure-s0-certificate-oracle-r6-20261003`, is absent from origin. I left it absent.

Schema: `claim-structure-scope-obligation-certificate-v0`, sha256 `a8c08d65413af8203bb40da4fa3f0bcd9f3fcb5038811a53181d5e656ba25e2c`.

Validator: `execution/s0r6/validate.py`, sha256 `2eb2b2765a59e80b0fd8fab8f50145e91e671733c46797bbe0c454e2c5f5059d`.

Mutation generator: `execution/s0r6/mutate.py`, sha256 `a9851915d087d27550c9759c32de2735280007c8593386faaa1457db51d2d107`.

## Corpus

17 decisive certificates and 5 synthetic calibration certificates. Family counts count a root once per family it carries.

| Family | Count |
| --- | ---: |
| atomic | 7 |
| all_of | 2 |
| conjunction | 2 |
| disjunction | 2 |
| conjunction_disjunction_contrast | 2 |
| attribution_scope | 2 |
| negation_scope | 3 |
| temporal_location_scope | 2 |
| modality_condition | 4 |
| condition | 1 |
| ambiguous | 4 |
| coordination_modifier_scope | 1 |

Public sources, with locators in `execution/packet/CORPUS.json`:

- Universal Dependencies `nsubj`, `conj`, `ccomp`, `advcl` examples.
- UD English-GUM `GUM_essay_system-51`.
- ACL Anthology `2021.scil-1.23` example (1), `W12-4626` example (1a), `2024.tacl-1.41` examples (1a) and Table 1, `J06-3002` examples (1) and (2), `2022.sigtyp-1.6` Table 1 examples (2) and (4), `C08-1055` page 7 realisation items (1) and (3).

Certificate hashes are in `execution/packet/CERTIFICATE-HASHES.json` at the packet commit.

## Reviewers

Same four local Ollama profiles. Request: `think` false, temperature 0, seed 7, `num_ctx` 16384. They are separate local model runs. Repeating one profile is not a second reviewer. `gemma3:12b` and `qwen3.5:9b` stayed excluded.

R6 prose calibration: zero eligible profiles. Record: `execution-r6b/evidence/r6-calibration-failure.json`.

R6b field-rule calibration: only `muse-glimmer:30b` was eligible. One profile is below the minimum of two, so decisive review stayed closed. Record: `execution-r6c/evidence/r6b-calibration.json`.

R6c required a field copy before the verdict. A profile is eligible only when the copy matches on every item, every known-good verdict is `ACCEPT_COMPLETE`, and no hard mutation is `ACCEPT_COMPLETE`. Record: `evidence/r6c-calibration.json`.

| Profile | Eligible | What failed |
| --- | --- | --- |
| `qwen3:14b` `bdbd181c33f2` | no | Accepted removed subject, object, qualifier, and negation after copying those fields. The disjunction copy invented a scope binding. |
| `qwen3-coder:30b` `06c1097efce0` | no | Rejected the known-good `must` certificate. Accepted the removed qualifier after copying it. Reported the altered span as exact. |
| `gemma4:12b` `4eb23ef187e2` | no | Accepted the removed negation after copying it. Invented a scope binding on the disjunction. |
| `muse-glimmer:30b` `de878ce33ad8` | no | Rejected a known-good attribution certificate. Nine items failed the copy or the verdict rule. |

Wall time for the r6c calls was 1706s, 542s, 2502s, and 4322s in that profile order.

## What was checked without a reviewer

On this result commit's parent tree, `uvx --with jsonschema --with pytest pytest` over `execution/tests`, `execution-r6b/tests`, and `execution-r6c/tests` passed 17 tests in 0.30s.

Those tests accept the 17 decisive certificates and the 5 calibration certificates under the external requirements. They reject every applicable hard mutation, including the required calibration mutations. They reject promoting Peter's excluded reading to a live reading.

That is mechanical validity. It does not establish semantic correctness, and it does not admit a certificate.

## Boundary

The frozen certificates, schema, validator, and mutations stay at `da60071`. I did not edit them after review began. I did not edit V1 `89ca88c7f0a661601f7eb798b6759667fa20ab3f`, Contract A, or a production dependency.

A later attempt needs a newly preregistered reviewer pool, calibrated to two eligible profiles before any decisive review, against the packet at `da60071`. Another paragraph for these four models is not that attempt. S1 is not next.
