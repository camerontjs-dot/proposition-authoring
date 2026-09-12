# Proposition Authoring

Research-stage upstream proposition authoring apparatus for the CAL Pipeline.

**Current posture:** V0 convergence prototype. Not production, not released, and not authorized as a pipeline dependency.

## Responsibility

Given one exact root proposition plus authorized source/context bytes, the apparatus either:

- emits a valid Contract A 2.0.0 `declared/all_of` handoff;
- emits a valid Contract A 2.0.0 `not_decomposed` handoff when the bounded authority establishes one proposition;
- abstains without emitting authoritative Contract A when a unique warranted authoring result cannot be established; or
- records material processing failure, with Contract A `failed` emission available only when the failure state is faithfully representable.

The V0 architecture is:

```text
plural proposal
    -> exact candidate ledger
    -> common semantic/binding authority
    -> semantic-equivalence clustering
    -> fail-closed resolution
    -> deterministic surface representative
    -> Contract A 2.0.0 emission
```

Proposal agreement is not authority. Retrieval, CAL verdicts, Decision Engine outputs, and downstream performance are prohibited as decomposition-selection inputs.

## Why this is a separate apparatus

The predecessor evidence converged on a responsibility with its own proposal diversity, evaluator assurance, provenance, versioning, failure/abstention state, deterministic receipts, and cross-repository conformance burden. Evidence Bundler remains a consumer of already-authored Contract A propositions; CAL remains downstream evidence-relative semantic audit.

Canonical architecture decision: `camerontjs-dot/apparatus-contracts#90`.

## Bootstrap

This repository intentionally does **not** copy predecessor research files by hand. Run:

```bash
python scripts/fetch_frozen_predecessors.py
```

The script fetches exact frozen predecessor bytes from immutable GitHub refs and verifies their Git blob identities (and the RC1 evaluator SHA-256) before writing them under `vendor/frozen/`.

Then:

```bash
python -m pytest
```

or, without pytest installed:

```bash
python -m unittest discover -s tests -v
```

## Prototype CLI

```bash
python -m proposition_authoring author request.json --receipt receipt.json --contract-a contract-a.json
```

If the result is `ABSTAINED`, no Contract A file is written.

## V0 nonclaims

This prototype does not establish universal semantic parsing, arbitrary natural-language decomposition correctness, independent evaluator validity, production readiness, LLM authority, a Contract A amendment, or safe automatic authoring outside the bounded tested profile.
