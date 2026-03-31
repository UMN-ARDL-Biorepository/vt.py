# Antigravity AI Agent Rules for VersaTrak API Client (vt.py)

This document provides instructions and context for AI coding agents (Antigravity, Cursor, etc.) working on the `versatrak_client` project.

## Core Architecture
- **Library**: `uplink` (declarative HTTP client)
- **Backend**: `aiohttp` (asynchronous)
- **Dependency Manager**: `uv`
- **Formatting/Linting**: `ruff` (via `prek`)

## Technical Standards
- **Sync/Async Dual Support**: Every API method MUST have both an asynchronous version and a synchronous version.
  - **Async methods**: Prefixed with `a` (e.g., `aget_users`).
  - **Sync methods**: No prefix (e.g., `get_users`).
  - **Sync Wrapper**: Sync methods MUST call their async counterpart specifically via `self._run_sync()`. This allows the client to be used in synchronous environments while leveraging the `aiohttp` backend.
- **Uplink Usage**:
  - Use decorators (`@get`, `@post`, etc.) for internal `_raw` methods.
  - Use `Body`, `Path`, `Query` annotations correctly.
- **Error Handling**: Use the `@response_handler(raise_for_status)` pattern defined in `api.py`.
- **Response Handling**: Follow the existing pattern of returning `.text()` for general data unless specific JSON parsing is required.

## Development Workflow
- **Adding new endpoints**:
  1. Add a decorated async method with `_raw` suffix (e.g., `@get("path") async def _anew_endpoint_raw(self): pass`).
  2. Add a public async method (e.g., `async def anew_endpoint(self): ...`).
  3. Add a public sync method that calls `self._run_sync(self.anew_endpoint())`.
- **Authentication**:
  - Always check `self.is_logged_on` before requests that require auth.
  - Auth tokens are managed in `self.token` and `self.refresh_token`.
  - The `Authorization` header is updated automatically in the `login` and `refresh` methods.
- **Testing**:
  - Use `pytest`.
  - Async tests should use `@pytest.mark.asyncio`.
  - Tests require a valid `.env` file with real credentials as they target a live or dev instance.

## Tooling
- **Dependency Management**: Always use `uv` (`uv add`, `uv sync`, `uv run`, etc.).
- **Linting & Formatting**: Run `uv run prek run --all-files` before submitting changes to ensure consistency with `ruff`.

## Environment Variables
- `VT_API_URL`: Base URL for the VersaTrak API.
- `VT_USERNAME`: VersaTrak username.
- `VT_PASSWORD`: VersaTrak password.
- `VT_INSTANCE_ID`: VersaTrak instance identifier.
