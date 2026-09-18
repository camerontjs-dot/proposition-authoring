# ClaimGate + EvidenceGate V1 RC3 Converged Output Contract

Status: implementation successor to Gate V1 RC2. RC3 encodes the converged V1 blueprint and remains a release candidate until qualification closes.

## V1 role

ClaimGate standardizes the proposition. EvidenceGate standardizes the supplied evidence world. Neither Gate owns retrieval, proposition-relative evidence semantics, Decision policy, or Authorization.

## ClaimGate

ClaimGate emits:
- exact proposition identity/text/hash;
- bounded descriptive categories;
- authoring/decomposition state and lineage;
- Contract A binding;
- explicit authority firewall;
- whole-object hash.

Quantitative classification requires positive quantitative semantics such as rate, count, percentage, measurement/unit, currency amount, or explicit numeric comparison. Numeric identifiers, citations, versions, dates, and standards references do not create quantitative classification by themselves.

## EvidenceGate

EvidenceGate is claim-independent and emits:
- intrinsic `evidence_world_id`;
- exact source IDs;
- normalized media type;
- exact content hashes;
- per-source `representation_id`;
- typed source origin;
- issuer and source role;
- typed proposition-independent `source_authority_basis`;
- document/evidence classification;
- bounded coverage/corpus declarations;
- explicit authority firewall;
- whole-object hash.

### Identities

`content_sha256` binds exact source bytes.

`representation_id` binds:
- source ID;
- normalized media type;
- content hash.

`evidence_world_id` binds the sorted set of representation IDs.

Therefore claim changes do not change EvidenceGate. Source byte, source ID, media type, or source membership changes do.

Metadata characterization changes the EvidenceGate output hash but does not change intrinsic evidence-world identity.

## Source origin

`source_origin` is source provenance, not artifact retention provenance.

Known source origin contains:
- controlled `origin_type`;
- optional typed locator;
- basis.

V1 origin vocabulary:
- official_database
- official_document
- official_website
- publisher_document
- organization_record
- repository
- user_supplied
- local_artifact
- other

Locator kinds:
- web_uri
- doi
- registry_identifier
- repository_reference
- file_reference
- other

A `web_uri` must be an absolute HTTP/HTTPS URI.

Pipeline-retention locators remain outside the Gate object and belong to the generic apparatus provenance system.

## Source authority basis

`source_authority_basis` is proposition-independent. It uses a controlled kind:
- official_issuer
- first_party_record
- publisher_record
- repository_record
- user_declaration
- other

It cannot encode SUPPORTS/REFUTES, proposition applicability, verdict, Decision participation, or Authorization.

## Validation

JSON Schema is the normative structural contract.

Runtime verification performs:
1. exact JSON Schema validation;
2. object-hash recomputation;
3. claim text hash recomputation;
4. representation-ID recomputation;
5. evidence-world-ID recomputation;
6. cross-artifact verification.

There is no second hand-written structural definition of a valid Gate object.

## Standardization receipt

The paired receipt binds:
- root proposition ID;
- evidence-world ID;
- ClaimGate output hash;
- EvidenceGate output hash;
- Contract A state/hash.

The receipt declares the pairing but does not independently prove referenced artifacts.

## Gate bundle verifier

The canonical consumer verifier receives:
- ClaimGate;
- EvidenceGate;
- Contract A or null;
- standardization receipt.

It verifies every individual artifact and then exact cross-artifact equality. Only a verified bundle is internally coherent for downstream consumption.

## Reconstruction

The runner retains exact `CLAIM-GATE-INPUT.json` and `EVIDENCE-GATE-INPUT.json` reconstruction inputs. These are provenance artifacts, not Gate contract fields.

Generic apparatus attestations/run manifests remain owned by the Apparatus provenance system.

## Authority

All Gate V1 downstream authority flags remain false:
- retrieval_authority
- evidence_relation_authority
- decision_authority
- authorization_authority

No Gate V1 release promotes descriptive EvidenceGate fields into Evidence Bundler causal authority.

## Qualification

RC3 must:
- pass the 44-case predecessor pressure matrix with zero falsified cases;
- pass successor-specific mutation and bundle-substitution tests;
- replay deterministically;
- rerun the real Health Canada case;
- validate exact output specimens against the frozen RC3 schemas.

Final `1.0.0` assignment remains a separate promotion decision.
