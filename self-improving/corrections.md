# Self-Improving Corrections Log

This file tracks specific corrections given by the user to improve behavior.

## 2026-04-13

### Correction 1: Validation Reporting
- **Issue**: Earlier report claimed clean validation before two compile/type issues were actually fixed
- **Correction**: Future summaries must distinguish "implemented" from "validated and clean"
- **Status**: Applied and logged

### Correction 2: Temporary Credential Handling
- **Issue**: Operational note mentioned temporary `~/.netrc` auth was recreated as needed for pushes
- **Correction**: Temporary credential material should be cleared after use, and prior PATs should be rotated/revoked
- **Status**: Acknowledged and will enforce cleanup discipline going forward