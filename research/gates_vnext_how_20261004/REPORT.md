# Deep research: how to build the ClaimGate + EvidenceGate north star

Date: 2026-10-04

Tracking: issue #69.

North-star authority: main `693888edbbfc32ddeb099f24c8545ff0962b6e28`.

## Executive conclusion

The strongest current architecture is **not** a larger regex system, a free-form LLM decomposer, or a full semantic parser acting as authority.

The most defensible build hypothesis is:

```
exact source text
    ↓
pinned linguistic observation layer
    ↓
source-anchored semantic intermediate representation
    ↓
deterministic proposition-structure compiler
    ↓
deterministic conservation / ambiguity / coverage checks
    ↓
ClaimGate authority

exact source universe
    ↓
content + representation + provenance manifests
    ↓
deterministic coverage / aperture declarations
    ↓
EvidenceGate

ClaimGate obligations + EvidenceGate declarations
    ↓
deterministic descriptive preflight
```

Learned NLP components may be useful in the **observation layer**, but they should not directly grant proposition authority. Every authoritative semantic object should be reproducible from typed observations and deterministic policy.

The first serious candidate should therefore be a **hybrid deterministic compiler**:

- Universal Dependencies / Enhanced UD as the main syntactic substrate;
- a compact ClaimGate semantic IR with predicate-role frames, operators, scope and source anchors;
- deterministic rules to compile observations into that IR;
- structural conservation instead of model entailment as the first authority check;
- explicit `AMBIGUOUS`, `COVERAGE_LIMITATION`, and `REPRESENTATION_UNSUPPORTED` states;
- EvidenceGate as a compact provenance/coverage manifest inspired by PROV/DCAT/Data Package patterns.

Do not start with AMR/UMR or an LLM as the production parser. Use them as research/reference lanes.

## 1. What downstream actually needs

### Evidence Bundler

Contract A already gives Evidence Bundler:

- exact root proposition identity/text;
- optional declared `all_of` children;
- source representations;
- exact lineage and integrity.

Evidence Bundler retrieves independently for declared children and must not invent proposition structure.

Therefore ClaimGate's output directly defines the **retrieval/audit units**.

### CAL

CAL's maintained architecture is already:

`retrieve -> entail -> deterministic rules`

and its public documentation explicitly says CAL answers whether supplied evidence carries the exact claim, not whether the claim is true in the world.

CAL research also names failures involving composition that CAL intentionally does not synthesize downstream.

Therefore upstream proposition structure should be complete enough that CAL evaluates propositions rather than simultaneously rewriting them.

### Decision

Decision consumes canonical epistemic state and policy context. It should never repair upstream claim structure or evidence-world boundaries.

## 2. Claim decomposition research

### Fine-grained verification is useful

FActScore evaluates long-form factuality by breaking outputs into atomic facts.

- https://aclanthology.org/2023.emnlp-main.741/

FactLens argues for fine-grained verification because holistic labels can hide nuanced errors and retrieval ambiguity.

- https://aclanthology.org/2025.findings-acl.929/

### But decomposition itself is difficult

CACDD provides expert-annotated atomic-claim decomposition data and reports that zero-shot, few-shot and fine-tuned LLM baselines still find the task challenging.

- https://arxiv.org/abs/2410.12558

Decomposition Dilemmas finds that decomposition can improve or degrade fact-checking and identifies decomposition-specific error families.

- https://aclanthology.org/2025.naacl-long.320/

### Context preservation is first-class

FactLens explicitly identifies context preservation and semantic equivalence as decomposition requirements.

DnDScore shows a direct tension: decomposition isolates facts while decontextualization adds context needed for verification, and strategy choice materially changes factuality results.

- https://aclanthology.org/2025.emnlp-main.1205/

**Implication:** ClaimGate should target **verification atoms**, not shortest possible propositions.

## 3. The semantic substrate

### Universal Dependencies is a strong baseline

UD provides a standardized dependency representation and active English treebanks.

Enhanced UD adds relations useful for our exact problem:

- conjunct propagation;
- controlled/raised subjects;
- elided predicates;
- relative-clause reference links;
- case/preposition information.

- https://universaldependencies.org/u/overview/enhanced-syntax.html
- https://universaldependencies.org/v2/enhanced.html

A 2021 study found that a small rule set over UD parses recovered 79.1% of argument-predicate pairs in a QA-SRL dataset. The remaining genuine errors largely required semantic reasoning rather than better dependency parsing.

- https://aclanthology.org/2021.law-1.5/

This makes UD an excellent **observation substrate**, but not a complete semantic representation.

### Enhanced UD is especially relevant to conjunction

Enhanced UD explicitly propagates shared subjects/objects and other dependencies across conjunctions.

Research on English enhanced UD shows why this matters and also shows hand-designed propagation rules have systematic errors.

- https://aclanthology.org/2021.eacl-main.67/

**Implication:** use enhanced dependency concepts, but qualify our exact propagation rules on ClaimGate-specific cases.

### Semantic-role labeling can add role structure

PropBank/SRL provides explicit predicate-argument roles and modifier roles such as temporal, locative, modal and negation.

A current implementation option is HanLP, which exposes English PropBank SRL, but its distributed model licensing is commonly CC BY-NC-SA even though the code is Apache-2.0. Treat it as a research lane unless model licensing is independently cleared.

- https://hanlp.hankcs.com/docs/annotations/srl/propbank.html
- https://github.com/hankcs/HanLP

**Implication:** first test whether UD/EUD is enough. Add SRL only where it measurably closes important role-binding gaps.

### OpenIE / MinIE offers a useful representation idea

MinIE separates compact fact extractions from semantic annotations such as:

- polarity;
- modality;
- attribution;
- quantities.

- https://aclanthology.org/D17-1278/

That decomposition is close to what ClaimGate needs internally even if MinIE itself is not the right production dependency.

## 4. Scope requires its own graph

Predicate-role structure alone is not enough.

UMR was motivated partly by AMR's gaps around:

- quantification;
- negation scope;
- modality.

UMR places the predicative core under an explicit scope graph.

- https://aclanthology.org/W19-3303/

Automatic UMR parsing is improving. SETUP (2025) reports strong sentence-level UMR parsing by fine-tuning AMR parsers and by leveraging a UD converter.

- https://arxiv.org/abs/2512.07068

But automatic UMR parsing is still a larger and less mature dependency than we need for the first ClaimGate successor.

**Recommendation:** borrow the scope model, not the whole stack.

## 5. Proposed ClaimGate IR: Audit Proposition Graph

The first research object should be a small, source-anchored semantic IR, tentatively:

`audit-proposition-graph-v0`

### Core node types

#### SourceAnchor

- start/end offsets;
- exact source text;
- source-text hash.

Every semantic object must be traceable to one or more anchors or an explicitly authorized context binding.

#### Entity / Referent

- referent id;
- source spans;
- resolution state;
- optional normalized identity.

Do not force coreference when unresolved.

#### PredicateFrame

- predicate id;
- predicate anchor;
- lemma/form;
- semantic roles;
- role anchors;
- voice/tense where relevant.

#### Proposition

- proposition id;
- predicate/frame references;
- attached qualifiers;
- attached operator/scope nodes.

#### Operator

Initial research vocabulary:

- `ALL_OF`
- `ANY_OF`
- `IF_THEN`
- `NEGATION`
- `MODAL`
- `ATTRIBUTION`

The first Contract-A-compatible authority experiment can remain `ALL_OF`-only.

#### Qualifier

At minimum:

- temporal;
- jurisdiction/location;
- quantity;
- unit;
- threshold;
- exception;
- condition.

#### ScopeEdge

Explicitly states which proposition(s) an operator/qualifier governs.

### Why source anchoring matters

The failed certificate/oracle experiments repeatedly exposed qualifier/role loss.

A source-anchored graph makes conservation mechanically testable:

