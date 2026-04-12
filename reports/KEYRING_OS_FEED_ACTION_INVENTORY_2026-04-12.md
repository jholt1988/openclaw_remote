# Keyring OS Admin Feed Action Inventory

Date: 2026-04-12
Decision:
- move away from generic feed façade mutations
- use direct domain mutations where a real domain owner exists
- keep only feed dismissal as a feed-owned mutation

---

## Live action inventory found in current admin feed generation

### Payments delinquency actions

1. `send_3_day_notice`
- Source: `feed-aggregator.service.ts`
- Domain owner: Payments
- New direct mutation:
  - `POST /payments/delinquency/by-payment/:paymentId/issue-notice`
- Notes:
  - backend resolves `paymentId -> leaseId`
  - issues a delinquency notice through the payments service

2. `send_late_notice`
- Source: `feed-aggregator.service.ts`
- Domain owner: Payments
- New direct mutation:
  - `POST /payments/delinquency/by-payment/:paymentId/issue-notice`
- Notes:
  - same direct route as above, intent carried in request body for message selection

3. `promise_to_pay`
- Source: `feed-aggregator.service.ts`
- Domain owner: Payments
- New direct mutation:
  - `POST /payments/delinquency/by-payment/:paymentId/promise-to-pay`
- Notes:
  - backend resolves `paymentId -> leaseId`
  - maps to legal-hold resolution with `PAYMENT_PLAN`

### Feed-owned action

4. `dismiss_manually`
- Source: `feed-aggregator.service.ts`
- Domain owner: Feed state
- Direct mutation:
  - `PATCH /feed/:id/dismiss`
- Notes:
  - this is not a business-domain mutation, it is a feed-state mutation
  - keeping it on the feed surface is correct

---

## Deprecated approach

Old generic façade assumption:
- `POST /api/v2/feed/:id/action`

Status:
- removed from active module wiring
- no longer used by frontend admin feed actions
- deleted from backend source during cleanup because the module no longer referenced it

Reason:
- it mixed heterogeneous business actions into a fake feed-owned command router
- direct domain routes are clearer, safer, and easier to test

---

## Frontend mapping rule

Frontend should execute mutation actions as follows:
- `send_3_day_notice` -> payments direct route
- `send_late_notice` -> payments direct route
- `promise_to_pay` -> payments direct route
- `dismiss_manually` -> feed dismiss route
- any unmapped mutation intent -> explicit error

---

## Follow-up recommendation

Cleanup status after final pass:
1. unsupported mutation intents already fail explicitly in the frontend server action mapper
2. stale mock-feed mutation intents were removed or downgraded to navigation-only actions
3. contract tests exist for the stabilized feed-action execution surface; full suite validation should still be run in a dependency-installed environment
