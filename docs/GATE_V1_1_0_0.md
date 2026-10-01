# ClaimGate + EvidenceGate V1.0.0

## Compatibility promise

Version `1.0.0` freezes the Gate standardization boundary demonstrated by the qualified RC3 candidate. Future incompatible changes to the declared V1 wire semantics require a major-version change.

## Public V1 artifacts

Normative structural schemas:

- `schema/gates/1.0.0/claim-gate-output.schema.json`
- `schema/gates/1.0.0/evidence-gate-output.schema.json`
- `schema/gates/1.0.0/standardization-receipt.schema.json`

Reference implementation and verification machinery:

- `src/proposition_authoring/gate_v1_rc3.py`
- `scripts/run_gate_v1_rc3.py`
- `scripts/verify_gate_bundle_v1_rc3.py`

The historical RC3 names identify implementation lineage. Emitted V1 artifacts carry version `1.0.0`.

## Frozen identity model

- `content_sha256`: exact content-byte identity.
- `representation_id`: source ID + normalized media type + content identity.
- `evidence_world_id`: sorted set of representation identities.
- Gate output hashes bind intrinsic identity plus descriptive characterization.
- The standardization receipt binds one claim root to one evidence world for a run.

## Authority boundary

ClaimGate owns proposition standardization.

EvidenceGate owns supplied evidence-world/source standardization.

Neither owns retrieval strategy, proposition-relative semantic judgment, Decision policy, or Authorization.

## Promotion basis

The release tree must preserve the exact qualified behavior of candidate `f02b752ee1f67ea7080771079e5b11c8c248776f` except for version/release metadata and the replacement of stale draft `1.0.0` schemas with the qualified RC3 wire definitions.

No semantic widening is authorized by this freeze.