- if a material anchor disappears, conservation fails;
- if a scope edge moves, conservation fails;
- if an operator changes `ANY_OF -> ALL_OF`, conservation fails;
- if an unanchored assertion appears, non-invention fails.

## 6. Deterministic authority by graph conservation

The key design opportunity is to stop proving decomposition correctness by asking another language model.

If root semantics is represented as a structured graph, decomposition can be treated as a **graph partition + inherited scope** problem.

For an `ALL_OF` decomposition:

1. build the root APG;
2. identify proposition subgraphs;
3. retain shared scope/qualifier nodes as inherited obligations;
4. construct child proposition objects from those subgraphs;
5. verify:
   - every required semantic node/edge in root is represented exactly once or explicitly shared;
   - no new semantic node/edge is introduced;
   - operator identity is unchanged;
   - role bindings are unchanged;
   - every material anchor remains accounted for;
6. canonicalize the reconstructed structure and compare it to the root APG.

This creates a deterministic conservation test.

### Rendered child text is a view, not the source of truth

Do not make semantic authority depend on a generated English rewrite.

The authoritative object should be the structured proposition + source/context bindings.

Child text can be a deterministic rendering required by today's Contract A.

Before promotion, optionally round-trip rendered text through the observation layer and require it to reproduce the intended proposition structure. A round-trip failure is a safe false negative.

## 7. Ambiguity vs coverage

The compiler should distinguish two cases that V1 can collapse:

### `AMBIGUOUS`

The observation/grammar supports multiple materially distinct structure graphs and authorized context does not select one.

Example: attribution or trailing-modifier attachment genuinely has two live readings.

### `COVERAGE_LIMITATION`

The construction is outside the qualified parser/compiler profile or required semantic information cannot be recovered.

Parser failure is not ambiguity.

### `REPRESENTATION_UNSUPPORTED`

The structure is understood but downstream Contract A cannot carry it.

Example: clear `ANY_OF` while Contract A remains `all_of`-only.

This distinction should exist internally before any contract widening.

## 8. Learned parsing and determinism

A learned dependency/SRL parser need not receive semantic authority.

It can be treated as a **frozen measurement instrument** producing typed observations.

For reproducibility:

- pin code/package version;
- pin model bytes/digest;
- run inference mode only;
- pin tokenizer/model configuration;
- prefer CPU for qualification;
- enable deterministic algorithms where the framework supports them;
- canonicalize observation output;
- record exact runtime/platform;
- run same-host byte replay and cross-host canonical-output conformance.

PyTorch explicitly supports deterministic-algorithm mode, but notes that reproducibility requires more than one flag and is defined relative to software/hardware conditions.

- https://docs.pytorch.org/docs/main/generated/torch.use_deterministic_algorithms.html

This means the production promise should be framed as **deterministic canonical Gate outcome under qualified pinned parser observations**, not as a magical guarantee that all floating-point internals are byte-identical on every architecture.

## 9. Practical parser candidates

### Stanza

Strengths:

- Python;
- Apache-2.0;
- Universal Dependencies output;
- actively maintained;
- straightforward pinning.

- https://stanfordnlp.github.io/stanza/depparse.html
- https://github.com/stanfordnlp/stanza

Recommended first parser candidate.

### Stanford CoreNLP

Strengths:

- current 4.6.0 release;
- direct enhanced dependency support;
- mature English NLP stack;
- dependency graph pattern machinery.

Risks:

- Java dependency;
- GPL/commercial licensing concerns for some distribution scenarios.

Useful research comparator, not the default first production dependency.

- https://stanfordnlp.github.io/CoreNLP/download.html

### spaCy

Strengths:

- MIT;
- mature Python packaging;
- dependency matcher supports rule patterns over parser outputs;
- easy to pin pipeline packages.

Risks:

- English parser labels/representation are not a clean drop-in for standardized UD/EUD semantics.

Useful rule-engine/prototyping option.

### Full AMR/UMR

Useful as a research comparator/reference representation.

Not recommended as first authority dependency because parser complexity and error surface are larger than the minimal ClaimGate need.

