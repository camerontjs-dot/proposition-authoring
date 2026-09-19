# ClaimGate + EvidenceGate V1 RC2 Output Contract

Status: bounded successor candidate to the previously qualified draft V1 surface. RC2 exists because the real Health Canada run in Draft PR #43 exposed two boundary counterexamples. It does not promote Gate metadata into EB, CAL, Decision, or Authorization authority.

## Purpose

The gates standardize incoming state for the pipeline.

- ClaimGate emits stable claim identity, bounded category, authoring/decomposition lineage, Contract A binding, and integrity.
- EvidenceGate emits stable evidence-world identity, exact source identities, source-origin/provenance characterization, bounded evidence classification/corpus declarations, and integrity.
- The paired receipt binds one claim/root to one evidence-world output for the run.

The intrinsic EvidenceGate object is claim-independent.

## RC2 corrections

### Identifier-safe claim categorization

Identifier-labelled tokens such as DIN, NDC, NPN, lot, serial, document, licence, application, registration, and explicit ID/identifier numbers do not create the `quantitative` category by themselves.

They do not suppress real quantitative cues. A claim containing a DIN plus a rate/count/percentage or an unlabelled numerical measurement can still be quantitative.

### Claim-independent evidence identity

`evidence_world_id` is derived only from sorted `(source_id, content_sha256)` pairs.

EvidenceGate RC2 contains no `root_id`. The claim/evidence association lives in the paired standardization receipt, which carries both `root_id` and `evidence_world_id`.

Thus:
- changing only the claim leaves the intrinsic EvidenceGate output unchanged;
- changing source bytes changes `evidence_world_id`;
- changing only source characterization changes `output_sha256` but not `evidence_world_id`.

### Source provenance vs pipeline provenance

EvidenceGate carries source provenance only.

Each source provenance block contains:
- `origin.origin_type`: what kind of origin the source has;
- `origin.source_uri`: an optional source-origin URI;
- `issuer`;
- `source_role`;
- `authority_basis`.

A source URI explains where evidence originated. It is not a durable retention locator and does not authenticate reconstructed bytes.

Pipeline retention/reconstruction provenance belongs to the cross-pipeline attestation/run-manifest architecture in Apparatus Contracts Draft PR #101.

## Reconstruction bridge

The RC2 runner additionally emits:
- `CLAIM-GATE-INPUT.json`;
- `EVIDENCE-GATE-INPUT.json`.

These are provenance-layer reconstruction artifacts, not Gate contract fields. They preserve the exact causal input state needed for later apparatus attestations, including source bytes and evidence metadata/declarations.

No Gate-specific attestation format is introduced here. The intended attestation authority is the generic Apparatus candidate in PR #101 once its identity/canonicalization rules are qualified.

## Versioning

RC2 uses compatibility marker `1.0.0-rc.2`. The earlier draft V1 candidate remains preserved as historical evidence. Final `1.0.0` is not assigned by this successor until qualification closes the demonstrated counterexamples.

## Authority

RC2 does not establish retrieval authority, proposition-relative evidence authority, CAL semantics, Decision policy, or operational Authorization.
