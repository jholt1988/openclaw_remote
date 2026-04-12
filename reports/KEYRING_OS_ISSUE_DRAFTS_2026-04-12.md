# Keyring OS ↔ Tenant Portal Backend Issue Drafts

Date: 2026-04-12
Source inputs:
- `reports/KEYRING_OS_CONTRACT_MATRIX_2026-04-12.md`
- `reports/KEYRING_OS_IMPLEMENTATION_BACKLOG_2026-04-12.md`

Purpose:
- provide GitHub/Jira-ready issue drafts for the highest-priority implementation work
- include scope, rationale, acceptance criteria, dependencies, and rough estimates

Estimate scale:
- XS: <0.5 day
- S: 0.5 to 1 day
- M: 1 to 3 days
- L: 3 to 5 days
- XL: 5+ days

---

## Issue 1. Define canonical admin feed contract

**Type:** Design / API contract
**Priority:** P0
**Estimate:** S
**Owners:** Backend lead, Frontend lead
**Depends on:** none

### Summary
Define and freeze the canonical admin feed route and response DTO used by Keyring OS admin surfaces.

### Problem
Admin feed currently drifts across multiple routes and payload assumptions:
- `/feed`
- `/api/feed`
- `/api/v2/feed`

The backend appears to expose `GET /feed`, but frontend consumers still assume alternate route families and a richer `FeedResponse` shape than some backend paths currently provide.

### Scope
- choose one canonical feed route, recommended: `GET /feed`
- define canonical response DTO, recommended: `FeedResponse { items, role, generatedAt }`
- define allowed query params if any, such as role/filter context
- document whether legacy feed routes are temporary compatibility aliases or deprecated immediately

### Acceptance criteria
- one route is explicitly documented as canonical
- one DTO is explicitly documented as canonical
- frontend and backend teams reference the same contract source
- non-canonical routes are marked compatibility-only or deprecated

### Deliverables
- shared contract note, ADR, or typed contract definition
- implementation note for migration plan

---

## Issue 2. Normalize backend admin feed response to canonical FeedResponse

**Type:** Backend
**Priority:** P0
**Estimate:** M
**Owners:** Backend
**Depends on:** Issue 1

### Summary
Update backend feed implementation to return the canonical `FeedResponse` DTO instead of raw ORM-style payloads.

### Problem
The backend feed path appears to return raw `feedItem.findMany(...)` output, while the frontend expects a normalized `FeedResponse` containing at least:
- `items`
- `role`
- `generatedAt`

That mismatch creates drift and forces frontend fallback logic.

### Scope
- update `src/feed/feed.controller.ts`
- update `src/feed/feed-aggregator.service.ts`
- map persistence entities to canonical DTO
- ensure `generatedAt` is always populated
- ensure role context is explicit and consistent
- strip backend-only/internal fields from outward response

### Acceptance criteria
- `GET /feed` returns canonical `FeedResponse`
- no raw ORM payload is returned directly to feed clients
- item list shape matches shared frontend expectations
- automated tests validate the response contract

### Deliverables
- DTO implementation
- mapping layer
- unit/integration tests

---

## Issue 3. Update frontend admin feed client to use one canonical route

**Type:** Frontend
**Priority:** P0
**Estimate:** S
**Owners:** Frontend
**Depends on:** Issue 1, ideally Issue 2

### Summary
Remove route guessing from frontend feed consumers and standardize on the canonical admin feed route.

### Problem
Frontend feed clients currently appear to branch between multiple route families. That makes the client fragile and obscures the true contract.

### Scope
- update `feed-api.ts`
- update `useCoPilotFeed()`
- remove legacy route-guessing and branching in production path
- align request params with canonical feed contract

### Acceptance criteria
- frontend feed client targets exactly one canonical route in normal operation
- no production code guesses between `/api/feed`, `/api/v2/feed`, and `/feed`
- feed UI works against canonical DTO

### Deliverables
- updated frontend data layer
- refreshed tests/fixtures/mocks

---

## Issue 4. Inventory and classify all admin feed actions

**Type:** Design / Product / API
**Priority:** P0
**Estimate:** S
**Owners:** Product, Frontend, Backend
**Depends on:** none

### Summary
Identify every action launched from the admin feed UI and classify whether it is:
- a real feed mutation
- a domain mutation launched from the feed surface
- a navigation shortcut only

### Problem
Frontend assumes a generic feed action mutation path exists, but the inspected backend surface does not clearly provide one beyond note updates. The team should not implement a generic endpoint blindly without classifying the action set.

### Scope
- inventory actions used in `useCoPilotFeed()`
- map each action to its true business owner
- identify dead/speculative actions
- decide whether a feed façade route is justified

