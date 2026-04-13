# Keyring OS Final Admin UI Implementation Plan

**Goal:** Deliver the final Keyring OS UI direction by upgrading admin decision surfaces, adding ambient intelligence, improving tenant workflows, and introducing a full rental application experience.

**Architecture:** Keep the current decision-driven architecture intact and extend it additively. Shared decision contracts expand first, backend feed aggregation and analytics follow, then admin and tenant UIs adopt the new metadata and ambient interaction patterns. Rental applications become a first-class workflow spanning tenant submission and admin review.

**Technology Stack:** Next.js App Router, React, TypeScript, TanStack Query, NestJS, Prisma, shared `@keyring/types`, Tailwind-style utility classes, existing event-emitter feed pipeline

---

## File Map

### Shared contracts
- Modify: `keyring-os/packages/types/src/copilot.ts`

### Admin frontend
- Modify: `keyring-os/apps/admin/src/features/payments/components/decision-card.tsx`
- Modify: `keyring-os/apps/admin/src/features/copilot/components/app-shell.tsx`
- Modify: `keyring-os/apps/admin/src/features/copilot/components/command-composer.tsx`
- Modify: `keyring-os/apps/admin/src/features/copilot/components/command-node.tsx`
- Create: `keyring-os/apps/admin/src/features/copilot/components/context-panel.tsx`
- Create: `keyring-os/apps/admin/src/features/copilot/components/workflow-timeline.tsx`
- Create: `keyring-os/apps/admin/src/features/copilot/components/floating-orb.tsx`
- Create: `keyring-os/apps/admin/src/features/copilot/components/ambient-signal-cluster.tsx`
- Create: `keyring-os/apps/admin/src/features/copilot/lib/decision-analytics.ts`

### Tenant frontend
- Modify: `keyring-os/apps/tenant-portal/src/app/layout.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/app/payments/page.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/app/maintenance/new/page.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/lib/tenant-api.ts`
- Create: `keyring-os/apps/tenant-portal/src/components/ambient/tenant-control-orb.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/forms/floating-validation.tsx`
- Create: `keyring-os/apps/tenant-portal/src/app/apply/page.tsx`
- Create: `keyring-os/apps/tenant-portal/src/app/apply/[id]/page.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/application-shell.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/identity-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/housing-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/employment-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/occupants-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/background-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/documents-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/review-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/auth/auth-decision-surface.tsx`

### Backend
- Modify: `pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.ts`
- Create: `pms-master/tenant_portal_backend/src/feed/feed.types.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/analytics.controller.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/analytics.service.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/dto/track-decision-event.dto.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/dto/track-ui-event.dto.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/rental-applications.controller.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/rental-applications.service.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/dto/create-rental-application.dto.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/dto/update-rental-application.dto.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/dto/review-rental-application.dto.ts`
- Create: Prisma schema/migration files for rental applications and analytics tables

### Tests
- Create: `keyring-os/packages/types/src/copilot.test.ts`
- Create: `keyring-os/apps/admin/src/features/payments/components/decision-card.test.tsx`
- Create: `keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx`
- Create: `pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/rental-applications.service.spec.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/analytics.controller.spec.ts`

---

### Task 1: Extend shared decision contracts

**Files:**
- Modify: `keyring-os/packages/types/src/copilot.ts`
- Test: `keyring-os/packages/types/src/copilot.test.ts`

- [ ] **Step 1: write failing shared-type assertions**

```ts
import type { Decision, DecisionAction } from './copilot';

const action: DecisionAction = {
  label: 'Approve',
  endpoint: '/decisions/1/approve',
  method: 'POST',
  variant: 'primary',
  tooltip: 'Approve this decision',
  confirmRequired: true,
  confirmation: {
    title: 'Approve decision?',
    message: 'This action cannot be undone.',
  },
  metadata: {
    trackingId: 'decision-1-approve',
    estimatedTime: '2m',
    dependencies: ['policy-check'],
  },
};

const decision: Decision = {
  id: 'd1',
  domain: 'payments',
  entityType: 'invoice',
  entityId: 'inv_1',
  title: 'Approve payment plan',
  context: 'Resident requested 2-part payment plan.',
  urgency: 'today',
  type: 'approval',
  priority: 8,
  confidenceScore: 91,
  reasoning: ['Resident paid on time 11 of last 12 months'],
  impact: { financial: 1250, risk: 'low', timeline: 'today' },
  relatedDecisionIds: ['d0'],
  workflow: { stage: 'review', totalStages: 3, currentStageIndex: 2, eta: '15m' },
  actions: [action],
  aiRecommendation: 'Approve with reminder',
};

expect(decision.confidenceScore).toBe(91);
expect(action.metadata?.estimatedTime).toBe('2m');
```

