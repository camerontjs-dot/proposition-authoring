# ClaimGate V1 Local Qualification and RC5 Runbook

## Objective

Mechanically install and test the frozen ClaimGate integration candidate locally, validate its authoritative outputs with released Contract A 2.0.0, and exercise the ClaimGate -> Contract A -> frozen Evidence Bundler RC5 boundary.

This is a qualification run, not a development task. Do not repair semantic behavior in place.

## Exact subjects

ClaimGate / Proposition Authoring:

- semantic source: `f9d0ae9ba81756c51d7f1d433616d699eb9b6fd3`
- target freeze: `9c76b3d87b4362b79a22c0467a13a48c0a380a16`
- integration branch: `integration/claimgate-v1-candidate-20260915`
- RC4b terminal record: `809b2534ffb34efa31c13975da55e65770460b99`

Contract A:

- public version: `2.0.0`
- wire token: `contract-a-wire-candidate-rc2`
- authority repository: `camerontjs-dot/apparatus-contracts`
- use the released external validator `validators/contract_a_rc2.py`

Evidence Bundler:

- Draft PR #79
- tested subject: `8e1e15a96308d20be24b0bd0f0a4d554b0f020cc`
- frozen receipt-only head: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- integration profile: `eb-v1-integration-10x3-rc0`

## 1. Local placement

Use the existing MainFrame CAL Pipeline conventions. Prefer an isolated worktree rather than moving an existing checkout.

Suggested locations:

- ClaimGate worktree under the proposition-authoring project `.worktrees/` directory;
- existing apparatus-contracts checkout/worktree;
- existing frozen Evidence Bundler PR #79 worktree;
- outputs under `/Users/admin/Desktop/MainFrame/20_live/cal-pipeline/cal-v1-studies/`.

Do not disturb already-frozen EB or CAL worktrees.

Record the exact absolute paths actually used.

## 2. Identity and runtime-drift check

Before installation, record:

```bash
git rev-parse HEAD
git status --short
git log -1 --oneline
```

Verify the ClaimGate runtime remains byte-identical to the scientific subject:

```bash
git diff --exit-code \
  f9d0ae9ba81756c51d7f1d433616d699eb9b6fd3..HEAD \
  -- BOOTSTRAP_AUTHORITY.json pyproject.toml Makefile scripts/fetch_frozen_predecessors.py src/proposition_authoring tests
```

This must produce no runtime/test diff attributable to the integration packaging. If it does, stop and report the exact diff.

## 3. Environment and installation

Use Python 3.11 or a newer version already supported by the candidate, but record the exact version.

Example:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pip check
```

Bootstrap the exact frozen predecessor/Contract A artifacts required by the candidate:

```bash
python scripts/fetch_frozen_predecessors.py
```

Do not substitute newer predecessor artifacts.

## 4. Maintained candidate checks

Run the maintained suite and static checks:

```bash
python -m unittest discover -s tests -v
python -m pytest -q
ruff check .
python -m compileall -q src tests integration
python -m pip check
```

Preserve exact pass/fail/skip counts and tool versions.

A failure is a stop/deviation unless clearly unrelated to this exact candidate and explicitly documented. Do not weaken a test or alter semantic files to obtain green output.

## 5. Frozen smoke fixtures

Fixtures are already supplied under:

`integration/claimgate_v1_candidate/fixtures/`

Expected outcomes are in `EXPECTATIONS.json`.

Create a fresh run directory, for example:

```bash
RUN=/Users/admin/Desktop/MainFrame/20_live/cal-pipeline/cal-v1-studies/claimgate-v1-rc5-$(date +%Y%m%dT%H%M%S)
mkdir -p "$RUN"/{declared,not_needed,abstained}
```

Run the three fixtures:

```bash
proposition-authoring author \
  integration/claimgate_v1_candidate/fixtures/declared.json \
  --receipt "$RUN/declared/receipt.json" \
  --contract-a "$RUN/declared/contract_a.json" \
  | tee "$RUN/declared/stdout.txt"

proposition-authoring author \
  integration/claimgate_v1_candidate/fixtures/not_needed.json \
  --receipt "$RUN/not_needed/receipt.json" \
  --contract-a "$RUN/not_needed/contract_a.json" \
  | tee "$RUN/not_needed/stdout.txt"

proposition-authoring author \
  integration/claimgate_v1_candidate/fixtures/abstained.json \
  --receipt "$RUN/abstained/receipt.json" \
  --contract-a "$RUN/abstained/contract_a.json" \
  | tee "$RUN/abstained/stdout.txt"