### Acceptance criteria
- every feed action has an identified backend owner
- dead or speculative actions are explicitly labeled
- team has a decision on façade route vs direct domain mutations

### Deliverables
- action inventory table
- decision note

---

## Issue 5. Implement canonical feed action mutation path or remove dead frontend assumption

**Type:** Backend + Frontend
**Priority:** P0
**Estimate:** M
**Owners:** Backend, Frontend
**Depends on:** Issue 4

### Summary
Eliminate the broken assumption that `POST /api/feed/actions` exists unless the team intentionally implements a canonical equivalent.

### Problem
Frontend expects a feed action mutation route that does not appear to exist in the inspected backend. That is a direct execution risk.

### Scope
Choose one path:

**Option A, façade route**
- implement canonical `POST /feed/actions`
- accept typed action payloads
- dispatch internally to domain handlers
- return normalized result payload

**Option B, direct domain routes**
- remove generic feed action endpoint assumption from frontend
- route actions directly to true domain APIs

### Acceptance criteria
- no frontend action targets a missing endpoint
- all supported feed actions execute end to end
- unsupported actions fail explicitly rather than silently drifting

### Deliverables
- implemented mutation path or removed abstraction
- updated frontend mutation layer
- action contract tests

### Recommendation
Prefer Option B if actions are truly heterogeneous and domain-owned. Prefer Option A only if product intentionally wants a feed orchestration façade.

---

## Issue 6. Normalize screening policy evaluation route

**Type:** Frontend + Backend
**Priority:** P0
**Estimate:** XS to S
**Owners:** Frontend, Backend
**Depends on:** none

### Summary
Resolve the route mismatch between frontend screening policy evaluation calls and the backend route that actually exists.

### Problem
Frontend expects:
- `GET /screening/:applicationId/policy-evaluation`

Backend exposes:
- `GET /rental-applications/:id/policy-evaluation`

This is a hard contract mismatch.

### Scope
- update frontend `fetchPolicyEvaluation(applicationId)` to call the canonical backend route
- optionally add compatibility alias on backend if release coordination is difficult
- update tests and references

### Acceptance criteria
- policy evaluation loads successfully in screening workspace
- active production code no longer depends on `/screening/:applicationId/policy-evaluation`
- route is documented consistently

### Deliverables
- updated client call
- optional compatibility alias
- route test coverage

### Recommendation
Keep `GET /rental-applications/:id/policy-evaluation` as canonical unless product has a stronger naming reason to expose a screening route family.

---

## Issue 7. Define canonical role enum and serialization strategy

**Type:** Architecture / Auth contract
**Priority:** P0
**Estimate:** S
**Owners:** Backend lead, Frontend lead
**Depends on:** none

### Summary
Define one canonical role vocabulary and casing strategy across frontend, backend guards, shared types, and mock/dev auth.

### Problem
Role drift currently appears in multiple forms:
- frontend roles: `owner | property_manager | leasing | maintenance`
- backend guard roles: `TENANT`, `PROPERTY_MANAGER`, `OWNER`, `ADMIN`
- mock headers and dev values: `admin`, `tenant`, `PROPERTY_MANAGER`

This creates authorization ambiguity and hidden breakage.

### Scope
- define canonical role enum
- define casing and wire-format rules
- define temporary legacy-to-canonical mapping if required
- decide whether roles like `LEASING` and `MAINTENANCE` are true auth roles or merely workspace personas

### Acceptance criteria
- one canonical role vocabulary is approved
- serialization/casing rules are explicit
- legacy values, if accepted, have a single documented mapping path

### Deliverables
- shared enum/contract definition
- mapping note or ADR

---

## Issue 8. Normalize frontend role usage, mock auth headers, and fixtures

**Type:** Frontend
**Priority:** P0
**Estimate:** M
**Owners:** Frontend
**Depends on:** Issue 7

### Summary
Remove ad hoc role values and casing drift from frontend code, mocks, and fixtures.

### Problem
Frontend still appears to rely on inconsistent role names and mock/dev headers. That leaks instability into both UI logic and local testing.

### Scope
- update frontend role types
- update auth helpers and mock headers
- centralize temporary role mapping if needed
- update tests and fixtures to canonical values

### Acceptance criteria
- no production frontend path depends on ad hoc role casing
- frontend role handling aligns with canonical enum
- fixtures and mocks no longer encode conflicting vocabularies

### Deliverables
- role utility module or shared role import usage
- updated tests/mocks

---

## Issue 9. Normalize backend role guards and ingress role parsing

**Type:** Backend / Auth
**Priority:** P0
**Estimate:** M
**Owners:** Backend
**Depends on:** Issue 7

### Summary
Ensure backend authorization and role parsing consistently interpret canonical role values.

### Problem
Backend guards and request parsing may be tolerant of multiple role strings today, but without a single ingress normalization point this becomes brittle and inconsistent.

