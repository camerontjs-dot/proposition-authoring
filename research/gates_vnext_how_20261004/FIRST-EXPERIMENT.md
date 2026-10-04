# Recommended first experiment: APG + UD/EUD feasibility

Tracking: issue #69.

## Question

Can a compact source-anchored Audit Proposition Graph (APG) plus pinned Universal Dependencies observations recover enough proposition structure for the actual CAL Pipeline claim domain to justify deeper implementation?

## Why this experiment first

It directly discriminates between two explanations of V1's coverage problem:

1. V1 is mainly limited because it discovers structure from brittle surface patterns;
2. the intended claim domain genuinely requires richer semantic machinery than syntax + bounded scope rules.

Do not add SRL, AMR/UMR, an LLM proposer, or an NLI verifier until this question is answered.

## Stage A — claim-domain census

Freeze a claim corpus from intended pipeline inputs before running any new parser.

Target 100–200 roots if available.

Classify only observable structural families, not expected Gate output:

- apparent atomic;
- coordination/conjunction;
- disjunction/alternative;
- conditional/exception;
- attribution/reporting;
- negation;
- modality;
- comparison/quantity;
- temporal;
- jurisdiction/location;
- reference/coreference;
- structurally unclear.

Multi-label is allowed.

This is prevalence evidence, not semantic gold.

## Stage B — APG representational fixtures

Create a separate small decisive fixture set from:

- published UD/SRL/scope examples;
- existing public ClaimGate adversarial cases;
- mechanically unambiguous constructed controls.

Hand-author APG objects before automatic extraction.

Include minimal pairs where one edge/operator/qualifier changes.

Freeze before parser execution.

## Stage C — pinned parser bakeoff

At minimum compare:

- Stanza English UD parser;
- one alternative parser/representation as a weak control where practical.

Run:

- exact same input twice;
- clean environment;
- pinned package/model hashes;
- CPU;
- deterministic framework settings where supported.

Record canonical parse output identity.

Do not compare downstream ClaimGate accuracy yet.

## Stage D — deterministic compiler v0

Implement only enough APG rules for the decisive fixtures:

- predicates;
- nsubj/obj/obl roles;
- explicit conjunction/disjunction;
- propagated conjunct subject/object;
- xcomp/control subject;
- ccomp attribution;
- negation;
- modals;
- temporal/location obliques;
- quantities/thresholds.

Every semantic node/edge must carry source spans.

Unknown/unsupported constructions remain `COVERAGE_LIMITATION`.

## Stage E — scoring

Measure separately:

- predicate recovery;
- required role recovery;
- operator recovery;
- qualifier recovery;
- scope attachment;
- false semantic nodes;
- unaccounted material spans;
- exact canonical replay.

Do not collapse into one accuracy number.

## Hard falsifiers

- `or` compiled as `all_of`;
- material negation/modality/attribution disappears;
- subject/object role is silently lost or swapped;
- qualifier attachment is silently broadened/narrowed;
- atomic root is split into materially different propositions;
- composite root is declared atomic because parser failed;
- unsupported construction is mislabeled semantic ambiguity;
- same pinned parser/runtime/input changes canonical observation bytes.

## Positive boundary

A positive result authorizes only R3/R4 work on role/scope coverage.

It does not authorize Contract A changes or a production ClaimGate successor.
