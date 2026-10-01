# ClaimGate + EvidenceGate V1 RC3 candidate

Status: implementation candidate for the converged V1 blueprint. Not final 1.0.0.

RC3 is stacked on the frozen RC2 subject from PR #44 and preserves the RC2 pressure evidence from PR #46.

## V1 boundary

ClaimGate standardizes proposition identity, bounded descriptive category, decomposition lineage, Contract A binding and integrity.

EvidenceGate standardizes a claim-independent evidence world, source representation identity, bounded source provenance/classification/coverage, corpus declarations and integrity.

The paired receipt binds one claim to one evidence world. The bundle verifier proves the presented ClaimGate, EvidenceGate, Contract A and receipt agree.

Neither Gate has retrieval, proposition-relative evidence, Decision or Authorization authority.

## Identity model

- `content_sha256`: exact text bytes.
- `representation_id`: hash of source ID + normalized media type + content hash.
- `evidence_world_id`: hash of sorted representation IDs.
- Gate output hash: binds intrinsic identity plus descriptive characterization.

Changing media type changes representation/evidence-world identity because it can change machine interpretation. Changing descriptive metadata alone changes EvidenceGate output hash but not intrinsic evidence-world identity.

## Source provenance

`source_origin` is typed and distinct from pipeline-retention provenance.

Origin type uses the bounded V1 vocabulary. Locator kinds are typed; `web_uri` accepts only absolute HTTP/HTTPS URIs.

`source_authority_basis` is explicitly proposition-independent descriptive provenance. It carries no evidence-relation authority.

Pipeline retention locators, attestations and run-manifest identities remain outside Gate contracts.

## Validation

JSON Schema is the normative structural wire contract.

Runtime verification performs:
1. exact JSON Schema validation;
2. object/text/representation/evidence-world hash recomputation;
3. cross-artifact verification via `verify_standardized_gate_bundle_v1_rc3`.

The consumer CLI `scripts/verify_gate_bundle_v1_rc3.py` verifies a presented frozen bundle without producer-private runtime state.

## Qualification

RC3 must not become 1.0.0 unless:
- inherited 44-case pressure matrix: 0 falsified;
- RC3 unit/mutation suite: pass;
- real Health Canada specimen: pass;
- deterministic replay: pass;
- independent bundle consumer: pass;
- ordinary repository CI: pass.

Generic apparatus attestation/run-manifest qualification remains owned by apparatus-contracts PR #101 and does not block testing this Gate wire candidate unless reconstruction policy later makes it a promotion requirement.
