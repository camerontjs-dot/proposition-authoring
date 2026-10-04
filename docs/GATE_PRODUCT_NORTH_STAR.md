# ClaimGate + EvidenceGate Product North Star

Status: Draft product/architecture target. This document defines what the gates should make true for the CAL Pipeline before choosing a successor implementation. It does not change frozen V1, Contract A, Evidence Bundler, CAL, Decision, or release authority.

## North-star sentence

> **Turn one exact root claim plus a bounded source universe into an audit-ready semantic task: exactly which propositions must be checked, how those propositions are logically and contextually related, and exactly what evidence world is available to check them against — with identity, provenance, scope, gaps, uncertainty, and lineage explicit, without performing retrieval or deciding support.**

The gates prepare the problem. Evidence Bundler retrieves. CAL judges claim↔evidence relations. Decision applies policy.

## 1. ClaimGate: audit-ready proposition structure

ClaimGate owns the proposition structure that downstream apparatuses are allowed to treat as authoritative.

### Required responsibility

Given one exact root claim plus only authorized context, ClaimGate should:

1. bind the exact root claim, context, identity, and lineage;
2. determine whether the root is:
   - one independently auditable proposition;
   - a composite proposition structure;
   - genuinely semantically ambiguous;
   - beyond current implementation coverage;
   - understood but not representable by the downstream proposition contract;
   - or failed due to apparatus error;
3. produce **verification atoms**: the smallest propositions that can be assessed independently without losing meaning required for verification;
4. preserve the operator structure joining those atoms rather than flattening it;
5. preserve every material:
   - negation;
   - modality;
   - attribution;
   - quantity, unit, bound, or threshold;
   - temporal scope;
   - jurisdiction/location scope;
   - causal or comparative relation;
   - subject/object/reference binding;
   - condition, exception, disjunction, conjunction, or shared modifier;
6. carry forward warranted context from the root or authorized context when a child would otherwise become misleading or unverifiable;
7. never invent new facts while decontextualizing a child;
8. emit reconstructable root→structure→child lineage.

### Granularity rule

The target is **auditability, not maximum atomization**.

A child is too large if materially independent assertions cannot be assessed separately.

A child is too small if removing context changes what the proposition means or what evidence could legitimately verify it.

### Desired terminal distinctions

Research and future contracts should distinguish at least:

- resolved atomic;
- resolved composite;
- genuine semantic ambiguity;
- coverage limitation;
- representation unsupported;
- apparatus failure.

A parser/proposer coverage failure is not semantic ambiguity.

A downstream wire-format limitation is not semantic ambiguity.

### Explicit non-authority

ClaimGate does not:

- retrieve or rank evidence;
- use Evidence Bundler or CAL performance to select a decomposition;
- decide whether supplied evidence supports/refutes a proposition;
- decide source trustworthiness;
- apply Decision policy;
- authorize action.

## 2. EvidenceGate: verification-ready evidence world

EvidenceGate owns the exact bounded evidence world handed into evidence construction.

Its intrinsic evidence-world identity should remain claim-independent.

### Required responsibility

EvidenceGate should:

1. bind the exact bounded source universe;
2. bind source IDs, representations, bytes/hashes, and representation identity;
3. preserve acquisition/transformation lineage when one representation derives from another;
4. record provenance/origin/issuer/source role and externally declared authority basis;
5. distinguish externally declared metadata from mechanically derived metadata;
6. characterize representation/document/evidence form;
7. record applicability-relevant declarations when explicit or mechanically recoverable:
   - temporal coverage;
   - jurisdiction/location coverage;
   - version/revision;
   - currency/supersession state;
8. record corpus aperture/scope;
9. record declared completeness and known gaps;
10. preserve explicit unknowns rather than guessing;
11. identify duplicate, supersession, or conflict relations only where mechanically or externally established;
12. expose representation readiness and fail closed or report unsupported representation instead of silently relabeling bytes.

### Provenance is not truth

EvidenceGate may describe where a source came from and what authority basis was declared.

It must not silently convert provenance, issuer, source type, popularity, or semantic plausibility into claim-relative truth or support.

Any future source-reliability or authority mechanism needs separate qualification.

### Explicit non-authority

EvidenceGate does not:

- retrieve or rank passages;
- decide passage relevance to a claim;
- decide SUPPORTS/REFUTES;
- decide corpus sufficiency from semantic intuition;
- prescribe query strings, sources, passages, rank weights, or admission decisions;
- apply Decision policy or Authorization.

## 3. Joint deterministic preflight

ClaimGate and EvidenceGate may feed a separate deterministic preflight that compares **claim-side verification obligations** with **evidence-world declarations**.

This is useful only where both sides provide an inspectable basis.

Candidate dimensions:

