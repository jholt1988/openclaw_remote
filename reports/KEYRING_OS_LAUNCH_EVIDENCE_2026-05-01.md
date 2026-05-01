# Keyring OS Launch Evidence — 2026-05-01

## Verdict

**Not production-ready yet.** Code readiness improved, but production launch remains blocked until seeded staging smoke and real provider verification evidence are produced.

Jordan's standard is explicit: "basically closed" is not closed. A task is only closed when it has reproducible evidence, or is marked blocked with the missing external input.

## Completed in this pass

- Enabled backend `QuickBooksModule` in `AppModule`; `/api/quickbooks/*` is now registered instead of being commented out.
- Updated QuickBooks minimal service test to match intended graceful degraded status behavior on DB read failure.
- Re-ran final local validation gates listed below.
- Confirmed seeded staging smoke cannot execute in this environment because required smoke env/data are not present.

## Validation evidence

### Admin frontend

Command:

```bash
corepack pnpm --filter @keyring/admin lint && \
corepack pnpm --filter @keyring/admin exec tsc --noEmit --pretty false && \
corepack pnpm check:no-mock-auth && \
corepack pnpm --filter @keyring/admin exec next build
```

Result:

- PASS: ESLint completed with **0 errors / 264 warnings**.
- PASS: TypeScript completed.
- PASS: `check:no-mock-auth` found no `X-Mock-User-Id` / `X-Mock-Role` in `apps/admin/src`.
- PASS: Next production build completed and generated 44 routes.
- Non-blocking warning: Next inferred workspace root from multiple lockfiles; can be silenced with `turbopack.root` later.

### Backend targeted production-readiness tests

Command:

```bash
npm test -- --runInBand \
  src/esignature/esignature-webhook.controller.spec.ts \
  src/esignature/esignature-webhook-signature.spec.ts \
  src/lease/lease.service.spec.ts \
  src/payments/payments.controller.spec.ts \
  src/payments/stripe.service.spec.ts
npm run build
```

Result:

- PASS: 5 suites passed.
- PASS: 44 tests passed, 2 skipped.
- PASS: backend TypeScript build completed.

### QuickBooks module activation

Command:

```bash
npm test -- --runInBand src/quickbooks/quickbooks-minimal.service.spec.ts
npm run build
```

Result:

- PASS: 1 suite passed.
- PASS: 16 tests passed.
- PASS: backend TypeScript build completed with `QuickBooksModule` imported into `AppModule`.

### Static contract probe

Command:

```bash
python3 reports/keyring_contract_probe_2026_05_01.py
```

Result:

- PASS: 183 frontend call sites scanned.
- PASS: 597 backend route declarations scanned.
- PASS: 0 potential misses.

### Seeded golden-path staging smoke

Command attempted:

```bash
npm run smoke:golden-path
```

Result:

- BLOCKED: `SMOKE_JWT is required. Run this against a seeded staging env, not an empty database.`

Required inputs:

- `SMOKE_BASE_URL`
- `SMOKE_JWT`
- `SMOKE_PAYMENT_ID`
- `SMOKE_LEASE_ID`
- `SMOKE_MAINTENANCE_ID`
- `SMOKE_VENDOR_ID`
- `SMOKE_INSPECTION_ID`
- optional `SMOKE_PROPERTY_ID`

## Remaining launch blockers

### 1. Seeded staging smoke execution

Status: **blocked by missing staging URL/JWT/seed IDs**.

Acceptance criteria:

- `npm run smoke:golden-path` passes against seeded staging.
- Output is attached to the release record.
- Any failed route is fixed or explicitly waived with a named owner and reason.

### 2. DocuSign sandbox verification

Status: **blocked by missing provider sandbox credentials/callback evidence**.

Acceptance criteria:

- Deployed callback receives DocuSign Connect webhook with `X-DocuSign-Signature-1`.
- Invalid signature is rejected.
- Envelope create/send/status path works against sandbox or production-equivalent staging.
- Required envs are present: `ESIGN_PROVIDER_BASE_URL`, account/user/auth credentials, and `ESIGN_WEBHOOK_SECRET` or `DOCUSIGN_CONNECT_SECRET`.

### 3. QuickBooks sandbox verification

Status: **blocked by missing QuickBooks sandbox OAuth/company evidence**.

Acceptance criteria:

- `/api/quickbooks/auth-url` returns a valid Intuit sandbox OAuth URL.
- OAuth callback stores an active connection.
- `/api/quickbooks/status` returns connected state for the seeded org.
- `/api/quickbooks/sync` completes or fails with an expected provider error that is documented.

### 4. Stripe production secret verification

Status: **locally tested, still needs environment evidence**.

Acceptance criteria:

- Production/staging env has `STRIPE_SECRET_KEY` and webhook secret configured, or a documented explicit override.
- Startup/runtime evidence confirms missing/disabled Stripe fails fast in production.

## Launch decision

Do **not** promote to production yet.

The remaining blockers are external-operational, not static code-contract blockers. The next unlock is providing seeded staging smoke variables and provider sandbox credentials/evidence so the actual end-to-end flows can be run and recorded.
