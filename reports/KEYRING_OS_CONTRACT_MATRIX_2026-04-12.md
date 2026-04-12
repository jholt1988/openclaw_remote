# Keyring OS ↔ Tenant Portal Backend Contract Matrix

Date: 2026-04-12
Scope:
- `pms-master/tenant_portal_backend`
- `keyring-os`

Purpose:
- convert the prior architecture/integration map into an execution-ready contract matrix
- identify canonical route, backend owner, expected type, current mismatch, and fix priority

---

## 1) Top-surface summary

Priority surfaces to stabilize first:
1. Tenant feed/home
2. Admin daily briefing/feed
3. Payments workspace
4. Leasing/screening workspace
5. Maintenance workspace

Strongest pattern observed:
- the frontend is already organized around role-specific workspaces
- the backend already contains several aggregation endpoints
- the main instability is not missing business logic, it is contract drift

---

## 2) Contract matrix

## A. Tenant feed / home

### A1. Tenant feed
- Frontend function:
  - `fetchTenantFeed()`
  - `useTenantFeed()`
- Frontend route consumers:
  - tenant portal `/feed`
- Expected route:
  - `GET /tenant/feed`
- Backend owner:
  - controller: `src/tenant/tenant-feed.controller.ts`
  - service: `src/tenant/tenant-feed.service.ts`
- Expected response type:
  - `TenantFeedResponse`
- Current backend behavior:
  - returns `{ items, generatedAt }`
  - items are scored/prioritized server-side
- Current mismatch:
  - low mismatch on shape, this is one of the cleaner contracts
  - frontend still has fallback synthesis if endpoint fails or returns empty
- Fix priority:
  - P1
- Recommended fix:
  - treat `/tenant/feed` as canonical
  - improve reliability/completeness so frontend fallback can eventually be removed

### A2. Tenant dashboard
- Frontend function:
  - `fetchTenantDashboard()`
- Expected route:
  - `GET /tenant/dashboard`
- Backend owner:
  - likely `src/dashboard/tenant-dashboard.controller.ts` or related tenant/dashboard service layer
- Expected response type:
  - `TenantDashboard`
- Current mismatch:
  - not yet verified in this pass at controller level
  - currently used as fallback source for feed synthesis
- Fix priority:
  - P2
- Recommended fix:
  - verify route ownership and shape
  - decide whether dashboard remains a first-class page contract or only a feed synthesis helper

### A3. Tenant lease composite surface
- Frontend functions:
  - `fetchMyLease()`
  - `fetchRenewalOffers()`
  - `fetchSigningEnvelopes()`
  - `submitMoveOutNotice()`
- Expected routes:
  - `GET /leases/my-lease`
  - `GET /leases/:leaseId/renewal-offers`
  - `GET /esignature/leases/:leaseId/envelopes`
  - `POST /leases/:leaseId/tenant-notices`
- Backend owner:
  - likely `lease.controller.ts` + `esignature.controller.ts`
- Expected response type:
  - `Lease`, `RenewalOffer[]`, `EsignEnvelope[]`
- Current mismatch:
  - not yet deeply verified in this pass
  - frontend depends on them for both lease page and feed fallback logic
- Fix priority:
  - P2
- Recommended fix:
  - verify response DTOs and role access for tenant path

### A4. Tenant payments
- Frontend functions:
  - `fetchPayments()`
  - `fetchInvoices()`
  - `fetchLedger()`
  - `createStripeCheckoutSession()`
  - `fetchAutopay()` / `enableAutopay()` / `disableAutopay()`
- Expected routes:
  - `GET /payments`
  - `GET /payments/invoices`
  - `GET /payments/ledger/accounts/:leaseId`
  - `POST /payments/stripe/checkout-session`
  - billing autopay routes
- Backend owner:
  - `src/payments/payments.controller.ts`
  - billing controller not inspected in this pass
- Expected response type:
  - payment/invoice lists, operational ledger account, checkout session URL
