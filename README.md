# VersaTrak API Client (vt.py)

A modern, declarative Python client for the [VersaTrak](https://versatrak.com/) v6 API. Built with [Uplink](https://uplink.readthedocs.io/) and [aiohttp](https://docs.aiohttp.org/).

## Features

- **Dual API Support**: Use the client in either synchronous or asynchronous environments.
- **Declarative Design**: Clean and extensible implementation using `uplink`.
- **Modern Async Backend**: Powered by `aiohttp` for high-performance requests.
- **Robust Authentication**: Automatic session management, JWT handling, and token refresh.
- **Unit Conversion**: Easily convert raw sensor readings to professional, human-readable units (e.g., % Saturation, ppm, Fahrenheit, Kelvin, Celsius).
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

### Unit Conversion
Raw values from the API often require scaling and formatting. You can use the built-in `UomConverter`:

```python
from vt.api import VersaTrak

vt = VersaTrak()
converter = vt.get_uom_converter()

# Convert a single value
# O2 raw reading 205103 -> 20.5 %
raw_val = 205103.13
uom_id = "3c4010d0-034f-48e5-bab6-5dcdb721ff93"

print(f"Human: {converter.format(raw_val, uom_id)}")
print(f"Float: {converter.convert(raw_val, uom_id)}")

# Use with Pandas
import pandas as pd
df = pd.read_parquet('sensor_history.parquet')
df['converted_val'] = converter.convert_series(df['value'], uom_id)
```

## Configuration

The client supports configuration through environment variables or a `.env` file.

| Variable | Description |
| :--- | :--- |
| `VT_API_URL` | The base URL for the VersaTrak API |
| `VT_USERNAME` | Your VersaTrak username |
| `VT_PASSWORD` | Your VersaTrak password |
| `VT_INSTANCE_ID` | Optional: Specific VersaTrak instance ID |

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

## GitHub Actions

Automated tests are executed on every push and pull request via GitHub Actions.

### Setting up Secrets
To allow the GitHub Actions workflow to run authenticated tests, you must add the following [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions) to your repository:

- `VT_API_URL`: The base URL for the VersaTrak API.
- `VT_USERNAME`: The service account username.
- `VT_PASSWORD`: The service account password.

The workflow will automatically use these secrets to populate the environment variables required by the test suite.

## License

MIT License. See `LICENSE` for details.
