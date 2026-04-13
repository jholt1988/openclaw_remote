# Keyring OS Tenant Workspace Contract Matrix

Date: 2026-04-13
Scope:
- `keyring-os/apps/tenant-portal`
- `pms-master/tenant_portal_backend`

Purpose:
- convert the next tenant-facing integration lane into an execution-grade contract matrix
- identify concrete frontend/backend drifts after the admin-feed stabilization pass
- recommend the next implementation order

---

## 1) Strongest direct answer

The next highest-leverage work is the tenant workspace contract lane.

What I verified in this pass:
- the tenant feed and tenant dashboard routes are real backend-owned contracts
- several tenant surfaces are still shape-fragile or rely on frontend fallback synthesis
- there are at least **three concrete contract mismatches** worth fixing next, not just abstract risk:
  1. tenant messaging create payload mismatch
  2. inspections list shape mismatch
  3. tenant feed still falls back to frontend synthesis when `/tenant/feed` is empty/failing

---

## 2) Canonical surface matrix

## A. Tenant feed and home

### A1. Tenant feed
- Frontend:
  - `fetchTenantFeed()` in `src/lib/tenant-api.ts`
  - `useTenantFeed()` in `src/hooks/useTenantFeed.ts`
- Frontend route consumers:
  - `/feed`
- Backend route:
  - `GET /tenant/feed`
- Backend owner:
  - `src/tenant/tenant-feed.controller.ts`
  - `src/tenant/tenant-feed.service.ts`
- Current status:
  - canonical route exists and is tenant-scoped
  - frontend still falls back to synthesized feed items when the endpoint errors or returns zero items
- Concrete drift:
  - the frontend still treats backend feed reliability/completeness as insufficient
- Risk:
  - medium
- Recommendation:
  - keep `GET /tenant/feed` as canonical
  - reduce the fallback path by making the backend feed complete enough to own the workspace feed fully

### A2. Tenant dashboard
- Frontend:
  - `fetchTenantDashboard()`
- Backend route:
  - `GET /tenant/dashboard`
- Backend owner:
  - `src/dashboard/tenant-dashboard.controller.ts`
  - `src/dashboard/dashboard.service.ts`
- Current status:
  - real backend-owned aggregation route exists
  - still used partly as fallback feed input, not just as a page contract
- Concrete drift:
  - dashboard is serving double duty: page contract plus feed-synthesis ingredient
- Risk:
  - medium
- Recommendation:
  - decide explicitly whether dashboard remains page-only or continues feeding tenant-feed synthesis

---

## B. Payments and billing

### B1. Payments list / invoices / ledger
- Frontend:
  - `fetchPayments()` -> `GET /payments`
  - `fetchInvoices()` -> `GET /payments/invoices`
  - `fetchLedger()` -> `GET /payments/ledger/accounts/:leaseId`
- Backend owner:
  - `src/payments/payments.controller.ts`
- Current status:
  - routes exist and are tenant-accessible
- Concrete drift:
  - ledger is already defensive on frontend because backend may return either an array or an object envelope with `entries`
- Risk:
  - medium
- Recommendation:
  - pick one ledger response shape and document it in shared types

### B2. Stripe checkout session
- Frontend:
  - `createStripeCheckoutSession()`
  - payments page consumes `checkoutUrl`
- Backend route:
  - `POST /payments/stripe/checkout-session`
- Backend owner:
  - `src/payments/payments.controller.ts`
- Current status:
  - previously mismatched, now aligned in the tenant frontend helper to `{ checkoutUrl, sessionId, invoiceId }`
- Risk:
  - low
- Recommendation:
  - keep this shape stable and add shared contract typing/tests if this lane is revisited

### B3. Autopay
- Frontend:
  - `GET /billing/autopay`
  - `POST /billing/autopay`
  - `PATCH /billing/autopay/:leaseId/disable`
- Backend owner:
  - `src/billing/billing.controller.ts`
- Current status:
  - routes exist and tenant access is explicit
- Concrete drift:
  - frontend type expects a flattened `AutopayEnrollment`, while backend tenant response may be a richer billing-service object depending on implementation path
- Risk:
  - medium
- Recommendation:
  - verify the exact tenant response body and either flatten it intentionally or widen the frontend type

---

## C. Lease and move-out flows

### C1. My lease
- Frontend:
  - `fetchMyLease()` -> `GET /leases/my-lease`
- Backend owner:
  - `src/lease/lease.controller.ts`
- Current status:
  - route exists and is tenant-only
  - controller intentionally returns `null` when no lease exists
- Risk:
  - low
- Recommendation:
  - treat this as canonical and keep nullability explicit in shared types

### C2. Renewal offers and tenant notices
- Frontend:
  - `GET /leases/:leaseId/renewal-offers`
  - `POST /leases/:leaseId/renewal-offers/:offerId/respond`
  - `POST /leases/:leaseId/tenant-notices`
- Backend owner:
  - `src/lease/lease.controller.ts`
- Current status:
  - tenant response / submission routes exist in the controller
- Unknown still needing verification:
  - `GET /leases/:leaseId/renewal-offers` route was used by frontend but not verified in the read slice here
- Risk:
  - medium
- Recommendation:
  - verify that the read path exists and matches the frontend assumptions before deeper tenant rollout work

---

## D. Maintenance

### D1. Maintenance list/detail/create
- Frontend:
  - `GET /maintenance`
  - `GET /maintenance/:id`
  - `POST /maintenance`
  - `POST /maintenance/:id/notes`
  - `POST /maintenance/:id/confirm-complete`
- Backend owner:
  - `src/maintenance/maintenance.controller.ts`
- Current status:
  - surface appears intentionally tenant-facing and is already wired into feed fallback synthesis