### Formal theorem proving

LangPro demonstrates transparent natural-language entailment using CCG-derived logical forms and tableau proof.

- https://aclanthology.org/D17-2020/

This may be valuable as an independent verifier on bounded constructions, but is too narrow/complex as the primary ClaimGate parser.

## 10. EvidenceGate architecture

EvidenceGate should not become a source-quality scorer.

The strongest design is a compact, content-bound manifest with three layers.

### A. Representation identity

For each representation:

- source id;
- representation id;
- exact media type;
- encoding;
- exact content hash;
- exact bytes/text identity;
- extraction/transformation id.

### B. Provenance graph

Use a compact subset inspired by W3C PROV:

- entity;
- activity;
- agent;
- used;
- generated;
- derived-from;
- attribution/role.

PROV explicitly separates entities, activities and agents.

- https://www.w3.org/TR/prov-primer/

Do not adopt RDF/PROV wholesale unless interoperability requires it. Preserve easy mapping.

### C. Dataset/corpus applicability metadata

DCAT provides useful vocabulary for:

- distributions/representations;
- temporal coverage;
- spatial coverage;
- version relationships;
- status.

- https://www.w3.org/TR/vocab-dcat-3/

DQV makes an important architectural point: quality metadata should enable consumers to judge fitness for purpose; the vocabulary does not itself define one universal quality truth.

- https://www.w3.org/TR/vocab-dqv/

That matches EvidenceGate's authority boundary.

### Packaging patterns

Frictionless Data Package and RO-Crate are useful references for portable manifests.

- https://specs.frictionlessdata.io/data-package/
- https://www.researchobject.org/ro-crate/specification

ClaimGate/EvidenceGate probably need a much smaller contract.

## 11. EvidenceGate fields to prioritize

### Tier 0: must-have identity

- source id;
- representation id;
- content hash;
- media type/encoding;
- exact transformation lineage;
- corpus membership;
- explicit unknowns.

### Tier 1: likely useful descriptive metadata

- issuer/origin;
- source role;
- document/evidence form;
- temporal coverage;
- jurisdiction/spatial coverage;
- version/revision;
- supersession relation when explicitly established;
- corpus aperture/scope;
- completeness declaration;
- known gaps.

### Tier 2: do not promote without dedicated evidence

- source trust/reliability score;
- claim relevance;
- expected evidence form inferred from semantics;
- source sufficiency;
- conflict/contradiction inferred from source text.

Research on reliability-aware RAG shows source reliability can matter, but that is evidence that a later reliability mechanism may be useful, not evidence that EvidenceGate should infer truth.

- https://aclanthology.org/2025.emnlp-main.1738/

## 12. Deterministic joint preflight

Preflight should operate only on explicit/qualified fields.

Inputs:

- ClaimGate proposition obligations;
- EvidenceGate corpus/source declarations;
- optionally a separately governed verification policy.

First dimensions worth testing:

- temporal scope vs temporal coverage;
- jurisdiction vs jurisdictional coverage;
- representation compatibility;
- version/currency compatibility;
- corpus aperture/completeness for absence/exhaustive claims;
- known gaps.

Outputs:

- `MATCH`
- `PARTIAL`
- `MISMATCH`
- `UNKNOWN`
- `NOT_APPLICABLE`

### Why this is justified

RAG research shows that:

- metadata can materially improve retrieval in structured corpora;
- out-of-scope or stale knowledge bases cause answer failures;
- systems are poor at deflecting when grounding is insufficient.

Relevant work:

- AMAQA: https://arxiv.org/abs/2505.13557
- metadata-aware RAG study: https://arxiv.org/abs/2601.11863
- GaRAGe: https://aclanthology.org/2025.findings-acl.875/
- UAEval4RAG: https://aclanthology.org/2025.acl-long.415/
- query/knowledge scope relevance: https://aclanthology.org/2024.emnlp-main.353/

These findings support **measuring the boundary**, not moving support/refutation into preflight.

## 13. Architecture alternatives

