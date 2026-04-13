# Proactivity Patterns

This file captures successful work patterns and strategies for future reuse.

## Tenant Workspace Contract Stabilization Pattern

### Phase 1: Analysis and Matrix Creation
- Create execution-ready contract matrix identifying frontend functions, expected routes, backend owners, and current mismatches
- Focus on concrete, provable broken/misaligned contracts rather than abstract cleanup

### Phase 2: Implementation Queue Prioritization
- Prioritize P0 fixes for hard contract mismatches
- Group related fixes into implementation passes
- Stop implementation before opening next workspace lane

### Phase 3: Targeted Implementation
- Fix one concrete mismatch at a time
- Use tsc --noEmit after each cluster to identify the true next frontier
- Add explicit contract checks in backend tests for implemented surfaces

### Phase 4: Validation
- Run targeted validations for affected surfaces:
  - `corepack pnpm exec tsc --noEmit` in relevant packages/apps
  - Backend Jest specs for controller/service contracts
  - Add e2e specs for later execution when DB is available
- Distinguish "implemented" from "validated and clean"

### Phase 5: Commit and Push
- Commit only targeted files related to the specific fixes
- Push changes to respective repositories
- Update outer repo with new submodule pointers

### Phase 6: Documentation and Anchor Update
- Update todo anchors to mark implementation items complete
- Create or refresh anchor files at natural barriers:
  - finishing a related cluster of fixes
  - completing a matrix, report, or implementation pass
  - changing from analysis to implementation
  - changing from implementation to validation/cleanup

## Admin Workspace API Alignment Pattern

### Phase 1: Wrapper Creation
- Add only wrappers backed by real NestJS controllers in pms-master/tenant_portal_backend
- Rerun TypeScript to surface the next lane after each cluster

### Phase 2: Typecheck Cluster Clearing
- Clear missing-export/typecheck clusters in priority order:
  - billing, reports, leasing
  - rent-optimization, move-orchestration, owner-portal
  - financials, lease-abstraction, chatbot

### Phase 3: Contract Normalization
- Identify and capture important contract notes during the run:
  - Route expectations and payload shapes
  - Response DTO alignments
  - Stale assumptions in frontend code

### Phase 4: Validation Discipline
- Use tsc --noEmit after each cluster to identify the true next frontier
- Avoid inventing endpoints - verify controller route names first
- Inspect exact admin page imports before editing copilot-api.ts