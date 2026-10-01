# Proposition Authoring

Research apparatus for bounded proposition/decomposition authoring upstream of Contract A in the CAL Pipeline.

## Current status

ClaimGate + EvidenceGate V1.0.0 is the frozen standardization compatibility surface. It standardizes proposition identity/lineage and supplied evidence-world identity/provenance without acquiring retrieval, CAL-semantic, Decision, or Authorization authority.

The V1 promotion lineage preserves the earlier research record, including the terminally falsified V0 candidate and the RC2 surface falsification that motivated the qualified RC3 successor. See `docs/GATE_V1_1_0_0.md` and `CHANGELOG.md` for the stable V1 boundary and evidence lineage.

## Responsibility boundary

Given one exact authoritative root proposition plus authorized context/source bytes, Proposition Authoring may eventually produce one of four internal outcomes:

- `NOT_NEEDED`: bounded authority establishes one proposition and no decomposition is required;
- `DECLARED`: one warranted `all_of` decomposition is established;
- `ABSTAINED`: no unique warranted declaration can be established;
- `FAILED`: the authoring apparatus materially failed.

Only supported, qualified implementations may emit authoritative Contract A objects. Retrieval, CAL verdicts, Decision Engine outputs, or downstream performance may not select or repair a decomposition.

Canonical architecture decision: `camerontjs-dot/apparatus-contracts#90`.

## Research north star

Build the smallest bounded authoring apparatus that is simultaneously:

1. **safe**: materially ambiguous or semantically non-conservative decompositions do not acquire authority;
2. **useful**: safe decomposable roots and genuine single propositions are resolved at a practical bounded coverage level;
3. **deterministic and inspectable**: exact inputs, proposals, evaluations, abstentions, selections, receipts, and Contract A emissions are reproducible;
4. **independently qualified**: promotion-critical evaluators and consumers survive weak controls, mutation/metamorphic tests, and independent/context-free reproduction;
5. **contract-conformant**: authoritative outputs validate against the released Contract A contract and preserve exact lineage.

This is not a universal semantic parser project. The programme prefers explicit bounded competence plus abstention over broad but unearned authority.

## Navigation

- `docs/RESEARCH_PROGRAM.md` - staged research direction, next experiments, falsifiers, and promotion boundary.
- `docs/PR_GOVERNANCE.md` - evidence requirements for pull requests.
- `research/README.md` - experiment layout and evidence conventions.
- `.github/ISSUE_TEMPLATE/research-experiment.md` - required shape for new research questions.

## Terminal V0 result

V0 correctly handled 26/30 fresh cases, including 6/6 `NOT_NEEDED`, and all 20 emitted Contract A objects validated. It was still falsified because one fail-closed attribution-scope case acquired authoritative `DECLARED/all_of` output. Aggregate accuracy does not override a hard semantic-safety failure.

The next authorized research question is therefore not a general rewrite. It is the smallest mechanism that preserves materially distinct attachment/scope interpretations before a candidate decomposition can acquire authority.
