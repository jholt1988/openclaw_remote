# Full Backend-to-Frontend Feature Gap Analysis

Run a complete gap analysis between `pms-master/tenant_portal_backend` backend modules and `keyring-os` frontend components, following decision-driven property management principles.

---

## System Context

| Layer | Location | Tech |
|-------|----------|------|
| Backend | `pms-master/tenant_portal_backend/src/` | NestJS, Prisma, PostgreSQL |
| Frontend (Admin) | `keyring-os/apps/admin/src/` | Next.js, React |
| Frontend (Tenant) | `keyring-os/apps/tenant-portal/src/` | Next.js, React |
| Shared Types | `keyring-os/packages/types/src/` | TypeScript |
| Issue Tracker | `openclaw_remote` | GitHub Issues |

## Philosophy (Non-Negotiable)

> **Decision-Driven**: Every visible element is either state (displayed) or a decision (actionable). No passive data tables. No raw forms. Every human-performed action surfaces as a decision card with 1-3 action buttons.

- **Contract-First**: Frontend DTOs MUST match backend exactly. No aliases. Ever.
- **Shared Types Only**: Import from `@keyring/types` — never define inline types
- **Structure**: `features/[domain]/components/` — domain owns its components
- **Data Fetching**: React Query only
- **Severity Required**: Every decision needs priority (critical/warning/info) + visual indicator

---

## Execution Steps

### Step 1: Map Backend Modules

Foreach module in `pms-master/tenant_portal_backend/src/`:
1. List ALL controllers (files ending in `.controller.ts`)
2. Extract ALL endpoints with HTTP method + path
3. Extract request DTOs (from `./dto/`) and response types
4. Identify which endpoints require human decision vs. passive data

```bash
# Example discovery commands
find pms-master/tenant_portal_backend/src -name "*.controller.ts" -exec grep -H "@Get\|@Post\|@Put\|@Delete" {} \;
find pms-master/tenant_portal_backend/src -name "dto/*.ts" | head -20;
```

### Step 2: Map Frontend Components

For both `apps/admin` and `apps/tenant-portal`:
1. List ALL pages in `src/app/[domain]/page.tsx`
2. List ALL feature components in `src/features/[domain]/components/`
3. List ALL API clients in `src/lib/*-api.ts`
4. Identify decision cards vs. raw displays

```bash
# Example discovery
find keyring-os/apps/admin/src -name "page.tsx" | grep -v layout | head -30;
find keyring-os/apps/admin/src/features -type d -maxdepth 1;
ls keyring-os/apps/admin/src/lib/*-api.ts 2>/dev/null;
```

### Step 3: Cross-Reference (The Gap Matrix)

For each backend endpoint, answer:

| Question | If No → Gap |
|----------|-------------|
| Does frontend have API client function? | **API client missing** |
| Is response type in `@keyring/types`? | **Type not shared** |
| Is there a component showing this? | **Component missing** |
| Is it a decision card (not table/form)? | **Not decision-driven** |
| Does card show severity? | **No priority signal** |
| Does card have action buttons? | **No actions** |

### Step 4: Severity Scoring

Rate each gap:

| Priority | Criteria |
|----------|----------|
| **HIGH** | Revenue-affecting (billing, payments), security-related (auth), or blocks core workflow |
| **MEDIUM** | Important but not urgent — partial feature, missing polish |
| **LOW** | Nice-to-have, edge case, or cosmetic |

---

## Output FORMAT

### Summary Stats
- Total backend endpoints analyzed: N
- Total frontend components found: N
- Gaps identified: N
- HIGH: N | MEDIUM: N | LOW: N

### Gap Report (Sorted by Priority)

#### HIGH: [Gap Title]
- **Backend Source**: `src/[module]/[controller].ts:L42` — `POST /api/[resource]`
- **Frontend State**: 
  - API client: [exists / missing]
  - Component: [exists / missing]
  - Type in `@keyring/types`: [yes / no]
- **Philosophy Violation**: [What principle is violated]
- **Suggested Fix**: [Concrete implementation]
- **Files**:
  - Create: `src/features/[module]/components/[name].tsx`
  - Modify: `src/features/[module]/components/index.ts`
  - Type: Add to `packages/types/src/[module].ts`

#### MEDIUM: [Gap Title]
... (same structure)

#### LOW: [Gap Title]
... (same structure)

---

## Example Output Entry

### HIGH: Autopay Enrollment Decision Missing
- **Backend Source**: `src/billing/billing.controller.ts:42` — `POST /api/billing/autopay`
- **Frontend State**: API client: `autopay-enrollment.ts` | Component: **MISSING** | Type: partially shared
- **Philosophy Violation**: Backend can enroll tenants in autopay (action requiring decision), but no decision card surfaces this in frontend
- **Suggested Fix**: Create `features/billing/components/autopay-enrollment-card.tsx` with:
  - Tenant name + property from context
  - Amount from backend response
  - Priority derived from payment history (HIGH if delinquent)
  - Actions: "Enable Autopay" / "Remind Later" / "Dismiss"
  - Follow `PaymentsDecisionCard` pattern from `features/payments/components/`
- **Files**:
  - Create: `apps/admin/src/features/billing/components/autopay-enrollment-card.tsx`
  - Update: `apps/admin/src/features/billing/components/index.ts`
  - Update: `packages/types/src/billing.ts` (ensure type shared)

---

## Prompt to Run

> Run this full analysis now. Start by mapping backend modules in `pms-master/tenant_portal_backend/src/`, then cross-reference with frontend in `keyring-os/apps/admin/src/` and `keyring-os/apps/tenant-portal/src/`. Output the complete gap report with severity scores and suggested fixes.