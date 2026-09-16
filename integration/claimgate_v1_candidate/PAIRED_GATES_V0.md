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
        |
        v
Contract C
        |
        v
Decision Engine
        |
        v
Contract D
        |
        v
Contract E / Authorization
        |
        v
Execution boundary / verifier
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

### Decision Engine / Contract D

Decision remains responsible for turning exact CAL / Contract C state into a bounded policy decision and exact requested effect / operation representation. Upstream evidence authority does not itself confer action authority.

### Contract E / Authorization

Contract E is a downstream operational-authorization boundary, not another epistemic gate.

Its question is approximately:

> Given the exact bound Decision / Contract D request, the exact target and current state, and independently trusted current AuthorityState / jurisdiction, is this exact operation authorized now?

Contract E must not allow ClaimGate or EvidenceGate source-authority labels to bypass CAL or Decision and become direct permission to act.

Upstream authority/provenance may matter only insofar as it is preserved through the exact validated pipeline artifacts and the resulting Decision / target binding. Contract E separately owns currentness, revocation, delegation/jurisdiction, exact subject/target/operation binding, replay resistance, and point-of-use authorization.

Contract E's current research evidence remains separate from this V0 programme and is not production-ready authority.

## Authority model

The gates should reduce hidden authority inference inside downstream components, but they do not create authority by classification alone.

Authority must be grounded in inspectable task declarations, source identity, provenance, issuer, corpus membership, document/record type, jurisdiction, version/effective date, or another explicit maintained rule.

Unknown authority remains unknown.

Keep three authority classes conceptually separate:

1. **epistemic/context authority** — what the task, claim, source or corpus is allowed to establish;
2. **decision authority** — what policy consequence follows from exact CAL / Contract C state;
3. **operational authorization** — whether an exact requested operation on an exact target is permitted now under Contract E / current AuthorityState.

No class automatically confers the next.

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
- shadow fields add no explanatory or predictive value on held-out naturalistic cases;
- upstream epistemic authority is treated as direct operational permission, bypassing Decision / Contract D / Contract E.

## Promotion rule

Do not promote the profiles as a single monolithic authority surface.

If a specific field proves useful and reproducible, qualify that field separately for a specific causal role. Examples might later include verification-world routing, source-aperture constraints, temporal filtering, or CAL family-resolution assistance.

No Contract A/B schema mutation, Evidence Bundler routing change, CAL routing change, Decision change, Contract E change, Authorization, or execution is authorized by V0.