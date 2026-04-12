# Keyring OS ↔ Tenant Portal Backend Integration Map

Date: 2026-04-12
Scope:
- `pms-master/tenant_portal_backend`
- `keyring-os`

## 1) Canonical architecture map

### Backend: `tenant_portal_backend`
Type: modular NestJS monolith
Primary role: system of record and operational API surface

Core platform layers:
- Auth, roles, org-context guards
- Prisma data access
- Config/env validation
- Middleware: dev mock auth, correlation IDs, legacy path rewriting, performance tracking
- Logging: Winston
- Scheduling: Nest schedule
- Rate limiting: global throttler outside test

Primary business domains:
- Tenant/property ops: `tenant`, `lease`, `property`, `maintenance`, `messaging`, `documents`, `notifications`, `inspections`, `payments`, `billing`
- Admin/manager ops: `leasing`, `rental-application`, `dashboard`, `reporting`, `bookkeeping`, `owner-portal`, `vendors`, `utility-billing`
- Advanced/integrations: `esignature`, `quickbooks`, `workflows`, `property-os`, `policy`, `privacy`, `mil`, `omnichannel`, `smart-devices`, `web3`

Architectural pattern:
- Mostly `controller -> service -> prisma/integration`
- Some aggregation endpoints exist already, especially for feed/briefing/tenant workspace behavior
- Repo is broad and operational, not a greenfield design

Important note:
- `pms-master/prisma/schema.prisma` appears centered on Property OS / workflow-intent structures, not obviously the full tenant-portal relational schema. Treat repo-level schema ownership as a potential architecture confusion point.

### Frontend: `keyring-os`
Type: Next.js workspace via pnpm + Turborepo
Primary role: newer admin and tenant operating surfaces

Workspace structure:
- `apps/admin`
- `apps/tenant-portal`
- `packages/types`
- `packages/ui`
- `packages/config`

Admin app route surfaces:
- `/payments`
- `/leasing`
- `/repairs`
- `/renewals`
- `/screening`
- `/financials`
- `/portfolio`
- `/tenants`
- `/workflows`
- `/reports`
- `/messages`
- `/documents`
- `/inspections`
- `/notifications`
- `/audit-log`

Tenant portal route surfaces:
- `/feed`
- `/lease`
- `/payments`
- `/maintenance`
- `/messages`
- `/documents`
- `/inspections`
- `/notifications`
- `/move-out`

Data access pattern:
- Thin frontend API libraries calling backend directly
- Shared contract intent lives in `packages/types`
- Current implementation still relies partly on dev mock headers

## 2) Canonical endpoint map

### Tenant app -> backend endpoints
Source files:
- `keyring-os/apps/tenant-portal/src/lib/tenant-api.ts`
- `keyring-os/apps/tenant-portal/src/hooks/useTenantFeed.ts`
- `pms-master/tenant_portal_backend/src/tenant/tenant-feed.controller.ts`

Canonical tenant-facing endpoints currently expected by frontend:
- `GET /tenant/feed`
- `GET /tenant/dashboard`
- `GET /leases/my-lease`
- `GET /leases/:leaseId/renewal-offers`
- `POST /leases/:leaseId/renewal-offers/:offerId/respond`
- `POST /leases/:leaseId/tenant-notices`
- `GET /esignature/leases/:leaseId/envelopes`
- `POST /esignature/envelopes/:envelopeId/recipient-view`
- `GET /payments`
- `GET /payments/invoices`
- `GET /payments/ledger/accounts/:leaseId`
- `POST /payments/stripe/checkout-session`
- `GET /billing/autopay`
- `POST /billing/autopay`
- `PATCH /billing/autopay/:leaseId/disable`
- `GET /maintenance`
- `GET /maintenance/:id`
- `POST /maintenance`
- `POST /maintenance/:id/notes`
- `POST /maintenance/:id/confirm-complete`
- `GET /documents`
- `GET /documents/:id/download`
- `GET /notifications`
- `PUT /notifications/:id/read`
- `GET /messaging/conversations`
- `GET /messaging/conversations/:id/messages`
- `POST /messaging/conversations`
- `POST /messaging/conversations/:id/messages`
- `GET /inspections`
- `GET /inspections/:id`

Tenant feed behavior:
- Primary contract is `GET /tenant/feed`
- Fallback synthesis occurs client-side if feed fails or returns empty
- Fallback sources: dashboard, invoices, maintenance, lease, envelopes, renewal offers

Implication:
- Backend already has the right product direction for tenant feed, but frontend still distrusts availability/completeness enough to synthesize locally

