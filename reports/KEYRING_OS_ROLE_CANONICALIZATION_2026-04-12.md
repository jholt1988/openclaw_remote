# Keyring OS / Tenant Portal Backend Role Canonicalization

Date: 2026-04-12

## Final decision

Canonical authenticated application roles are:
- `ADMIN`
- `OWNER`
- `PROPERTY_MANAGER`
- `TENANT`

These are the only shared auth-role values that should cross the frontend/backend contract.

## Non-canonical legacy values

The following values are treated as compatibility aliases, not canonical roles:
- `admin`
- `owner`
- `property_manager`
- `pm`
- `property-manager`
- `property manager`
- `propertymanager`
- `property_managers`
- `tenant`
- `administrator`
- `leasing`
- `maintenance`
- `operator`

## Semantic decision

`leasing`, `maintenance`, and `operator` are not auth roles.
They are legacy workspace/persona labels and now normalize to `PROPERTY_MANAGER` at the backend ingress/query layer.

## Implementation consequences

### Backend
- Mock auth ingress normalizes incoming role headers to canonical Prisma `Role` values.
- Guard evaluation normalizes incoming user roles before authorization checks.
- Feed role filtering queries include compatibility aliases so legacy stored `roleAccess` values still resolve during rollout.
- Feed responses normalize outgoing `allowedRoles` and `role` fields to canonical uppercase values.

### Frontend / shared types
- Shared `UserRole` values are canonical uppercase app roles only.
- Admin mock feed fixtures now emit canonical roles only.
- Stale mock mutation intents were downgraded or remapped so fallback UI no longer advertises dead generic mutations.

## Compatibility posture

Short term:
- accept legacy aliases at backend ingress and feed-query compatibility boundaries
- emit only canonical uppercase roles on stabilized contracts

Long term:
- migrate stored legacy `roleAccess` arrays to canonical values and then remove alias-expansion logic

## Why this is the right boundary

- Prisma and backend guards already treat uppercase enum roles as the source of truth.
- Emitting lowercase/persona values in shared contracts creates drift and hidden authorization coupling.
- Treating workspace personas separately from auth roles keeps authorization, routing, and UI segmentation cleaner.
