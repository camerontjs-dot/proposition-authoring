# S0 targeted corpus contract

Tracking: #60

## Purpose

Freeze a capability-discriminating set of pre-existing/public claims before S1 proposer execution.

The targeted corpus is not a prevalence sample.

## Source requirements

Every decisive case must be traceable to a pre-existing public source or another independently pre-existing source permitted by project privacy rules.

Synthetic text is not allowed as a decisive targeted case.

Synthetic text belongs only in the mutation/metamorphic control set.

Do not source cases from:

- ClaimGate output;
- V1 failure lists selected because of their observed result;
- a proposer/verifier run under this programme;
- generated examples authored to make one implementation pass.

## Required source manifest fields

Each case must preserve:

- case_id;
- source_namespace;
- source_locator;
- source_item_id/version/commit when available;
- source_observed_at;
- exact root text;
- exact root sha256;
- authorized context or explicit empty context;
- context sha256;
- source class;
- whether public bytes may be reproduced in-repo;
- custody note if exact bytes remain local-only.

## Capability design

Before labels are exposed to any S1 implementation agent, freeze intended minimum coverage across:

- ATOMIC;
- ALL_OF;
- AMBIGUOUS;
- ANY_OF;
- IF_THEN;
- scope/qualifier/reference difficulty;
- realistic wording variation.

Aim for at least four independently sourced cases in each of ATOMIC, ALL_OF, AMBIGUOUS, ANY_OF and IF_THEN after blind adjudication, but do not relabel or cherry-pick cases after review merely to hit quotas.

If a class misses the intended minimum after blind review, record the shortfall and either:

1. stop S0 as insufficient; or
2. preregister a fresh additional source-acquisition tranche before any S1 output is observed.

Do not silently top up after S1 exposure.

## Acquisition strata

Source acquisition should intentionally sample structurally diverse public prose without using Gate behavior:

- government/regulatory factual prose;
- software/project issue prose;
- technical documentation;
- research/benchmark prose;
- operational incident/status prose.

No one source family should dominate the entire targeted set.

## Minimal contrasts

The corpus should include naturally occurring pairs or near-pairs where possible, but each member must be a pre-existing source claim.

Synthetic operator swaps, qualifier drops and scope changes belong in the mutation suite, not the decisive public corpus.

## Isolation

Corpus acquisition role may see source metadata and the annotation guide.

Blind reviewers may see exact root/context/source provenance but not acquisition intent labels such as 'candidate ambiguous' or 'candidate all_of'.

S1 implementation/execution roles receive corpus inputs but not adjudicated gold until raw proposer outputs are frozen.
