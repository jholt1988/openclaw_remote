# Sub-Agent Execution Plan

Generated: 2026-04-17

## Overview

This plan breaks down each high-priority task into sub-agent digestible chunks, including design review components. Each sub-agent will be assigned a focused, time-boxed task with clear deliverables.

## Master Task 1: Remove Duplicate Modules

### Sub-Agent 1.1: Inspection Module Cleanup
**Task:** Delete `pms-master/tenant_portal_backend/src/inspection/` and verify no conflicts
**Deliverable:** 
- PR removing the directory
- Verification that no controllers/routes are broken
- Update to ENDPOINT_ISSUES_FOUND.md

### Sub-Agent 1.2: QuickBooks Controller Cleanup
**Task:** Delete unused `pms-master/tenant_portal_backend/src/quickbooks/quickbooks.controller.ts`
**Deliverable:**
- PR removing the file
- Verification that quickbooks-minimal.controller.ts still works
- Update documentation

## Master Task 2: Consolidate Route Prefixes

### Sub-Agent 2.1: Route Analysis
**Task:** Investigate `/leasing/*` vs `/api/leasing/*` route duplication
**Deliverable:**
- Report identifying all duplicate routes
- Analysis of client-side usage of each route
- Recommendation for normalization

### Sub-Agent 2.2: Route Normalization Implementation
**Task:** Normalize routes to single pattern based on analysis
**Deliverable:**
- PR implementing recommended route changes
- Client-side update PRs
- Migration guide for external consumers

## Master Task 3: Add Circuit Breaker

### Sub-Agent 3.1: Circuit Breaker Service Design
**Task:** Create circuit breaker service for external APIs
**Deliverable:**
- Design document for circuit breaker pattern
- Implementation plan for NestJS
- Configuration schema

### Sub-Agent 3.2: Stripe Integration
**Task:** Integrate circuit breaker with Stripe webhook handler
**Deliverable:**
- PR adding circuit breaker to Stripe integration
- Test cases for failure scenarios
- Monitoring dashboard setup

### Sub-Agent 3.3: DocuSign Integration
**Task:** Integrate circuit breaker with DocuSign webhook handler
**Deliverable:**
- PR adding circuit breaker to DocuSign integration
- Test cases for failure scenarios
- Monitoring dashboard setup

### Sub-Agent 3.4: QuickBooks Integration
**Task:** Integrate circuit breaker with QuickBooks service
**Deliverable:**
- PR adding circuit breaker to QuickBooks integration
- Test cases for failure scenarios
- Monitoring dashboard setup

## Master Task 4: Comprehensive E2E Tests

### Sub-Agent 4.1: Test Coverage Audit
**Task:** Audit current test coverage (Jest + Supertest)
**Deliverable:**
- Test coverage report by module
- Gap analysis of critical paths
- Priority list of missing tests

### Sub-Agent 4.2: Lease Creation Flow Tests
**Task:** Create E2E test suite for lease creation flow
**Deliverable:**
- Test suite covering full lease creation
- Test data setup scripts
- CI integration

### Sub-Agent 4.3: Payment Processing Tests
**Task:** Create E2E test suite for payment processing (Stripe)
**Deliverable:**
- Test suite covering Stripe integration
- Test data setup scripts
- CI integration

### Sub-Agent 4.4: Maintenance Request Tests
**Task:** Create E2E test suite for maintenance request flow
**Deliverable:**
- Test suite covering maintenance request → assignment
- Test data setup scripts
- CI integration

### Sub-Agent 4.5: Move Orchestration Tests
**Task:** Create E2E test suite for move orchestration flow
**Deliverable:**
- Test suite covering move orchestration
- Test data setup scripts
- CI integration

### Sub-Agent 4.6: Workflow Engine Tests
**Task:** Add workflow E2E tests
**Deliverable:**
- Test suite covering workflow engine
- Test data setup scripts
- CI integration

### Sub-Agent 4.7: API Integration Tests
**Task:** Add API integration tests for all 66 controllers
**Deliverable:**
- Test suite covering all controllers
- Test data setup scripts
- CI integration

## Master Task 5: Feature Flags System

### Sub-Agent 5.1: Feature Flag Module Design
**Task:** Create feature flag config module
**Deliverable:**
- Design document for feature flag system
- Implementation plan for NestJS
- Configuration schema

### Sub-Agent 5.2: Frontend Integration
**Task:** Implement flag evaluation in frontend
**Deliverable:**
- React hook for feature flag evaluation
- UI component for flag status display
- Integration with existing components

