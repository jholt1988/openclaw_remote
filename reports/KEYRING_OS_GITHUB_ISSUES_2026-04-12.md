# Keyring OS ↔ Tenant Portal Backend GitHub Issue Copy

Date: 2026-04-12
Purpose:
- copy-paste issue bodies for the highest-priority contract stabilization work
- based on `KEYRING_OS_CONTRACT_MATRIX_2026-04-12.md`, `KEYRING_OS_IMPLEMENTATION_BACKLOG_2026-04-12.md`, and `KEYRING_OS_ISSUE_DRAFTS_2026-04-12.md`

Suggested labels:
- `contract-drift`
- `api`
- `frontend`
- `backend`
- `auth`
- `payments`
- `screening`
- `feed`
- `p0` / `p1`

---

## Issue 1

**Title:** Define canonical admin feed contract

**Labels:** `p0`, `feed`, `api`, `contract-drift`

**Body:**
```md
## Summary
Define and freeze the canonical admin feed route and response DTO used by Keyring OS admin surfaces.

## Problem
Admin feed currently drifts across multiple routes and payload assumptions:
- `/feed`
- `/api/feed`
- `/api/v2/feed`

The backend appears to expose `GET /feed`, but frontend consumers still assume alternate route families and a richer `FeedResponse` shape than some backend paths currently provide.

## Scope
- choose one canonical feed route, recommended: `GET /feed`
- define canonical response DTO, recommended: `FeedResponse { items, role, generatedAt }`
- define allowed query params if any, such as role/filter context
- document whether legacy feed routes are temporary compatibility aliases or deprecated immediately

## Acceptance Criteria
- one route is explicitly documented as canonical
- one DTO is explicitly documented as canonical
- frontend and backend teams reference the same contract source
- non-canonical routes are marked compatibility-only or deprecated

## Deliverables
- shared contract note, ADR, or typed contract definition
- implementation note for migration plan
```

---

## Issue 2

**Title:** Normalize backend admin feed response to canonical FeedResponse

**Labels:** `p0`, `backend`, `feed`, `api`, `contract-drift`

**Body:**
```md
## Summary
Update backend feed implementation to return the canonical `FeedResponse` DTO instead of raw ORM-style payloads.

## Problem
The backend feed path appears to return raw `feedItem.findMany(...)` output, while the frontend expects a normalized `FeedResponse` containing at least:
- `items`
- `role`
- `generatedAt`

That mismatch creates drift and forces frontend fallback logic.

## Scope
- update `src/feed/feed.controller.ts`
- update `src/feed/feed-aggregator.service.ts`
- map persistence entities to canonical DTO
- ensure `generatedAt` is always populated
- ensure role context is explicit and consistent
- strip backend-only/internal fields from outward response

## Acceptance Criteria
- `GET /feed` returns canonical `FeedResponse`
- no raw ORM payload is returned directly to feed clients
- item list shape matches shared frontend expectations
- automated tests validate the response contract

## Deliverables
- DTO implementation
- mapping layer
- unit/integration tests
```

---

## Issue 3

**Title:** Update frontend admin feed client to use one canonical route

**Labels:** `p0`, `frontend`, `feed`, `contract-drift`

**Body:**
```md
## Summary
Remove route guessing from frontend feed consumers and standardize on the canonical admin feed route.

## Problem
Frontend feed clients currently appear to branch between multiple route families. That makes the client fragile and obscures the true contract.

## Scope
- update `feed-api.ts`
- update `useCoPilotFeed()`
- remove legacy route-guessing and branching in production path
- align request params with canonical feed contract

## Acceptance Criteria
- frontend feed client targets exactly one canonical route in normal operation
- no production code guesses between `/api/feed`, `/api/v2/feed`, and `/feed`
- feed UI works against canonical DTO

## Deliverables
- updated frontend data layer
- refreshed tests/fixtures/mocks
```

---

## Issue 4

**Title:** Inventory and classify all admin feed actions

**Labels:** `p0`, `feed`, `api`, `product`, `contract-drift`

**Body:**
```md
## Summary
Identify every action launched from the admin feed UI and classify whether it is:
- a real feed mutation
- a domain mutation launched from the feed surface
- a navigation shortcut only

## Problem
Frontend assumes a generic feed action mutation path exists, but the inspected backend surface does not clearly provide one beyond note updates. The team should not implement a generic endpoint blindly without classifying the action set.

## Scope
- inventory actions used in `useCoPilotFeed()`
- map each action to its true business owner
- identify dead/speculative actions
- decide whether a feed façade route is justified

## Acceptance Criteria
- every feed action has an identified backend owner
- dead or speculative actions are explicitly labeled
- team has a decision on façade route vs direct domain mutations

## Deliverables
- action inventory table
- decision note
```

---

## Issue 5

**Title:** Implement canonical feed action mutation path or remove dead frontend assumption

**Labels:** `p0`, `frontend`, `backend`, `feed`, `contract-drift`

