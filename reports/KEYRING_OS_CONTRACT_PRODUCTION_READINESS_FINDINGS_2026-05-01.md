# Keyring OS Contract Production-Readiness Findings

Date: 2026-05-01  
Scope: `keyring-os/apps/admin` frontend vs `pms-master/tenant_portal_backend` backend  
Baseline plan: `reports/KEYRING_OS_PRODUCTION_READINESS_PLAN_2026-05-01.md`

## Executive verdict

**Contract state: not production-ready.** The backend exposes a large set of launch-relevant routes and many admin calls are prefix-compatible, but the frontend still mixes direct backend calls, Next proxy calls, `/api`, `/api/v2`, and unprefixed route assumptions. The highest-risk gap is not only missing endpoints; it is that the deployed base URL/prefix/auth strategy can make otherwise-valid calls hit the wrong host/path or omit JWT forwarding.

## Evidence collected

- Added static probe: `reports/keyring_contract_probe_2026_05_01.py`.
- Ran: `python3 reports/keyring_contract_probe_2026_05_01.py`.
- Probe output: **181 frontend call sites**, **542 backend route declarations**, **49 potential misses** before manual triage.
- Backend global prefix evidence: `pms-master/tenant_portal_backend/src/index.ts` sets global prefix `api`, while excluding `leasing`, `api/leasing`, `esignature`, `api/esignature`, and webhooks.
- Frontend proxy evidence:
  - `keyring-os/apps/admin/src/app/api/v2/[...path]/route.ts` forwards cookies as `Authorization: Bearer <auth_token>` and appends `/api/v2` to configured base.
  - `keyring-os/apps/admin/src/app/api/auth/[...path]/route.ts` separately proxies auth with different base handling.
  - `keyring-os/apps/admin/src/lib/copilot-api.ts` calls `NEXT_PUBLIC_API_URL ?? ''` directly with mostly unversioned paths.
  - `keyring-os/apps/admin/src/app/api/remediation-api.ts` hardcodes `API_BASE = '/api/v2'`.
- Auth/storage evidence:
  - `src/proxy.ts` now protects routes by checking `auth_token`/`accessToken` cookies or bearer header.
  - `src/app/login/page.tsx` still writes `auth_token` into JS-readable cookie and `localStorage`.
  - `src/hooks/use-auth.ts` still reads token/user from `localStorage`.
- Mock-header evidence:
  - No `X-Mock-*` frontend call sites found in current `keyring-os/apps/admin/src`.
  - Backend CORS still allows `X-Mock-User-Id` and `X-Mock-Role` in `src/index.ts`.

## Contract matrix: launch-critical frontend calls vs backend routes

