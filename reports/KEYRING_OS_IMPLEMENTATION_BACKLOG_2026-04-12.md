# Keyring OS ↔ Tenant Portal Backend Implementation Backlog

Date: 2026-04-12
Source report:
- `reports/KEYRING_OS_CONTRACT_MATRIX_2026-04-12.md`

Purpose:
- convert identified P0/P1 contract drift into implementation-ready backlog items
- sequence work to reduce downstream rework
- define concrete scope, dependencies, deliverables, and acceptance criteria

---

## Executive recommendation

Start here, in order:
1. Admin feed route and response normalization
2. Feed action mutation contract
3. Policy evaluation route normalization
4. Role vocabulary normalization
5. Payments checkout response alignment
6. Workspace aggregation ownership decisions for payments, leasing, repairs

Reason:
- feed and role drift contaminate multiple admin surfaces
- policy evaluation is a hard route break
- payments mismatch is smaller and isolated
- workspace aggregation decisions should happen after the highest-risk contract drift is under control

---

## Delivery principles

- Prefer canonical contracts over ad hoc compatibility where practical
- Use compatibility aliases only to reduce release risk or unblock incremental rollout
- Put DTO-level contract tests around every P0/P1 surface before broad UI expansion
- Do not let frontend mocks/dev-auth remain the source of truth for role semantics

---

# EPIC 1. Admin feed stabilization

## T1. Define canonical admin feed contract
Priority: P0
Owner: Backend + Frontend lead
Status: Ready

### Goal
Freeze one canonical route and one canonical response DTO for admin feed consumption.

### Scope
- Choose canonical route for feed, recommended: `GET /feed`
- Define canonical response shape, recommended:
  - `FeedResponse { items, role, generatedAt }`
- Document whether query params include role, filters, pagination, or workspace context
- Decide whether legacy aliases remain temporarily supported

### Deliverables
- written contract in shared types and/or backend DTOs
- route decision documented in repo docs or ADR
- deprecation note for legacy routes if applicable

### Acceptance criteria
- one route is explicitly marked canonical
- one DTO is explicitly marked canonical
- frontend and backend teams can point to the same contract definition
- any non-canonical route is marked compatibility-only with removal target

### Dependencies
- none

### Notes
If the team cannot align fast, use `GET /feed` as the canonical backend route and add aliases only as temporary shims.

---

## T2. Normalize backend admin feed response shape
Priority: P0
Owner: Backend
Status: Ready

### Goal
Make backend feed responses conform to the canonical `FeedResponse` instead of raw ORM output.

### Scope
- Update `src/feed/feed.controller.ts`
- Update `src/feed/feed-aggregator.service.ts`
- Wrap raw feed items into canonical DTO
- Ensure `generatedAt` is always present
- Ensure role context is explicit and consistent
- Remove leakage of ORM-only fields not intended for UI contract

### Deliverables
- backend DTO implementation
- mapper from persistence model to `FeedResponse`
- unit tests for response shape

### Acceptance criteria
- `GET /feed` returns `FeedResponse`
- response shape matches shared frontend expectations
- no raw `feedItem.findMany(...)` payload escapes directly to clients
- tests verify response keys and item-level shape

### Dependencies
- T1

---

## T3. Add temporary compatibility aliases for legacy feed routes
Priority: P0
Owner: Backend
Status: Ready

### Goal
Prevent frontend breakage during migration while canonical feed contract rolls out.

### Scope
- Add compatibility handling for:
  - `/api/feed`
  - `/api/v2/feed`
- Route both to the canonical feed handler or gateway/proxy mapping
- Return canonical DTO from aliases as well
- Emit deprecation logging or metrics if available

### Deliverables
- alias routes or proxy mappings
- deprecation markers in code/comments/docs

### Acceptance criteria
- legacy feed consumers receive canonical `FeedResponse`
- alias usage is observable in logs or telemetry
- canonical route remains the documented source of truth

### Dependencies
- T1, T2

### Notes
This is a migration ticket, not a permanent architecture choice.

---

## T4. Update frontend feed client to use canonical route only
Priority: P0
Owner: Frontend
Status: Ready

### Goal
Remove route guessing in frontend feed consumers.

### Scope
- Update `feed-api.ts`
- Update `useCoPilotFeed()`
- Remove fallback route switching between `/api/feed`, `/api/v2/feed`, and others
- Align request params with canonical contract

