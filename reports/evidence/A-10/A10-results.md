# A-10 Owner Portal Minimum — Verification Results (2026-04-05)

## Request Context
- Owner user: `jordan_owner` (org role: OWNER in Sunset Property Management)
- Created request title: `A10 Owner Request 1775366598424`
- Request ID: `68fae30a-3c20-4db7-bb78-fd4a49ad534b`

## Checks
1. **Create request without propertyId**
   - Result: **Blocked (expected)**
   - HTTP 400
   - Message: `propertyId is required for owners when creating a maintenance request`

2. **Create request with propertyId**
   - Result: **Allowed (expected)**
   - HTTP 201

3. **Add note/comment to request**
   - Result: **Allowed (expected)**
   - HTTP 201

4. **Attempt status change**
   - Result: **Blocked (expected)**
   - HTTP 403
   - Message: `Owners are read-only for maintenance status changes`

5. **Attempt technician assignment**
   - Result: **Blocked (expected)**
   - HTTP 403
   - Message: `Owners are read-only for technician assignment`

6. **Manual UI read path**
   - Result: **Verified**
   - Owner account can view maintenance list and request detail for created ticket.

## Evidence Files
- `a10-owner-portal-verification-recording.webm`
- `a10-01-owner-maintenance-list.png`
- `a10-02-owner-request-detail.png`
