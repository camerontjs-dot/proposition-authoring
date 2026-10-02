# External research synthesis

Date: 2026-10-02.

Purpose: identify mechanisms worth testing for broad proposition-structure discovery while preserving ClaimGate's existing authority discipline.

## 1. LLM atomic-claim decomposition is established practice, but it is not self-validating

FActScore popularized decomposing long-form text into atomic facts before verification. Later systems such as VeriScore, FactSearch, VISTA and related factuality pipelines likewise use claim-level decomposition as an explicit stage.

Sources:

- FActScore: https://arxiv.org/abs/2305.14251
- VeriScore: https://aclanthology.org/2024.findings-emnlp.552/
- FactSearch: https://aclanthology.org/2026.acl-demo.36/
- VISTA: https://aclanthology.org/2026.acl-long.1890/

Implication for ClaimGate: a learned/LLM proposer is a reasonable way to increase discovery coverage, but the proposal itself should remain non-authoritative.

## 2. Claim decomposition itself is hard

The CACDD claim-decomposition benchmark reports that identifying atomic/checkworthy claims remains challenging even for zero-shot, few-shot and fine-tuned LLM baselines.

Source: https://arxiv.org/abs/2410.12558

FactLens emphasizes two requirements directly relevant here: subclaims must preserve context and remain semantically equivalent to the original complex claim.

Source: https://aclanthology.org/2025.findings-acl.929/

Implication: evaluate discovery recall separately from semantic preservation. Do not infer correctness from fluency or apparent atomicity.

## 3. Decomposition can create new errors

`Decomposition Dilemmas` finds that decomposition can improve or hurt fact-checking because splitting introduces noise and characteristic decomposition errors.

Source: https://aclanthology.org/2025.naacl-long.320/

DnDScore shows a specific tension between decomposition and decontextualization: isolated atomicity can remove context needed for verification, while adding context can itself make a subclaim non-atomic.

Source: https://aclanthology.org/2025.emnlp-main.1205/

Implication: ClaimGate must preserve attribution, negation, modality, temporal/jurisdictional qualifiers, reference, shared modifiers and other scoped obligations. 'Shorter' is not equivalent to 'better decomposed.'

## 4. Optimizing decomposition for a verifier can improve performance, but creates a governance hazard here

Dynamic-decomposition work shows that decomposition policy and verifier behavior interact, and that optimizing decomposition against the downstream verifier can improve verification performance.

Sources:

- https://aclanthology.org/2025.acl-long.254/
- EACL 2026 findings volume: https://aclanthology.org/volumes/2026.findings-eacl/

For CAL Pipeline this is a useful research result but **not an authority design**. Evidence Bundler/CAL success must not become the target signal that selects proposition structure, because that would let downstream behavior rewrite upstream semantics.

Implication: verifier-aligned optimization may be tested only as a weak/control or proposal-quality experiment, never as semantic authority.

## 5. Semantic role and graph parsing provide useful independent structure, but no single formalism solves the problem

PropBank-style semantic role labeling represents predicate-argument structure and is useful for identifying events/relations and their roles.

Sources:

- https://aclanthology.org/L10-1040/
- https://aclanthology.org/2022.lrec-1.181/

AMR provides graph-structured semantic content including roles, coreference and negation, and can abstract over surface form.

Source: https://aclanthology.org/P17-1043/

But AMR has known scope limitations, especially around negation/quantification/modality. Work on UMR and logico-semantic graphs explicitly adds scope machinery.

Sources:

- https://aclanthology.org/W19-3303/
- https://aclanthology.org/2021.law-1.3/
- https://aclanthology.org/2020.acl-main.605/

Out-of-the-box LLMs are also unreliable as exact AMR annotators, despite capturing useful core event/argument information.

Source: https://aclanthology.org/2023.findings-emnlp.553/

Implication: syntax/SRL/AMR-like analysis is valuable as an independent proposal or measurement lane, but should not be treated as a complete semantic oracle.

## 6. Learned entailment/alignment is a plausible independent semantic measurement

AlignScore trains a general information-alignment function across NLI, QA, paraphrasing, fact verification, retrieval, semantic similarity and summarization, and reports strong cross-task factual-consistency performance.

Source: https://aclanthology.org/2023.acl-long.634/

MiniCheck shows that relatively small learned fact-checking models can achieve strong grounding judgments using purpose-built synthetic training.

Source: https://arxiv.org/abs/2404.10774

However, NLI-based factuality work shows that decomposition granularity and retained context materially affect scores.

Source: https://aclanthology.org/2022.gem-1.7/

Implication: test bidirectional semantic alignment as an **instrument under test**:

- root -> each asserted child under the declared operator;
- structured children -> root;
- hard negative mutations for dropped qualifiers, role swaps, negation, modality, numbers, dates, attribution and injected facts.

Do not grant authority from one model score or threshold until the instrument survives its own qualification.

## 7. Recommended research architecture

The strongest transfer is a hybrid:

### Discovery

- preserve current P1-P5 as frozen baseline;
- add one broad structured LLM proposer with fully recorded model/prompt/settings and frozen outputs;
- add one structurally different syntax/SRL/semantic lane if practical;
- pool candidates without voting.

### Intermediate proposition structure

Represent operator and scope explicitly before translating to Contract A. At minimum distinguish:

- atomic;
- `all_of` conjunction;
- disjunction/alternatives;
- conditional structure;
- scoped attribution/negation/modality/qualifiers;
- semantic ambiguity;
- implementation coverage limitation;
- representation unsupported.

### Authority

- existing deterministic frame/binding checks;
- existing root-scope veto and conservation checks;
- learned entailment/alignment only as a shadow instrument first;
- mutation/metamorphic discrimination;
- no majority vote and no model confidence as authority;
- unique warranted semantic structure required for authoritative output.

## 8. Smallest discriminating next test

Do not immediately build a production LLM decomposer.

First freeze a targeted evaluation set with:

- unambiguous atomic roots;
- unambiguous real `all_of` composites across diverse wording;
- materially ambiguous minimal pairs;
- non-`all_of` composites that current Contract A cannot represent;
- adversarial mutations of known-good decompositions.

Then compare current V1, structured LLM proposal, structural parser proposal, and pooled proposal **only on candidate recall/quality**. This tells us whether discovery is the dominant bottleneck before changing authority.
