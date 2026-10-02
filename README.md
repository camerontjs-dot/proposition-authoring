# Proposition Authoring

ClaimGate + EvidenceGate are upstream assurance boundaries for proposition structure and supplied evidence identity before Evidence Bundler and CAL.

## Product responsibility

**ClaimGate's job is to determine the authoritative proposition structure of one exact root claim.**

- If the root is one proposition, ClaimGate should establish `NOT_NEEDED`.
- If the root is structurally composite, ClaimGate should preserve that structure as an authoritative decomposition whenever the meaning can be warranted from the claim and authorized context.
- `ABSTAINED` is for genuine unresolved semantic ambiguity or insufficient authority. A mere parser/proposer coverage gap is not the desired end state for an otherwise unambiguous composite claim.
- `FAILED` is reserved for material apparatus failure.

The long-term responsibility is therefore broader than recognizing a few surface patterns: within the intended CAL Pipeline input domain, ClaimGate should handle composite claims regardless of wording while preserving every material operator, qualifier, scope, reference, negation, attribution, and other semantic obligation.

**EvidenceGate's job is different.** It deterministically standardizes the exact evidence representations supplied with the claim: source identity, content and representation identity, provenance, declared classification/coverage, corpus declarations, explicit unknowns, and integrity. It does not decide whether evidence supports or refutes the claim.

## Current V1 boundary

ClaimGate + EvidenceGate V1.0.0 is the frozen standardization compatibility surface around a **bounded** authoring implementation.

Current V1 can emit:

- `NOT_NEEDED`: bounded authority establishes one proposition and no decomposition is required;
- `DECLARED`: one warranted Contract A `all_of` decomposition is established;
- `ABSTAINED`: the bounded apparatus does not establish unique proposition authority;
- `FAILED`: the apparatus materially fails.

V1 currently authorizes only Contract A `all_of` decomposition. It does **not** establish complete coverage for every unambiguous composite claim, and it must not flatten disjunction, alternatives, conditionals, or other non-`all_of` structure into conjunction merely to avoid abstention.

The V1 promotion lineage preserves the earlier research record, including the terminally falsified V0 candidate and the RC2 surface falsification that motivated the qualified RC3 successor. See `docs/GATE_V1_1_0_0.md` and `CHANGELOG.md` for the stable V1 boundary and evidence lineage.

Only supported, qualified implementations may emit authoritative Contract A objects. Retrieval, CAL verdicts, Decision Engine outputs, or downstream performance may not select or repair proposition structure.

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