- [ ] **Step 2: run the shared type test and confirm failure**

Run: `pnpm test keyring-os/packages/types/src/copilot.test.ts`
Expected: FAIL because `tooltip`, `confidenceScore`, `impact`, `workflow`, and `relatedDecisionIds` are not yet defined.

- [ ] **Step 3: implement additive contract changes**

Add these exact fields in `copilot.ts`:

```ts
export type DecisionType = 'approval' | 'review' | 'escalation';
export type DecisionRisk = 'low' | 'medium' | 'high';

export interface DecisionWorkflow {
  stage: string;
  totalStages?: number;
  currentStageIndex?: number;
  eta?: string;
}

export interface DecisionImpact {
  financial?: number;
  timeline?: string;
  risk?: DecisionRisk;
}
```

Then extend existing interfaces:

```ts
export interface DecisionAction {
  label: string;
  endpoint: string;
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: Record<string, unknown>;
  variant: 'primary' | 'danger' | 'neutral' | 'secondary';
  confirmRequired?: boolean;
  description?: string;
  tooltip?: string;
  confirmation?: DecisionActionConfirmation;
  metadata?: {
    trackingId?: string;
    category?: string;
    estimatedTime?: string;
    dependencies?: string[];
    [key: string]: unknown;
  };
}

export interface Decision {
  id: string;
  domain: Domain;
  entityType: string;
  entityId: string;
  title: string;
  summary?: string;
  context: string;
  reasoning?: string[];
  priority?: number;
  type?: DecisionType;
  confidenceScore?: number;
  impact?: DecisionImpact;
  relatedDecisionIds?: string[];
  workflow?: DecisionWorkflow;
  aiRecommendation?: string;
  actions: DecisionAction[];
  urgency: Urgency;
}
```

- [ ] **Step 4: rerun the shared type test**

Run: `pnpm test keyring-os/packages/types/src/copilot.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/packages/types/src/copilot.ts keyring-os/packages/types/src/copilot.test.ts
git commit -m "feat: extend copilot decision contracts"
```

### Task 2: Normalize feed types and enhanced payload mapping

**Files:**
- Create: `pms-master/tenant_portal_backend/src/feed/feed.types.ts`
- Modify: `pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.ts`
- Test: `pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts`

- [ ] **Step 1: write failing mapping tests**

```ts
it('maps evidence metadata into enhanced decision fields', () => {
  const item = {
    id: 'item-1',
    domain: 'payments',
    type: 'decision',
    title: 'Approve hardship plan',
    summary: 'Resident requested help',
    priorityScore: 82,
    createdAt: new Date('2026-04-13T10:00:00.000Z'),
    updatedAt: new Date('2026-04-13T10:05:00.000Z'),
    actions: [{ label: 'Approve', intent: 'approve', variant: 'primary' }],
    roleAccess: ['admin'],
    evidence: {
      reasoning: ['Resident has 11 month streak'],
      type: 'approval',
      confidenceScore: 88,
      impact: { financial: 1400, risk: 'low', timeline: 'today' },
      relatedDecisionIds: ['prev-1'],
      workflow: { stage: 'manager_review', totalStages: 3, currentStageIndex: 2 },
    },
  };

  const mapped = service['toCanonicalFeedItem'](item);
  expect(mapped.metadata?.confidenceScore).toBe(88);
  expect(mapped.metadata?.workflow).toEqual({ stage: 'manager_review', totalStages: 3, currentStageIndex: 2 });
});
```

- [ ] **Step 2: run backend feed tests and confirm failure**

Run: `pnpm test pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts`
Expected: FAIL because enhanced fields are not normalized into structured feed types.

- [ ] **Step 3: create explicit feed type definitions**

Create `feed.types.ts` with:

