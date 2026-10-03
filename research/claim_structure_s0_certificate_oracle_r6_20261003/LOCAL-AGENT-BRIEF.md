# Local agent brief — S0-R6 source-bound certificate qualification

Act as the local research and qualification owner for issue #63.

## Authority

Inspect live GitHub first.

Repository:

`camerontjs-dot/proposition-authoring`

Frozen predecessor:

- Draft PR #62
- commit `45607c923d03c36299f0a6cea29be287d538fcff`
- disposition `FALSIFIED_EVALUATION_SURFACE`

Successor issue:

`#63 — S0 successor: qualify source-bound scope/obligation certificates`

Read this directory completely before execution.

Frozen V1 remains unchanged at:

`89ca88c7f0a661601f7eb798b6759667fa20ab3f`

## Objective

Determine whether a source-bound semantic certificate protocol can become a qualified S0 evaluation surface.

Do not retry the R1-R5 raw-model oracle.

Do not begin S1 proposer comparison until this stage reaches a positive terminal disposition.

## First: source fresh public minimal pairs

Find fresh public/published examples with inspectable semantic analysis.

Prefer:

- public annotated corpora;
- papers with explicit scope/role examples;
- linguistic minimal pairs whose stated analysis is part of the publication;
- mechanically indisputable positive controls from public text.

Prioritize the semantic families in the preregistration.

Capture exact source locator, source bytes where allowed, hash, and location/page/example number.

Do not rely on remembered examples.

## Build certificates

For each candidate example create a certificate under the frozen schema.

Every certificate must include:

- exact root bytes/hash;
- predicate spans;
- explicit role bindings;
- operator;
- scope bindings;
- propositions/readings;
- obligations;
- material-span completeness ledger;
- external analysis basis.

For ambiguity, represent every materially live externally supported reading. Do not ask the model to pick one.

Drafting may use scripts or models, but drafts have zero authority.

## Implement mechanical validation

Build the smallest validator that can check at least:

- schema validity;
- root/content hashes;
- span offsets reproduce exact text;
- referenced predicate/role/obligation/readings exist;
- completeness flags are internally consistent;
- `unassigned_material_spans` must be empty for an admitted complete certificate;
- operator/readings/classification combinations are coherent;
- all material object references resolve.

Mechanical validity is necessary but not semantic sufficiency.

## Reviewer calibration

Before decisive review, freeze a calibration set made from known-good certificates plus hostile mutations.

A reviewer profile must reject all hard calibration mutations before it can review decisive cases.

Preserve exact provider/model/runtime/prompt/config identities.

Do not describe two runs of the same correlated mechanism as independent without qualification.

If no eligible review path is available, return `BLOCKED_CERTIFICATE_SURFACE` rather than pretending model agreement is gold.

## Independent review

Use at least two eligible independent review executions.

Give them only:

- exact source/root;
- external analysis basis;
- frozen certificate;
- certificate schema/checklist.

Do not reveal prior review outputs or future ClaimGate outputs.

Record every objection.

No majority vote.

Material disagreement requires explicit adjudication tied to inspectable source/analysis evidence. If it cannot be resolved, mark the case inconclusive and do not admit it.

## Hostile mutation qualification

For each admitted certificate generate applicable hostile variants from the preregistered mutation list.

The protocol must reject every hard mutation.

Pay special attention to the predecessor failure families:

- Ontario/location scope dropped;
- local-only reading omitted;
- predicate subject lost;
- `or` converted to `and`;
- ambiguity silently collapsed.

## Continue-until rule

Continue through routine certificate design, validators, reviewer calibration, fresh public sourcing, successor packet freezes and qualification runs without asking the operator for routine implementation choices.

A failed certificate/protocol attempt is evidence. Preserve it, freeze a smaller successor hypothesis if justified, and continue.

Stop only when:

1. `SUPPORTED_CERTIFICATE_SURFACE_FOR_S0_PACKET`;
2. `FALSIFIED_CERTIFICATE_SURFACE` with no smaller successor justified inside issue #63;
3. `INCONCLUSIVE_CERTIFICATE_SURFACE` because evidence cannot discriminate;
4. `BLOCKED_CERTIFICATE_SURFACE` because a genuinely required external authority/reviewer is unavailable;
5. the next step would require changing frozen V1, Contract A, product responsibility, or a production dependency.

## Git/evidence discipline

Use Draft Research PRs/evidence comments.

For every successor freeze exact:

- question;
- source corpus;
- certificates;
- schema;
- validator;
- mutation generator;
- review prompts/checklists;
- reviewer identities/config;
- expected controls;
- falsifiers;
- commit/tree/blob/hash identities.

Never repair a frozen decisive certificate after review.

## Terminal return

Return:

- exact branch/commit/tree;
- terminal disposition;
- corpus count and source families;
- certificate schema/validator identities;
- certificate hashes;
- reviewer calibration results;
- reviewer identities/config;
- per-certificate review/adjudication;
- hostile mutation results;
- all preserved failures;
- whether every material predicate/role/operator/qualifier/live reading was accounted for;
- evidence record/PR;
- observed evidence;
- bounded inference;
- remaining live alternatives;
- smallest justified next action.

Do not proceed to S1 unless the certificate surface is positively qualified.