### Sub-Agent 5.3: Flag Implementation
**Task:** Add flags for key features
**Deliverable:**
- Feature flags for:
  - New lease abstraction
  - AI triage routing
  - Rent optimization ML
  - Chatbot beta
- Configuration files
- Documentation

### Sub-Agent 5.4: Admin UI
**Task:** Add admin UI for flag management
**Deliverable:**
- Admin UI for managing feature flags
- CRUD operations for flags
- User interface design

## Master Task 6: Dashboard-to-Briefing Migration

### Sub-Agent 6.1: Design Review - Briefing Focus
**Task:** Replace `/page.tsx` landing with Briefing view
**Deliverable:**
- Design mockup of briefing-focused landing
- User flow analysis
- Accessibility considerations

### Sub-Agent 6.2: Implementation - Briefing Default
**Task:** Make Briefing the default authenticated route
**Deliverable:**
- PR changing default route
- Redirect logic implementation
- Testing for various user roles

### Sub-Agent 6.3: Implementation - Widget Removal
**Task:** Remove dashboard-style widgets from landing
**Deliverable:**
- PR removing dashboard components
- Replacement with briefing components
- Performance improvements

### Sub-Agent 6.4: Implementation - Quick Actions
**Task:** Add quick-action buttons directly on briefing
**Deliverable:**
- Quick action component implementation
- Integration with existing briefing data
- User testing feedback incorporation

## Master Task 7: Reduce Navigation-Heavy Design

### Sub-Agent 7.1: Design Review - Navigation Audit
**Task:** Audit all 45+ admin routes for necessity
**Deliverable:**
- Navigation audit report
- Categorization of routes by importance
- Recommendations for consolidation

### Sub-Agent 7.2: Implementation - Route Consolidation
**Task:** Consolidate related pages under single workflows
**Deliverable:**
- PR consolidating related pages
- Updated navigation structure
- User documentation

### Sub-Agent 7.3: Implementation - Intent Bar
**Task:** Implement intent-bar as primary navigation
**Deliverable:**
- Intent bar component implementation
- Integration with existing search/commands
- User testing feedback incorporation

### Sub-Agent 7.4: Implementation - Sidebar Reduction
**Task:** Reduce sidebar items by 50%
**Deliverable:**
- PR reducing sidebar items
- Updated information architecture
- User testing feedback incorporation

## Master Task 8: Action-First Design Adoption

### Sub-Agent 8.1: Design Review - Form Reduction
**Task:** Audit forms for multi-step reduction
**Deliverable:**
- Form audit report
- Recommendations for step reduction
- User flow optimization suggestions

### Sub-Agent 8.2: Implementation - Inline Actions
**Task:** Implement inline actions in feed cards
**Deliverable:**
- Inline action component implementation
- Integration with existing feed system
- Performance testing

### Sub-Agent 8.3: Implementation - Execute Actions
**Task:** Replace "view details" with "execute action" patterns
**Deliverable:**
- PR replacing view details patterns
- New execute action components
- User testing feedback incorporation

### Sub-Agent 8.4: Implementation - Keyboard Shortcuts
**Task:** Add keyboard shortcuts for common actions
**Deliverable:**
- Keyboard shortcut implementation
- User documentation
- Accessibility compliance

## Master Task 9: "Show Less, Mean More" Enforcement

### Sub-Agent 9.1: Design Review - Component Audit
**Task:** Audit all components against manifesto rule
**Deliverable:**
- Component audit report
- Prioritization of components to refactor
- Design principles document

### Sub-Agent 9.2: Implementation - Data Table Removal
**Task:** Remove data tables from primary views
**Deliverable:**
- PR removing data tables
- Replacement with decision-focused cards
- Performance improvements

### Sub-Agent 9.3: Implementation - Decision Cards
**Task:** Replace with decision-focused cards
**Deliverable:**
- Decision card component implementation
- Integration with existing data sources
- User testing feedback incorporation

### Sub-Agent 9.4: Implementation - Empty States
**Task:** Add empty states that drive action
**Deliverable:**
- Empty state component implementation
- Integration with all relevant views
- User testing feedback incorporation

## Execution Plan Summary

| Category | Sub-Agents | Total Tasks |
|----------|------------|-------------|
| Technical Cleanup | 4 | 7 tasks |
| Testing | 7 | 12 tasks |
| Feature Development | 4 | 10 tasks |
| Design/UX | 13 | 23 tasks |
| **Total** | **28** | **52 tasks** |

Estimated timeline: 4-6 weeks with parallel execution