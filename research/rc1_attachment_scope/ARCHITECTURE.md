# RC1 Architecture — Root Interpretation Hazard Gate

## Core change

V0 granted authority when exactly one candidate semantic cluster survived the frozen candidate evaluator. RC1 adds one earlier question:

> Does the root itself still admit more than one materially distinct scope/attachment interpretation relevant to the candidate decomposition?

If yes, candidate survival is insufficient for authority.

```text
root + context
  -> unchanged P1/P2/P3 proposals
  -> unchanged RC1 candidate evaluator
  -> surviving semantic clusters
  -> ROOT SCOPE HAZARD ANALYSIS
       - no unresolved material finding -> normal V0 resolution
       - unresolved material finding    -> ABSTAINED
  -> Contract A only after both candidate authority and root-scope gate permit it
```

The gate has veto power only. It cannot create children, select one candidate over another, repair a candidate, or turn an evaluator rejection into acceptance.

## Why this is not a lexical blacklist

The target represents typed structural ambiguity findings. Each finding records:

- family;
- trigger span/type;
- competing scope descriptions;
- whether an explicit bounded disambiguator was observed.

The target rule is generic within each preregistered family: if two materially distinct attachment analyses remain structurally live, authority is blocked. Specific words only identify bounded scope-bearing constructions; they do not directly encode case IDs or expected answers.

## Bounded families

### Matrix attribution/evidential scope

Pattern class:

`MATRIX_SUBJECT + SCOPE_PREDICATE + CLAUSE_A + COORDINATOR + CLAUSE_B`

Potential readings:

1. matrix predicate scopes over both clauses;
2. matrix predicate scopes only over clause A and clause B is independently asserted.

Explicit repeated matrix predicates, repeated complementizers, or `both` can collapse the bounded ambiguity.

### Trailing adjunct scope

Pattern class:

`CLAUSE_A + COORDINATOR + CLAUSE_B + TRAILING_ADJUNCT`

Potential readings:

1. adjunct modifies only clause B;
2. adjunct modifies the coordinated proposition.

Prefix-shared adjuncts and repeated local adjuncts are clear bounded counterparts.

### Sentential negation over coordination

Pattern class:

an explicit sentential-negation operator scopes over a coordinated proposition without explicit distribution.

Potential readings must differ in proposition-level polarity or scope. Ordinary local verbal negation such as `A did not pass and B failed` is not automatically ambiguous.

## Resolution semantics

The gate runs after proposal/evaluation so the receipt can preserve all candidate evidence, but before any `DECLARED` or `NOT_NEEDED` Contract A emission.

- material unresolved finding + otherwise one cluster -> `ABSTAINED / MATERIAL_ROOT_SCOPE_AMBIGUITY`
- material unresolved finding + zero clusters -> normal abstention, with scope finding preserved
- material unresolved finding + multiple clusters -> normal multiple-cluster abstention, with scope finding preserved
- no finding -> V0 resolution behavior unchanged

The gate cannot convert `ABSTAINED` to an authoritative state.

## Receipts

RC1 receipts add a deterministic `root_scope_findings` array. It is diagnostic evidence, not a new Contract A field.

Each finding is canonicalized before receipt hashing so equivalent whitespace/punctuation variations do not change authority merely by ordering of diagnostics.

## Metamorphic expectations

Authority must be invariant under:

- insignificant whitespace;
- terminal punctuation changes;
- proposer dictionary order;
- candidate order within a proposer;
- repeated execution.

Comma insertion alone cannot resolve an otherwise material attachment ambiguity in this bounded profile.

## Nonclaims

RC1 does not establish universal attachment parsing, universal ambiguity detection, semantic completeness, production readiness, or independent evaluator validity. It tests only whether this bounded veto layer closes the V0 Q29-class safety hole without destroying clear counterparts.
