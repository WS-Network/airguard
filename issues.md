# Issues Log

## Format
- **Issue**: Brief description of the issue.
- **Status**: Resolved / Not Resolved
- **Attempts**: Steps tried to resolve the issue.

---

## Logged Issues

1. **Issue**: Missing Docker setup files.
   - **Status**: Resolved
   - **Attempts**: Created `docker-compose.yml` and Dockerfiles for `api` and `web`.
2. **Issue**: Docker Compose failed to fetch the `ai-core` image.
   - **Status**: Not Resolved
   - **Attempts**:
     1. Removed the obsolete `version` attribute from `docker-compose.yml`.
     2. Verified Docker Desktop is running and configured for WSL2.