### Scope
- audit guard/decorator/middleware role handling
- align checks to canonical enum
- if legacy values must remain temporarily supported, normalize them in one place only
- add tests for role parsing and authorization behavior

### Acceptance criteria
- backend authorization uses canonical role semantics consistently
- canonical values work across protected routes
- legacy role support, if present, is centralized and explicit

### Deliverables
- updated auth guard or ingress normalization layer
- guard/integration tests

---

## Issue 10. Align Stripe checkout session response contract

**Type:** Backend + Frontend
**Priority:** P1
**Estimate:** XS to S
**Owners:** Backend, Frontend
**Depends on:** none

### Summary
Resolve the mismatch between frontend checkout expectation `{ url }` and backend response `{ checkoutUrl, sessionId, invoiceId }`.

### Problem
The checkout redirect flow depends on a property name mismatch. It is small but concrete and easy to break.

### Scope
Preferred direction:
- keep richer backend response
- update frontend to consume `checkoutUrl`
- expose typed response contract

Optional migration shim:
- backend temporarily also returns `url`

### Acceptance criteria
- checkout redirect works end to end
- frontend and backend share one explicit response type
- no untyped property assumption remains in checkout flow

### Deliverables
- aligned DTO
- updated redirect consumer
- test coverage for redirect path

### Recommendation
Use the richer DTO as canonical and patch the frontend unless release timing strongly favors a temporary alias.

---

## Issue 11. Decide canonical aggregation ownership for payments workspace

**Type:** Architecture / Product
**Priority:** P1
**Estimate:** S
**Owners:** Product, Backend, Frontend
**Depends on:** none

### Summary
Decide whether payments workspace remains frontend-composed or becomes backend-aggregated.

### Problem
Current workspace assembly appears frontend-composed from multiple APIs. That is not necessarily wrong, but it is currently implicit rather than intentional.

### Scope
- review current sources:
  - `/payments/delinquency/queue`
  - `/payments/ops-summary`
  - `/payments/invoices`
- assess latency, consistency, auth, caching, and ownership tradeoffs
- choose between backend aggregate endpoint vs documented frontend composition

### Acceptance criteria
- team has a written decision
- ownership of workspace assembly is explicit
- follow-up implementation ticket exists if a backend aggregate endpoint is chosen

---

## Issue 12. Decide canonical aggregation ownership for leasing/screening and repairs workspaces

**Type:** Architecture / Product
**Priority:** P1
**Estimate:** M
**Owners:** Product, Backend, Frontend
**Depends on:** none

### Summary
Make workspace aggregation ownership explicit for leasing/screening and repairs, and clean up path-family governance where it is currently loose.

### Problem
The system currently mixes frontend composition with backend aggregation and also shows path drift such as both `api/leasing` and `leasing`. That makes the architecture harder to reason about.

### Scope
- review leasing and screening workspace composition paths
- choose canonical public path family
- decide aggregation owner for leasing/screening
- verify maintenance list sort/filter contract for repairs workspace
- decide whether repairs gets a backend aggregate endpoint or a documented composed contract

### Acceptance criteria
- one canonical path family is documented for leasing where needed
- workspace ownership is explicit for leasing/screening and repairs
- sort/filter behavior for repairs inputs is documented and tested

---

# Suggested rollout order

## Wave 1, immediate
1. Issue 1. Define canonical admin feed contract
2. Issue 2. Normalize backend admin feed response
3. Issue 3. Update frontend feed client
4. Issue 4. Inventory and classify all admin feed actions
5. Issue 6. Normalize screening policy evaluation route
6. Issue 7. Define canonical role enum and serialization strategy

## Wave 2, after contract alignment
7. Issue 5. Implement feed action path or remove dead assumption
8. Issue 8. Normalize frontend role usage and mock auth
9. Issue 9. Normalize backend role guards and ingress parsing
10. Issue 10. Align Stripe checkout session response contract

## Wave 3, architecture clarification
11. Issue 11. Decide payments workspace aggregation ownership
12. Issue 12. Decide leasing/screening and repairs aggregation ownership

---

# Best immediate assignment set

If assigning today, give the team this split:

## Backend
- Issue 2
- Issue 9
- support for Issue 5 if façade route chosen

## Frontend
- Issue 3
- Issue 6
- Issue 8
- Issue 10 frontend piece

## Joint backend/frontend/design
- Issue 1
- Issue 4
- Issue 5 decision
- Issue 7

---

# Recommended next step

Create actual tracker tickets from Issues 1 through 10 first.

If needed, the next pass should produce either:
- GitHub issue markdown, one block per issue
- Jira ticket format with summary, description, ACs, and labels
- a dependency board grouped by owner and sprint