### Deliverables
- single route usage in frontend feed data layer
- tests or mocks updated to canonical contract

### Acceptance criteria
- frontend feed client targets one canonical route
- no hardcoded legacy route branching remains in production path
- feed rendering works against canonical DTO

### Dependencies
- T1, ideally T2; T3 if staged rollout needed

---

## T5. Reduce or remove frontend admin feed synthesis fallback
Priority: P1
Owner: Frontend
Status: Blocked by feed verification

### Goal
Stop compensating for backend uncertainty once feed contract is reliable.

### Scope
- audit fallback logic in admin home/workspace surfaces
- remove only the fallback paths that duplicate server aggregation
- preserve graceful error states without synthesizing incorrect business data

### Deliverables
- simplified admin feed consumption path
- clearer error/loading states

### Acceptance criteria
- admin feed UI renders from canonical backend data in normal operation
- fallback no longer fabricates core business content from unrelated endpoints
- errors degrade visibly and safely

### Dependencies
- T2, T4

---

# EPIC 2. Feed action mutation contract

## T6. Inventory intended feed actions and their domain owners
Priority: P0
Owner: Product + Backend + Frontend
Status: Ready

### Goal
Clarify what “feed actions” actually are before implementing a route.

### Scope
- enumerate actions invoked from `useCoPilotFeed()`
- map each action to underlying domain behavior
  - note add/update
  - assign task
  - snooze/dismiss
  - navigate only
  - approve/review/escalate
- separate true feed mutations from domain mutations merely launched from feed UI

### Deliverables
- action inventory table
- owner mapping by action
- decision on which actions deserve a feed façade route

### Acceptance criteria
- every frontend feed action has an identified backend owner
- dead or speculative actions are called out explicitly
- implementation approach is chosen: façade route vs direct domain routes

### Dependencies
- none

---

## T7. Implement canonical feed action mutation path or remove dead assumption
Priority: P0
Owner: Backend + Frontend
Status: Ready

### Goal
Eliminate the current broken assumption that `POST /api/feed/actions` exists unless it truly will.

### Scope
One of two paths:

#### Option A, recommended for speed
- implement canonical mutation route, recommended: `POST /feed/actions`
- accept typed action payload
- route internally to domain handlers
- return normalized action result

#### Option B, recommended for purity
- remove generic feed action endpoint assumption from frontend
- route each action to its actual domain endpoint directly

### Deliverables
- implemented route or removed abstraction
- updated frontend mutation layer
- action result type definition

### Acceptance criteria
- no frontend action points at a non-existent endpoint
- each supported action succeeds end to end in UI and API tests
- unsupported actions fail with explicit error, not silent drift

### Dependencies
- T6

### Notes
If actions are heterogeneous and domain-owned, Option B is architecturally cleaner.

---

## T8. Add contract tests for feed actions
Priority: P1
Owner: Backend + Frontend QA
Status: Ready

### Goal
Prevent reintroduction of dead mutation paths.

### Scope
- API tests for supported feed actions
- UI integration tests for at least top 3 admin actions
- explicit assertion for success and error payload shapes

### Acceptance criteria
- build fails if frontend action route drifts from backend implementation
- test coverage exists for happy path and unsupported action path

### Dependencies
- T7

---

# EPIC 3. Screening policy evaluation route normalization

## T9. Normalize policy evaluation route
Priority: P0
Owner: Backend + Frontend
Status: Ready

### Goal
Resolve hard route mismatch for policy evaluation.

### Scope
Recommended path:
- keep backend canonical route as `GET /rental-applications/:id/policy-evaluation`
- update frontend `fetchPolicyEvaluation(applicationId)` to call canonical route
- optionally add compatibility alias for `/screening/:applicationId/policy-evaluation` if release coordination is difficult

### Deliverables
- updated frontend client
- optional backend alias if needed
- route test coverage

### Acceptance criteria
- policy evaluation loads successfully from screening workspace
- route used by frontend matches documented backend contract
- no unresolved references to `/screening/:applicationId/policy-evaluation` remain in active production path

### Dependencies
- none

### Notes
This looks like a clean fix. Do not over-engineer it.

---

# EPIC 4. Role vocabulary normalization

## T10. Define canonical role enum and casing strategy
Priority: P0
Owner: Architecture + Backend + Frontend
Status: Ready

