# S0 external gold/source acquisition plan

Tracking: #60

Purpose: reduce self-authored gold risk by using pre-existing independently annotated public datasets where they map cleanly to the S0 semantic task, while preserving licensing/custody restrictions and requiring local blind adjudication for the remaining classes.

## Candidate external sources

### FactLens

Repository: https://github.com/megagonlabs/factlens

Useful signal:
- manually curated fine-grained fact-verification benchmark;
- decomposed subclaims;
- synthetic perturbation set with two human annotators scoring atomicity, sufficiency, fabrication, coverage and redundancy.

Use:
- candidate source for independently annotated complex-to-subclaim examples and mutation-control families;
- do not treat its annotations as automatic ClaimGate gold because its task is not identical to proposition-structure authority.

Custody restriction:
- the repository explicitly states that actual datasets used with the components may not be redistributed and only links may be distributed;
- CoverBench portions carry their own license terms, including CC BY-ND 4.0.

Therefore:
- keep any FactLens/CoverBench bytes used for S0 under local research custody;
- commit only source identifiers, hashes, indices and permissible derived annotations;
- do not copy restricted dataset rows into this repository without a separately verified license basis.

### CACDD

Repository: https://github.com/FBzzh/CACDD
Paper: https://arxiv.org/abs/2410.12558

Useful signal:
- expert-annotated atomic claim decomposition;
- 500 question-answer pairs and thousands of atomic claims reported by the paper;
- useful as an external decomposition-coverage source.

Limits:
- Chinese-language corpus;
- derived from WebCPM, so upstream provenance/license must be checked before copying rows;
- decomposition objective is related but not identical to ClaimGate operator/scope authority.

Use:
- local candidate pool for atomic/composite/decomposition review;
- source identifiers and hashes may be committed; exact row bytes only if license/provenance review permits.

### AmbiEnt

Repository: https://github.com/alisawuffles/ambient
License: CC BY 4.0

Useful signal:
- author-curated and linguist-annotated ambiguity examples;
- larger overgeneration/filtering corpus with expert annotation;
- explicit human ambiguity/disambiguation work.

Use:
- primary external candidate source for S0 AMBIGUOUS cases;
- preserve exact dataset/version identity and original ambiguity annotation;
- still map each selected case prospectively through the S0 annotation guide rather than assuming every AmbiEnt ambiguity is proposition-structure ambiguity relevant to ClaimGate.

### Scope Ambiguities in Large Language Models

Repository: https://github.com/McGill-NLP/scope-ambiguity

Useful signal:
- dedicated scope-ambiguity datasets plus human-result files;
- repository states most data may be freely used under MIT.

Restriction:
- Experiment 1A data derived from AnderBois et al. (2012) requires permission from the original copyright holders.

Use:
- exclude the restricted Experiment 1A subset unless permission is independently established;
- use only unrestricted repository data for S0 scope/quantifier ambiguity candidates;
- preserve dataset split/file/row identities and hashes.

### DUST

Repository: https://github.com/frank-wildenburg/DUST
License: CC BY-NC-SA for research/non-commercial use

Useful signal:
- minimal pairs of semantically underspecified and more specified sentences;
- labels include logical-form, ellipsis, PP attachment, VP attachment, conjunction ambiguity, referential ambiguity and related phenomena.

Use:
- candidate source for naturally paired ambiguity/underspecification contrasts;
- particularly useful for the S0 requirement for difficult minimal contrasts.

Limit:
- not every underspecification maps to a proposition-structure AMBIGUOUS gold label;
- each selected case still requires blinded S0 adjudication.

## External-annotation role

External annotations are evidence, not automatic S0 gold.

For every selected external case record separately:

1. upstream dataset annotation;
2. S0 reviewer A label;
3. S0 reviewer B label;
4. adjudicated S0 label;
5. whether the upstream annotation agrees, disagrees or is not directly comparable.

Do not resolve reviewer disagreement by deferring to ClaimGate output.

## Source mix target

Before any S1 proposer output is exposed, acquire a candidate pool broad enough to yield the preregistered targeted capability minimum after blind review.

Preferred mix:

- independently annotated decomposition data for ATOMIC / ALL_OF candidates;
- independently annotated ambiguity/scope data for AMBIGUOUS candidates;
- pre-existing public prose with explicit disjunction/conditional operators for ANY_OF / IF_THEN;
- public technical/government/operational prose for realistic wording variation.

No single dataset should define the whole evaluation target.

## Licensing rule

Before exact source bytes are committed:

- verify the exact row/file license and upstream provenance;
- if redistribution is restricted or uncertain, keep bytes local and commit only content hashes, source locators, row IDs and permissible derived metadata;
- do not convert a local-only custody object into a public GitHub artifact for convenience.

## Independence rule

External dataset annotations reduce self-authored-gold risk but do not replace the required blind S0 review because ClaimGate's semantic taxonomy differs from each upstream task.

The stage remains incomplete until reviewer-specific first-pass labels and adjudication records exist.