```ts
export interface CanonicalFeedMetadata {
  reasoning?: string[];
  type?: 'approval' | 'review' | 'escalation';
  confidenceScore?: number;
  impact?: {
    financial?: number;
    timeline?: string;
    risk?: 'low' | 'medium' | 'high';
  };
  relatedDecisionIds?: string[];
  workflow?: {
    stage: string;
    totalStages?: number;
    currentStageIndex?: number;
    eta?: string;
  };
  notes?: unknown[];
  [key: string]: unknown;
}
```

Refactor `feed-aggregator.service.ts` to import these types and stop using anonymous `Record<string, unknown>` where the metadata shape is known.

- [ ] **Step 4: map enhanced evidence fields in the service**

In `toCanonicalFeedItem`, preserve the existing behavior and add exact extraction:

```ts
const metadata: CanonicalFeedMetadata | undefined = evidence
  ? {
      ...evidence,
      reasoning: Array.isArray(evidence.reasoning) ? evidence.reasoning as string[] : undefined,
      type: typeof evidence.type === 'string' ? evidence.type as CanonicalFeedMetadata['type'] : undefined,
      confidenceScore: typeof evidence.confidenceScore === 'number' ? evidence.confidenceScore : undefined,
      impact: evidence.impact as CanonicalFeedMetadata['impact'] | undefined,
      relatedDecisionIds: Array.isArray(evidence.relatedDecisionIds)
        ? evidence.relatedDecisionIds as string[]
        : undefined,
      workflow: evidence.workflow as CanonicalFeedMetadata['workflow'] | undefined,
    }
  : undefined;
```

Also extend action mapping so `description`, `tooltip`, and nested confirmation are preserved.

- [ ] **Step 5: rerun feed tests**

Run: `pnpm test pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add pms-master/tenant_portal_backend/src/feed/feed.types.ts pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.ts pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts
git commit -m "feat: normalize enhanced feed metadata"
```

### Task 3: Add analytics ingestion endpoints

**Files:**
- Create: `pms-master/tenant_portal_backend/src/analytics/analytics.controller.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/analytics.service.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/dto/track-decision-event.dto.ts`
- Create: `pms-master/tenant_portal_backend/src/analytics/dto/track-ui-event.dto.ts`
- Test: `pms-master/tenant_portal_backend/src/analytics/analytics.controller.spec.ts`

- [ ] **Step 1: write failing controller test**

```ts
it('records a decision analytics event', async () => {
  const payload = {
    decisionId: 'd1',
    actionTaken: 'approve',
    timeToDecisionMs: 14000,
    confidenceAtTime: 88,
  };

  const response = await request(app.getHttpServer())
    .post('/analytics/decision-events')
    .send(payload)
    .expect(201);

  expect(response.body.ok).toBe(true);
});
```

- [ ] **Step 2: run analytics tests and confirm failure**

Run: `pnpm test pms-master/tenant_portal_backend/src/analytics/analytics.controller.spec.ts`
Expected: FAIL because analytics module does not exist.

- [ ] **Step 3: implement DTOs and controller**

Use these exact DTO shapes:

```ts
export class TrackDecisionEventDto {
  decisionId!: string;
  actionTaken!: string;
  timeToDecisionMs!: number;
  confidenceAtTime?: number;
  outcome?: 'approved' | 'rejected' | 'deferred' | 'escalated';
}

export class TrackUiEventDto {
  eventType!: 'decision_view' | 'action_click' | 'panel_expand' | 'context_switch' | 'application_step_view';
  elementId?: string;
  sessionDurationMs?: number;
  path?: string[];
}
```

Controller routes:
- `POST /analytics/decision-events`
- `POST /analytics/ui-events`
- `GET /analytics/decision-summary`
- `GET /analytics/workflow-performance`

Return `{ ok: true }` for POSTs in the first pass.

- [ ] **Step 4: rerun analytics tests**

Run: `pnpm test pms-master/tenant_portal_backend/src/analytics/analytics.controller.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pms-master/tenant_portal_backend/src/analytics
git commit -m "feat: add analytics ingestion endpoints"
```

### Task 4: Upgrade DecisionCard UI

**Files:**
- Modify: `keyring-os/apps/admin/src/features/payments/components/decision-card.tsx`
- Test: `keyring-os/apps/admin/src/features/payments/components/decision-card.test.tsx`

- [ ] **Step 1: write failing UI test**

