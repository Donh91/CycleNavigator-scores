# Cycle Navigator Public Proof Protocol v1 — implementation design

Status: DESIGN_ONLY / NOT DEPLOYED, 2026-10-11.

## Non-negotiable scope

Keep the current Investering CN forecast, PUBLIC_SERIES_INDEX, freeze receipts, forward-range ledger, completed public scorecard materializer, Master Monday outcomes and Site/Compass authority as the sole production owners. This public repository publishes and verifies copies; no duplicate score computation, official forecast, portfolio advice or scheduled analysis here.

Never copy private wallets, secrets, nonpublic research, proprietary raw feeds, unlicensed vendor data or private GitHub repository paths into public artifacts. All public bundles must be generated through a strict allowlist and privacy scanner.

## Historical truth boundary

It is not mathematically possible to turn a historical score into an ex-ante independently anchored claim after the scored week ends. For historical backfill, preserve original forecast bytes/hash, best available public publication receipt, source URL, exact observation timestamps and the limitation flag LEGACY_ATTESTED. No retroactive VERIFIED promotion solely because the migration's GitHub commit is newly signed.

Keep public issue and machine issue separate. Public forecast identity = series key, public CN number, forecast ISO week and original immutable forecast source. Explicit score era tagging:
- Legacy public Market/Structure CN1–26 remains visible and unchanged if historically established.
- From CN27 Market/Structure precision = null, analysis-only.
- Price Range precision is separately named, never a combined overall.
- Frozen-claim precision is a separate research audit figure, never investment alpha.
- Bull/Bear is not precision or probability.

## Record states

DRAFT -> FREEZE_PUBLISHED -> FREEZE_SEALED -> OUTCOME_MATURED -> SCORE_PUBLISHED -> SCORE_SEALED -> VERIFIED.

If any gate is not met: PROVISIONAL or UNVERIFIABLE, with reason and no false headline. Correction and revocation events are new versioned releases, never modifications of sealed prior releases.

## Forecast freeze release

Name: forecast-CNnn-YYYY-Www-v1

Freeze must occur **before** first eligible scored outcome observation. Each release includes:
- FORECAST.json: full allowlisted source-derived public forecast, no post-hoc additions.
- IDENTITY.json: series, public issue, forecast week, source owner, frozen UTC time, original source path, source commit/blob SHA, score-window policy.
- MANIFEST.json: deterministic canonical UTF-8 bytes with format version, source digests, each asset's SHA-256, predecessor manifest SHA-256, issuer identity and creation time.
- RECEIPT.json: canonical frozen-source receipt, GitHub release URL/tag/attestation, externally anchored digest with timestamp status.
- Supporting human-readable summary is optional and never score authority.

Immutable GitHub releases should be enabled in repo Settings **before** publishing production releases. Check that tags/assets cannot be replaced using repository settings and independent verification; this setting is not equivalent to deletion-proof or independently timestamped historical existence. Publication before the outcome is separately mandatory.

## Completed score release

Name: score-CNnn-YYYY-Www-v1

Never create before period completion and coverage validation. Bind forecast release digest and its ex-ante proof, public scorecard original file digest, score contract version, freeze-window policy and exact observed period. Include:
- SCORECARD.json, identical in public score semantics to canonical public scorecard;
- EVIDENCE.json (source IDs, timestamp range, missingness/completeness, observed low/high and other legally shareable inputs);
- METHOD.json (method/version, formula and weight provenance; reference to canonical scorer);
- RESULT-VALIDATION.json (independent recomputation/equivalence checks, each test PASS/FAIL);
- MANIFEST.json and RECEIPT.json.

Only assert reproducibility if legally accessible input is sufficient to independently recompute; otherwise mark 'method inspectable, source data restricted' and proof not fully verified.

## Timestamp and anchor layering

- Layer A: pinned frozen source Git blob/commit and immutable GitHub release.
- Layer B: GitHub release attestation and verified publisher identity if available.
- Layer C: independent time witness: OpenTimestamps Bitcoin confirmation, a transparency log or another independently reviewable authority. Store receipt/proof bytes or permanent public witness links.
- Layer D: optional offsite public mirror/export to protect availability from repository deletion.

Do not label an OTS calendar promise or pending anchor as Bitcoin CONFIRMED; verifier must evaluate its actual status. Proving the file hash existed is not by itself proof that its score was calculated honestly: score source, method, selection bias, sharpness and outcome evidence remain separately audited.

## Corrections

A new correction-CNnn-YYYY-Www-vN references original release digest, describes affected fields and reason, holds before/after values and independent reviewer record. Original remains visible. The public site reports 'Corrected on DATE; original retained' instead of substituting history without disclosure. If release deletion makes the source inaccessible, verification fails closed (independent mirrors may assist evidence recovery).

## Agent-readable verifier interface

Provide an immutable verification target per issue:
- GET releases-index.json for navigation only;
- GET release assets and manifests using exact tag/release ID;
- recompute SHA-256 over original bytes (never reserialize JSON for hash check);
- verify manifest asset digests and predecessor chain;
- verify GitHub release immutability + publisher attestation, independent third-party anchor, time-before-outcome;
- compare the forecast's public-series identity, freeze-window policy and score method with the completed scorecard;
- independently recompute public price-range result from eligible observed data and report containment/sharpness separately if the method demands;
- return VERDICT, reasons and URLs to proof/evidence, including explicit unverifiable items.

Minimum JSON status schema:
{
  "contract": "CN_PUBLIC_VERIFY_RESULT_v1",
  "public_issue_number": null,
  "forecast_week": null,
  "forecast_sha256": null,
  "score_sha256": null,
  "method_version": null,
  "release_attestation_valid": false,
  "external_anchor_status": "NOT_PRESENT",
  "forecast_ex_ante_valid": false,
  "score_recomputed": false,
  "verdict": "PROVISIONAL",
  "reasons": ["BOOTSTRAP_NOT_PUBLISHED"]
}

## Required release-gate test matrix

1. Original forecast prediction is available and independently timestamped before scored period.
2. Wrong public issue to machine issue join rejected.
3. Different scoring eras never mixed/averaged; no fabricated overall percentage.
4. Canonical/public scorecard mismatch -> hard FAIL.
5. Old unsealed tag cannot be accepted as immutable.
6. Same tag replaced, data tampered, altered manifest, hash chain split or missing anchor -> hard FAIL.
7. Missing/incomplete hourly outcomes -> STALE/PENDING/UNVERIFIABLE, never scored as clean.
8. Historical backfill remains LEGACY_ATTESTED.
9. Correction remains appended, predecessor unmodified.
10. No secrets or restricted fields leak.
11. CN public site reads verified status as **display only**, never forecast/action authority.
12. No new daily schedule: use the existing CN weekly publication and completed-score owner to trigger publishing after their respective successful existing lifecycle events.

## Acceptance and release workflow

Phase A: bootstrap docs, schemas and verifier fixtures in PR. No proof claim.
Phase B: align exact CN scoring materializer, public index and site freeze receipt from current main and all overlapping owner PRs; define read-only exporter.
Phase C: score repo branch protection + immutable releases + attestation + independent anchor, first dry run with deliberate tampering/rewrite failure fixture.
Phase D: first **prospective** weekly freeze publication, verify it existed before outcomes.
Phase E: complete week's score, audit and release, independent agent verification. Gradually backfill historical records with their true legacy statuses.
Phase F: site PROOF consumes versioned read-only verified manifest projection. X remains optional promotion.

No automatic migration, signing/keys, score value edits or production release is authorized by this design document alone.
