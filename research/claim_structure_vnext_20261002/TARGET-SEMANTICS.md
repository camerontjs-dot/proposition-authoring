# Target semantics for ClaimGate successor research

## Product-level responsibility

Given one exact authoritative root claim plus explicitly authorized context, ClaimGate should determine the proposition structure required for downstream claim-level verification.

### Atomic

A root is atomic for this programme when it expresses one independently verifiable proposition after preserving every material qualifier and scope obligation.

Desired result: `NOT_NEEDED`.

### Composite

A root is composite when more than one independently verifiable proposition is asserted or when proposition-level operator structure relates multiple propositions.

For an unambiguous composite root, the desired result is an authoritative structure that preserves the root's meaning.

### Ambiguous

`AMBIGUOUS` means more than one materially distinct semantic structure remains live from the claim plus authorized context and the programme has insufficient authority to select one.

This is the intended semantic reason to abstain.

### Coverage limitation

`COVERAGE_LIMITATION` means the evaluation/gold says the root has a determinate structure, but the current discovery/analysis machinery cannot produce or validate it.

This is an implementation deficiency, not semantic ambiguity.

### Representation unsupported

`REPRESENTATION_UNSUPPORTED` means the root's structure is sufficiently understood, but the current downstream wire/contract cannot express it faithfully.

Example: a clear disjunction when the current Contract A authority supports only `all_of`.

Do not flatten such structures to `all_of` and do not relabel them as ambiguous.

### Failed

`FAILED` is reserved for material apparatus failure: missing required runtime, parser/model crash, invalid internal object, identity drift, or equivalent execution failure.

## Equivalence burden for decomposition

An authoritative decomposition must satisfy all of these:

1. **Propositionhood** — each leaf is independently evaluable as a proposition in the authorized context.
2. **Completeness** — no asserted proposition or material obligation from the root is dropped.
3. **Non-invention** — no child introduces a material assertion not warranted by the root/context.
4. **Operator preservation** — conjunction, disjunction, condition, negation, modality, attribution and other operators remain attached to the correct scope.
5. **Role/reference preservation** — subjects, objects, referents and argument roles are not silently changed.
6. **Qualifier preservation** — quantities, units, dates, temporal/jurisdictional scope, thresholds and other material qualifiers remain attached correctly.
7. **Reconstructability** — combining the children under the declared structure preserves the proposition-level meaning of the root.

Surface wording need not be identical.

## Research-only internal structure vocabulary

This is **not** a Contract A change. It is a shadow vocabulary for experiments.

- `ATOMIC`
- `ALL_OF`
- `ANY_OF`
- `IF_THEN`
- `SCOPED` — wrapper/group structure for attribution, modality, negation or another scoped obligation when needed;
- `OTHER` — structure observed but not yet typed;
- `AMBIGUOUS`
- `COVERAGE_LIMITATION`
- `REPRESENTATION_UNSUPPORTED`
- `FAILED`

Early authority experiments should focus on `ATOMIC` and `ALL_OF` because released Contract A 2.0 can already express those. Other operators remain shadow observations until separately represented and qualified.

## Important distinction

Proposal failure is not evidence that a root is atomic.

Parser failure is not evidence that a root is ambiguous.

One LLM's confidence is not evidence that a structure is warranted.

Downstream retrieval or CAL success is not evidence that an upstream decomposition was semantically correct.