```tsx
it('renders priority, confidence, reasoning, and impact summary', () => {
  render(
    <DecisionCard
      decision={{
        id: 'd1',
        domain: 'payments',
        entityType: 'invoice',
        entityId: 'inv_1',
        title: 'Approve payment plan',
        context: 'Resident requested 2-part payment plan.',
        urgency: 'today',
        type: 'approval',
        priority: 8,
        confidenceScore: 91,
        reasoning: ['Resident history supports approval'],
        impact: { financial: 1250, risk: 'low', timeline: 'today' },
        actions: [{ label: 'Approve', endpoint: '/approve', method: 'POST', variant: 'primary' }],
      }}
      onExecute={vi.fn()}
      onDismiss={vi.fn()}
    />,
  );

  expect(screen.getByText('P8')).toBeInTheDocument();
  expect(screen.getByText('91% confidence')).toBeInTheDocument();
  expect(screen.getByText('Resident history supports approval')).toBeInTheDocument();
  expect(screen.getByText('$1,250 impact')).toBeInTheDocument();
});
```

- [ ] **Step 2: run DecisionCard test and confirm failure**

Run: `pnpm test keyring-os/apps/admin/src/features/payments/components/decision-card.test.tsx`
Expected: FAIL because the component does not render enhanced fields.

- [ ] **Step 3: implement the smallest enhanced UI**

Add the following UI blocks without changing existing button behavior:
- top-left type badge
- top-right priority pill showing `P{priority}`
- confidence pill showing `{confidenceScore}% confidence`
- reasoning list under context when present
- impact summary line using `financial`, `risk`, `timeline`
- preserve dismiss and primary action behavior

Use exact fallback rules:
- no reasoning block if `decision.reasoning?.length` is falsy
- no confidence badge if `typeof decision.confidenceScore !== 'number'`
- no impact row if `!decision.impact`

- [ ] **Step 4: rerun DecisionCard test**

Run: `pnpm test keyring-os/apps/admin/src/features/payments/components/decision-card.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/admin/src/features/payments/components/decision-card.tsx keyring-os/apps/admin/src/features/payments/components/decision-card.test.tsx
git commit -m "feat: enhance admin decision cards"
```

### Task 5: Add admin context panel and workflow timeline

**Files:**
- Create: `keyring-os/apps/admin/src/features/copilot/components/context-panel.tsx`
- Create: `keyring-os/apps/admin/src/features/copilot/components/workflow-timeline.tsx`
- Modify: `keyring-os/apps/admin/src/features/copilot/components/app-shell.tsx`

- [ ] **Step 1: write failing render tests for new components**

```tsx
it('renders workflow stage and reasoning in context panel', () => {
  render(
    <ContextPanel
      open
      onClose={() => {}}
      decision={{
        id: 'd1',
        title: 'Approve payment plan',
        context: 'Resident requested help',
        reasoning: ['Income verified'],
        workflow: { stage: 'review', totalStages: 3, currentStageIndex: 2, eta: '15m' },
      } as any}
    />,
  );

  expect(screen.getByText('Approve payment plan')).toBeInTheDocument();
  expect(screen.getByText('Income verified')).toBeInTheDocument();
  expect(screen.getByText('review')).toBeInTheDocument();
});
```

- [ ] **Step 2: run tests and confirm failure**

Run: `pnpm test keyring-os/apps/admin/src/features/copilot/components/context-panel.test.tsx`
Expected: FAIL because the components do not exist.

- [ ] **Step 3: build thin, presentational versions first**

`context-panel.tsx` should:
- slide from the right
- accept `open`, `onClose`, `decision`
- render title, context, reasoning, workflow, related decisions count

`workflow-timeline.tsx` should:
- accept `workflow`
- render stage, `currentStageIndex / totalStages`, ETA

Then mount a dormant panel shell in `app-shell.tsx` so the ambient architecture is ready even if selection state is mocked initially.

- [ ] **Step 4: rerun tests**

Run: `pnpm test keyring-os/apps/admin/src/features/copilot/components/context-panel.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/admin/src/features/copilot/components/context-panel.tsx keyring-os/apps/admin/src/features/copilot/components/workflow-timeline.tsx keyring-os/apps/admin/src/features/copilot/components/app-shell.tsx
git commit -m "feat: add admin decision context panel"
```

### Task 6: Add admin ambient orb primitives

