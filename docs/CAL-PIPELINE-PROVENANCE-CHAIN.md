# CAL Pipeline Provenance Chain

**Status:** cross-repo architecture pointer / local obligation record. No ClaimGate, EvidenceGate, Contract A, retrieval, CAL, Decision, Authorization, release, or production behavior is changed by this document.

## Canonical blueprint

The canonical proposed architecture is maintained in `camerontjs-dot/apparatus-contracts` Draft PR #101:

- `docs/architecture/CAL-PIPELINE-PROVENANCE-CHAIN-BLUEPRINT.md`
- canonical proposal head at this pointer's creation: `d16e5e14cab55ed23bdeee4cdeecf48724c542db`

Apparatus Contracts owns the cross-pipeline blueprint. This repository owns ClaimGate/EvidenceGate implementation details and conformance to any later-qualified provenance schema.

## Local requirement

The CAL Pipeline is expected to be reconstructable later from immutable artifacts. Proposition Authoring therefore must preserve the exact front-door identity from raw task input into Contract A / downstream evidence processing without giving descriptive Gate state downstream authority it has not earned.

### ClaimGate must eventually attest

- exact raw claim artifact digest;
- exact ClaimGate implementation identity;
- exact ClaimGate V1 output digest;
- exact terminal authoring state/reason;
- exact work/handoff/producer lineage;
- exact decomposition lineage;
- exact Contract A digest when emitted;
- explicit absence of Contract A when abstained/failed;
- independent authority inputs used to establish authoring/decomposition;
- durable locators for reconstruction-required artifacts.

### EvidenceGate must eventually attest

- exact supplied source artifact digests;
- exact EvidenceGate implementation identity;
- exact EvidenceGate V1 output digest;
- exact `evidence_world_id`;
- exact source IDs/content hashes represented in that world;
- corpus declaration/gap state identity;
- durable locators for reconstruction-required artifacts;
- explicit statement that descriptive Gate state is not retrieval, semantic, Decision, or Authorization authority unless separately qualified.

## Required role separation

A later attestation must distinguish at least `causal_input`, `authority_input`, `compatibility_input`, `observed_context`, and `diagnostic_input` roles as applicable. EvidenceGate visibility must not silently become Evidence Bundler steering authority.

## Negative terminal requirement

A legitimate `ABSTAINED` or `FAILED` ClaimGate result must remain reconstructable as that exact terminal state. Missing downstream Contract A/B/C/D objects must be attributable to the recorded front-door stop rather than appearing as an unexplained pipeline gap.

## Nonclaims

This pointer does not freeze an attestation schema, alter Gate V1 bytes, promote the current Gate V1 candidate, widen Contract A, or authorize causal consumption of descriptive metadata.
