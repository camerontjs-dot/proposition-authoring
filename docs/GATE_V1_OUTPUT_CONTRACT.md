# ClaimGate + EvidenceGate V1 Output Contract

Status: candidate V1 standardization contract. This document defines the intended downstream-visible output surface for the gate V1 build tracked by issue #40. It does not promote the branch, release a version, or grant EB/CAL/Decision/Authorization authority beyond the fields stated here.

## 1. Purpose

ClaimGate and EvidenceGate are pipeline standardization boundaries.

They convert incoming claim/evidence state into deterministic, typed, traceable objects so later apparatuses know exactly what they are receiving.

They are not mini reasoning engines.

- ClaimGate answers: **what claim object is entering the pipeline, what bounded category does it have, and what decomposition lineage was authoritatively established?**
- EvidenceGate answers: **what exact evidence representations were supplied, where do they come from, how are they mechanically/declaratively characterized, and what corpus declarations accompany them?**

Downstream relational judgments remain downstream.

## 2. Governing separation

The V1 outputs do not replace Contract A or Contract B.

- Contract A remains the authoritative proposition/source-representation handoff into Evidence Bundler.
- ClaimGate V1 references the exact Contract A handoff hash when ClaimGate emitted one.
- EvidenceGate V1 binds metadata to the exact source IDs/content hashes supplied in the same request. Raw source content is not duplicated into EvidenceGate V1.
- Evidence Bundler still owns retrieval, ranking, selection, admission and Contract B production.
- CAL still owns proposition-relative evidence semantics.
- Decision still owns policy conclusions.
- Authorization remains separate.

## 3. Canonical serialization and integrity

The implementation uses the repository canonical JSON function:

- recursively sorted object keys;
- compact separators;
- UTF-8 Unicode emitted directly;
- NaN/Infinity forbidden.

CLI files add exactly one trailing LF.

Each gate output contains `output_sha256`, computed over the complete object excluding that field.

The paired standardization receipt separately binds both output hashes and the exact Contract A handoff hash when present.

## 4. ClaimGate V1

Schema token: `claim-gate-output-v1`

Compatibility version: `1.0.0`

Top-level fields are exactly:

- `schema`
- `version`
- `implementation_identity`
- `authoring`
- `claim`
- `lineage`
- `contract_a_binding`
- `authority`
- `output_sha256`

### 4.1 `authoring`

Exact ClaimGate terminal state and reason:

```json
{"state":"NOT_NEEDED|DECLARED|ABSTAINED|FAILED","reason":"..."}
```

This preserves a legitimate abstention/failure instead of coercing a proposition structure.

### 4.2 `claim`

Contains:

- exact `proposition_id`;
- exact claim `text`;
- exact `text_sha256`;
- `categories`.

`categories.values` is a non-empty sorted subset of the finite V1 vocabulary:

- `comparative`
- `causal`
- `attribution`
- `quantitative`
- `temporal`
- `definitional`
- `existence`
- `status`
- `compliance`
- `other`

Multiple categories may apply. `other` is a valid bounded outcome when no named V1 pattern applies.

The category basis is explicitly `bounded_classifier_v1`. It is descriptive standardization, not a CAL verdict and not evidence-routing authority.

V1 intentionally does **not** include expected-evidence requirements. Mapping a claim category to a retrieval/evidence strategy is a separately governed downstream rule.

### 4.3 `lineage`

Contains exact upstream identity:

- `handoff_id`
- `producer_id`
- `producer_version`
- `work_id`
- `decomposition`

When Contract A exists, `decomposition` is the exact Contract-A decomposition object (`not_decomposed`, `failed`, or `declared` with exact children/operator/sequence).

When ClaimGate abstains and no Contract A exists, V1 emits an explicit `unresolved` decomposition observation with the authoring-state basis. It does not invent `not_decomposed`.

### 4.4 `contract_a_binding`

Exactly one of:

```json
{"state":"present","handoff_sha256":"sha256:..."}
```

or

```json
{"state":"absent","handoff_sha256":null}
```

A downstream component that requires Contract A must stop on `absent`.

## 5. EvidenceGate V1

Schema token: `evidence-gate-output-v1`

Compatibility version: `1.0.0`

Top-level fields are exactly:

- `schema`
- `version`
- `implementation_identity`
- `root_id`
- `evidence_world_id`
- `source_count`
- `sources`
- `corpus`
- `authority`
- `output_sha256`

### 5.1 Evidence-world identity

`evidence_world_id` is content-derived from:

- exact `root_id`;
- sorted `(source_id, content_sha256)` pairs.

It identifies the supplied evidence byte-world independently from descriptive metadata. Changing source bytes changes the evidence-world identity. Changing only characterization metadata changes `output_sha256` but not the evidence-world identity.

### 5.2 Source rows

Sources are sorted by `source_id` and source IDs must be unique.

Each row contains exactly:

- `source_id`
- exact supplied `media_type`
- exact `content_sha256`
- `provenance`
- `classification`
- `coverage`

Raw `content` is deliberately absent. The governing representation remains upstream/Contract A.

### 5.3 Explicit observation shape

Descriptive fields use:

```json
{
  "state":"known",
  "value":"...",
  "basis":{"kind":"...","detail":"...","source_ref":"..."}
}
```

or:

```json
{
  "state":"unknown",
  "value":null,
  "basis":{"kind":"no_basis","detail":"...","source_ref":"..."}
}
```

Missing metadata never becomes a guessed value.

### 5.4 Provenance

`provenance` contains:

- `origin`
- `issuer`
- `source_role`
- `authority_basis`

These describe the source. They do not establish claim-relative authority or truth.

### 5.5 Classification

`classification` contains:

- `document_type`
- `evidence_form`

A value may come from explicit source metadata or the frozen V1 media-type mapping. The basis records which mechanism supplied it.

Current built-in mapping:

- PDF/plain/Markdown/HTML -> `document_text`;
- CSV/JSON/XML -> `database_record`;
- matching document types are `pdf_document`, `text_document`, `markdown_document`, `html_document`, `tabular_record`, or `structured_record`.

Unknown media types remain unknown unless explicitly declared.

### 5.6 Coverage

`coverage` contains explicit-known/unknown observations for:

- `temporal`
- `jurisdiction`
- `version`
- `currency`

V1 transports declarations. It does not attempt temporal interval reasoning or jurisdiction hierarchy reasoning.

### 5.7 Corpus declarations

`corpus` contains:

- `verification_world`
- `scope`
- `completeness`
- `known_gaps`

`known_gaps.state` is exactly one of:

- `unknown`: no declaration supplied;
- `declared_none`: the task explicitly declares no known gaps;
- `declared_some`: one or more gaps are explicitly declared.

This avoids the V0 ambiguity between silence and an explicit empty declaration.

## 6. Explicit authority statement

Both outputs contain an `authority` block stating what the gate standardizes and explicitly setting these to false:

- retrieval authority;
- evidence-relation authority;
- Decision authority;
- Authorization authority.

The authority block is descriptive of the V1 boundary. It does not grant new downstream authority merely by being present.

## 7. Deliberately excluded V0 capabilities

The following remain available as shadow/research instrumentation but are not part of the V1 downstream contract:

- expected evidence forms / evidence requirement mapping;
- claim scope ambiguity;
- context dependence;
- negation/modality/attribution flags beyond the bounded category vocabulary;
- entity/relation-target extraction;
- conflict/supersession relation observations;
- Preflight compatibility conclusions;
- query/source/rank/admission suggestions;
- proposition-specific source applicability;
- SUPPORTS/REFUTES;
- Decision/Authorization state.

Their exclusion is intentional. V1 should remain stable even as those research capabilities evolve.

## 8. Downstream consumption rule

A downstream apparatus may rely only on fields present in the relevant V1 output or governing contract.

It must not reconstruct omitted experimental state from the current implementation.

For the current pipeline:

```text
raw task
  -> ClaimGate V1 + Contract A
  -> EvidenceGate V1
  -> Evidence Bundler consumes Contract A plus only separately authorized gate metadata
  -> Contract B
  -> CAL
  -> Contract C
  -> Decision
  -> Contract D
  -> Authorization
```

Gate V1 standardization does not by itself authorize Evidence Bundler to use descriptive gate metadata causally. That requires a separate field/consumer qualification.

## 9. V1 freeze criteria

The V1 output contract is freeze-ready only if one exact implementation head demonstrates:

- unchanged ClaimGate authoring/Contract A bytes;
- deterministic replay;
- strict validation of owned fields and integrity hashes;
- EvidenceGate source-order invariance;
- source-content mutation sensitivity;
- explicit unknown behavior;
- explicit gap tri-state behavior;
- bounded category controls including the preserved `standard deviation`/compliance counterexample;
- no prohibited routing, semantic-verdict, Decision or Authorization fields.

A later semantic or metadata capability should normally be added as a shadow successor or a separately versioned V1.x contract change, not silently inserted into this surface.