| Domain | Frontend call pattern | Backend route status | Severity | Notes |
|---|---|---:|---|---|
| Auth login/me/logout | `/api/v2/auth/login`, `/api/v2/auth/me`, `/api/v2/auth/logout`; login page also calls `NEXT_PUBLIC_API_URL + /api/v2/auth/login` | Backend has `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout` via global prefix. Probe treats `/api/v2` as prefix-compatible only by normalization; backend does **not** explicitly declare `/api/v2`. | **P0** | Either proxy must translate `/api/v2/auth/*` to `/api/auth/*`, or backend must expose v2. Current `app/api/v2` proxy appends `/api/v2`, likely wrong against current backend. |
| Route protection | `proxy.ts` protects non-public admin routes | Frontend-side protection exists; backend guards enforce JWT on most business controllers | P0/P1 | Improved from prior audit, but JS-readable token path remains. Need unauthenticated route smoke. |
| Payments remediation | `/api/v2/payments/:id/message-tenant`, `/record-manual`, `/payments/stripe/checkout-session`, delinquency routes | Backend has unversioned controller routes under `/api/payments/*` | **P0** | Same `/api/v2` translation problem. Payment calls are launch-critical. |
| Lease doc/signature | `/api/v2/leases/:id/generate-document`, `/send-for-signature` | Backend route exists under `/api/leases/*` | **P0** | Prefix-compatible only if proxy rewrites. Backend service is still stubbed per readiness plan, so route existence does not mean production readiness. |
| Maintenance dispatch | `/api/v2/maintenance/:id/assign-vendor`, `/notify-tenant`, `/notify-owner`; direct `/maintenance` calls | Backend has `/api/maintenance/*` | P1 | Endpoint coverage good; prefix strategy and JWT forwarding are the risk. |
| Property move-in | `/api/v2/property/units/:unitId/start-onboarding`, `/complete-move-in` | Backend has controller aliases `properties` and `property`, route exists under `/api/property/units/*` | P1 | Prefix-compatible if proxy translates `/api/v2` to `/api`; otherwise 404. |
| Screening reasoning | `/api/v2/rental-applications/:id/screening-reasoning` | Backend has `portal/rental-applications/:id/screening-reasoning`, not `rental-applications/:id/screening-reasoning`; legacy `rental-application` has different screen/review routes | **P1** | Likely real route mismatch. |
| Billing statement send | `/api/v2/billing/statements/:id/send` | Backend has `POST /api/billing/statements/:id/send` | P1 | Prefix-compatible only. |
| Telemetry | `/api/v2/telemetry/track`, `/action`, `/decision`, `/summary` | Backend has `/api/telemetry/*` | P1 | Prefix-compatible only. Backend targeted test already has telemetry mock failure. |
| Feed | `/feed`, `/api/v2/feed`, `/api/feed/:id/notes` | Backend has `/api/feed`, `/api/v2/feed` aggregator, and `/api/feed/:id/notes` | P1 | Mixed but mostly covered. Direct `/feed` only works if `NEXT_PUBLIC_API_URL` includes `/api`. |
| Briefing | `/api/briefing/daily`, `/briefing/inject-risk-item` | Backend has `/api/briefing/daily`, `/api/briefing/inject-risk-item` | P1 | Covered when host/base is correct. |
| Tours | `/api/tours/*` | Backend controller is `api/tours`, global prefix likely yields `/api/api/tours/*` unless excluded; probe flagged `/api/tours/lead/:id` mismatch | **P1** | High likelihood of double-`api` prefix bug. |
| Policy settings | `/api/policy/:propertyId`; also `/api/policy/:id/underwriting`, `/payment-plan`, `/maintenance`, `/denial-compliance` | Backend has only `GET/PATCH /api/policy/:propertyId` plus approval-task routes | **P1** | Sub-setting write routes appear missing. |
| Estimates | `/api/estimates`, `/estimates`, `/estimates/:id/approve`, `/reject` | No backend estimates controller found by probe | **P1** | Missing workflow if estimates are launch scope. |
| Reporting | Frontend calls `/reporting/*` | Backend controller is `/api/reports/*`, not `/api/reporting/*` | **P1** | Clear namespace mismatch. |
| Schedule | Frontend calls `/schedule/events`; backend exposes `/api/schedule`, `/summary`, `/daily`, `/weekly`, etc. | Missing exact route | P2/P1 if briefing calendar launch-critical | Needs frontend or backend rename. |
| Inspections | Frontend calls `/inspections*`; backend controller is `inspections-legacy` | **P1** | Clear namespace mismatch unless another proxy exists. |
| Documents | Frontend calls `/documents`, `/documents/upload`; backend has both management and upload routes | P1 | Coverage good; verify auth and multipart paths. |
| QuickBooks | `/quickbooks/auth-url`, `/status`, `/sync`, `/disconnect`, `/test-connection` | Backend has corresponding routes | P1 | Route coverage good; readiness still blocked by live sandbox verification. |
| eSignature | `/esignature/*` | Backend has `esignature` and `api/esignature` aliases, excluded from global prefix | P0/P1 | Route coverage good; webhook signature validation and fallback/mock behavior remain blockers. |
| Feature flags | `/api/feature-flags/check`, `/check-batch` | Backend has `/api/feature-flags/check/:key`, not query-based `check` or `check-batch` | P2/P1 | Missing exact contract. |