**Body:**
```md
## Summary
Eliminate the broken assumption that `POST /api/feed/actions` exists unless the team intentionally implements a canonical equivalent.

## Problem
Frontend expects a feed action mutation route that does not appear to exist in the inspected backend. That is a direct execution risk.

## Scope
Choose one path:

### Option A, façade route
- implement canonical `POST /feed/actions`
- accept typed action payloads
- dispatch internally to domain handlers
- return normalized result payload

### Option B, direct domain routes
- remove generic feed action endpoint assumption from frontend
- route actions directly to true domain APIs

## Acceptance Criteria
- no frontend action targets a missing endpoint
- all supported feed actions execute end to end
- unsupported actions fail explicitly rather than silently drifting

## Deliverables
- implemented mutation path or removed abstraction
- updated frontend mutation layer
- action contract tests
```

---

## Issue 6

**Title:** Normalize screening policy evaluation route

**Labels:** `p0`, `frontend`, `backend`, `screening`, `contract-drift`

**Body:**
```md
## Summary
Resolve the route mismatch between frontend screening policy evaluation calls and the backend route that actually exists.

## Problem
Frontend expects:
- `GET /screening/:applicationId/policy-evaluation`

Backend exposes:
- `GET /rental-applications/:id/policy-evaluation`

This is a hard contract mismatch.

## Scope
- update frontend `fetchPolicyEvaluation(applicationId)` to call the canonical backend route
- optionally add compatibility alias on backend if release coordination is difficult
- update tests and references

## Acceptance Criteria
- policy evaluation loads successfully in screening workspace
- active production code no longer depends on `/screening/:applicationId/policy-evaluation`
- route is documented consistently

## Deliverables
- updated client call
- optional compatibility alias
- route test coverage
```

---

## Issue 7

**Title:** Define canonical role enum and serialization strategy

**Labels:** `p0`, `auth`, `api`, `contract-drift`

**Body:**
```md
## Summary
Define one canonical role vocabulary and casing strategy across frontend, backend guards, shared types, and mock/dev auth.

## Problem
Role drift currently appears in multiple forms:
- frontend roles: `owner | property_manager | leasing | maintenance`
- backend guard roles: `TENANT`, `PROPERTY_MANAGER`, `OWNER`, `ADMIN`
- mock headers and dev values: `admin`, `tenant`, `PROPERTY_MANAGER`

This creates authorization ambiguity and hidden breakage.

## Scope
- define canonical role enum
- define casing and wire-format rules
- define temporary legacy-to-canonical mapping if required
- decide whether roles like `LEASING` and `MAINTENANCE` are true auth roles or merely workspace personas

## Acceptance Criteria
- one canonical role vocabulary is approved
- serialization/casing rules are explicit
- legacy values, if accepted, have a single documented mapping path

## Deliverables
- shared enum/contract definition
- mapping note or ADR
```

---

## Issue 8

**Title:** Normalize frontend role usage, mock auth headers, and fixtures

**Labels:** `p0`, `frontend`, `auth`, `contract-drift`

**Body:**
```md
## Summary
Remove ad hoc role values and casing drift from frontend code, mocks, and fixtures.

## Problem
Frontend still appears to rely on inconsistent role names and mock/dev headers. That leaks instability into both UI logic and local testing.

## Scope
- update frontend role types
- update auth helpers and mock headers
- centralize temporary role mapping if needed
- update tests and fixtures to canonical values

## Acceptance Criteria
- no production frontend path depends on ad hoc role casing
- frontend role handling aligns with canonical enum
- fixtures and mocks no longer encode conflicting vocabularies

## Deliverables
- role utility module or shared role import usage
- updated tests/mocks
```

---

## Issue 9

**Title:** Normalize backend role guards and ingress role parsing

**Labels:** `p0`, `backend`, `auth`, `contract-drift`

**Body:**
```md
## Summary
Ensure backend authorization and role parsing consistently interpret canonical role values.

## Problem
Backend guards and request parsing may be tolerant of multiple role strings today, but without a single ingress normalization point this becomes brittle and inconsistent.

## Scope
- audit guard/decorator/middleware role handling
- align checks to canonical enum
- if legacy values must remain temporarily supported, normalize them in one place only
- add tests for role parsing and authorization behavior

## Acceptance Criteria
- backend authorization uses canonical role semantics consistently
- canonical values work across protected routes
- legacy role support, if present, is centralized and explicit

## Deliverables
- updated auth guard or ingress normalization layer
- guard/integration tests
```

---

## Issue 10

**Title:** Align Stripe checkout session response contract

**Labels:** `p1`, `frontend`, `backend`, `payments`, `contract-drift`

**Body:**
```md
## Summary
Resolve the mismatch between frontend checkout expectation `{ url }` and backend response `{ checkoutUrl, sessionId, invoiceId }`.

## Problem
The checkout redirect flow depends on a property name mismatch. It is small but concrete and easy to break.

## Scope
Preferred direction:
- keep richer backend response
- update frontend to consume `checkoutUrl`
- expose typed response contract

Optional migration shim:
- backend temporarily also returns `url`

## Acceptance Criteria
- checkout redirect works end to end
- frontend and backend share one explicit response type
- no untyped property assumption remains in checkout flow

## Deliverables
- aligned DTO
- updated redirect consumer
- test coverage for redirect path
```
