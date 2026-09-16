# ClaimGate V1 default pooled runtime successor RC1

**Classification:** Qualification-apparatus successor only.

## Trigger

RC0 workflow run `35055489780` did not reach the scientific discriminators. Its maintained-regression step invoked unscoped `pytest -q` after checking RC4b, Apparatus, and Evidence Bundler repositories out beneath the working tree. Pytest recursively collected foreign suites in the ClaimGate environment and failed on foreign dependencies.

This is `QUALIFICATION_HARNESS_SCOPE_DEFECT`.

## Frozen runtime subject

RC1 does not change the runtime subject introduced in RC0:

- runtime binding commit: `11f0d23a6a67239a1d3e0627ea542265f4eafbbf`;
- exact `src/proposition_authoring/engine.py` blob: `42ce4798e960a2f48afa7ab90147cac4fdf5799b`;
- predecessor integration head: `b3278e960707720f5add10935027a7187725d446`;
- semantic change remains only default `AuthoringEngine()` -> existing `CoverageBackend("pooled")`.

No runtime, proposer, evaluator, authority, profile, ambiguity, Contract A, or fixture change is permitted in RC1.

## Apparatus correction

The only intended correction is to scope maintained regression collection to ClaimGate-owned tests (`tests/`) rather than recursively collecting nested authority checkouts.

All previously preregistered scientific gates remain unchanged and unrevealed:

1. bounded runtime diff;
2. exact 44-case default-vs-explicit-pooled canonical equivalence;
3. exact 44-case RC4b gold preservation with no unsafe authority or Contract A error;
4. three frozen public CLI fixtures twice with byte-identical replay;
5. released external Contract A validation;
6. five Contract A hostile mutation rejections;
7. exact frozen EB consumer conformance, deterministic replay, and stale-root/stale-child rejection;
8. maintained ClaimGate tests/static checks.

## Stop rule

Any runtime blob change from `42ce4798...`, any semantic-file change, or any mismatch at a scientific gate falsifies RC1. Do not alter expectations or downstream consumers to obtain green.
