# Tenant workspace next

Primary next implementation queue:
1. [x] Fix tenant messaging create flow
   - tenant frontend now fetches property managers and starts a thread with `POST /messaging/threads`
   - the new-message UI collects a recipient explicitly instead of sending the wrong payload to `/messaging/conversations`

2. [x] Fix inspections list normalization
   - tenant frontend now normalizes `GET /inspections` whether it returns a bare array or an envelope with `data/items/inspections`

3. [ ] Add tenant contract checks for those two surfaces

4. [ ] Then choose between:
   - reducing `/tenant/feed` fallback synthesis, or
   - normalizing tenant autopay response shape

Reference report:
- `reports/KEYRING_OS_TENANT_WORKSPACE_CONTRACT_MATRIX_2026-04-13.md`