### Goal
Stop role drift across frontend, backend guards, mocks, and headers.

### Scope
- define canonical roles, for example:
  - `TENANT`
  - `PROPERTY_MANAGER`
  - `OWNER`
  - `ADMIN`
  - plus any truly required roles such as `LEASING` or `MAINTENANCE` only if they are first-class platform roles
- define casing and serialization rules
- define legacy-to-canonical mapping rules if temporary coexistence is unavoidable

### Deliverables
- shared enum or shared contract definition
- mapping table for legacy values
- short ADR or contract note

### Acceptance criteria
- one canonical role vocabulary exists
- frontend and backend compile against the same meaning
- mock/dev values are explicitly mapped, not invented ad hoc

### Dependencies
- none

---

## T11. Normalize frontend role usage and mock headers
Priority: P0
Owner: Frontend
Status: Ready

### Goal
Remove mixed-case and mixed-vocabulary role assumptions from frontend code.

### Scope
- update frontend type roles
- update auth helpers and mock headers
- remove values like `admin`, `tenant`, and inconsistent role aliases from production paths
- centralize role mapping utility if temporary compatibility is needed

### Deliverables
- frontend role utility/module
- updated mock/dev auth behavior
- updated tests and fixtures

### Acceptance criteria
- no production frontend code depends on ad hoc role casing
- frontend outgoing role signals align with canonical enum
- tests pass with canonical values only or explicit mapped legacy values

### Dependencies
- T10

---

## T12. Normalize backend role guards and request parsing
Priority: P0
Owner: Backend
Status: Ready

### Goal
Ensure backend authorization and request parsing interpret roles consistently.

### Scope
- audit guards/decorators/middleware for role parsing
- align role checks with canonical enum
- support temporary legacy mapping at ingress only if needed
- remove ambiguous casing sensitivity where possible

### Deliverables
- updated guard logic
- ingress normalization for legacy values if needed
- auth/guard tests

### Acceptance criteria
- backend authorization behavior is consistent across endpoints
- canonical roles work everywhere
- legacy role values, if still accepted, are normalized in one place only

### Dependencies
- T10

---

## T13. Remove role drift from shared types and docs
Priority: P1
Owner: Frontend + Backend
Status: Ready

### Goal
Eliminate latent drift in `packages/types`, fixtures, and developer guidance.

### Scope
- update shared types
- update seed/mock fixtures
- update docs/examples to canonical roles

### Acceptance criteria
- no conflicting role vocab remains in shared contracts or reference examples

### Dependencies
- T10, T11, T12

---

# EPIC 5. Payments checkout contract alignment

## T14. Align checkout session response contract
Priority: P1
Owner: Backend + Frontend
Status: Ready

### Goal
Resolve mismatch between frontend expectation `{ url }` and backend response `{ checkoutUrl, sessionId, invoiceId }`.

### Scope
Choose one of two paths:

#### Option A, recommended
- preserve richer backend shape
- update frontend to read `checkoutUrl`
- expose typed response DTO such as:
  - `{ checkoutUrl, sessionId, invoiceId }`

#### Option B
- backend also returns `url` alias temporarily
- frontend migrates later

### Deliverables
- aligned DTO
- updated frontend consumer for checkout redirect
- tests for redirect flow

### Acceptance criteria
- checkout flow redirects successfully in UI
- frontend and backend share one explicit response type
- no untyped property assumptions remain

### Dependencies
- none

### Notes
Option A is cleaner. A temporary `url` alias is acceptable only as a migration shim.

---

# EPIC 6. Workspace aggregation ownership

## T15. Decide canonical aggregation strategy for payments workspace
Priority: P1
Owner: Architecture + Product + Backend + Frontend
Status: Ready

### Goal
Decide whether payments workspace remains frontend-composed or becomes backend-aggregated.

### Scope
- evaluate current composed sources:
  - `/payments/delinquency/queue`
  - `/payments/ops-summary`
  - `/payments/invoices`
- assess latency, consistency, caching, authorization, and UI coupling
- choose one of:
  - backend-owned `GET /payments/workspace`
  - documented frontend composition as the long-term contract

### Deliverables
- decision record
- follow-up implementation ticket if backend aggregation is chosen

### Acceptance criteria
- team has a documented answer
- no ambiguity remains about source of truth for payments workspace assembly

