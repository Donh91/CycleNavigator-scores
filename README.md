# CycleNavigator-scores

**PUBLIC VERIFICATION ARCHIVE — BOOTSTRAP (NOT YET PROOF-SEALED)**

This repository will give humans and independent AI agents a simple, reproducible way to audit Cycle Navigator's frozen weekly forecasts and subsequent outcomes **without relying on a post to X**.

**IMPORTANT:** Public Git commits can be rewritten by repository administrators; a SHA-256 hash alone is not proof that a prediction existed before its outcome. This README defines the required publication and evidence gates, not a claim that any historical result is already independently cryptographically verified.

## Staged import snapshot (2026-10-11)

This repository mirrors the existing CN historical scoreboard for public issue numbers 1 through 27 as a source-exact legacy record. It also stages individual existing public scorecards for CN23 through CN27. The earliest records are original archive claims with differing metrics and do not satisfy independent ex-ante timestamp verification. No immutable releases or external timestamp anchors have been issued.

## Current status

- The authoritative forecasts and completed scorecards currently live in the existing Investering Framework repository.
- Historical score mirrors are available as readable public files, but no independently proven prospective forecast freezes, immutable releases, third-party timestamp confirmations or production publication workflow are in place yet.
- A GitHub release, by itself, is not independent external attestation. GitHub's immutable-release setting must be enabled before new production releases; independent timestamp anchoring is a separate gate.
- The current production website and on-chain/market decision engines are unchanged.

## The one-rule AI verifier

**Never infer a public score from a screenshot, website headline, X post, or matching internal machine issue number alone.** Resolve the original forecast by **public CN number + forecast week + frozen publication source**, confirm that this source existed before evaluation, then reproduce the completed score with the named method and exact outcome evidence. Keep different score families and scoring eras distinct.

## Public score semantics

- **Price Range Precision**: the actual public, forecast-vs-realization metric according to its frozen methodological version.
- **Frozen-claim precision**: a distinct coverage/claim-evaluation metric. It is NOT overall market prediction accuracy or investment return.
- **Market / Structure**: preserve legacy historical scores through public CN #26; from CN #27 onward, it is analysis-only and has **no percentage score**.
- **Bull/Bear**: an evidence-balance forecast, not a probability or scored precision metric.
- **Combined overall score**: remains **UNDEFINED** without a separate prospective, validated aggregation contract.
- **No data / abstention / failure**: retain explicitly, never silently omit.

## Planned release identities

- Forecast freeze: `forecast-CNnn-YYYY-Www-v1`
- Completed score: `score-CNnn-YYYY-Www-v1`
- Subsequent correction: `correction-CNnn-YYYY-Www-vN`

Each package binds to the earlier published forecast hash and, where applicable, the previous release digest. The independent verifier must check the hashes, package authenticity, release immutability status, actual publication time, scoring version and evidence completeness.

## Repository layout

- `PROTOCOL.md`: publication, verification, failure and correction gates.
- `schema/`: deterministic manifests and score contracts.
- `forecasts/YYYY/Www/CNnn/`: public read-through copies; not proof on their own.
- `scores/YYYY/Www/CNnn/`: human/AI read-through copies; not proof on their own.
- `corrections/`: append-only correction and revocation events.
- `verify/`: standalone zero-login verifier and verification notes.
- `releases-index.json`: convenience navigation, **not cryptographic proof**.

## Verification badges (evidence based, not marketing)

- **VERIFIED**: original forecast predates outcome, immutable release and attestation validated, independently timestamped digest validated, original evidence and scoring reproduced.
- **PROVISIONAL**: source and methods are accessible but one or more proof gates remain outstanding.
- **LEGACY_ATTESTED**: historical record has an archive or witness, without retrospective claim of independent ex-ante proof.
- **CORRECTED**: original remains visible, with a verifiable linked correction.
- **UNVERIFIABLE**: required proof or source is missing, contradictory or invalid.
- **REVOKED**: explicit published revocation event.

**Site policy:** the public website must not label results VERIFIED before the verifier has produced a reproducible receipt.

## Source references

- [Canonical public CN-series index](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json)
- [Historical issue/scoring-era retrieval rules](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/05_CYCLE_NAVIGATOR/CANONICAL_SCORE_AND_LINEAGE.md)
- [Existing completed public scorecards](https://github.com/Donh91/Investering-Framework-Archive-v1/tree/main/05_CYCLE_NAVIGATOR/public_scorecards)
- [Website data integrity contract](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md)

The core framework continues to calculate the score. The public scores repo is **distribution and verification only**; it is not another owner of what the market forecast means.

See [PROTOCOL.md](PROTOCOL.md) for the release/proof design and independent-audit acceptance criteria.
