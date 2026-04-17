# Production Readiness — High Priority Tasks

Generated: 2026-04-17

## High Priority Items

### 1. Remove Duplicate Modules ✅ COMPLETED
- [x] **1.1** Delete `pms-master/tenant_portal_backend/src/inspection/` (unregistered duplicate)
- [x] **1.2** Delete unused `pms-master/tenant_portal_backend/src/quickbooks/quickbooks.controller.ts`
- [x] **1.3** Verify no conflicts after removal

### 2. Consolidate Route Prefixes ⏳ IN PROGRESS
- [ ] **2.1** Investigate `/leasing/*` vs `/api/leasing/*` route duplication
- [ ] **2.2** Normalize routes to single pattern
- [ ] **2.3** Update any client references

### 2. Consolidate Route Prefixes
- [ ] **2.1** Investigate `/leasing/*` vs `/api/leasing/*` route duplication
- [ ] **2.2** Normalize routes to single pattern
- [ ] **2.3** Update any client references

### 3. Add Circuit Breaker ⏳ IN PROGRESS
- [x] **3.1** Create circuit breaker service for external APIs
- [ ] **3.2** Integrate with Stripe webhook handler
- [ ] **3.3** Integrate with DocuSign webhook handler
- [ ] **3.4** Integrate with QuickBooks service
- [ ] **3.5** Add fallback behavior for each integration

### 4. Comprehensive E2E Tests
- [ ] **4.1** Audit current test coverage ( Jest + Supertest)
- [ ] **4.2** Create E2E test suite for critical paths:
  - [ ] Lease creation flow
  - [ ] Payment processing (Stripe)
  - [ ] Maintenance request → assignment
  - [ ] Move orchestration flow
- [ ] **4.3** Add workflow E2E tests
- [ ] **4.4** Add API integration tests for all 66 controllers

### 5. Feature Flags System
- [ ] **5.1** Create feature flag config module
- [ ] **5.2** Implement flag evaluation in frontend
- [ ] **5.3** Add flags for:
  - New lease abstraction
  - AI triage routing
  - Rent optimization ML
  - Chatbot beta
- [ ] **5.4** Add admin UI for flag management

---

## Manifesto Drift Remediation

### 6. Dashboard-to-Briefing Migration ⏳ IN PROGRESS
- [x] **6.1** Replace `/page.tsx` landing with Briefing view (design review complete)
- [ ] **6.2** Make Briefing the default authenticated route
- [ ] **6.3** Remove dashboard-style widgets from landing
- [ ] **6.4** Add quick-action buttons directly on briefing

### 7. Reduce Navigation-Heavy Design
- [ ] **7.1** Audit all 45+ admin routes for necessity
- [ ] **7.2** Consolidate related pages under single workflows
- [ ] **7.3** Implement intent-bar as primary navigation (instead of sidebar)
- [ ] **7.4** Reduce sidebar items by 50%

### 8. Action-First Design Adoption
- [ ] **8.1** Audit forms for multi-step reduction
- [ ] **8.2** Implement inline actions in feed cards
- [ ] **8.3** Replace "view details" with "execute action" patterns
- [ ] **8.4** Add keyboard shortcuts for common actions

### 9. "Show Less, Mean More" Enforcement
- [ ] **9.1** Audit all components against manifesto rule
- [ ] **9.2** Remove data tables from primary views
- [ ] **9.3** Replace with decision-focused cards
- [ ] **9.4** Add empty states that drive action

---

## Notes

- Items prioritized by production risk and manifesto alignment
- Each checkbox = ~2-4 hour task for experienced dev
- Manifesto items (6-9) require design review before implementation