**Files:**
- Create: `keyring-os/apps/admin/src/features/copilot/components/floating-orb.tsx`
- Create: `keyring-os/apps/admin/src/features/copilot/components/ambient-signal-cluster.tsx`
- Modify: `keyring-os/apps/admin/src/features/copilot/components/command-node.tsx`
- Modify: `keyring-os/apps/admin/src/features/copilot/components/command-composer.tsx`

- [ ] **Step 1: write failing UI tests**

```tsx
it('renders a floating orb with severity state', () => {
  render(<FloatingOrb severity="high" label="3 urgent items" />);
  expect(screen.getByText('3 urgent items')).toBeInTheDocument();
});
```

- [ ] **Step 2: run tests and confirm failure**

Run: `pnpm test keyring-os/apps/admin/src/features/copilot/components/floating-orb.test.tsx`
Expected: FAIL because the ambient components do not exist.

- [ ] **Step 3: implement ambient primitives**

`floating-orb.tsx` props:

```ts
{
  severity: 'critical' | 'high' | 'medium' | 'low';
  label: string;
  pulse?: boolean;
}
```

Behavior:
- radial gradient background
- severity-driven accent ring
- optional pulse animation

Update `command-node.tsx` to wrap the existing command button in the new orb styling instead of replacing behavior.

Update `command-composer.tsx` placeholder from `What needs to happen now?` to:

```ts
"Ask, decide, or jump to a workflow"
```

- [ ] **Step 4: rerun ambient tests**

Run: `pnpm test keyring-os/apps/admin/src/features/copilot/components/floating-orb.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/admin/src/features/copilot/components/floating-orb.tsx keyring-os/apps/admin/src/features/copilot/components/ambient-signal-cluster.tsx keyring-os/apps/admin/src/features/copilot/components/command-node.tsx keyring-os/apps/admin/src/features/copilot/components/command-composer.tsx
git commit -m "feat: add ambient admin interaction layer"
```

### Task 7: Add tenant control orb and payments ambient state

**Files:**
- Create: `keyring-os/apps/tenant-portal/src/components/ambient/tenant-control-orb.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/app/layout.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/app/payments/page.tsx`

- [ ] **Step 1: write failing tenant orb test**

```tsx
it('shows overdue state in tenant control orb', () => {
  render(<TenantControlOrb state="overdue" label="Payment due" />);
  expect(screen.getByText('Payment due')).toBeInTheDocument();
});
```

- [ ] **Step 2: run tenant orb tests and confirm failure**

Run: `pnpm test keyring-os/apps/tenant-portal/src/components/ambient/tenant-control-orb.test.tsx`
Expected: FAIL because the component does not exist.

- [ ] **Step 3: implement orb and page integration**

`tenant-control-orb.tsx` props:

```ts
{
  state: 'healthy' | 'attention' | 'overdue' | 'lease_expiring' | 'maintenance_open';
  label: string;
}
```

Layout integration:
- mount orb near the lower-right viewport area
- keep sidebar and main content unchanged

Payments page integration:
- compute orb state from `totalDue` and `nextDue`
- add a compact ambient status row above the balance card
- if `totalDue > 0`, show text `Action needed` with amber styling

- [ ] **Step 4: rerun tenant orb tests**

Run: `pnpm test keyring-os/apps/tenant-portal/src/components/ambient/tenant-control-orb.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/tenant-portal/src/components/ambient/tenant-control-orb.tsx keyring-os/apps/tenant-portal/src/app/layout.tsx keyring-os/apps/tenant-portal/src/app/payments/page.tsx
git commit -m "feat: add tenant ambient control orb"
```

### Task 8: Upgrade maintenance form transitions and validation hints

**Files:**
- Create: `keyring-os/apps/tenant-portal/src/components/forms/floating-validation.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/app/maintenance/new/page.tsx`

- [ ] **Step 1: write failing validation-hint test**

```tsx
it('renders validation message beside a field', () => {
  render(<FloatingValidation message="Title is required" />);
  expect(screen.getByText('Title is required')).toBeInTheDocument();
});
```

- [ ] **Step 2: run test and confirm failure**

Run: `pnpm test keyring-os/apps/tenant-portal/src/components/forms/floating-validation.test.tsx`
Expected: FAIL because the component does not exist.

- [ ] **Step 3: implement minimal enhancement**

Create `floating-validation.tsx` as a small badge-like helper.

Replace inline error `<p>` blocks in `maintenance/new/page.tsx` with `<FloatingValidation message={errors.title} />` pattern.

