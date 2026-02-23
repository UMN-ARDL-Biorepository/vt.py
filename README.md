# VersaTrak API Client (vt.py)

A modern, declarative Python client for the [VersaTrak](https://versatrak.com/) v6 API. Built with [Uplink](https://uplink.readthedocs.io/) and [aiohttp](https://docs.aiohttp.org/).

## Features

- **Dual API Support**: Use the client in either synchronous or asynchronous environments.
- **Declarative Design**: Clean and extensible implementation using `uplink`.
- **Modern Async Backend**: Powered by `aiohttp` for high-performance requests.
- **Robust Authentication**: Automatic session management, JWT handling, and token refresh.
- **Developer Friendly**: Managed with `uv`, includes comprehensive `pytest` suites, and supports Python 3.10 through 3.13.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone https://github.com/UMN-ARDL-Biorepository/vt.py.git
cd vt.py

# Install dependencies and create virtual environment
uv sync
```

## Quick Start

### Synchronous Usage
For classic scripts and notebooks.

```python
from vt.api import VersaTrak

# Initialize (reads credentials from environment variables by default)
vt = VersaTrak()

# Fetch data
status = vt.currentstatus()
print(status)

# Always remember to log off
vt.logoff()
```

### Asynchronous Usage
For modern async applications (FastAPI, etc.).

```python
import asyncio
from vt.api import VersaTrak

async def main():
    vt = VersaTrak()

    # Use the 'a' prefixed methods for async
    status = await vt.acurrentstatus()
    print(status)

    await vt.alogoff()

asyncio.run(main())
```

## Configuration

The client supports configuration through environment variables or a `.env` file.

| Variable | Description |
| :--- | :--- |
| `API_URL` | The base URL for the VersaTrak API |
| `USERNAME` | Your VersaTrak username |
| `PASSWORD` | Your VersaTrak password |
| `INSTANCE_ID` | Optional: Specific VersaTrak instance ID |

### Local Development
Copy `example.env` to `.env` and fill in your details:
```bash
cp example.env .env
```

## Development

### Running Tests
We maintain both sync and async test suites.

```bash
# Run all tests
uv run pytest

# Run only async tests
uv run pytest tests/test_async_client.py
```

### Formatting and Linting
We use `ruff` via `prek`.

```bash
uv run prek run --all-files
```

## License

MIT License. See `LICENSE` for details.