- Current mismatch:
  - concrete mismatch already found: frontend expects `{ url: string }` for checkout session, backend returns `{ checkoutUrl, sessionId, invoiceId }`
- Fix priority:
  - P1
- Recommended fix:
  - standardize checkout session response or adapt frontend now

### A5. Tenant maintenance
- Frontend functions:
  - `fetchMaintenanceRequests()`
  - `fetchMaintenanceRequest()`
  - `createMaintenanceRequest()`
  - `addMaintenanceNote()`
  - `confirmMaintenanceComplete()`
- Expected routes:
  - `GET /maintenance`
  - `GET /maintenance/:id`
  - `POST /maintenance`
  - `POST /maintenance/:id/notes`
  - `POST /maintenance/:id/confirm-complete`
- Backend owner:
  - `src/maintenance/maintenance.controller.ts`
- Expected response type:
  - tenant-scoped maintenance records and mutation responses
- Current mismatch:
  - low to medium risk, controller is tenant-aware and role-scoped
  - frontend shape assumptions still need DTO verification
- Fix priority:
  - P2
- Recommended fix:
  - keep as canonical tenant maintenance contract
  - add explicit DTO contract checks

### A6. Tenant messages
- Frontend functions:
  - `fetchConversations()`
  - `fetchMessages()`
  - `createConversation()`
  - `sendMessage()`
- Expected routes:
  - `GET /messaging/conversations`
  - `GET /messaging/conversations/:id/messages`
  - `POST /messaging/conversations`
  - `POST /messaging/conversations/:id/messages`
- Backend owner:
  - `src/messaging/messaging.controller.ts`
- Current mismatch:
  - not inspected in this pass
  - known prior history suggests this area has had participant visibility issues before
- Fix priority:
  - P2
- Recommended fix:
  - verify exact response shapes and participant scoping

---

## B. Admin daily briefing / feed

### B1. Admin briefing
- Frontend function:
  - `fetchBriefing()`
  - `useBriefing()`
- Frontend route consumers:
  - admin home / workspace surfaces
- Expected route:
  - `GET /briefing/daily`
- Backend owner:
  - controller: `src/briefing/briefing.controller.ts`
  - service: `src/briefing/briefing.service.ts`
- Expected response type:
  - `BriefingData`
- Current backend behavior:
  - returns `{ signals, decisions, events, metrics }`
  - pulls from invoices, emergency maintenance, expiring leases, rental applications, repair estimates, schedule events, bookkeeping financial signals/decisions/events
- Current mismatch:
  - this is structurally close to the frontend type and is the strongest admin aggregation contract found so far
  - fallback logic still exists in frontend because reliability/completeness is not trusted yet
- Fix priority:
  - P1
- Recommended fix:
  - make `/briefing/daily` the single canonical admin home briefing contract
  - reduce fallback synthesis once verified end to end

### B2. Admin feed
- Frontend functions:
  - `fetchFeed()` in `feed-api.ts`
  - `useCoPilotFeed()`
- Expected route(s), currently inconsistent:
  - `/api/feed?role=...`
  - `/api/v2/feed`
- Backend owner:
  - controller: `src/feed/feed.controller.ts`
  - service: `src/feed/feed-aggregator.service.ts`
- Actual backend route found:
  - `GET /feed`
- Expected response type:
  - `FeedResponse`
- Current backend behavior:
  - appears to return raw `feedItem.findMany(...)`
- Current mismatch:
  - route drift: `/feed` vs `/api/feed` vs `/api/v2/feed`
  - shape drift: raw ORM list vs `FeedResponse { items, role, generatedAt }`
  - role vocabulary drift in filtering/access
- Fix priority:
  - P0
- Recommended fix:
  - pick one canonical feed route
  - wrap backend results in the shared `FeedResponse` DTO
  - align role enum and casing before further UI work

### B3. Admin feed actions
- Frontend function:
  - `performAction` inside `useCoPilotFeed()`