Add these exact motion-oriented class upgrades to the form card wrapper:

```ts
className="transition-all duration-300 hover:shadow-[0_18px_60px_rgba(2,8,23,0.28)]"
```

- [ ] **Step 4: rerun validation-hint test**

Run: `pnpm test keyring-os/apps/tenant-portal/src/components/forms/floating-validation.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/tenant-portal/src/components/forms/floating-validation.tsx keyring-os/apps/tenant-portal/src/app/maintenance/new/page.tsx
git commit -m "feat: improve maintenance form focus states"
```

### Task 9: Add rental application API contracts in tenant client

**Files:**
- Modify: `keyring-os/apps/tenant-portal/src/lib/tenant-api.ts`
- Test: `keyring-os/apps/tenant-portal/src/lib/tenant-api.test.ts`

- [ ] **Step 1: write failing client API test**

```ts
it('posts rental application draft', async () => {
  global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 'app_1', status: 'draft' }) }) as any;
  const result = await createRentalApplication({ propertyId: 'prop_1', applicant: { firstName: 'A', lastName: 'B' } });
  expect(result.id).toBe('app_1');
});
```

- [ ] **Step 2: run test and confirm failure**

Run: `pnpm test keyring-os/apps/tenant-portal/src/lib/tenant-api.test.ts`
Expected: FAIL because rental application client helpers do not exist.

- [ ] **Step 3: add exact client functions**

Add these exports:

```ts
export async function createRentalApplication(data: Record<string, unknown>) {
  return api('/rental-applications', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateRentalApplication(id: string, data: Record<string, unknown>) {
  return api(`/rental-applications/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export async function submitRentalApplication(id: string) {
  return api(`/rental-applications/${id}/submit`, { method: 'POST', body: JSON.stringify({}) });
}

export async function fetchRentalApplication(id: string) {
  return api(`/rental-applications/${id}`);
}
```

- [ ] **Step 4: rerun tenant API tests**

Run: `pnpm test keyring-os/apps/tenant-portal/src/lib/tenant-api.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/tenant-portal/src/lib/tenant-api.ts keyring-os/apps/tenant-portal/src/lib/tenant-api.test.ts
git commit -m "feat: add rental application tenant api client"
```

### Task 10: Build rental application shell and first three steps

**Files:**
- Create: `keyring-os/apps/tenant-portal/src/app/apply/page.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/application-shell.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/identity-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/housing-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/employment-step.tsx`
- Test: `keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx`

- [ ] **Step 1: write failing page test**

```tsx
it('renders rental application identity step', () => {
  render(<ApplicationPage />);
  expect(screen.getByText('Rental Application')).toBeInTheDocument();
  expect(screen.getByLabelText('First name')).toBeInTheDocument();
});
```

- [ ] **Step 2: run application page test and confirm failure**

Run: `pnpm test keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx`
Expected: FAIL because the route and components do not exist.

- [ ] **Step 3: build the shell and first steps**

`application-shell.tsx` props:

```ts
{
  step: number;
  totalSteps: number;
  title: string;
  children: React.ReactNode;
  onNext?: () => void;
  onBack?: () => void;
}
```

Identity step fields:
- First name
- Last name
- Date of birth
- Email
- Phone

Housing step fields:
- Current address
- Landlord name
- Monthly rent
- Reason for leaving

Employment step fields:
- Employer
- Position
- Monthly income
- Employment start date

Use local state only in this task. Do not submit yet.

- [ ] **Step 4: rerun page test**

Run: `pnpm test keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/tenant-portal/src/app/apply/page.tsx keyring-os/apps/tenant-portal/src/components/rental-application/application-shell.tsx keyring-os/apps/tenant-portal/src/components/rental-application/identity-step.tsx keyring-os/apps/tenant-portal/src/components/rental-application/housing-step.tsx keyring-os/apps/tenant-portal/src/components/rental-application/employment-step.tsx keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx
git commit -m "feat: add rental application entry flow"
```

### Task 11: Complete application steps and submit flow

**Files:**
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/occupants-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/background-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/documents-step.tsx`
- Create: `keyring-os/apps/tenant-portal/src/components/rental-application/review-step.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/app/apply/page.tsx`
- Create: `keyring-os/apps/tenant-portal/src/app/apply/[id]/page.tsx`

