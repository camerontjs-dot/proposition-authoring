# Deviation 001 — qualification working-directory defect

## Observed run

Workflow run: `35419508114`

The run stopped during the preserved predecessor control before any successor execution.

`scripts/fetch_frozen_predecessors.py` succeeded inside the `predecessor/` checkout and created the expected frozen vendor files there. The next command invoked the predecessor from the repository-workspace root with `PYTHONPATH=predecessor/src`. The runtime resolves its default frozen vendor directory relative to the current working directory, so it looked for `vendor/frozen/proposers.py` at the workspace root rather than `predecessor/vendor/frozen/proposers.py`.

Observed error:

`RuntimeError: missing frozen predecessor vendor/frozen/proposers.py; run scripts/fetch_frozen_predecessors.py`

## Classification

`APPARATUS_INVALID_BEFORE_SUBJECT_EXPOSURE`

No candidate execution occurred. No predecessor scientific result was measured in this run. The preregistered success/failure criteria, exact predecessor, exact Contract A authority, candidate code, fixtures, and expected outcomes are unchanged.

## Correction

Run each Gate checkout from its own checkout directory so the existing relative frozen-vendor lookup resolves exactly as it does in the maintained workflows.

This is a harness-path correction only. No system-under-test file or preregistered criterion changes because of this deviation.
