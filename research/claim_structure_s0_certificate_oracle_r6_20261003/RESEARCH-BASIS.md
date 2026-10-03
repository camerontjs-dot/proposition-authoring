# Research basis for source-bound certificates

This note records why S0-R6 uses explicit roles, scope, obligations and completeness rather than a free-form model oracle.

## Predicate/role binding

PropBank-style semantic-role annotation provides an explicit predicate-argument view. Core arguments are predicate-specific and adjunct roles include temporal, locative, modal and negation information.

Useful background:

- PropBank / role-labeling overview: https://doi.org/10.1162/COLI_a_00145
- Dependency-based PropBank SRL: https://aclanthology.org/D08-1008/

For ClaimGate, the transferable idea is not the exact PropBank label inventory. It is the requirement that a certificate cannot say "two propositions" while silently losing who did what to whom.

## Coverage/completeness in semantic annotation

QA-SRL represents predicate-argument structure using question-answer pairs. Its project emphasizes richly structured, interpretable annotations.

- QA-SRL project: https://qasrl.org/
- Controlled Crowdsourcing for High-Quality QA-SRL Annotation: https://aclanthology.org/2020.acl-main.626/

The controlled-annotation study is especially relevant: a seemingly usable annotation process produced insufficient coverage, and quality improved only with reviewer selection/training plus a consolidation phase.

For ClaimGate, completeness must therefore be an explicit object, not an assumption that a reviewer who produced valid JSON must have captured all semantic obligations.

## Scope representation

Ordinary AMR has documented gaps around quantification, negation and modality scope. UMR-style work adds explicit scope structure.

- Modeling Quantification and Scope in AMR / UMR: https://aclanthology.org/W19-3303/
- Universal Dependencies to Logical Form with Negation Scope: https://aclanthology.org/W17-1804/
- 2026 UMR tutorial: https://aclanthology.org/2026.propor-2.41/

For ClaimGate, attribution, negation, modality and shared qualifiers need explicit attachment targets. A label such as `AMBIGUOUS` without the live readings is not enough.

## Decomposition quality

FactLens argues that fine-grained claim decomposition must preserve context and semantic equivalence.

- FactLens: https://aclanthology.org/2025.findings-acl.929/

DnDScore shows that decomposition and decontextualization can work against each other: isolating an atomic fact can remove context, while re-adding context can introduce additional factual content.

- DnDScore: https://aclanthology.org/2025.emnlp-main.1205/

Decomposition Dilemmas documents characteristic decomposition errors and shows that decomposition can add noise instead of improving verification.

- https://aclanthology.org/2025.naacl-long.320/

For ClaimGate, the certificate must record what must survive decomposition, not merely the expected number of children.

## Design implication

The S0 oracle should be a reconstructable semantic evidence object:

```
root bytes
  -> source-bound predicates / roles / operators / qualifiers
  -> one or more complete readings
  -> completeness ledger
  -> independent review
```

A model may help propose such an object, but the object itself must be inspectable and falsifiable.
