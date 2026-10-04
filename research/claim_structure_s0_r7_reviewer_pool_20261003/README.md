# S0-R7 reviewer-pool qualification

Tracking: issue #65.

## Purpose

R6/R6b/R6c did not falsify the frozen certificate packet. They failed to produce two eligible reviewer profiles.

R7 changes exactly one thing: **reviewer population**.

The frozen certificate packet remains:

`da6007163bfe96d39ef1026f9efb98e42edbbbeb`

The terminal predecessor remains:

`fb3e907d1b1e94f69eb8ccbf1f92e01bc7fed9e5`

Disposition:

`BLOCKED_CERTIFICATE_SURFACE`

## Hypothesis

At least two genuinely new reviewer profiles, outside the already-tested reviewer families, may pass the unchanged R6c calibration and become eligible to perform decisive review.

If they cannot, the certificate surface remains blocked for lack of qualified reviewers.

## Non-goals

R7 does not:

- alter any certificate;
- alter the review checklist/prompt;
- alter calibration mutations;
- alter eligibility rules;
- test S1 discovery;
- test S2 verifiers;
- change V1;
- change Contract A.

## Allowed dispositions

- `SUPPORTED_NEW_REVIEWER_POOL_FOR_DECISIVE_REVIEW`
- `BLOCKED_NEW_REVIEWER_POOL`
- `INCONCLUSIVE_NEW_REVIEWER_POOL`
- `FALSIFIED_CERTIFICATE_PACKET_BY_NEW_REVIEWER_EVIDENCE`

A positive result authorizes only decisive certificate review using the unchanged packet.
