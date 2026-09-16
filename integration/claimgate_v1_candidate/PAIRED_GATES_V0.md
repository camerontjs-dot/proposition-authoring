# Paired Pre-Retrieval Gates V0

## Status

Research infrastructure only. This programme is stacked on the exact frozen ClaimGate integration candidate from Draft PR #23 and does not modify that candidate's runtime or RC5 qualification subject.

Tracking issue: #24.

## Architecture

```text
verification task / context
        |
        +--> raw claim -----------------> ClaimGate --------> Claim Profile V0
        |
        +--> raw evidence world --------> EvidenceGate -----> Evidence World Profile V0
                                                        
Claim Profile V0 + Evidence World Profile V0
        |
        v
Evidence Bundler
        |
        v
Contract B
        |
        v
CAL
```

Both ClaimGate and EvidenceGate operate before Evidence Bundler retrieval.

Candidate-level evidence characterization, post-retrieval typed selection, and reranking are explicitly deferred to Evidence Bundler issue #80 / Draft PR #81.

## Separation of responsibilities

### ClaimGate

Characterizes the epistemic problem and preserves proposition/decomposition authority.

Candidate shadow observations include claim family, verification world, expected evidence form, domain, temporal scope, jurisdiction, and explicit unknowns.

### EvidenceGate

Characterizes the epistemic resources available before retrieval.

Candidate shadow observations include source inventory/provenance, evidence forms, source roles, corpus boundaries, completeness basis, temporal coverage, jurisdictional coverage, known gaps, and explicit unknowns.

### Evidence Bundler

Remains responsible for retrieval, candidate generation, selection/retention, and admission. V0 gate profiles do not steer those operations.

### CAL

Remains responsible for proposition-relative semantic judgment. Neither pre-retrieval gate may decide SUPPORTS / REFUTES or equivalent terminal semantic relations.

## Authority model

The gates should reduce hidden authority inference inside downstream components, but they do not create authority by classification alone.

Authority must be grounded in inspectable task declarations, source identity, provenance, issuer, corpus membership, document/record type, jurisdiction, version/effective date, or another explicit maintained rule.

Unknown authority remains unknown.

## V0 experiment

The first paired-gate experiment is observational.

For each frozen naturalistic input:

1. preserve the exact verification task/context;
2. run ClaimGate normally and emit/record Claim Profile V0 in shadow;
3. characterize the exact supplied evidence world with Evidence World Profile V0 in shadow;
4. run Evidence Bundler unchanged;
5. preserve native EB retrieval/admission receipts;
6. run downstream CAL unchanged where applicable;
7. compare the shadow profiles with observed downstream behavior.

Questions include:

- did Claim Profile V0 correctly identify a useful claim family without forcing uncertain cases?
- did Evidence World Profile V0 expose incomplete corpus, temporal mismatch, jurisdiction mismatch, or missing expected evidence form before retrieval?
- did profile fields predict or explain retrieval misses, admission outcomes, CAL unsupported-family outcomes, or abstentions?
- which fields were reproducible and which were unstable?
- did any field appear useful enough to justify a separate causal qualification experiment?

## Falsifiers / stop conditions

The V0 concept weakens if:

- profile generation requires access to downstream answers or CAL judgments;
- authority labels cannot be reconstructed from explicit provenance/context;
- profiles routinely force guesses where `unknown` should have been emitted;
- evidence-world characterization collapses into passage-level SUPPORTS/REFUTES judgment;
- ClaimGate and EvidenceGate duplicate each other's authority instead of exposing distinct claim-side and evidence-side state;
- shadow fields add no explanatory or predictive value on held-out naturalistic cases.

## Promotion rule

Do not promote the profiles as a single monolithic authority surface.

If a specific field proves useful and reproducible, qualify that field separately for a specific causal role. Examples might later include verification-world routing, source-aperture constraints, temporal filtering, or CAL family-resolution assistance.

No Contract A/B schema mutation, Evidence Bundler routing change, CAL routing change, or Decision change is authorized by V0.