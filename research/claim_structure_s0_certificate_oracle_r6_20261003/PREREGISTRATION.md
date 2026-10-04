# S0-R6 preregistration — source-bound certificate qualification

## Frozen predecessor

Draft PR #62 publication commit:

`45607c923d03c36299f0a6cea29be287d538fcff`

Predecessor disposition:

`FALSIFIED_EVALUATION_SURFACE`

Do not modify predecessor objects.

## Research question

Can explicit source-bound scope/obligation certificates, independently reviewed for role/scope/completeness, support a reliable S0 evaluation packet where free-form local model oracle classification failed?

## Scientific subject

The subject is the **certificate protocol**, not a ClaimGate implementation and not any proposer/model.

The decisive protocol version must freeze:

- `CERTIFICATE-SCHEMA.json`;
- annotation instructions;
- review checklist;
- reviewer calibration set;
- certificate validator;
- hostile certificate-mutation generator;
- fresh public/published minimal-pair corpus;
- analysis-basis citations/locators;
- reviewer profiles/identities available to the executor;
- disposition rules.

## Fresh corpus requirement

Use fresh public examples not present in R1-R5 decisive controls.

Prefer examples whose semantics are externally inspectable through:

- published linguistic annotation;
- published semantic analysis;
- public annotated corpora;
- explicit source wording that makes the intended reading mechanically indisputable for a positive control.

Do not invent ambiguous gold from model intuition.

Synthetic examples may be used as labeled calibration/mutation controls only.

## Minimum semantic families

The decisive packet must include at least:

- 2 atomic controls;
- 2 unambiguous `ALL_OF` controls;
- 2 conjunction/disjunction contrasts;
- 2 attribution-scope cases;
- 2 negation-scope cases;
- 2 temporal/location shared-vs-local scope cases;
- 2 modality/condition cases;
- 2 genuinely ambiguous cases with externally supported multiple readings.

A single example may cover more than one family, but report that explicitly.

## Certificate generation

Certificate construction may use deterministic tooling or a model as a drafting aid, but drafting is non-authoritative.

Before decisive review, each certificate is frozen with:

- root/source identity;
- predicates/roles;
- readings;
- scope bindings;
- obligations;
- completeness ledger;
- external analysis basis.

Do not edit a decisive certificate after reviewer exposure. A defect starts a new successor certificate identity.

## Reviewer calibration

Each reviewer profile must first classify a frozen hostile calibration set.

Hard failures include accepting:

- dropped subject/object;
- dropped qualifier;
- negation loss;
- attribution moved to the wrong child;
- `or` changed to `and`;
- invented proposition.

A reviewer profile that fails a hard calibration case is not eligible for decisive review.

## Decisive review

Use at least two independently executed eligible reviewers.

They verify the certificate; they do not freehand the oracle.

All material objections are preserved.

If reviewers disagree materially, adjudication must cite inspectable external/source evidence and answer each objection. Otherwise the case remains inconclusive and is not admitted as decisive gold.

## Hostile certificate mutations

For admitted certificates, create frozen mutated copies that:

- delete one predicate;
- delete one role binding;
- delete one qualifier;
- reattach a qualifier;
- reattach attribution;
- drop negation;
- change modality;
- change `ALL_OF` to `ANY_OF` or vice versa;
- remove one live ambiguous reading;
- inject a new proposition;
- alter a source span so it no longer reconstructs the represented obligation.

The certificate protocol must reject every applicable hard mutation.

## Hard falsifiers

The protocol is falsified if any decisive admitted certificate:

1. omits a material predicate, role, operator, qualifier or externally supported live reading;
2. contains an invented material assertion;
3. admits a hostile mutation above;
4. allows `or`→`and` without rejection;
5. allows predicate subject/object loss without rejection;
6. treats reviewer/model agreement as sufficient authority;
7. relies on hidden conversation memory;
8. cannot trace a material semantic obligation to exact source bytes/spans and analysis basis;
9. claims completeness while the material-span ledger contains unresolved/unassigned material content.

## Allowed terminal dispositions

- `SUPPORTED_CERTIFICATE_SURFACE_FOR_S0_PACKET`
- `FALSIFIED_CERTIFICATE_SURFACE`
- `INCONCLUSIVE_CERTIFICATE_SURFACE`
- `BLOCKED_CERTIFICATE_SURFACE`

## Positive boundary

A positive result authorizes only creation of a new targeted S0 evaluation packet and later S1/S2 testing against that packet.

It does not qualify:

- a proposer;
- an LLM;
- an NLI model;
- a verifier;
- a resolver;
- a production ClaimGate successor;
- Contract A changes.
