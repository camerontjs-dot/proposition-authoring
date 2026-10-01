# Paired ClaimGate + EvidenceGate Shadow Prototype V0

## Classification

Research infrastructure / executable prototype for issue #28. This prototype is stacked on exact ClaimGate subject `7daaf3031b405499851b4d3fd946a05c53a25f25` and must not change its existing authoring semantics or Contract A behavior.

## Decision this prototype supports

Determine whether the paired pre-retrieval architecture can be made executable as a reconstructable shadow surface before testing whether any individual profile field deserves causal use.

## Hard boundaries

- Existing `AuthoringEngine` behavior is protected.
- Existing Contract A output is protected.
- Claim Profile is descriptive only and cannot affect authoring state.
- EvidenceGate characterizes supplied evidence before retrieval. It does not retrieve, rank, retain, admit, SUPPORT, REFUTE, or mutate Contract B.
- Preflight Compatibility compares explicit/bounded profile fields only and emits observations, never downstream instructions.
- Unknown state remains explicit rather than guessed.
- Profile and receipt identity must bind exact allowed inputs and configuration.

## Implementation plan

### 1. Typed shadow models

Add immutable types for:

- Claim Profile V0;
- Evidence World Profile V0;
- source-world metadata;
- Preflight Compatibility V0;
- paired preflight result.

### 2. Claim Profile V0

Generate a bounded descriptive profile from exact claim text plus explicitly supplied task metadata. Initial observations are deliberately conservative:

- claim-family tags from transparent bounded indicators;
- evidence-form expectations only where the surface supplies a useful signal;
- explicit temporal scope;
- explicit jurisdiction/task declarations;
- verification-world declaration only from task metadata;
- domain only from task metadata.

No profile field is semantic authority for proposition authoring.

### 3. EvidenceGate V0

Characterize the supplied evidence universe from exact source representations and explicit source/task metadata:

- source inventory and content hashes;
- media/evidence forms;
- declared source roles and provenance basis;
- explicit temporal/jurisdictional coverage;
- declared corpus scope/completeness;
- known gaps;
- verification-world declaration.

Set-like inventories are canonicalized independently of input ordering.

### 4. Preflight Compatibility V0

Compare only fields with explicit/bounded representation:

- expected evidence forms vs available forms;
- claim temporal scope vs evidence temporal coverage;
- claim jurisdiction vs evidence jurisdictional coverage;
- claim verification world vs evidence-world declaration.

Each comparison yields `match`, `mismatch`, `partial`, `unknown`, or `not_applicable` with a reconstructable basis.

### 5. Executable wrapper

Add a separate prototype entry point that:

1. runs existing ClaimGate unchanged;
2. generates Claim Profile V0 independently;
3. runs EvidenceGate V0 independently;
4. generates Preflight Compatibility V0;
5. emits all shadow artifacts and hashes beside the unchanged authoring result.

The wrapper must not feed shadow state back into ClaimGate or Evidence Bundler.

### 6. Tests

Required prototype evidence:

- maintained ClaimGate tests stay green;
- shadow wrapper preserves exact ClaimGate state/reason/Contract A/receipt for the same request;
- atomic, decomposed, and abstained ClaimGate paths can all emit Claim Profile;
- deterministic replay identity;
- evidence-source reordering invariance;
- source-content/provenance mutation sensitivity;
- unknown-forcing controls;
- matcher never emits CAL relation vocabulary or retrieval directives.

## Stop rule

Stop this prototype if implementing it requires changing existing ClaimGate authoring semantics, Contract A, Evidence Bundler behavior, CAL behavior, or Decision behavior. Those changes require separate experiments.

## Explicit nonclaims

A successful prototype establishes executable plumbing and reconstructable observations only. It does not establish profile accuracy, retrieval benefit, semantic coverage, or production authority.