- temporal scope vs temporal coverage;
- jurisdiction vs jurisdictional coverage;
- representation readiness;
- required/available evidence form where separately qualified;
- open/closed-world requirement vs declared corpus aperture;
- known gaps;
- version/currency compatibility.

Per-dimension output should remain descriptive, for example:

- match;
- partial;
- mismatch;
- unknown;
- not applicable.

Preflight is not a support verdict.

Preflight does not automatically steer Evidence Bundler unless a later field-specific experiment demonstrates that a particular observation is safe and useful as a causal hint.

## 4. Why the pipeline needs this boundary

### Evidence Bundler

Contract A already needs exact proposition text/identity and optional declared children.

Evidence Bundler retrieves independently for declared children and retains root/decomposition lineage. Therefore upstream proposition structure directly determines the units for evidence construction.

Evidence Bundler should not need to invent semantic decomposition.

### CAL

CAL answers a narrower question: whether supplied evidence carries the exact claim.

Its own architecture separates retrieval, probabilistic entailment, and deterministic rules.

Current CAL evidence records include failures involving composition that CAL does not form downstream. This supports making proposition structure explicit before CAL rather than teaching CAL to rewrite the claim while judging evidence.

Evidence-world boundary/completeness declarations can also matter to abstention and absence-style claims. Those should arrive as explicit upstream/evidence-construction state rather than being inferred from missing passages.

### Decision

Decision consumes canonical epistemic state.

It should not repair proposition structure, source provenance, corpus aperture, or missing evidence context.

## 5. External research implications

### Fine-grained verification is useful

FActScore and related work show why mixed factual content should be evaluated as smaller factual units rather than one holistic sentence.

FactLens specifically argues that fine-grained subclaims can improve transparency and reduce ambiguity in evidence retrieval.

### Decomposition must preserve context

FactLens and DnDScore show that subclaims must preserve context and semantic equivalence. Decomposition and decontextualization can work against each other.

This is why ClaimGate targets verification atoms, not shortest possible claims.

### Decomposition itself is a hard task

Claim-decomposition benchmarks show that identifying atomic/checkworthy claims remains difficult even for strong models.

The north star should therefore describe the output obligation without assuming a particular parser/model can already meet it.

### Predicate-role structure is a useful substrate

PropBank/SRL, Universal Dependencies, OpenIE/MinIE, and related work provide mechanisms for predicate-argument structure.

But UD-only extraction is incomplete, and surface relation extraction does not by itself solve scope/reference semantics.

### Scope needs explicit representation

UMR and related semantic-representation work explicitly model negation, modality, quantification, and scope because predicate-argument structure alone is insufficient.

That is directly relevant to ClaimGate's conservation burden.

### Provenance should be explicit and portable

W3C PROV distinguishes entities, activities, derivations, agents, and bundles.

EvidenceGate need not adopt PROV wholesale, but its lineage model should be compatible with the principle that provenance is an inspectable record, not an inferred trust score.

### Evidence metadata and sufficiency matter

RAG research increasingly evaluates metadata, source quality, grounding sufficiency, and abstention separately from semantic relevance.

This supports EvidenceGate carrying applicability and corpus-boundary state while leaving retrieval and claim-relative judgment downstream.

## 6. Current V1 relative to the north star

Frozen V1 already demonstrates useful parts of this target:

- deterministic claim/evidence identity;
- explicit authoring terminal states;
- bounded `all_of` proposition authority;
- claim-independent evidence-world identity;
- provenance/classification/coverage declarations;
- explicit unknowns;
- content-bound receipts;
- retrieval/CAL/Decision authority firewalls.

Its main ClaimGate gap is semantic-structure coverage.

Its main EvidenceGate gap is that useful evidence-world characterization and any preflight value have not yet been proven sufficiently complete or causally useful to downstream consumers.

Do not reinterpret those gaps as defects in the frozen V1 compatibility promise.

## 7. Research questions before vNext implementation

Before selecting a successor architecture, answer:

1. What is the smallest semantic intermediate representation that can express the proposition structures actually encountered by CAL Pipeline?
2. Can Universal Dependencies + deterministic rules recover enough predicate/argument structure for that domain?
3. Where is SRL or a richer meaning representation needed?
4. What explicit scope representation is minimally necessary for negation, modality, attribution, temporal/location scope, and quantification?
5. Can a frozen learned parser be treated as deterministic feature extraction while all proposition authority remains deterministic and inspectable?
6. How can root↔children conservation be checked without making an LLM the semantic oracle?
7. Which EvidenceGate metadata fields measurably improve Evidence Bundler or CAL behavior without leaking semantic authority?
8. Which joint preflight checks are truly deterministic from explicit declarations?
9. Does Contract A need richer proposition operators beyond `all_of`, and if so which operator is first justified by real pipeline need?
10. What failure state should cross-repository consumers see for genuine ambiguity vs coverage limitation vs representation limitation?

Implementation should start only after smaller experiments discriminate among these choices.
