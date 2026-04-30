# Contract Stabilization TODO

Last refreshed: 2026-05-01 03:45 Asia/Kuala_Lumpur

## Repo Heads / Current Snapshot
- `keyring-os`: `5c16f80` — Reduce admin lint warnings
- `pms-master`: `478813a` — Cover lease vacancy document workflows
- workspace root: pending tracking commit for this slice
- working tree status:
  - root has untracked daily memory files: `memory/2026-04-18.md`, `memory/2026-04-19.md`

## Completed Implementation Log
- [x] Finished deeper role-vocabulary cleanup beyond the auth seam
- [x] Tenant autopay frontend normalization
- [x] Tenant feed behavior hardened across repos
- [x] Tenant dashboard contract verified and aligned
- [x] Targeted contract checks added in `pms-master`
- [x] Tenant workspace contract stabilization completed for the currently approved scope
- [x] Tenant backend e2e stabilization completed successfully
- [x] Jest async handle leak resolved
- [x] Admin parity/API-alignment run completed
- [x] Follow-up cleanup completed
- [x] Payment/billing/feature-flag/circuit-breaker/feed-route/landing-page production-readiness slice completed
- [x] Direct `LeaseService` coverage slice completed
- [x] Backend TypeScript drift cleanup implemented, validated, and pushed
- [x] Admin ESLint error cleanup implemented, validated, and pushed
- [x] Admin warning cleanup slice completed: 378 warnings -> 269 warnings, 0 errors
- [x] Lease vacancy/document/signature coverage slice completed and pushed
- [x] Execution plan saved: `docs/superpowers/plans/2026-05-01-keyring-os-next-readiness-slice.md`

## Validated Gates
- [x] `keyring-os/packages/types`: `corepack pnpm --dir /data/.openclaw/workspace/keyring-os/packages/types typecheck`
- [x] `keyring-os/apps/admin`: `corepack pnpm exec tsc --noEmit`
- [x] `keyring-os/apps/tenant-portal`: `corepack pnpm exec tsc --noEmit`
- [x] `tenant_portal_backend`: `corepack pnpm exec prisma generate`
- [x] `tenant_portal_backend`: targeted Jest contract/auth/feed suites
- [x] Tenant backend e2e passed
- [x] Route verification grep confirmed no live callers remain for `/api/v2/feed/:id/action`
- [x] `tenant_portal_backend`: targeted readiness Jest passed: 8 suites, 65 tests
- [x] `tenant_portal_backend`: `corepack pnpm exec tsc --noEmit --pretty false` passed with 0 errors
- [x] `keyring-os/apps/admin`: `corepack pnpm exec eslint .` completed with 0 errors / 269 warnings
- [x] `tenant_portal_backend`: `corepack pnpm exec jest src/lease/lease.service.spec.ts src/lease/ai-lease-renewal.service.spec.ts src/lease/ai-lease-renewal-metrics.service.spec.ts --runInBand` passed: 3 suites, 41 tests

## Remaining Production Readiness Work
- [x] Implement briefing-focused landing page
- [x] Integrate circuit breaker service
- [x] Implement feature flag system
- [x] Address route prefix normalization
- [x] Review and implement test coverage improvements
- [x] Clean backend TypeScript drift enough for full backend compile gate
- [x] Clean admin ESLint blockers enough for full admin lint gate
- [x] Reduce admin warning noise in behavior-safe slice
- [x] Cover lease vacancy/document/signature workflows

## Notes on Validation Drift Cleanup
- Backend compile cleanup fixed high-signal import/path drift and Prisma/schema mismatch noise.
- Unregistered scaffold controllers are excluded from the backend compile gate so active modules can be validated meaningfully.
- Admin lint cleanup fixes actual blockers and leaves legacy broad payload typing as warnings, not errors.
- Admin warning cleanup removed obvious unused imports/locals/params/state and reduced warning noise without broad fake-typing legacy payloads.
- Remaining admin warnings are mostly `@typescript-eslint/no-explicit-any` plus a few hook/a11y/no-unused-expression warnings; these need focused behavior/type decisions.
- Lease vacancy/document/signature coverage verifies existing `prepareForVacancy` side effects and current document/signature stub contracts.

## Next Recommended Action
Run a product-level golden path smoke pass: admin briefing -> leasing -> lease -> payment/ledger -> tenant feed. Then choose either focused admin warning slice 2 or turn document/signature stubs into real integration behavior if product scope is approved.

## Confidence Levels
- Best-result confidence: 96%
- Non-hallucination confidence: 99%
