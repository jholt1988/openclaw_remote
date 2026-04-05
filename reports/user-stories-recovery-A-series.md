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
- Acceptance criteria: same structure as above.
- Evidence required: same structure as above.
- Status: Pending manual UX run.

### 3) A-07 — Manual UX verification closure
- Why it matters: Ensures role/flow behavior remains correct post-remediation.
- Acceptance criteria: same structure as above.
- Evidence required: same structure as above.
- Status: Pending manual UX run.

### 4) A-09 — Manual UX verification closure
- Why it matters: Closes one of the known residual QA risks.
- Acceptance criteria: same structure as above.
- Evidence required: same structure as above.
- Status: Pending manual UX run.

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