### Dependencies
- none

---

## T16. Decide canonical aggregation strategy for leasing and screening workspace
Priority: P1
Owner: Architecture + Product + Backend + Frontend
Status: Ready

### Goal
Make leasing/screening aggregation ownership explicit.

### Scope
- review current composition from leasing stats, leads, ops summary, and rental applications
- decide canonical path family and aggregation owner
- specifically clean up dual path governance around `api/leasing` and `leasing`

### Deliverables
- path governance decision
- aggregation ownership decision
- follow-up implementation ticket(s)

### Acceptance criteria
- one canonical public path family is documented
- one aggregation ownership model is chosen

### Dependencies
- none

---

## T17. Decide canonical aggregation strategy for repairs workspace
Priority: P1
Owner: Architecture + Product + Backend + Frontend
Status: Ready

### Goal
Make repairs workspace contract explicit and verify filter/sort support.

### Scope
- verify support for `sortBy` and `sortOrder` in maintenance list path
- decide whether repairs workspace gets a backend aggregate endpoint
- define supported query contract if composition remains frontend-owned

### Deliverables
- query contract note
- aggregation ownership decision
- follow-up implementation ticket if needed

### Acceptance criteria
- sort/filter behavior is documented and tested
- workspace assembly ownership is explicit

### Dependencies
- none

---

# EPIC 7. Cross-cutting contract safety net

## T18. Add DTO-level contract tests for all P0/P1 surfaces
Priority: P1
Owner: Backend QA + Frontend QA
Status: Ready

### Goal
Catch future drift mechanically instead of by archaeology.

### Scope
Cover at minimum:
- admin feed response
- feed action mutation payload/result
- policy evaluation route
- role serialization and authorization cases
- checkout session response

### Deliverables
- API contract tests
- typed fixtures or snapshot contracts
- CI gating on contract failures

### Acceptance criteria
- CI fails on contract regressions for covered surfaces
- each P0/P1 item has at least one automated contract assertion

### Dependencies
- T2, T7, T9, T12, T14

---

# Recommended sprint sequencing

## Sprint 1, stop the bleeding
- T1 Define canonical admin feed contract
- T2 Normalize backend admin feed response shape
- T4 Update frontend feed client to canonical route
- T6 Inventory intended feed actions
- T9 Normalize policy evaluation route
- T10 Define canonical role enum and casing strategy

## Sprint 2, restore end-to-end reliability
- T3 Add temporary compatibility aliases for legacy feed routes
- T7 Implement canonical feed action path or remove dead assumption
- T11 Normalize frontend role usage and mock headers
- T12 Normalize backend role guards and request parsing
- T14 Align checkout session response contract

## Sprint 3, remove scaffolding and clarify architecture
- T5 Reduce/remove frontend admin feed synthesis fallback
- T13 Remove role drift from shared types and docs
- T15 Decide payments workspace aggregation strategy
- T16 Decide leasing/screening aggregation strategy
- T17 Decide repairs workspace aggregation strategy
- T18 Add DTO-level contract tests for all P0/P1 surfaces

---

# Recommended ownership model

## Backend-heavy items
- T2, T3, T7 option A, T12, T14 option B, T17 verification work

## Frontend-heavy items
- T4, T5, T11, T14 option A

## Joint design/architecture items
- T1, T6, T10, T15, T16, T17, T18

---

# Fastest path vs cleanest path

## Fastest path
- shim feed aliases
- patch frontend to current backend routes
- add minimal role mapping layer
- add `url` alias for checkout response

### Advantage
Lower immediate breakage risk.

### Cost
More temporary compatibility debt.

## Cleanest path
- define canonical DTOs/routes first
- make frontend and backend match them exactly
- remove route guessing and role guesswork
- add contract tests before more feature expansion

### Advantage
Less long-term drag and less hidden coupling.

### Cost
Requires tighter coordination this week.

### Recommendation
Use the clean path for feed and roles. Use shims only where they materially reduce rollout risk.

---

# Immediate next action

Start implementation with this exact ticket order:
1. T1
2. T2
3. T4
4. T6
5. T7
6. T9
7. T10
8. T11
9. T12
10. T14

If the team wants, the next pass should turn this backlog into:
- GitHub/Jira-ready issue text
- engineering estimates
- dependency graph
- owner-by-owner workstreams
