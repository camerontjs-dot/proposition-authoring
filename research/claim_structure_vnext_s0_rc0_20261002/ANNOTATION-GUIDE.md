# S0 annotation guide — proposition structure

Tracking: #60

This guide defines the semantic gold task for S0. It is not a ClaimGate runtime contract and does not change Contract A.

## Reviewer aperture

Reviewers receive only:

- exact root claim bytes;
- explicitly authorized context bytes;
- source identity/provenance supplied with the case;
- this guide.

Reviewers must not inspect:

- ClaimGate output;
- proposer output;
- current V1 code behavior for the case;
- model confidence/rationale;
- Evidence Bundler, CAL, Decision or downstream outcomes.

## Unit of judgment

Judge the proposition structure asserted by the exact root under the authorized context.

Preserve every material:

- operator;
- qualifier;
- scope;
- reference;
- negation;
- attribution;
- quantity;
- unit;
- threshold;
- temporal constraint;
- jurisdictional constraint;
- modality;
- causal/comparative relation;
- subject/object role.

Surface brevity is not evidence of atomicity.

## Labels

### ATOMIC

The root asserts one independently verifiable proposition after all material qualifiers and scope obligations are preserved.

A sentence may contain several noun phrases, adjectives or subordinate descriptive material and still be ATOMIC if those elements belong to one proposition rather than separately asserted proposition leaves.

### ALL_OF

The root unambiguously asserts two or more independently verifiable propositions and warrants them conjunctively.

The gold representation must list the proposition leaves required to preserve the root's material meaning.

Shared attribution, negation, modality, temporal scope, jurisdiction, thresholds and modifiers must remain attached to every leaf they semantically govern.

### ANY_OF

The root unambiguously expresses alternatives/disjunction among proposition structures.

Do not flatten ANY_OF to ALL_OF because current Contract A cannot express it.

### IF_THEN

The root unambiguously asserts a conditional relation.

The gold must identify antecedent and consequent at proposition level.

A conditional is not equivalent to asserting both antecedent and consequent as unconditional ALL_OF leaves.

### SCOPED

Use only when the proposition structure requires an explicit scope wrapper whose semantics cannot be represented faithfully by simply attaching text qualifiers to each leaf.

Examples may include shared attribution, sentential negation or modality whose scope is itself part of the proposition structure.

Do not use SCOPED merely because a sentence contains a reporting verb or modifier.

### OTHER

The structure is determinate enough to distinguish from ambiguity, but it does not fit the frozen S0 operator vocabulary.

Record the smallest descriptive structure possible without inventing a new authority vocabulary during adjudication.

### AMBIGUOUS

Two or more materially distinct semantic structures remain live from the exact root plus authorized context, and choosing among them would change proposition-level meaning.

AMBIGUOUS is about the source semantics.

Do not use AMBIGUOUS when:

- a reviewer is merely unsure;
- the sentence is difficult;
- current ClaimGate cannot parse it;
- Contract A cannot represent it;
- a proposer failed to generate it.

### EXCLUDE_INSUFFICIENT_ADJUDICATION

Use when the case cannot support reliable semantic gold under the frozen reviewer aperture.

Examples:

- required context is absent or unauthorized;
- source text is corrupt/incomplete;
- the claim depends on domain conventions the review protocol cannot establish;
- independent reviewers identify a material disagreement that cannot be adjudicated from the allowed evidence.

This is an evaluation-surface exclusion, not a semantic AMBIGUOUS label.

## Required gold fields

Each reviewer record must contain:

- case_id;
- reviewer_id;
- root_sha256;
- context_sha256;
- label;
- operator if applicable;
- ordered or canonically normalized proposition leaves if applicable;
- scoped obligations;
- material qualifiers;
- unresolved alternatives for AMBIGUOUS;
- representation notes;
- short basis;
- confidence as reviewer metadata only.

Reviewer confidence is never runtime authority.

## Proposition leaves

A leaf must be independently evaluable as a proposition in the authorized context.

Leaves must collectively satisfy:

1. propositionhood;
2. completeness;
3. non-invention;
4. operator preservation;
5. role/reference preservation;
6. qualifier preservation;
7. reconstructability under the declared structure.

## Materiality test

A difference is material when changing or dropping it could change whether downstream evidence supports/refutes the proposition or could change the real-world state asserted.

Examples usually material:

- who did what to whom;
- negation;
- attribution;
- modal force;
- amount/unit/threshold;
- date/time window;
- jurisdiction;
- comparative direction;
- causal direction;
- operator choice.

Pure punctuation, harmless paraphrase and non-semantic formatting are not material.

## Reviewer disagreement protocol

Reviewers label independently first.

Do not allow reviewer B to see reviewer A's label before B freezes a first-pass record.

Preserve both first-pass records.

Adjudication may consult:

- exact source bytes;
- authorized context;
- this guide;
- reviewer written bases.

Adjudication may not consult ClaimGate/proposer/verifier/downstream outputs.

Record one of:

- AGREED_FIRST_PASS;
- ADJUDICATED_WITH_REASON;
- UNRESOLVED_EXCLUDE.

Never overwrite the raw labels.

## Minimal-pair handling

Pairs may be grouped for analysis only after each member is independently labeled.

A reviewer must not infer one member's label solely from the intended contrast with another member.

## Separation from runtime terminal states

These are not S0 semantic gold labels:

- COVERAGE_LIMITATION;
- REPRESENTATION_UNSUPPORTED;
- FAILED.

Those are observations about a system under test after semantic gold is frozen.

A determinate ANY_OF or IF_THEN case can later produce REPRESENTATION_UNSUPPORTED under released Contract A, but its S0 gold remains ANY_OF or IF_THEN.
