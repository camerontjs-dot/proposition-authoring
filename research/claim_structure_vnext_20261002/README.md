# ClaimGate proposition-structure successor programme

Tracking: issue #58.

## Why this exists

ClaimGate's product responsibility is broader than the current frozen V1 discovery machinery. The desired responsibility is:

- establish `NOT_NEEDED` for an unambiguous atomic root;
- establish the warranted proposition structure for an unambiguous composite root;
- abstain on genuinely unresolved semantic ambiguity;
- distinguish semantic ambiguity from implementation coverage limits and representation limits;
- never use retrieval, Evidence Bundler, CAL, Decision, or downstream success to choose or repair proposition structure.

The exact frozen V1 Slice 1 remains a control:

`89ca88c7f0a661601f7eb798b6759667fa20ab3f`

Do not modify that subject in this programme.

## Programme hypothesis

A broader ClaimGate is more likely to succeed if **structure discovery and authority are separated**:

1. broad proposal/structure discovery may use learned or generative methods;
2. proposals have zero authority by themselves;
3. independent instruments test propositionhood, operator/scope preservation, semantic conservation, and equivalence;
4. a deterministic resolver grants authority only when the evidence for one structure is sufficient and competing structures are eliminated;
5. unresolved ambiguity, implementation coverage failure, and representation failure remain distinct terminal observations.

## Candidate architecture

```text
root claim + authorized context
        |
        v
broad structure discovery
  - frozen V1 P1-P5 baseline
  - learned/LLM structured proposer
  - syntax/SRL/semantic-graph proposer where useful
        |
        v
candidate proposition structures
        |
        +--> deterministic V1 frame / scope / conservation checks
        +--> independent learned entailment/alignment measurement (shadow first)
        +--> mutation/metamorphic discrimination
        |
        v
authority resolver
  - unique warranted structure -> authoritative candidate
  - genuine semantic ambiguity -> AMBIGUOUS
  - no adequate discovery -> COVERAGE_LIMITATION
  - meaning understood but current wire cannot express it -> REPRESENTATION_UNSUPPORTED
        |
        v
only separately qualified structure may later bind Contract A
```

## Stages

- **S0** freeze target semantics, research representation, annotation rules, decisive corpora, and metrics.
- **S1** compare proposal/structure-discovery lanes. No proposal lane may acquire authority.
- **S2** qualify semantic-equivalence/conservation instruments against adversarial mutations.
- **S3** compose discovery + authority and test the new terminal-state distinctions.
- **S4** independent/context-free reproduction on fresh cases.
- **S5** naturalistic shadow qualification.
- **S6** only after positive evidence, draft the smallest production/contract successor.

Each stage gets a separate frozen experiment identity. A later stage does not rewrite an earlier failure.

## What counts as success

For the final bounded decisive cohort, the target is strict:

- zero unsafe authoritative proposition structures;
- every preregistered unambiguous atomic root is handled correctly;
- every preregistered unambiguous `all_of` composite root is handled correctly;
- every preregistered materially ambiguous root abstains;
- adversarial semantic mutations are rejected;
- proposal ordering and proposer identity cannot change authority;
- deterministic replay and reconstructable receipts;
- unsupported non-`all_of` structure is identified as a representation limit rather than silently flattened or mislabeled as semantic ambiguity.

A positive finite-cohort result is still a bounded competence claim, not a universal-language guarantee.

## Files

- `EXTERNAL-RESEARCH.md` — research synthesis and design implications.
- `TARGET-SEMANTICS.md` — exact semantic responsibility and failure taxonomy.
- `EXPERIMENT-LADDER.md` — staged test programme and falsifiers.
- `LOCAL-AGENT-BRIEF.md` — context-free execution handoff.
- `PROGRAM.json` — machine-readable stage/authority manifest.