| Candidate | Coverage potential | Determinism / inspectability | Scope fidelity | Dependency cost | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Extend V1 regex/proposers | low-medium | very high | low-medium | low | weak baseline only |
| UD/EUD + deterministic APG compiler | medium-high | high | medium | low-medium | **first serious candidate** |
| UD/EUD + SRL + deterministic APG | high | high if pinned | medium-high | medium | second arm if UD gaps matter |
| AMR/UMR parser + policy | high | medium | high | high | research comparator |
| LLM structure proposer + checks | high | low-medium | variable | medium-high | counterexample/proposal arm only |
| CCG/formal theorem proving | bounded | very high proof transparency | high on supported fragment | high | verifier lane, not primary |

## 14. Recommended implementation research sequence

Do not build vNext all at once.

### R0 — operator/prevalence census

Use intended CAL Pipeline claims and classify only surface/externally inspectable structure:

- atomic;
- conjunction/all_of candidate;
- disjunction;
- conditional;
- attribution;
- negation/modality;
- temporal/jurisdictional scope;
- other/unknown.

Purpose: determine what structure actually matters.

No Gate output used to define prevalence.

### R1 — APG representation qualification

Implement only the APG schema and hand-authored/publicly annotated fixtures.

Test whether it can losslessly represent the required families.

No automatic parser.

### R2 — UD/EUD observation baseline

Pin one parser and extract canonical linguistic observations.

Build deterministic rules for:

- predicate frames;
- conjunct propagation;
- controlled subjects;
- negation;
- modality;
- attribution complements;
- temporal/location modifiers;
- explicit conjunction/disjunction;
- quantities/bounds.

Measure against R1 fixtures.

### R3 — SRL incremental value

Only if R2 has role-binding gaps, add a frozen SRL lane in shadow.

Question: does it close important gaps that UD/EUD cannot, without increasing unsafe authority?

### R4 — scope compiler

Build explicit scope graphs and ambiguity enumeration.

Target predecessor failure families first:

- attribution scope;
- trailing/shared modifiers;
- negation scope;
- modality;
- coordination.

### R5 — deterministic structure/decomposition

Compile APG into verification atoms.

Use graph partition/recomposition for conservation.

No LLM entailer.

### R6 — child rendering

Render Contract-A-compatible child text for `ALL_OF`.

Require source/context traceability and optional deterministic round-trip checks.

### R7 — EvidenceGate vNext manifest

Implement representation/provenance/coverage manifest independently of ClaimGate semantics.

### R8 — deterministic preflight

Start with one or two highly inspectable dimensions such as representation readiness and explicit jurisdiction/temporal mismatch.

### R9 — end-to-end shadow

Run real claims through:

ClaimGate APG -> Contract-A-compatible subset -> Evidence Bundler -> CAL

Measure whether upstream structure reduces known downstream composition/coverage failure families without semantic leakage.

## 15. What would falsify the leading architecture

Reconsider the APG compiler approach if:

- intended claims regularly require semantic distinctions that cannot be represented compactly without recreating full formal semantics;
- pinned UD/EUD observations are too unstable or wrong on the dominant claim families;
- deterministic scope rules require endless sentence-specific patches rather than reusable abstractions;
- structural conservation accepts materially wrong decompositions or rejects routine paraphrase/rendering too often;
- a learned parser's observation errors routinely acquire false authority despite coverage guards;
- EvidenceGate metadata cannot be recovered reliably enough to support even descriptive preflight;
- useful downstream gains require letting retrieval/CAL results choose upstream proposition structure.

## Recommendation

Start with **R0 + R1 + R2 only**.

The highest-value discriminating question is:

> Can a compact source-anchored proposition graph plus pinned UD/EUD observations deterministically recover the semantic obligations of the claim families the CAL Pipeline actually sees?

If yes, the rest of the architecture becomes incremental.

If no, we will know exactly whether the missing information is roles, scope, coreference or a genuinely richer semantic representation before adopting SRL/UMR/LLMs.
