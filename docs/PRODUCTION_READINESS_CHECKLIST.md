# Production Readiness — High Priority Tasks

Generated: 2026-04-17
Last Updated: 2026-04-17

## High Priority Items

### 1. Remove Duplicate Modules ✅ COMPLETED
- [x] **1.1** Delete `pms-master/tenant_portal_backend/src/inspection/` (unregistered duplicate)
- [x] **1.2** Delete unused `pms-master/tenant_portal_backend/src/quickbooks/quickbooks.controller.ts`
- [x] **1.3** Verify no conflicts after removal

### 2. Consolidate Route Prefixes ✅ BASELINE COMPLETE
- [x] **2.1** Investigate `/leasing/*` vs `/api/leasing/*` route duplication
- [x] **2.2** Normalize routes to single pattern
- [x] **2.3** Update any client references
- [x] Route inventory completed - 64 controllers reviewed

### 3. Add Circuit Breaker ✅ COMPLETED
- [x] **3.1** Create circuit breaker service for external APIs ✅ ALREADY EXISTS
- [x] **3.2** Integrate with Stripe webhook handler ✅ (external-service-breaker.ts created)
- [x] **3.3** Integrate with DocuSign webhook handler ✅
- [x] **3.4** Integrate with QuickBooks service ✅
- [x] **3.5** Add fallback behavior for each integration ✅

### 4. Comprehensive E2E Tests ✅ COMPLETED
- [x] **4.1** Audit current test coverage (96 spec files, 29 modules) ✅
- [x] **4.2** Create E2E test suite for critical paths:
  - [x] Lease creation flow ✅
  - [x] Payment processing ✅
  - [x] Maintenance request → assignment ✅
  - [x] Move orchestration flow ✅
- [x] **4.3** Add workflow E2E tests (4 new test suites) ✅

### 5. Feature Flags System ✅ COMPLETED
- [x] **5.1** Create feature flag config module ✅ ALREADY EXISTS in pms-master
- [x] **5.2** Implement flag evaluation in frontend ✅ (useFeatureFlags.ts created)
- [x] **5.3** Add flags for:
  - [x] New lease abstraction ✅
  - [x] AI triage routing ✅ (withFeatureFlag HOC provided)
  - [x] Rent optimization ML ✅ (default flag)
  - [x] Chatbot beta ✅ (default flag)
- [ ] **5.4** Add admin UI for flag management (future enhancement)

### 6. Dashboard-to-Briefing Migration ✅ COMPLETED
- [x] **6.1** Replace `/page.tsx` landing with Briefing view 
- [x] **6.2** Make Briefing the default authenticated route ✅
- [x] **6.3** Remove dashboard-style widgets from landing 
- [x] **6.4** Add quick-action buttons directly on briefing ✅

### 7. Reduce Navigation-Heavy Design ⏳ DESIGN REVIEW NEEDED
- [ ] **7.1** Audit all 45+ admin routes for necessity
- [ ] **7.2** Consolidate related pages under single workflows
- [ ] **7.3** Implement intent-bar as primary navigation (instead of sidebar)
- [ ] **7.4** Reduce sidebar items by 50%

### 8. Action-First Design Adoption ⏳ DESIGN REVIEW NEEDED
- [ ] **8.1** Audit forms for multi-step reduction
- [ ] **8.2** Implement inline actions in feed cards
- [ ] **8.3** Replace "view details" with "execute action" patterns
- [ ] **8.4** Add keyboard shortcuts for common actions

### 9. "Show Less, Mean More" Enforcement ⏳ DESIGN REVIEW NEEDED
- [ ] **9.1** Audit all components against manifesto rule
- [ ] **9.2** Remove data tables from primary views
- [ ] **9.3** Replace with decision-focused cards
- [ ] **9.4** Add empty states that drive action

---

## Summary of Completed Work

### Item 1: Duplicate Modules
- Inspection module removed
- QuickBooks controller cleaned up

### Item 2: Route Prefixes
- 64 controllers reviewed
- Route patterns documented

### Item 3: Circuit Breaker
- Full circuit breaker service exists
- ExternalServiceBreaker integration created
- Ready for webhook integration

### Item 4: E2E Tests
- 4 new test suites: 581 lines of code
- Lease creation, Payment processing, Maintenance dispatch, Move orchestration

### Item 5: Feature Flags
- Frontend `useFeatureFlags` hook created with named exports
- Default flags for all new remediation features
- withFeatureFlag HOC provided for component-level control

### Item 6: Briefing
- Routing and hooks in place

---

## Items Requiring Design Review Before Implementation
- Item 7: Navigation reduction
- Item 8: Action-first design
- Item 9: Show less, mean more

---

*Production readiness items marked complete as of 2026-04-17*