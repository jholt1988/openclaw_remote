# Keyring OS Next Readiness Slice 实现计划

**目标：** Reduce remaining admin lint warning noise in safe batches and add contract-critical backend coverage for lease document/signing/vacancy workflows.

**架构：** Split into two independent workstreams: frontend hygiene in `keyring-os/apps/admin`, backend coverage in `pms-master/tenant_portal_backend`. Each workstream must preserve existing behavior, run the smallest meaningful validation gate, then report exact files changed and remaining blockers.

**技术栈：** Next.js/React/TypeScript/ESLint for admin; NestJS/Prisma/Jest for backend.

---

## Workstream A: Admin warning reduction

**Scope:** Behavior-safe warning cleanup only. Do not fake-type broad legacy API payload surfaces in `src/lib/copilot-api.ts` unless a specific local type can be inferred safely.

**Files likely modified:**
- `keyring-os/apps/admin/src/**/*.tsx`
- `keyring-os/apps/admin/src/**/*.ts`

### Task A1: Baseline warning inventory
- Run:
  ```bash
  corepack pnpm exec eslint . -f json > /tmp/keyring-admin-eslint.json || true
  python3 - <<'PY'
  import json
  data=json.load(open('/tmp/keyring-admin-eslint.json'))
  by_rule={}
  by_file={}
  for r in data:
      for m in r['messages']:
          if m['severity'] == 1:
              by_rule[m.get('ruleId') or 'unknown']=by_rule.get(m.get('ruleId') or 'unknown',0)+1
              by_file[r['filePath']]=by_file.get(r['filePath'],0)+1
  print('rules')
  for k,v in sorted(by_rule.items(), key=lambda x:-x[1])[:20]: print(v,k)
  print('files')
  for k,v in sorted(by_file.items(), key=lambda x:-x[1])[:30]: print(v,k)
  PY
  ```
- Expected: 0 errors; warning inventory printed.

### Task A2: Remove unused imports/vars in high-count files
- Modify only unused imports/vars where removal is obviously behavior-neutral.
- Prefer ESLint autofix if safe:
  ```bash
  corepack pnpm exec eslint . --fix
  ```
- Then manually inspect `git diff` for accidental formatting churn.

### Task A3: Re-run admin lint
- Run:
  ```bash
  corepack pnpm exec eslint .
  ```
- Expected: 0 errors; warning count lower than 378.
- Report exact before/after warning count.

## Workstream B: Lease document/signing/vacancy backend coverage

**Scope:** Add tests around existing service/controller behavior; do not invent missing production methods. If methods are stubs, verify current stub contract explicitly.

**Files likely modified:**
- `pms-master/tenant_portal_backend/src/lease/lease.service.spec.ts`
- Possibly additional focused spec files if existing tests are better homes.

### Task B1: Inspect lease document/signing/vacancy methods
- Read `src/lease/lease.service.ts` methods:
  - `generateLeaseDocument`
  - `sendForSignature`
  - vacancy/move-out preparation methods if present
- Identify existing collaborators and Prisma calls.

### Task B2: Add failing tests for current contract
- Add Jest tests that assert:
  - unauthorized org/user access is blocked before writes
  - successful document generation records expected state/history/audit side effects if implemented
  - send-for-signature validates lease/org and records signature state/audit if implemented
  - vacancy/move-out prep behavior is covered where existing methods support it
- Use current project mocking patterns already in `lease.service.spec.ts`.

### Task B3: Minimal implementation only if tests expose real missing behavior
- If tests fail because a method exists but has broken behavior, fix the smallest production code path.
- If a method does not exist, do not create feature scope unless it is directly referenced by existing controller/service contract.

### Task B4: Run targeted backend tests
- Run:
  ```bash
  corepack pnpm exec jest src/lease/lease.service.spec.ts src/lease/ai-lease-renewal.service.spec.ts src/lease/ai-lease-renewal-metrics.service.spec.ts --runInBand
  ```
- Expected: PASS.

## Integration gate

### Task C1: Review subagent diffs
- In each repo:
  ```bash
  git diff --stat
  git diff --check
  ```

### Task C2: Run final validation gates
- Admin:
  ```bash
  corepack pnpm exec eslint .
  ```
- Backend:
  ```bash
  corepack pnpm exec tsc --noEmit --pretty false
  corepack pnpm exec jest src/lease/lease.service.spec.ts src/lease/ai-lease-renewal.service.spec.ts src/lease/ai-lease-renewal-metrics.service.spec.ts --runInBand
  ```

### Task C3: Commit/push
- Commit separate repos:
  ```bash
  git add <changed files>
  git commit -m "Reduce admin lint warnings"
  git push
  git add <changed files>
  git commit -m "Cover lease document workflows"
  git push
  ```
- Update workspace tracking files and commit root pointer updates.

## Self-review checks
- No broad fake typing of legacy `any` surfaces.
- No claims of clean status without tool output.
- Preserve distinction between 0 errors and warning count.
- If confidence drops to mid-70s or lower, stop and report blocker.