- Expected route:
  - `POST /api/feed/actions`
- Backend owner:
  - not found in inspected controller set
- Current mismatch:
  - likely missing route or indirect implementation path
  - backend inspected route only includes `PATCH /feed/:id/notes`
- Fix priority:
  - P0
- Recommended fix:
  - either implement canonical feed-action mutation route or remove dead frontend assumption

---

## C. Payments workspace

### C1. Payments workspace aggregate
- Frontend functions:
  - `fetchPaymentsWorkspace()`
  - `usePaymentsWorkspace()`
- Current frontend composition:
  - `GET /payments/delinquency/queue`
  - `GET /payments/ops-summary`
  - `GET /payments/invoices`
- Backend owner:
  - `src/payments/payments.controller.ts`
- Expected response type:
  - currently frontend-composed ad hoc workspace object
- Current mismatch:
  - no single canonical payments workspace endpoint, frontend composes one itself
- Fix priority:
  - P1
- Recommended fix:
  - create a backend-owned payments workspace DTO/endpoint, or formally bless frontend composition as the stable pattern

### C2. Delinquency queue
- Frontend functions:
  - `fetchPaymentsWorkspace()`
  - `fetchBriefing()` fallback
- Expected route:
  - `GET /payments/delinquency/queue`
- Backend owner:
  - `payments.controller.ts`
- Current mismatch:
  - low route mismatch
  - shape may vary between queue buckets and item summaries used by different UI consumers
- Fix priority:
  - P2
- Recommended fix:
  - document queue response DTO and reuse it across payments + briefing consumers

### C3. Manual payments / notices
- Frontend functions:
  - `logManualPayment()`
  - `issueDelinquencyNotice()`
- Expected routes:
  - `POST /payments/manual`
  - `POST /payments/delinquency/issue-notice`
- Backend owner:
  - `payments.controller.ts`
- Current mismatch:
  - low route mismatch found
  - auth/role assumptions still depend on inconsistent role casing in frontend mocks
- Fix priority:
  - P2

---

## D. Leasing / screening workspace

### D1. Leasing workspace aggregate
- Frontend functions:
  - `fetchLeasingWorkspace()`
  - `useLeasingWorkspace()`
- Current frontend composition:
  - `GET /leasing/ops-summary`
  - `GET /leasing/statistics`
  - `GET /leasing/leads`
- Backend owner:
  - `src/leasing/leasing.controller.ts`
- Current mismatch:
  - no single canonical leasing workspace endpoint, frontend composes it
  - controller supports both `api/leasing` and `leasing`, which is useful but leaves path governance loose
- Fix priority:
  - P1
- Recommended fix:
  - pick canonical public path family and freeze it
  - decide if leasing remains frontend-composed or becomes backend-aggregated

### D2. Screening workspace aggregate
- Frontend functions:
  - `fetchScreeningWorkspace()`
  - `useScreeningWorkspace()`
- Current frontend composition:
  - `GET /rental-applications`
- Backend owner:
  - `src/rental-application/rental-application.controller.ts`
- Current mismatch:
  - low on core list route
  - deeper mismatch found for policy evaluation path
- Fix priority:
  - P1

### D3. Policy evaluation
- Frontend function:
  - `fetchPolicyEvaluation(applicationId)`
- Frontend expected route:
  - `GET /screening/:applicationId/policy-evaluation`
- Backend actual route found:
  - `GET /rental-applications/:id/policy-evaluation`
- Backend owner:
  - `rental-application.controller.ts`
- Current mismatch:
  - hard route mismatch
- Fix priority:
  - P0
- Recommended fix:
  - either update frontend to `/rental-applications/:id/policy-evaluation` or add compatibility alias on backend

### D4. Review actions
- Frontend function:
  - `reviewApplication()`
- Frontend expected route:
  - `POST /rental-applications/:id/review-action`
- Backend actual route:
  - matches exactly
- Fix priority:
  - P2

