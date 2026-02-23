# VersaTrak API Client - AI Coding Agent Hints

## Core Architecture
- **Uplink Consumer**: This client uses the `uplink` library to define API endpoints declaratively.
- **Async/Sync Dual Support**: Every API method has both an async version (prefixed with `a`, e.g., `alogin`) and a sync version (e.g., `login`).
- **Sync Wrapper**: Sync methods use `_run_sync` to wrap the async implementations. This allows the client to be used in synchronous scripts while still benefiting from the `aiohttp` backend.
- **Aiohttp backend**: The client is initialized with `AiohttpClient()`.

## Best Practices for Modifications
- **Adding new endpoints**:
  1. Add a decorated async method with `_raw` suffix (e.g., `@get("path") async def _anew_endpoint_raw(self): pass`).
  2. Add a public async method (e.g., `async def anew_endpoint(self): ...`).
  3. Add a public sync method that calls `_run_sync(self.anew_endpoint())`.
- **Authentication**:
  - Always check `self.is_logged_on` before requests that require auth.
  - Auth tokens are managed in `self.token` and `self.refresh_token`.
  - The `Authorization` header is updated automatically in the `login` and `refresh` methods.

## Environment Variables
- `API_URL`: Base URL for the API.
- `USERNAME`, `PASSWORD`: Credentials.
- `INSTANCE_ID`: VersaTrak instance identifier.

## Testing
- Use `pytest`.
- Async tests should use `@pytest.mark.asyncio`.
- Most tests require a valid `.env` file with real credentials as they hit the live API (or a dev instance).

## Tooling
- **uv**: Always use `uv` for dependency management (`uv add`, `uv sync`, etc.).
- **prek**: Use `uv run prek run --all-files` for linting/formatting before submitting.
