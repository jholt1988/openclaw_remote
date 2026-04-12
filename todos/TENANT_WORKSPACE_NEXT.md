# Tenant workspace next

Primary next implementation queue:
1. [x] Fix tenant messaging create flow
   - tenant frontend now fetches property managers and starts a thread with `POST /messaging/threads`
   - the new-message UI collects a recipient explicitly instead of sending the wrong payload to `/messaging/conversations`

2. [x] Fix inspections list normalization
   - tenant frontend now normalizes `GET /inspections` whether it returns a bare array or an envelope with `data/items/inspections`

3. [x] Add tenant contract checks for those two surfaces
   - added backend checks for tenant autopay response shape and tenant feed failure surfacing

4. [x] Normalize tenant autopay response shape
   - tenant frontend now models `GET /billing/autopay` as `{ leaseId, enrollment }`
   - tenant autopay enable flow now requires a real payment method id and uses saved payment methods

5. [x] Reduce `/tenant/feed` fallback masking
   - backend tenant feed no longer swallows build errors into empty success responses
   - frontend fallback now triggers only on hard request failure, not on empty feed items

6. [x] Verify tenant dashboard contract explicitly and remove stale fallback assumptions
   - tenant dashboard is modeled from backend `leases[]/summary/recentNotifications` shape now
   - feed synthesis no longer assumes `dashboard.lease`; it derives from `dashboard.leases`

7. [x] Add targeted contract tests for tenant feed and autopay surfaces
   - `src/billing/billing.service.autopay.spec.ts`
   - `src/tenant/tenant-feed.service.spec.ts`

Status:
- tenant workspace todo run is complete for the currently approved scope

Reference report:
- `reports/KEYRING_OS_TENANT_WORKSPACE_CONTRACT_MATRIX_2026-04-13.md`
