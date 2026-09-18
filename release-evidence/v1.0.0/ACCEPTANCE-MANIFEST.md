# Gate V1.0.0 acceptance artifact preservation

This branch preserves the release-acceptance identity for Gate V1.0.0 without moving or modifying the immutable release tag.

## Release identity

- tag: `v1.0.0`
- tag object: `d81dd121f5b5baba2f837e5138c8e7f47108ec15`
- release commit: `c0da10e2e3b9aada5f66af9859cf27964fd3c5fc`
- release tree: `4ea9d0fa5ab9d926e0bf960da2103be8c202d400`

## Acceptance run

- workflow: `Gate V1 1.0.0 Release Freeze`
- run: `35296155951`
- Actions artifact ID: `10527433832`
- artifact name: `gates-v1-1.0.0-release-freeze`
- ZIP size: `8489` bytes
- ZIP SHA-256: `0f58fbf0e63dc912166194c00d5ab1462a4b6b26b48db8212b95035500b652b0`
- Actions retention expiry: `2026-12-17`

The artifact was re-downloaded after release tagging and the ZIP SHA-256 was independently recomputed; it matched the frozen acceptance digest exactly.

## Artifact members

| Original member | SHA-256 |
| --- | --- |
| `tmp/release-specimen/AUTHORING-RECEIPT.json` | `d4535cf3f37bac13bc04dfbbb7e6eaae6d67f99e33ead55731c6b684a42495a8` |
| `tmp/release-specimen/CLAIM-GATE-INPUT.json` | `47f8aa5487ec8ac5e6a3811e6ec6dc9baf1f9fe03eb9fbf7007c24ff36ed8810` |
| `tmp/release-specimen/CLAIM-GATE.json` | `b576f9542f018a96dd6ddcbcf98a4c0f9a0015c437ac2982843026732de10218` |
| `tmp/release-specimen/CONTRACT-A.json` | `356c33e01f301955119ce5cb61d955722ddc57f96ada0609bb1d2670a4036d64` |
| `tmp/release-specimen/EVIDENCE-GATE-INPUT.json` | `275544ce1972f5be12a11bb4d0b9fc25b118d9eedd00ea29ed6e187afb19dbec` |
| `tmp/release-specimen/EVIDENCE-GATE.json` | `88b512c4bd905b00d43ec452f5d115fb0b8d47abc482bbd679c624c6974a44a7` |
| `tmp/release-specimen/STANDARDIZATION-RECEIPT.json` | `851c12db71050b4bb7185af3dc0f6090c6151348461321f2b2c3678dd856e691` |
| `home/runner/work/proposition-authoring/proposition-authoring/pressure-result/RESULT.json` | `2dc10c7dd81535107728c332a57179db3e7b047076203fe7c7dcd9b45c2ac697` |

## Scope

This record does not create a new release, change Gate semantics, or replace the original Actions artifact. The GitHub Release should attach the exact ZIP whose SHA-256 is recorded above.