## P0 blockers

1. **`/api/v2` proxy mismatch against backend global prefix.** Backend declares `/api/*`; frontend remediation and auth proxy assume `/api/v2/*`. The `app/api/v2/[...path]` proxy currently appends `/api/v2` to the backend base, which likely produces 404s for launch-critical auth/payments/lease/maintenance calls unless deployment routes rewrite it externally.
2. **Auth token storage is still unsafe/inconsistent.** HttpOnly cookie proxy exists, but login still writes token to JS-readable cookie and `localStorage`; a second auth hook reads `localStorage`.
3. **Lease document/signature remains route-present but implementation-stubbed.** Contract route exists, but production behavior is not real.
4. **Backend still permits mock identity headers in CORS.** Frontend no longer appears to send `X-Mock-*`, but backend production CORS should not allow them.

## P1 blockers

1. **Clear namespace mismatches:** frontend `reporting/*` vs backend `reports/*`; frontend `inspections/*` vs backend `inspections-legacy/*`; frontend `estimates/*` has no backend route.
2. **Tours likely double-prefixed:** backend controller `@Controller('api/tours')` under global `/api` probably yields `/api/api/tours/*` while frontend calls `/api/tours/*`.
3. **Policy sub-setting endpoints are missing:** frontend calls `/policy/:id/underwriting`, `/payment-plan`, `/maintenance`, `/denial-compliance`; backend has generic `GET/PATCH /policy/:propertyId` only.
4. **Screening reasoning mismatch:** frontend remediation calls `rental-applications/:id/screening-reasoning`; backend route found under `portal/rental-applications/:id/screening-reasoning`.
5. **Golden-path smoke coverage is absent.** Need executable checks for login, protected admin route, payments remediation, lease doc/signature, maintenance dispatch, dashboard/briefing, and reporting/inspection pages.

## Critical golden-path smoke checks to add

Minimum contract smoke suite should run against a seeded staging backend with real JWTs:

1. `POST /api/auth/login` then `GET /api/auth/me` through the Next `/api/v2/auth/*` proxy and directly against backend canonical `/api/auth/*`.
2. Unauthenticated admin route access: `/payments`, `/leasing`, `/maintenance`, `/reports` redirect/block.
3. Payment remediation: message tenant, record manual payment, Stripe checkout-session, Stripe webhook signed request.
4. Lease launch path: generate lease document, create/send envelope, webhook update, signed document/certificate retrieval.
5. Maintenance: create request, assign vendor, notify tenant/owner, confirm complete.
6. Dashboard/briefing/feed: daily briefing, delinquency queue, action-intents/feed notes.
7. Reporting/inspections: current frontend pages must call backend canonical routes without namespace 404s.
8. CORS/auth: production env rejects `X-Mock-User-Id`/`X-Mock-Role`; every protected backend route requires a bearer JWT and org context.

## Recommended next fixes

1. Choose one canonical API strategy: **recommend backend canonical `/api/*`; Next local proxy `/api/v2/*` may exist only if it rewrites to `/api/*`, not `/api/v2/*`.**
2. Update `app/api/v2/[...path]/route.ts` to normalize configured backend base to `/api`, or add backend v2 prefix explicitly. Then smoke auth/payment/lease.
3. Remove JS-readable auth token writes from login and retire/localize `src/hooks/use-auth.ts` localStorage token reads.
4. Remove `X-Mock-User-Id` and `X-Mock-Role` from production CORS allowed headers.
5. Fix concrete namespace misses: `reporting -> reports`, `inspections -> inspections-legacy` or backend alias, `estimates` controller or hide feature, `policy` subroutes, `screening-reasoning` path, tours double-prefix.

## Validation status

- Static contract probe created and executed successfully.
- No repo code was changed outside `reports/`.
- This is static analysis, not a live HTTP smoke; production readiness still requires seeded staging verification.
