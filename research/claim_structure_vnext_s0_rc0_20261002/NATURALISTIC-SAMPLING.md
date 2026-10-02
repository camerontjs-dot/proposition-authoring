# S0 naturalistic prevalence sampling definition

Tracking: #60

This document freezes the sampling method only. It does not freeze a prevalence result.

## Question

When S5 runs, what proposition-structure classes occur in ordinary intended CAL Pipeline inputs, and how often does the exact qualified successor cover them safely?

This is a prevalence question, not a capability-balancing exercise.

## Population

Eligible population:

- real root claims presented for ClaimGate authoring in intended CAL Pipeline use;
- captured before any ClaimGate structure result is used for selection;
- exact root bytes and explicitly authorized context must be recoverable;
- source identity/custody must be sufficient to content-bind the case.

Exclude:

- synthetic/adversarial benchmark cases;
- cases created specifically for proposition-authoring development;
- replays/duplicates of the same exact root+context identity;
- cases selected because ClaimGate succeeded, failed or abstained;
- private cases whose bytes cannot remain under the required local custody boundary.

## Sampling window

At S5 preregistration time, freeze one contiguous intended-use window before reading Gate outcomes for that sample.

Default window candidate:

- most recent 30 calendar days ending before S5 protocol freeze.

If that window has fewer than the preregistered target population, extend backward contiguously rather than cherry-picking another source.

Any change to this default must be preregistered before the eligible pool is enumerated.

## Unit identity

Naturalistic sampling unit:

`sha256(source_namespace || NUL || source_item_id || NUL || root_bytes || NUL || authorized_context_bytes)`

Preserve exact root/context hashes separately.

## Deduplication

Deduplicate exact unit identities only before selection.

Do not semantically deduplicate paraphrases unless a separate preregistered rule exists. Paraphrase prevalence may itself be informative.

## Selector

Freeze the eligible pool first.

Default selector seed:

`claim-structure-vnext-naturalistic-s5::PROGRAM_HEAD::S0_FREEZE_SHA`

Replace the placeholders only with exact frozen identities when S5 is preregistered.

Rank each eligible unit by:

`sha256(seed || NUL || unit_id)`

Select ascending.

No stratification by ClaimGate result, semantic class, source type or expected authorability.

## Target size

Default target: 60 distinct eligible units.

If fewer than 60 eligible units exist in the frozen window, use the entire eligible population and report the smaller denominator.

Do not manufacture cases to reach 60.

## Annotation

Apply the frozen S0 annotation guide after selection.

Report prevalence on the selected naturalistic sample separately from targeted capability results.

If a class has low or zero prevalence, report that observation. Do not add cases to rebalance the sample.

## Non-response / exclusion

Cases excluded during blinded annotation must remain in the denominator accounting with an explicit exclusion reason.

Do not silently replace excluded cases with the next ranked unit unless the S5 preregistration explicitly defines replacement before selection.

Default: no replacement.

## Outcome separation

S5 must report at least:

- semantic class prevalence;
- annotation exclusion rate;
- atomic coverage;
- composite discovery coverage;
- composite authority coverage;
- semantic ambiguity rate;
- coverage-limitation rate;
- representation-unsupported rate;
- unsafe-authority count;
- runtime failure rate;
- replay/determinism behavior.

Capability conclusions remain anchored in the targeted corpus; prevalence conclusions remain anchored in this naturalistic sample.