- Concrete drift:
  - no confirmed route break found in this pass, but frontend types are still optimistic and not driven by shared DTOs
- Risk:
  - medium
- Recommendation:
  - keep this surface, but add explicit DTO contract verification if we implement tenant contract tests next

---

## E. Documents

### E1. Documents list/download
- Frontend:
  - `GET /documents`
  - `GET /documents/:id/download`
- Backend owner:
  - `src/documents/documents.controller.ts`
- Current status:
  - routes exist and are auth-protected
- Concrete drift:
  - document listing is generic and not obviously tenant-shaped; frontend assumes a simple array of `{ id, name, fileType, category, createdAt }`
- Risk:
  - medium
- Recommendation:
  - define a tenant document list DTO explicitly so tenant portal is not depending on broad internal document entity shape

---

## F. Notifications

### F1. Notifications list/read
- Frontend:
  - `GET /notifications`
  - `PUT /notifications/:id/read`
- Backend owner:
  - `src/notifications/notifications.controller.ts`
- Current status:
  - routes exist and list endpoint returns a bare array (`result.data`)
- Concrete drift:
  - frontend marks all read by iterating `PUT /:id/read`, while backend already has `POST /notifications/read-all`
- Risk:
  - low to medium
- Recommendation:
  - switch frontend to the dedicated `read-all` endpoint to reduce request fanout and align intent

### F2. Unread count
- Frontend:
  - tenant header references notification unread queries
- Backend route:
  - `GET /notifications/unread-count`
- Current status:
  - route exists
- Recommendation:
  - use this as canonical for header badges instead of deriving count from the full list whenever practical

---

## G. Messaging

### G1. Conversations list
- Frontend:
  - `fetchConversations()` -> `GET /messaging/conversations`
- Backend owner:
  - `src/messaging/messaging.controller.ts`
- Current status:
  - route exists
  - backend supports versioned shapes using `X-API-Version`
  - v1 returns a bare array, v2 returns `{ data, pagination, meta }`
- Concrete drift:
  - frontend assumes v1 bare array and ignores the versioning path entirely
- Risk:
  - medium
- Recommendation:
  - either lock tenant portal to v1 intentionally or upgrade it deliberately to v2 envelope support

### G2. Create conversation
- Frontend:
  - `createConversation({ subject, content })`
- Backend route:
  - `POST /messaging/conversations`
- Backend DTO:
  - `CreateConversationDto { participantIds: string[]; initialMessage?: string }`
- Concrete mismatch:
  - **hard mismatch**: frontend sends `{ subject, content }`, backend expects `participantIds` and optional `initialMessage`
- Risk:
  - high, concrete
- Recommendation:
  - fix this next
  - likely options:
    1. switch frontend to `POST /messaging/threads` using `{ recipientId or participantIds, content, subject }`
    2. or reshape the backend create-conversation contract to match the tenant UI intent
- Recommendation strength:
  - prefer option 1, because `CreateThreadDto` already matches the tenant UX better

### G3. Messages list/send
- Frontend:
  - `GET /messaging/conversations/:id/messages`
  - `POST /messaging/conversations/:id/messages`
- Backend owner:
  - `src/messaging/messaging.controller.ts`
- Current status:
  - routes exist and are structurally compatible with the current frontend helper
- Risk:
  - low

---

## H. Inspections

### H1. Inspections list
- Frontend:
  - `fetchInspections()` expects `Inspection[]`
- Backend route:
  - `GET /inspections`
- Backend owner:
  - `src/inspection/inspection.controller.ts`
- Current status:
  - backend intentionally returns an envelope, not a bare array:
    - `data`
    - `items`
    - `meta`
    - plus other fields from the service result
- Concrete mismatch:
  - **hard mismatch**: frontend expects `Inspection[]`, backend returns an object envelope
- Risk:
  - high, concrete
- Recommendation:
  - fix this next by either:
    1. adapting frontend to accept the envelope and read `data` or `items`, or
    2. freezing a canonical bare-array tenant route and removing the envelope ambiguity
- Recommendation strength:
  - prefer adapting frontend now, because backend is already carrying a compatibility envelope for mixed clients

### H2. Inspection detail
- Frontend:
  - `GET /inspections/:id`
- Backend owner:
  - `src/inspection/inspection.controller.ts`
- Current status:
  - route exists and looks compatible at a high level
- Risk:
  - medium
- Recommendation:
  - verify field-level DTO alignment when the list mismatch is fixed

---

## 3) Prioritized next implementation queue

## P0, fix next
1. **Messaging create flow**
   - frontend `createConversation()` payload is incompatible with backend `CreateConversationDto`
   - likely fix: switch tenant portal to `POST /messaging/threads`

2. **Inspections list fetcher**
   - frontend expects `Inspection[]`
   - backend returns envelope object
   - adapt tenant fetcher to normalize the envelope

## P1, fix after P0
3. **Tenant feed ownership**
   - reduce frontend synthesis fallback by improving `/tenant/feed` completeness and reliability

4. **Autopay response contract**
   - verify tenant autopay response shape and align type intentionally

5. **Notifications mark-all-read**
   - move frontend from N individual `PUT` calls to backend `POST /notifications/read-all`

## P2, verify and then normalize
6. lease read-path DTOs
7. tenant documents DTO
8. tenant messaging v1 vs v2 contract choice
9. tenant dashboard’s role as page contract vs feed helper

---

## 4) Recommended execution order

If continuing implementation immediately, the best order is:
1. fix tenant messaging create flow
2. fix tenant inspections list normalization
3. add tenant-surface contract tests/helpers for those two paths
4. then decide whether to attack feed fallback removal or autopay normalization next

That sequence is strongest because it starts with **provable broken/misaligned contracts**, not abstract cleanup.
