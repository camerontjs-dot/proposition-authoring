# Deviation 002 — cross-repository artifact export filename incompatibility

## Observed run

Workflow run: `35419720286`

All preregistered behavioral steps completed successfully before evidence export:

- valid Gate predecessor/successor paths were byte-identical;
- exact Evidence Bundler outputs from those valid paths were byte-identical;
- the successor HTML path stopped with no Contract A before Evidence Bundler;
- the hostile V1.0.0 HTML Contract A was rejected by Evidence Bundler;
- `RESULT.json` was written with disposition `SUPPORTED FOR PROMOTION`.

The final `actions/upload-artifact` step then failed because the Evidence Bundler output contains passage filenames with a colon, for example:

`passage:60230fa1ae64ba1ff2d4f141c5663d6f.yaml`

GitHub's artifact action intentionally rejects such filenames for cross-filesystem portability.

## Classification

`POST_RESULT_EVIDENCE_EXPORT_INVALID`

The scientific/conformance subject, candidate, consumer, fixtures, controls, and result classification were not changed. The failure affects durable artifact export only.

## Correction

Archive the generated directory trees into a single tarball before `actions/upload-artifact`. Upload the tarball plus the small top-level result/control files.

No runtime, contract, Gate, Evidence Bundler, threshold, expected result, or preregistered behavioral check may change as part of this correction.
