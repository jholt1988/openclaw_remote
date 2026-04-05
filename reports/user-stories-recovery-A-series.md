# Property-Pulse User Stories Recovery — A-Series Manual UX Closure

Date: 2026-04-05
Source of truth: memory history only

## Objective
Close the remaining A-series user stories that are currently PARTIAL by completing manual UX verification and recording evidence.

## Current known status (from memory)
- PASS: A-04, A-12, PAY-01..08, PRIC-01..03
- PARTIAL (manual UX required): A-03, A-06, A-07, A-09, A-10, A-11
- Constraint: requires seeded database + full stack UI walkthrough environment

---

## Story Queue (Priority Order)

### 1) A-03 — Manual UX verification closure
- Why it matters: Removes ambiguity between backend-complete and user-observable behavior.
- Acceptance criteria:
  - End-to-end UI path executes without critical defects.
  - Expected state changes are visible in UI and persisted.
  - Negative-path behavior matches intended guardrails.
- Evidence required:
  - Screenshot set or screen recording of full walkthrough.
  - Request/response snapshots for key actions.
  - Pass/fail checklist entry.
- Status: PASS (2026-04-05)
- Evidence:
  - `reports/evidence/A-03/a03-login-flow-recording-success.webm`
  - `reports/evidence/A-03/a03-01-login-page.png`
  - `reports/evidence/A-03/a03-03-login-before-submit.png`
  - `reports/evidence/A-03/a03-04-after-submit.png`
- Notes:
  - Root cause of prior block: frontend auto-enabled MSW in development, returning mock non-JWT login token and preventing auth state persistence.
  - Fix applied: MSW now only starts when `VITE_USE_MSW === 'true'`; `.env.local` set to `VITE_USE_MSW=false` and `VITE_API_URL=http://localhost:3001/api`.

### 2) A-06 — Manual UX verification closure
- Why it matters: Prevents hidden UX regressions in operational flow.
- Acceptance criteria:
  - PM can access Lease Management and reach assign flow UI.
  - Tenant can view active lease details in My Lease.
  - Tenant can see lease-linked document visibility path.
- Evidence required: same structure as above.
- Status: PASS (2026-04-05)
- What passed:
  - PM login and Lease Management assign flow UI verified.
  - Tenant login and active lease visibility verified in My Lease.
  - Tenant lease-linked document visibility now surfaced in My Lease (`Lease Documents` section with open/download action).
- Evidence:
  - `reports/evidence/A-06/a06-pm-flow-recording-success.webm`
  - `reports/evidence/A-06/a06-tenant-flow-recording-success.webm`
  - `reports/evidence/A-06/a06-01-pm-dashboard.png`
  - `reports/evidence/A-06/a06-02-pm-lease-management.png`
  - `reports/evidence/A-06/a06-03-tenant-dashboard.png`
  - `reports/evidence/A-06/a06-04-tenant-my-lease.png`
- Notes:
  - Implemented Option A: expose lease-linked docs directly in `My Lease` instead of opening tenant access to `/documents`.
  - `/documents` remains role-restricted for TENANT by design.

### 3) A-07 — Manual UX verification closure
- Why it matters: Ensures role/flow behavior remains correct post-remediation.
- Acceptance criteria:
  - Tenant maintenance request appears in tenant maintenance feed.
  - PM queue shows photo count indicator on request card.
  - PM request detail shows photo gallery with rendered image.
- Evidence required: same structure as above.
- Status: PASS (2026-04-05)
- What passed:
  - Full in-UI tenant creation flow executed (modal form + photo upload).
  - Tenant can see the submitted target request in maintenance feed.
  - PM queue card shows photo count indicator.
  - PM detail view renders photo gallery for the request.
- Evidence:
  - `reports/evidence/A-07/a07-01-tenant-maintenance-list.png`
  - `reports/evidence/A-07/a07-02-pm-queue.png`
  - `reports/evidence/A-07/a07-03-pm-detail-photo-gallery.png`
  - `reports/evidence/A-07/a07-tenant-request-recording-success.webm`
  - `reports/evidence/A-07/a07-pm-queue-detail-recording-success.webm`
- Notes:
  - UI selection widgets required keyboard-driven selection for deterministic automation in headless mode.

### 4) A-09 — Manual UX verification closure
- Why it matters: Closes one of the known residual QA risks.
- Acceptance criteria:
  - Messaging thread creation works tenant → PM.
  - Attachment URLs can be sent and rendered in conversation UI.
  - Audit trail captures attachment metadata for sent message.
- Evidence required: same structure as above.
- Status: PARTIAL (2026-04-05)
- What passed:
  - Tenant created/sent thread message with attachment URL from messaging UI.
  - Tenant thread UI renders `Attachment 1` link.
  - Backend audit log includes `MESSAGE_SENT` event with `hasAttachments=true`, `attachmentCount=1`, and URL metadata.
- What remains:
  - PM inbox did not surface the new thread in current UI session during automation run; PM-side attachment rendering in UI remains unverified.
- Evidence:
  - `reports/evidence/A-09/a09-tenant-thread-attachment-recording.webm`
  - `reports/evidence/A-09/a09-pm-inbox-recording.webm`
  - `reports/evidence/A-09/a09-01-tenant-sent-with-attachment.png`
  - `reports/evidence/A-09/a09-02-pm-thread-with-attachment.png`
- Audit evidence (backend log):
  - `AuditLogService` entry at `2026-04-05T04:42:11.722Z` with module `MESSAGING`, action `MESSAGE_SENT`, metadata showing attachment fields.

### 5) A-10 — Manual UX verification closure
- Why it matters: Completes user-visible validation for previously remediated backend path.
- Acceptance criteria: same structure as above.
- Evidence required: same structure as above.
- Status: Pending manual UX run.

### 6) A-11 — Manual UX verification closure
- Why it matters: Finishes A-series closure and removes remaining partial state.
- Acceptance criteria: same structure as above.
- Evidence required: same structure as above.
- Status: Pending manual UX run.

---

## Operational plan (execution-level)
1. Confirm environment readiness:
   - Seeded database available
   - Frontend + backend running
   - Test accounts for required roles
2. Execute manual UX checklist card-by-card in this order:
   - A-03 → A-06 → A-07 → A-09 → A-10 → A-11
3. Capture evidence during each run (do not batch after).
4. Mark each story PASS/PARTIAL/FAIL immediately after run.
5. Publish closure summary with residual risks (if any).

## Bottleneck
Environment fidelity (seed data + role accounts + full stack health) is the gating constraint.

## Leverage point
Use one standard evidence template for all six stories to reduce verification overhead and improve consistency.
