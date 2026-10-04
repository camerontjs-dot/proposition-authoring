# Annotation instructions

These instructions govern the S0-R6 certificate packet. Drafting, including drafting by a model, has zero authority. A certificate is an inspectable object, not a model label.

## Root bytes

The root is the exact UTF-8 string in `root.text`. Its hash is SHA-256 of those bytes, prefixed `sha256:`. There is no case folding and no whitespace normalization after the root is chosen.

Two roots were joined across a PDF line break before hashing:

- `You must upload your homework as a PDF.` The PDF text layer breaks after `your`.
- `the old men and the old women`. The PDF text layer breaks after `and`.

`the old men and women` omits the realisation-list comma. The space before that comma is an extraction artifact, not part of the NP.

The horse and Peter sentences use U+2019 in `didn’t`. The synthetic calibration sentence `Every guest didn't leave.` uses ASCII `'`.

## What a certificate records

- Every predicate head used by a live reading, with its source span.
- Every materially required role, with its source span.
- Every live reading and any reading the cited analysis explicitly rejects.
- Scope bindings for negation, modality, attribution, quantifiers, condition, time, location, and other modifiers.
- Obligations whose source spans are exact root slices.
- A ledger that partitions the root. Every word is material and covered by a referenced span.

## Classification

- `ATOMIC`: one live reading, operator `ATOMIC`, one proposition. Reports, negated clauses, modal clauses, and single-event PP modification use this class.
- `ALL_OF`: one live reading, operator `ALL_OF`, at least two propositions.
- `NON_ALL_OF`: one live reading whose operator is `ANY_OF` or `IF_THEN`.
- `AMBIGUOUS`: at least two materially live readings.

An attribution sentence is one matrix clause. Its complement is a role, not a second coordinate, unless the cited analysis says otherwise.

## Disclosed limits

A role may apply a Universal Dependencies guideline to a nominal that the cited sdparse does not itself annotate. The analysis basis states that limit. The certificate does not pretend the missing relation was printed.

Imperatives do not receive an invented subject.

`with the telescope` is `OTHER`. The cited paper calls it an instrument or a nominal modifier, not a location.

## Families

One root may belong to more than one family. The family list is outside the certificate, in `packet/CORPUS.json`.

The temporal/location pair is the block sentence, where both PPs attach to the verb, and the telescope sentence, where the PP is either verb-level or nominal. The old-men coordination is the shared-versus-local modifier analogue. It is not a place-name example.