- [ ] **Step 1: write failing submit-flow test**

```tsx
it('submits the rental application and shows status page link', async () => {
  render(<ApplicationPage />);
  await user.click(screen.getByText('Submit application'));
  expect(mockSubmitRentalApplication).toHaveBeenCalled();
});
```

- [ ] **Step 2: run submit-flow test and confirm failure**

Run: `pnpm test keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx`
Expected: FAIL because later steps and submit flow do not exist.

- [ ] **Step 3: implement later steps and status page**

Add steps with these required fields:
- Occupants: co-applicant count, dependents, pets, vehicles
- Background: eviction history, bankruptcy disclosure, criminal disclosure acknowledgment
- Documents: ID upload placeholder, income proof upload placeholder
- Review: summary blocks + consent checkbox

Submit behavior:
- create draft on first save
- patch updates on next/back transitions after draft exists
- call `submitRentalApplication(id)` on final submit
- navigate to `/apply/[id]` after submit

Status page should render:
- application id
- status badge
- last updated date
- next expected step text

- [ ] **Step 4: rerun submit-flow tests**

Run: `pnpm test keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/tenant-portal/src/components/rental-application/occupants-step.tsx keyring-os/apps/tenant-portal/src/components/rental-application/background-step.tsx keyring-os/apps/tenant-portal/src/components/rental-application/documents-step.tsx keyring-os/apps/tenant-portal/src/components/rental-application/review-step.tsx keyring-os/apps/tenant-portal/src/app/apply/page.tsx keyring-os/apps/tenant-portal/src/app/apply/[id]/page.tsx
git commit -m "feat: complete rental application workflow"
```

### Task 12: Build rental application backend module

**Files:**
- Create: `pms-master/tenant_portal_backend/src/rental-applications/rental-applications.controller.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/rental-applications.service.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/dto/create-rental-application.dto.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/dto/update-rental-application.dto.ts`
- Create: `pms-master/tenant_portal_backend/src/rental-applications/dto/review-rental-application.dto.ts`
- Create: Prisma migration files
- Test: `pms-master/tenant_portal_backend/src/rental-applications/rental-applications.service.spec.ts`

- [ ] **Step 1: write failing rental application service test**

```ts
it('creates a draft rental application', async () => {
  const created = await service.create({
    propertyId: 'prop_1',
    applicant: { firstName: 'Ada', lastName: 'Lovelace' },
  }, 'tenant_1');

  expect(created.status).toBe('draft');
});
```

- [ ] **Step 2: run rental application backend tests and confirm failure**

Run: `pnpm test pms-master/tenant_portal_backend/src/rental-applications/rental-applications.service.spec.ts`
Expected: FAIL because module and schema do not exist.

- [ ] **Step 3: implement the module and schema**

Required status enum:

```ts
'draft' | 'submitted' | 'under_review' | 'info_requested' | 'approved' | 'denied' | 'withdrawn' | 'expired'
```

Required service methods:
- `create(dto, tenantId)`
- `update(id, dto, tenantId)`
- `submit(id, tenantId)`
- `getById(id, tenantId)`
- `listForUser(tenantId)`
- `review(id, dto, userId)`

Controller routes:
- `POST /rental-applications`
- `PATCH /rental-applications/:id`
- `POST /rental-applications/:id/submit`
- `GET /rental-applications/:id`
- `GET /rental-applications`
- `POST /rental-applications/:id/review`

- [ ] **Step 4: rerun rental application backend tests**

Run: `pnpm test pms-master/tenant_portal_backend/src/rental-applications/rental-applications.service.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pms-master/tenant_portal_backend/src/rental-applications prisma
git commit -m "feat: add rental application backend module"
```

### Task 13: Emit application review decisions into the admin feed

**Files:**
- Modify: `pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.ts`
- Modify: `keyring-os/apps/admin/src/features/payments/components/decision-card.tsx`
- Test: `pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts`

- [ ] **Step 1: write failing feed test for application review metadata**

```ts
it('emits application review decision with review type and related workflow', async () => {
  await service.handleApplicationScored({ applicationId: 'app_1', score: 92, urgency: 'HIGH' });
  const saved = await prisma.feedItem.findUnique({ where: { id: 'app_scored_app_1' } });
  expect(saved?.evidence).toMatchObject({ type: 'review' });
});
```

