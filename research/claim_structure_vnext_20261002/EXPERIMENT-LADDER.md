# Experiment ladder

Every stage is a separate evidence record. Freeze scientific objects before decisive outputs. Preserve failures.

## S0 — target and corpus freeze

### Question

Can we create a discriminating, independent evaluation surface for proposition structure without selecting cases from Gate output?

### Build

Create two corpora:

1. **targeted capability corpus** — intentionally balanced across atomic, unambiguous `all_of`, materially ambiguous, and clearly non-`all_of` structures;
2. **naturalistic prevalence corpus** — frozen independently to estimate how often each class occurs in intended use.

Use genuine pre-existing/public claims where possible. Synthetic cases are allowed only as labeled mutation/metamorphic controls and may not masquerade as naturalistic evidence.

Freeze annotation rules, reviewer identities/isolation, claim/source hashes and gold before successor execution.

### Stop

Blocked if the target classes cannot be adjudicated independently enough to test the apparatus.

## S1 — broad discovery comparison

### Question

Can a broad proposal lane recover unambiguous composite structures that frozen V1 P1-P5 misses, without using gold at runtime?

### Arms

- A: exact frozen V1 P1-P5 candidate generation.
- B: structured LLM proposer. Pin provider/model/version/prompt/settings. Cache exact raw responses. Proposal only.
- C: structurally different syntax/SRL/semantic parser proposal lane where locally practical.
- D: union of A+B+C with duplicate semantic candidates normalized, no voting.

### Measure

- candidate recall against frozen gold;
- candidate semantic error taxonomy;
- operator/scope preservation;
- deterministic/replay behavior where the proposer allows determinism;
- model/prompt sensitivity as a mutation.

Do not tune an arm on the decisive set after results.

### Decision

Continue only with lanes that add real safe candidate recall. Proposal precision may be imperfect because authority is separate, but pathological overgeneration that defeats downstream discrimination is a negative result.

## S2 — authority-instrument qualification

### Question

Which independent measurements can discriminate correct structures from semantically wrong but fluent decompositions?

### Instruments

- exact current deterministic semantic-frame evaluator;
- current root-scope ambiguity detector;
- current surface-scope conservation instrument;
- learned NLI/alignment measurement in shadow;
- optional second LLM semantic critic with no access to proposer identity/output rationale, used only as measurement.

### Mutation suite

Starting from known-good structures create frozen hostile variants:

- drop one child;
- inject an unsupported child;
- swap subject/object or referents;
- remove or redistribute negation;
- remove/change modality;
- lose or overdistribute attribution;
- alter number, unit, threshold or date;
- lose temporal/jurisdictional qualifier;
- change `and` to `or` or flatten `or` to `all_of`;
- attach a shared modifier to only one child or vice versa;
- duplicate a child;
- paraphrase without semantic change.

Each instrument must be evaluated as a system under test. Do not promote a learned score because it correlates on average while missing hard semantic falsifiers.

## S3 — composed shadow authority

### Question

Can broad discovery plus qualified independent measurements produce the correct terminal distinction and structure?

### Required resolver behavior

- atomic and warranted -> `NOT_NEEDED` candidate;
- unique warranted `ALL_OF` -> `DECLARED` shadow candidate;
- materially competing structures -> `AMBIGUOUS`;
- determinate gold but no adequate candidate/analysis -> `COVERAGE_LIMITATION`;
- understood structure not expressible by released contract -> `REPRESENTATION_UNSUPPORTED`;
- apparatus failure -> `FAILED`.

Do not emit new production Contract A authority in this stage.

### Hard falsifiers

- any unsafe structure receives shadow authority;
- gold ambiguity is silently resolved;
- coverage failure is mislabeled atomic or ambiguous;
- unsupported operator is flattened to `all_of`;
- proposer ordering or duplicate proposal count changes authority;
- learned confidence/majority vote overrides a critical semantic objection.

## S4 — independent/context-free reproduction

Freeze exact code/model/prompt/config/corpus/evaluator identities and hand the packet to a separate executor with no development transcript.

Require fresh decisive cases and preserved deviations.

## S5 — naturalistic shadow qualification

Run a new deterministic naturalistic sample from intended CAL Pipeline inputs.

Report separately:

- prevalence by structure class;
- atomic coverage;
- composite discovery coverage;
- authoritative composite coverage;
- semantic ambiguity rate;
- coverage-limitation rate;
- representation-unsupported rate;
- unsafe-authority count;
- deterministic replay.

A naturalistic sample that happens to contain few composites is still useful prevalence evidence but cannot substitute for the targeted capability corpus.

## S6 — smallest justified promotion

Only after S0-S5 support one exact successor should the programme decide whether to:

- replace/extend the ClaimGate authoring implementation while keeping Contract A `all_of` only;
- add a separately versioned internal/output status distinction;
- propose a Contract A successor for additional operators.

Promotion must be the smallest change supported by the evidence.