```

Required observations:

- declared fixture: state `DECLARED`; authoritative Contract A exists; `decomposition.state == declared`; operator `all_of`; exact two expected children;
- not-needed fixture: state `NOT_NEEDED`; authoritative Contract A exists; `decomposition.state == not_decomposed`; root identity/text unchanged;
- abstained fixture: state `ABSTAINED`; receipt exists; **no authoritative Contract A file may exist**.

The declared and not-needed root texts are taken from already-qualified RC4b semantic families. The abstention root is an already-qualified fail-closed RC4b case.

## 6. External Contract A 2.0 validation

Against the separate apparatus-contracts checkout, validate both authoritative outputs with the released external engine:

```bash
python "$CONTRACTS/validators/contract_a_rc2.py" "$RUN/declared/contract_a.json"
python "$CONTRACTS/validators/contract_a_rc2.py" "$RUN/not_needed/contract_a.json"
```

Both must print `VALID` and exit 0.

Do not validate the abstained case because there must be no authoritative Contract A object.

## 7. Tamper controls

Make copies of the valid generated outputs. Do not mutate originals.

At minimum produce and test:

1. root text changed with stale root hash / handoff hash;
2. declared child text changed with stale child hash / handoff hash;
3. top-level `handoff_sha256` altered;
4. declared operator changed away from `all_of`;
5. one declared child removed while retaining stale lineage/binding.

Every tampered object must fail the released Contract A validator.

Also attempt to pass at least the stale-root and stale-child objects to the frozen EB integration runner. EB must reject rather than silently reconstruct or repair proposition identity.

Preserve the tampered objects and stderr/exit codes as negative receipts.

## 8. Frozen Evidence Bundler consumer conformance

Use the exact frozen EB candidate. Do not substitute generic EB defaults.

From the EB frozen worktree, install/use its already-qualified environment and run its maintained candidate/projection tests. Record the exact commands and results.

Then consume the two authoritative ClaimGate outputs using the exact integration runner:

```bash
python scripts/run_v1_integration_candidate.py \
  "$RUN/declared/contract_a.json" \
  --compatibility-carrier research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json \
  --out-dir "$RUN/declared/eb"

python scripts/run_v1_integration_candidate.py \
  "$RUN/not_needed/contract_a.json" \
  --compatibility-carrier research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json \
  --out-dir "$RUN/not_needed/eb"
```

Do not invoke Evidence Bundler for the abstained case.

RC5 checks:

- EB accepts both externally valid Contract A objects;
- EB does not require ClaimGate proposer/evaluator internals;
- root identity/text/hash are preserved;
- `not_decomposed` remains attached to the root path;
- declared children are consumed in exact Contract A sequence with exact text/IDs/hashes;
- EB does not mint, normalize, paraphrase, or repair authoritative proposition text;
- source representations originate only from Contract A;
- malformed/tampered handoffs fail closed;
- outputs are deterministic on exact replay.

This is consumer conformance, not a retrieval-quality claim.

## 9. Replay

Repeat the declared and not-needed ClaimGate runs into fresh directories using identical inputs and environment.

Hash at minimum:

- authoring receipts;
- Contract A outputs;
- EB native packages;
- Contract B bundles/projector receipts where emitted.

The same exact inputs/configuration must reproduce byte-identical or canonically identical outputs according to each component's existing identity rules.

Use SHA-256 and preserve a checksum file in the run directory.

## 10. Claim Profile V0

Do not implement causal claim categorization during this qualification.

`CLAIM_PROFILE_V0.md` is a shadow design surface only. The local operator may copy it into the local study folder for visibility, but no downstream component should read it and no result depends on it.

## 11. Freeze/receipt output

Create one local qualification receipt recording:

- ClaimGate branch/head and semantic source;
- runtime-drift check result;
- OS/architecture;
- Python/pip/pytest/ruff versions;
- exact apparatus-contracts SHA;
- exact EB SHA;
- test counts;
- smoke dispositions;
- external Contract A validator results;
- negative/tamper results;
- EB conformance results;
- replay hashes;
- exact run directory;
- any deviation or failure.

Do not update GitHub semantics merely because the local run fails. Preserve the result and report it.

## Qualification disposition

If all gates pass, report:

`SUPPORTED_CLAIMGATE_V1_TO_CONTRACT_A_2_TO_EB_V1_RC5`

This supports moving to bounded naturalistic shadow qualification (RC6) and using the exact frozen ClaimGate candidate in the local whole-pipeline smoke.

It does not authorize merge, tag, release, semantic widening, claim-profile routing, or production use.