### Admin app -> backend endpoints
Source files:
- `keyring-os/apps/admin/src/lib/feed-api.ts`
- `keyring-os/apps/admin/src/lib/copilot-api.ts`
- `pms-master/tenant_portal_backend/src/feed/feed.controller.ts`
- `pms-master/tenant_portal_backend/src/briefing/briefing.controller.ts`

Canonical admin-facing endpoints currently expected by frontend:
- `GET /briefing/daily`
- `GET /api/feed?role=:role` (from `fetchFeed`)
- `GET /api/v2/feed` (briefing fallback path)
- `GET /payments/delinquency/queue`
- `POST /payments/delinquency/issue-notice`
- `GET /payments/ops-summary`
- `GET /payments/invoices`
- `POST /payments/manual`
- `GET /payments/ledger/accounts/:leaseId`
- `GET /leasing/ops-summary`
- `GET /leasing/statistics`
- `GET /leasing/leads`
- `GET /maintenance?sortBy=priority&sortOrder=asc`
- `GET /maintenance?unitId=:id`
- `GET /maintenance?propertyId=:id`
- `GET /maintenance/ai-metrics`
- `GET /estimates`
- `PATCH /estimates/:id/approve`
- `PATCH /estimates/:id/reject`
- `GET /leases`
- `POST /leases`
- `POST /leases/:leaseId/notices`
- `POST /leases/:leaseId/renewal-offers`
- `GET /rental-applications`
- `POST /rental-applications`
- `POST /rental-applications/:id/review-action`
- `GET /screening/:applicationId/policy-evaluation`
- `GET /bookkeeping/workspace`
- `GET /bookkeeping/reconciliation`
- `GET /bookkeeping/chart-of-accounts`
- `PATCH /bookkeeping/transactions/:id/categorize`
- `PATCH /bookkeeping/owner-statements/:id/approve`
- `PATCH /bookkeeping/owner-statements/:id/send`
- `GET /properties`
- `POST /properties`
- `GET /properties/:id`
- `PATCH /properties/:id`
- `GET /properties/:id/rollup`
- `POST /properties/:propertyId/units`
- `PATCH /properties/:propertyId/units/:unitId`
- `GET /properties/units/:unitId/rollup`
- `POST /properties/units/:unitId/transition`
- `GET /workflows`
- `GET /workflows/executions?limit=20`
- `POST /workflows/:id/execute`
- `GET /audit-logs`
- `GET /tenants`
- `GET /tenants/:id`
- `GET /tenants/:id/workspace`
- `GET /tenants/:id/health`
- `GET /tenants/:id/activity`
- `PUT /tenants/:id/profile`
- `POST /tenants/:id/household`
- `POST /tenants/:id/violations`
- `GET /notifications`
- `POST /notifications/read-all`
- `DELETE /notifications/:id`
- `GET /messaging/conversations`
- `GET /messaging/conversations/:id/messages`
- `POST /messaging/conversations`
- `POST /messaging/conversations/:id/messages`
- `GET /documents`
- `POST /documents/upload`
- `GET /documents/:id/download`
- `GET /esignature/risk-queue`
- `PATCH /esignature/envelopes/:id/void`
- `POST /esignature/envelopes/:id/resend`
- `GET /esignature/envelopes/:id/documents/signed`
- `GET /reporting/rent-roll`
- `GET /reporting/profit-loss`
- `GET /reporting/vacancy-rate`
- `GET /reporting/delinquency-analytics`
- `GET /reporting/maintenance-analytics`
- `GET /reporting/payment-history`
- `GET /reporting/analytics/capex`
- `GET /schedule/events`

Admin briefing/feed behavior:
- Primary intended aggregation endpoint is `GET /briefing/daily`
- Frontend has fallback synthesis using delinquency queue + feed + schedule
- There is also feed route drift between `/feed`, `/api/feed`, and `/api/v2/feed`

## 3) Contract and gap analysis

### A. Feed path drift
Observed:
- Backend controller: `@Controller('feed')` => `GET /feed`
- Admin frontend `fetchFeed`: requests `${NEXT_PUBLIC_API_URL}/api/feed?role=...`
- Admin frontend fallback: requests `/api/v2/feed`

Gap:
- Three feed path assumptions for what appears to be one concept
- The frontend type expects `FeedResponse`, while backend `GET /feed` currently appears to return raw Prisma items from `feedItem.findMany`

Impact:
- High. This will create brittle runtime integration and type mismatch.

Recommendation:
- Pick one canonical route, likely `GET /api/feed` or `GET /feed`, then normalize response to `FeedResponse`
- Remove or deprecate alternate paths explicitly

### B. Role naming drift
Observed:
- Shared frontend type `UserRole`: `owner | property_manager | leasing | maintenance`
- Backend roles include uppercase tokens like `TENANT`, `PROPERTY_MANAGER`, `OWNER`, `ADMIN`
- Mock headers in frontend use inconsistent values: `admin`, `tenant`, `PROPERTY_MANAGER`

