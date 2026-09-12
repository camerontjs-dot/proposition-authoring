# Proposition Authoring V0 — Fresh Qualification Preregistration

## Status

This file is frozen **before** any fresh decisive case or decisive gold is authored.

This is a bounded convergence qualification of the standalone Proposition Authoring V0 candidate. It is not an independent/context-free reproduction and cannot authorize production insertion or release.

## Research question

Can the integrated V0 apparatus preserve the supported plural-proposal/fail-closed-authority architecture while safely emitting Contract A 2.0.0 for bounded single propositions and explicit `all_of` decompositions, and abstaining rather than inventing authority when a unique warranted result cannot be established?

## Systems

### T0 — V0 target

Exact `AuthoringEngine` path frozen before fresh cases.

### Weak controls

- `C0_FORCE_NOT_DECOMPOSED`: emits `not_decomposed` for every non-crashing case.
- `C1_FIRST_PROPOSAL`: treats the first syntactically available proposal as declared without semantic authority.
- `C2_MAJORITY_PROPOSER`: selects the decomposition surface proposed by the largest proposer count, ignoring material semantic-cluster disagreement.
- `C3_SILENT_ABSTENTION_COERCION`: runs the target but converts `ABSTAINED` into Contract A `not_decomposed`.

Weak controls are evaluator-discrimination evidence only. They are not candidate implementations.

## Fresh decisive surface

Author only after target, profile, receipt format, Contract A emission/identity rules, runner, scorer, weak-control definitions, and this preregistration are frozen.

Exactly 30 fresh roots:

- 6 `NOT_NEEDED` single-proposition controls;
- 8 **core must-resolve** explicit `all_of` roots, split across shared-subject and two-explicit-clause families;
- 8 **advanced safe** `all_of` roots covering at least four of: shared/local scope, modality/negation, quantifier/threshold, comparison/direction, attribution, reference, ellipsis;
- 8 fail-closed roots covering intrinsic ambiguity, disjunction/out-of-profile connective structure, unresolved reference, and at least one semantically decomposable root for which the bounded proposer/authority machinery has no warranted emission.

No root may reuse exact predecessor wording or be a mere noun/number substitution of a predecessor root.

Runtime case bytes contain only case ID, exact root/request inputs, and source/context bytes. Expected state, acceptable child sets, family labels, must-resolve status, and rationale live only in post-raw gold.

## Gold states

Each gold row records:

- `case_id`;
- `class`: `NOT_NEEDED | CORE_DECLARED | ADVANCED_DECLARED | FAIL_CLOSED`;
- `family`;
- `expected_state`: `NOT_NEEDED | DECLARED | ABSTAINED`;
- zero or more semantically allowed exact child-text sets;
- rationale;
- whether an abstention on a safe case is a bounded false negative rather than an unsafe result.

A safe case is correct only when the state is correct and, for `DECLARED`, emitted children match one allowed semantic child set exactly after preserving intended child text/case punctuation.

## Decisive gates

### Hard safety gates

All must pass:

1. **zero unsafe authoritative emissions**. Any `DECLARED` with a disallowed child set, or `NOT_NEEDED` on a case requiring decomposition/fail-closed behavior, is a falsifier;
2. all 8 `FAIL_CLOSED` cases produce `ABSTAINED` and **no Contract A object**;
3. all emitted Contract A objects validate with the exact released Contract A 2.0.0 validator;
4. no proposer identity or vote count changes target authority;
5. raw target execution cannot access gold;
6. exact target replay is byte-identical for canonical receipts and emitted Contract A outputs;
7. no post-fresh semantic repair occurs.

### Positive coverage gates

All must pass for `SUPPORTED_FOR_INDEPENDENT_QUALIFICATION`:

1. all 6 `NOT_NEEDED` controls emit correct `not_decomposed` Contract A;
2. all 8 core must-resolve decompositions emit correct `declared/all_of` Contract A;
3. at least 5 of 8 advanced safe decompositions emit correctly;
4. therefore at least 19 of 22 safe-authorable roots are correctly authored overall;
5. advanced correct emissions span at least 3 distinct advanced semantic families;
6. C0-C3 each fail at least one hard safety or core coverage gate for the intended reason;
7. maintained hosted CI succeeds on the exact scientific head.

A safe-case `ABSTAINED` result above the allowed false-negative budget is not a semantic falsifier by itself. If safety gates pass but the positive coverage gates do not, disposition is `INCONCLUSIVE`.

`FAILED` on a semantic case counts as a false negative and additionally as a processing/reliability deviation; it cannot satisfy a positive-case gate.

## Metamorphic checks

On preregistered eligible cases:

- proposer dictionary iteration order must not change state, selected semantic cluster, receipt semantic content, or Contract A bytes;
- candidate order within a proposer must not change them;
- semantically irrelevant `all_of` child order may change `sequence` and whole-object handoff identity but must not change each exact child proposition ID;
- repeated exact execution must preserve canonical raw bytes.

## Contract A identity rule under test

For `declared/all_of` V0:

- each child proposition ID is deterministically derived from root proposition ID plus exact child-text SHA-256 prefix;
- child sequence remains explicit ordering metadata and is not part of semantic child identity;
- decomposition ID is derived from the selected semantic-cluster identity;
- whole Contract A identity remains governed by released Contract A canonical hashing.

Collision resistance of a 12-hex display prefix is not treated as a universal identity proof. A collision in the tested cohort or any evidence that truncation creates practical ambiguity blocks positive disposition and requires a new identity design.

## Failure mapping rule under test

Only an apparatus/runtime exception in the authoring attempt maps to internal `FAILED` and provisional Contract A `failed`. Semantic ambiguity, unsupported semantic structure, proposer exhaustion, or authority indeterminacy must map to `ABSTAINED` with no Contract A emission.

## Terminal dispositions

- `SUPPORTED_FOR_INDEPENDENT_QUALIFICATION`: all hard safety + positive coverage gates pass;
- `FALSIFIED`: any hard safety falsifier, gold/runtime contamination, replay drift, or post-result scientific repair;
- `INCONCLUSIVE`: hard safety passes but coverage/hosted/evaluator-discrimination burden is not met;
- `SUPERSEDED`: only if a successor protocol is frozen before decisive execution.

A positive result does not authorize merge, release, or pipeline insertion. The next gate is a separate fresh/context-free or independent qualification.
