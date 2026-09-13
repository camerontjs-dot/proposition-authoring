---
name: Research experiment
description: Preregister a bounded Proposition Authoring experiment
title: "Research: "
labels: []
assignees: []
---

## Research question

State one bounded question this experiment can answer.

## Current observed evidence

Separate direct observations from inference. Link exact predecessor PRs, commits, blobs, artifacts, and terminal records.

## Hypothesis

What specific claim is being tested?

## Competing explanations

What else could explain the existing evidence?

## Highest-weight assumption

Which assumption carries the most inferential weight?

## Smallest discriminating test

Why is this experiment smaller or more informative than a broader build?

## Target architecture / change surface

State exactly what may change and what remains frozen.

## Controlled variables / invariants

List the semantic and apparatus properties that must remain unchanged.

## Development/regression evidence

Existing cases may guide development, but cannot become fresh decisive evidence.

## Fresh decisive surface

Define the families and minimum discriminating coverage before authoring fresh cases.

## Weak controls

List strategies that should fail if the experiment is meaningful.

## Hard falsifiers

State conditions that force `FALSIFIED` regardless of aggregate accuracy.

## Positive evidence burden

State the complete gate for a positive result.

## Evaluator / adjudication assurance

Describe evaluator independence, gold creation, contamination controls, human review limits, and known assurance gaps.

## Exact freeze plan

Specify which files/refs/blobs must freeze before fresh evidence is exposed.

## Runtime authority exclusions

Confirm that gold labels, retrieval quality, CAL verdicts, Decision Engine outputs, and downstream performance are not available as decomposition-selection authority.

## Expected terminal dispositions

Use the project research vocabulary:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

## Non-claims

List adjacent claims this experiment cannot establish.

## Authorized next step if supported

State the smallest action a positive result would authorize.

## Authorized next step if falsified/inconclusive

State whether the result should terminate, narrow, or trigger a successor experiment.