---

## E. Maintenance workspace

### E1. Repairs workspace aggregate
- Frontend functions:
  - `fetchRepairsWorkspace()`
  - `useRepairsWorkspace()`
- Current frontend composition:
  - `GET /maintenance?sortBy=priority&sortOrder=asc`
  - `GET /estimates`
  - `GET /maintenance/ai-metrics`
- Backend owner:
  - maintenance controller verified
  - estimate route likely `inspection/estimate.controller.ts`
- Current mismatch:
  - no single canonical repairs workspace endpoint
  - maintenance filter parser in inspected controller supports status/priority/propertyId/unitId/etc, but not obviously `sortBy`/`sortOrder`
- Fix priority:
  - P1
- Recommended fix:
  - verify whether sort params are ignored, unsupported, or implemented deeper in service
  - either add canonical repairs workspace endpoint or document supported filter contract precisely

### E2. Maintenance list/detail/mutations
- Frontend functions:
  - fetch/create/update-style maintenance functions across admin and tenant apps
- Expected routes:
  - `GET /maintenance`
  - `GET /maintenance/:id`
  - `POST /maintenance`
  - `POST /maintenance/:id/notes`
  - `PATCH /maintenance/:id/status`
  - `PATCH /maintenance/:id/assign`
  - `POST /maintenance/:id/confirm-complete`
- Backend owner:
  - `maintenance.controller.ts`
- Current mismatch:
  - low to medium, backend is clearly role-aware and mature here
  - still need DTO verification for page consumers
- Fix priority:
  - P2

---

## 3) Cross-cutting contract risks

### R1. Route family drift
Observed examples:
- `/feed` vs `/api/feed` vs `/api/v2/feed`
- `/screening/:id/policy-evaluation` vs `/rental-applications/:id/policy-evaluation`
- `api/leasing` and `leasing` dual-controller paths

Priority:
- P0

Recommendation:
- define one canonical path per capability
- add temporary compatibility aliases only when necessary
- document deprecation windows

### R2. Role vocabulary drift
Observed examples:
- frontend type roles: `owner | property_manager | leasing | maintenance`
- backend guard roles: `TENANT`, `PROPERTY_MANAGER`, `OWNER`, `ADMIN`
- mock headers: `admin`, `tenant`, `PROPERTY_MANAGER`

Priority:
- P0

Recommendation:
- define canonical role enum + casing strategy
- expose an explicit frontend/backend mapping if legacy names must coexist

### R3. Dev-auth scaffolding still in the main path
Observed:
- mock headers used in frontend libraries
- dev auth middleware exists in backend

Priority:
- P1

Recommendation:
- stabilize auth before broadening UI surface area

### R4. Shared types are partly aspirational
Observed:
- `packages/types` defines strong shapes
- some backend routes appear to return ad hoc or raw ORM shapes instead of those contracts

Priority:
- P1

Recommendation:
- add DTO-level contract tests for top surfaces

### R5. ID-type inconsistency
Observed:
- strings and numbers mixed across entities and frontend types

Priority:
- P2

Recommendation:
- normalize by entity, then update shared types and route params accordingly

---

## 4) Execution recommendation

Fix in this order:
1. Admin feed route + shape normalization
2. Policy evaluation route mismatch
3. Role vocabulary normalization
4. Payments checkout response mismatch
5. Decide whether top workspaces are backend-aggregated or frontend-composed

If speed matters most:
- add compatibility shims first
- then clean up contracts under test

If architecture matters most:
- define canonical contracts first
- then refactor frontend and backend to match exactly

---

## 5) Best next task after this report

Create an implementation backlog with one ticket per P0/P1 mismatch:
- normalize admin feed route and response DTO
- implement/replace missing feed action mutation path
- fix policy evaluation route mismatch
- normalize role names across frontend types, mock auth, and backend guards
- align payments checkout response contract
- decide canonical workspace aggregation strategy for payments, leasing, repairs
