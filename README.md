# CycleNavigator-scores

**PUBLIC VERIFICATION ARCHIVE — BOOTSTRAP (NOT YET PROOF-SEALED)**

This repository will give humans and independent AI agents a simple, reproducible way to audit Cycle Navigator's frozen weekly forecasts and subsequent outcomes **without relying on a post to X**.

**IMPORTANT:** Public Git commits can be rewritten by repository administrators; a SHA-256 hash alone is not proof that a prediction existed before its outcome. This README defines the required publication and evidence gates, not a claim that any historical result is already independently cryptographically verified.

## Current public-source readback · 12 October 2026

**New official weekly source:** public **CN #29 / 2026-W42** was generated 2026-10-12 06:32:25 UTC with first eligible weekly hour 07:00 UTC. Source SHA binding is captured in [CN29 provisional readback](v2/source-receipts/2026/W42/CN29_PROVISIONAL_SOURCE_READBACK.json) and the [public v2 index](v2/scorebook-index.json). The original read-only source remains in the Archive repo.

**New v2 binary score status: NONE**. All 10 W42 claim snapshots are **ABSTAIN**: they do not have an ex-ante typed measurable predicate, and the official pullback state was only `BUILDING` (watch, not a 5% material warning). They must NOT be shown as 10/10, 0/10, accuracy, prediction failure, or market Edge.

**Latest completed public Price Range:** **CN #28 / W41 = 49.56%** from the exact original public scorecard; BTC 62.94%, ETH 36.17%, 168 hourly observation coverage. [Source-exact CN28 mirror](scores/2026/W41/CN28/CANONICAL_PUBLIC_SCORECARD.json). Market/Structure and combined overall score are null. This price result is a completed **pre-v2** issue, not a binary Edge score.

**Independent proof is NOT sealed:** W42's original source freeze time predates the first eligible weekly hour according to the source receipt, but the public readback mirror is authored afterward; neither proves independent external timestamp existence before the initial scoring window. Immutable release + independent external time witness and completed observation verification remain open at [proof issue #2](https://github.com/Donh91/CycleNavigator-scores/issues/2).

## Staged import snapshot (2026-10-11)

This repository mirrors the existing CN historical scoreboard for public issue numbers 1 through 27 as the original byte-exact legacy overview. In addition, source-exact individual scorecards now cover CN23 through CN28 (the settled W41 result). The earliest records are original archive claims with differing metrics and do not satisfy independent ex-ante timestamp verification. No immutable releases or external timestamp anchors have been issued.

## Current status

- The authoritative forecasts and completed scorecards currently live in the existing Investering Framework repository.
- Historical score mirrors are available as readable public files, but no independently proven prospective forecast freezes, immutable releases, third-party timestamp confirmations or production publication workflow are in place yet.
- A GitHub release, by itself, is not independent external attestation. GitHub's immutable-release setting must be enabled before new production releases; independent timestamp anchoring is a separate gate.
- The current production website and on-chain/market decision engines are unchanged.

## The new CN v2 era starts with 2026-W42 / public CN #29

From **Monday 12 October 2026**, the new public-facing evaluation architecture adds three independent evidence families:

1. **Price Range Weekly + Intraday**: the prior BTC/ETH price-range source formula (**70% containment + 30% Jaccard**) is unchanged. Report the full week separately from each D1–2, D3–4 and D5–7 window.
2. **Direction / Flow / Rotation**: original bilingual, type-checked prospective statements are scored **100 = supported; 0 = refuted; null = pending/abstain/not evaluable** only where the measurable predicate, source and horizon were frozen before outcomes. Individual weekly / 14 / 21 / 28 / 56-day claims retain their original issue identity until maturity.
3. **Pullback Edge**: track the presence or absence of an explicit warning, actual BTC material pullback onset, severity, possible recovery/end, warning lead time and independently reproducible altcoin-basket impact. False alarms and missed declines must not disappear from reported denominators. No-warning requires a valid, explicit source state; missing risk data is NOT a successful no-warning.

**As of 2026-10-12**, there are **no settled W42 new-era binary scores**. The original W42 source freeze exists and is now mirrored as provisional readback, but its ten claims are all ABSTAIN. Mature observations, genuinely eligible forward predicates, immutable release proof and independent claim verification are still outstanding.

Core public files:
- [Prospectively registered scoring rules](CN_V2_EDGE_SCOREBOOK_PROTOCOL_2026-W42.md)
- [Typed bilingual assertion schema](schema/cn-v2-frozen-claims.schema.json)
- [Deterministic individual binary claim evaluator](verify/evaluate_cn_v2_claims.py)
- [Hourly BTC pullback evidence extractor](verify/pullback_events.py)
- [Machine-readable v2 publication status](v2/scorebook-index.json)
- [Public zero-login proof project](https://github.com/Donh91/CycleNavigator-scores/issues/2)
- [Source CN W42 weekly capture implementation](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1577)
- [CN vNext website preview](https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/)
- [Work execution and true scoring integration mission](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578)

**Important for external AI audits:** Legacy 1–27 scores remain publicly available, but they must not be averaged with v2 binary claims or newly labeled independently timestamped. Price Range precision is not investment return and correct no-warning classifications during a calm market do not alone establish useful pullback Edge. Compare hits, misses, false alarms, prevalence and independence-adjusted controls.

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