- [ ] **Step 2: run feed tests and confirm failure**

Run: `pnpm test pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts`
Expected: FAIL because `handleApplicationScored` does not enrich evidence sufficiently.

- [ ] **Step 3: enrich application-scored event payload**

Update `handleApplicationScored` create/update payloads with:

```ts
evidence: {
  applicationId,
  score,
  status: 'SCORED',
  type: 'review',
  confidenceScore: score,
  reasoning: ['Application scoring completed and ready for manager review'],
  workflow: { stage: 'screening_review', totalStages: 3, currentStageIndex: 1 },
}
```

Also change summary to:

```ts
`Rental application scored: ${score}/100`
```

- [ ] **Step 4: rerun feed tests**

Run: `pnpm test pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.ts pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts
git commit -m "feat: emit enriched application review decisions"
```

### Task 14: Add auth decision surface

**Files:**
- Create: `keyring-os/apps/tenant-portal/src/components/auth/auth-decision-surface.tsx`
- Modify: `keyring-os/apps/tenant-portal/src/app/layout.tsx`

- [ ] **Step 1: write failing auth surface test**

```tsx
it('renders password and magic link auth options', () => {
  render(<AuthDecisionSurface />);
  expect(screen.getByText('Continue with password')).toBeInTheDocument();
  expect(screen.getByText('Send magic link')).toBeInTheDocument();
});
```

- [ ] **Step 2: run auth tests and confirm failure**

Run: `pnpm test keyring-os/apps/tenant-portal/src/components/auth/auth-decision-surface.test.tsx`
Expected: FAIL because the component does not exist.

- [ ] **Step 3: implement non-blocking auth surface shell**

Build a presentational surface with three options:
- Continue with password
- Send magic link
- Use device sign-in

Mount it behind a guarded condition in layout so it can be enabled without disrupting current sessions.

- [ ] **Step 4: rerun auth tests**

Run: `pnpm test keyring-os/apps/tenant-portal/src/components/auth/auth-decision-surface.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add keyring-os/apps/tenant-portal/src/components/auth/auth-decision-surface.tsx keyring-os/apps/tenant-portal/src/app/layout.tsx
git commit -m "feat: add decision-focused auth surface"
```

### Task 15: Final verification

**Files:**
- Verify all modified and created files above

- [ ] **Step 1: run shared and frontend tests**

Run:
```bash
pnpm test keyring-os/packages/types/src/copilot.test.ts
pnpm test keyring-os/apps/admin/src/features/payments/components/decision-card.test.tsx
pnpm test keyring-os/apps/tenant-portal/src/app/apply/page.test.tsx
```
Expected: PASS

- [ ] **Step 2: run backend tests**

Run:
```bash
pnpm test pms-master/tenant_portal_backend/src/feed/feed-aggregator.service.spec.ts
pnpm test pms-master/tenant_portal_backend/src/rental-applications/rental-applications.service.spec.ts
pnpm test pms-master/tenant_portal_backend/src/analytics/analytics.controller.spec.ts
```
Expected: PASS

- [ ] **Step 3: run targeted app checks**

Run:
```bash
pnpm --dir keyring-os lint
pnpm --dir pms-master/tenant_portal_backend lint
```
Expected: PASS or only pre-existing warnings

- [ ] **Step 4: Commit verification fixes if needed**

```bash
git add -A
git commit -m "chore: finalize keyring os ui integration"
```

---

## Commit Sequence

1. `feat: extend copilot decision contracts`
2. `feat: normalize enhanced feed metadata`
3. `feat: add analytics ingestion endpoints`
4. `feat: enhance admin decision cards`
5. `feat: add admin decision context panel`
6. `feat: add ambient admin interaction layer`
7. `feat: add tenant ambient control orb`
8. `feat: improve maintenance form focus states`
9. `feat: add rental application tenant api client`
10. `feat: add rental application entry flow`
11. `feat: complete rental application workflow`
12. `feat: add rental application backend module`
13. `feat: emit enriched application review decisions`
14. `feat: add decision-focused auth surface`
15. `chore: finalize keyring os ui integration`

## Execution Recommendation

Recommended path: **Sub-agent driven** for Tasks 10 through 14, sequential in-session for Tasks 1 through 9. The earlier tasks are contract-sensitive and should be tightly reviewed. The rental application and UI shells can be parallelized after shared types and APIs stabilize.