Gap:
- Role vocabulary is not canonical across frontend types, mock auth, and backend guards

Impact:
- High. This can break feed filtering, access control assumptions, and UI conditional rendering.

Recommendation:
- Define a single canonical role enum and provide a strict frontend/backend mapping layer if legacy values must remain

### C. Auth is not production-integrated yet
Observed:
- Frontend API clients still use `X-Mock-User-Id` and `X-Mock-Role`
- Backend middleware includes `DevMockAuthMiddleware`
- Some server-side comments already note JWT forwarding is still pending

Gap:
- Contract works in development but is not yet a real authentication/session integration

Impact:
- High for production readiness
- Medium for architecture work, because it can hide real authorization problems

Recommendation:
- Decide the auth boundary before large UI expansion
- Prefer one real auth/session flow for both `apps/admin` and `apps/tenant-portal`

### D. Aggregation responsibility is split
Observed:
- Backend already exposes aggregation-style endpoints: `/tenant/feed`, `/briefing/daily`
- Frontend still synthesizes tenant/admin workspaces from many endpoints when primary endpoints fail or are incomplete

Gap:
- Product intent says "workspace APIs", implementation still says "frontend orchestration backup"

Impact:
- Medium to high. It increases frontend complexity and weakens contract clarity.

Recommendation:
- Move toward backend-owned workspace aggregation for priority surfaces:
  - tenant home/feed
  - admin daily briefing
  - payments workspace
  - leasing workspace
  - repairs workspace

### E. Response shape uncertainty
Observed:
- `packages/types` has clearly intended contracts like `FeedResponse`, `TenantFeedResponse`, `BriefingData`
- Some backend endpoints may return raw ORM or ad hoc JSON shapes instead of these contracts

Gap:
- Shared types appear aspirational in some places rather than guaranteed

Impact:
- Medium to high. Frontend fallback code is a symptom of this mismatch.

Recommendation:
- Introduce canonical DTO tests or contract tests between backend responses and `packages/types`

### F. ID type inconsistency
Observed:
- Frontend mixes `string` and `number` IDs across leases, envelopes, inspections, documents, messages
- Backend route params vary across modules

Gap:
- Some entity contracts are not normalized

Impact:
- Medium. This becomes painful in routing, caching, optimistic updates, and typed mutations.

Recommendation:
- Normalize ID conventions per entity and reflect them in shared types

### G. Schema ownership and domain boundary ambiguity
Observed:
- Repo-level Prisma schema appears Property OS centric
- Backend domains are classic PMS + tenant portal + workflow/property-os layers combined

Gap:
- Architecture story is not cleanly separated at repo/data-model level

Impact:
- Medium. This creates confusion during future refactors and data ownership decisions.

Recommendation:
- Clarify whether Property OS is a subsystem inside PMS, or a separate platform layer sharing infra

## 4) Strategic interpretation

Most likely direction:
- `tenant_portal_backend` remains the operational backend and source of truth
- `keyring-os` becomes the newer admin and tenant UI layer
- The product is moving from fragmented CRUD pages toward role-specific operational workspaces

Most important architectural decision still unresolved:
- Is `keyring-os` a full replacement UI, or a parallel experimental surface?

That decision changes:
- how much backend cleanup is worth doing now
- whether to preserve legacy endpoints unchanged
- whether to centralize on workspace APIs immediately

## 5) Recommended next steps

Priority order:
1. Define canonical auth + role vocabulary
2. Define canonical endpoint paths for feed/briefing/workspace APIs
3. Lock response contracts for the top 5 surfaces
4. Reduce frontend fallback synthesis once backend aggregation endpoints are stable
5. Add contract tests between backend DTOs and `keyring-os/packages/types`

Suggested top 5 surfaces to stabilize first:
1. Tenant feed/home
2. Admin daily briefing/feed
3. Payments workspace
4. Leasing/screening workspace
5. Maintenance workspace

## 6) Continuation notes for next session

Best next task:
- Produce a canonical contract matrix with columns:
  - frontend function
  - expected route
  - backend controller/service owner
  - expected response type
  - current mismatch
  - fix priority

Strong candidates to inspect next:
- `pms-master/tenant_portal_backend/src/tenant/tenant-feed.service.ts`
- `pms-master/tenant_portal_backend/src/briefing/briefing.service.ts`
- `pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.ts`
- `keyring-os/apps/admin/src/app/hooks/useCoPilotFeed.ts`
- `keyring-os/apps/admin/src/app/hooks/useBriefing.ts`
- page-level consumers in both admin and tenant apps
