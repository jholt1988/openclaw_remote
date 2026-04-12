# Contract Stabilization Todo Anchor

Last updated: 2026-04-12 22:17 GMT+8

## Project
Stabilize the integration contract between:
- `pms-master/tenant_portal_backend`
- `keyring-os`

Tracking repo for issues:
- `openclaw_remote`

## Original prompt / goal
Original user direction for this work:
- Focus on `pms-master/tenant_portal_backend` and `keyring-os`
- Inspect the integration seams
- Identify contract drift and implementation gaps
- Then directly implement fixes, commit, push, and keep proceeding

Operational goal that emerged from the work:
- Treat `tenant_portal_backend` as the backend source of truth
- Treat `keyring-os` as the newer frontend layer
- Remove high-risk contract drift between them, especially around:
  - feed route and response shape
  - feed action execution
  - screening policy-evaluation route
  - auth/role normalization
  - checkout response DTOs

## Repos / resources in use
Workspace:
- `/data/.openclaw/workspace`

Repos:
- `/data/.openclaw/workspace/pms-master`
- `/data/.openclaw/workspace/keyring-os`
- outer repo: `/data/.openclaw/workspace` (`openclaw_remote`)

Key reports/artifacts:
- `reports/KEYRING_OS_BACKEND_INTEGRATION_MAP_2026-04-12.md`
- `reports/KEYRING_OS_CONTRACT_MATRIX_2026-04-12.md`
- `reports/KEYRING_OS_IMPLEMENTATION_BACKLOG_2026-04-12.md`
- `reports/KEYRING_OS_GITHUB_ISSUES_2026-04-12.md`
- `reports/KEYRING_OS_ISSUE_DRAFTS_2026-04-12.md`

Issue tracker:
- `https://github.com/jholt1988/openclaw_remote/issues`

## Key decisions made
- Canonical admin feed route normalized around `/feed`
- Canonical admin feed response shape normalized to:
  - `{ items, role, generatedAt }`
- Keep compatibility routes only where they reduce rollout risk
- Screening policy-evaluation should use:
  - `GET /rental-applications/:id/policy-evaluation`
- Fix the frontend to match the richer checkout DTO instead of adding more backend aliases
- Normalize the highest-risk auth seam first:
  - frontend dev/mock headers
  - backend mock auth normalization
- Active admin feed action model is direct domain mutation, not the old generic feed-action abstraction
- Legacy `api/v2/feed` action controller is compatibility-only

## User instructions that matter
- Prefer direct execution over long planning loops
- Keep proceeding when the next step is clear
- Update GitHub issues in `openclaw_remote`
- Append responses with two confidence ratings:
  - best-result confidence
  - non-hallucination confidence
- User preference: avoid responses below roughly 85%-70% confidence unless necessary
- Current instruction: continue the work without reporting back until done or blocked

## Completed implementation log
### Analysis / planning artifacts
- `openclaw_remote@8badbbe`
  - Add keyring-os contract matrix handoff

### Feed contract stabilization
- `keyring-os@7dd843e`
  - Normalize admin feed contract usage
- `pms-master@606f288`
  - Add canonical feed response and module wiring
- `openclaw_remote@f8e3779`
  - Update submodule pointers for feed contract implementation

### Policy evaluation route normalization
- `keyring-os@f18d62a`
  - Use canonical rental application policy route
- `pms-master@14bfebb`
  - Align policy evaluation API route
- `openclaw_remote@eb9949e`
  - Update submodules for policy evaluation route fix

### Role normalization at auth seam
- `keyring-os@ca4051c`
  - Normalize dev mock auth role headers
- `pms-master@27c3b7b`
  - Normalize mock auth roles to canonical values
- `openclaw_remote@2aef7e4`
  - Update submodules for role normalization fix

### Feed action contract hardening
- `pms-master@55b825e`
  - Fix canonical feed action mapping
- `openclaw_remote@728a6fd`
  - Update submodule for feed action mapping fix

### Checkout response alignment
- `keyring-os@490e193`
  - Align tenant checkout session contract
- `openclaw_remote@4ebbf74`
  - Update submodule for checkout contract fix

### Contract safety net / cleanup
- `pms-master@218143e`
  - Add contract tests for stabilized API surfaces
- `openclaw_remote@341c24a`
  - Update submodule for contract test pass

## Issue tracker status in `openclaw_remote`
Closed:
- `#10` Define canonical admin feed contract
- `#9` Normalize backend admin feed response to canonical FeedResponse
- `#8` Update frontend admin feed client to use one canonical route
- `#5` Normalize screening policy evaluation route
- `#1` Align Stripe checkout session response contract
- `#6` Implement canonical feed action mutation path or remove dead frontend assumption

Still open, with progress notes:
- `#4` Define canonical role enum and serialization strategy
- `#3` Normalize frontend role usage, mock auth headers, and fixtures
- `#2` Normalize backend role guards and ingress role parsing
- `#7` Inventory and classify all admin feed actions

## Remaining todo
### Highest priority
- [x] Finish the deeper role-vocabulary cleanup beyond the auth seam
  - canonical shared auth roles: `ADMIN`, `OWNER`, `PROPERTY_MANAGER`, `TENANT`
  - `leasing`, `maintenance`, and `operator` are treated as legacy personas/workspaces, not auth roles
  - shared frontend types and backend normalization now emit canonical uppercase roles
- [x] Audit frontend role usage and fixtures beyond current active mock-auth paths
- [x] Audit backend role parsing/guards beyond `MockAuthGuard`
- [x] Decide whether the legacy `feed-action.controller` should stay temporarily or be removed fully
- [x] Write down the feed action inventory explicitly if issue `#7` should be fully closed

### Validation / cleanup
- [x] Run the strongest local validation available in a dependency-installed environment
- [x] Confirm no remaining live callers depend on removed/drifting routes
- [ ] Re-check `openclaw_remote` issues after the next implementation pass / push

## Validation completed in this pass
- `keyring-os/packages/types`: `corepack pnpm --dir /data/.openclaw/workspace/keyring-os/packages/types typecheck`
- `keyring-os/apps/admin`: `corepack pnpm exec tsc --noEmit`
- `tenant_portal_backend`: `corepack pnpm exec prisma generate`
- `tenant_portal_backend`: `corepack pnpm exec jest src/auth/mock-auth.guard.spec.ts src/auth/roles.guard.spec.ts src/feed/feed-aggregator.service.spec.ts test/property-os-v16-contract.spec.ts --runInBand`
- Route verification grep confirmed no live callers remain for `/api/v2/feed/:id/action`, `executeFeedAction`, or `feed-actions`

## Current known limitation
The strongest targeted validations now pass locally. A full monorepo-wide test sweep was still not run because it is materially broader than the stabilized contract surface.

## Current repo heads
- `openclaw_remote@341c24a`
- `keyring-os@490e193`
- `pms-master@218143e`

## Notes for future continuation
If context compacts, resume from this file first.
Recommended next active task:
1. push the final repo set and let the outer-repo issue-closing commit close the remaining role/inventory issues
2. if desired afterward, run broader monorepo validation outside the stabilized contract slice
