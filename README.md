# VersaTrak API Client (vt.py)

A modern Python client for the [VersaTrak](https://versatrak.com/) v6 API, designed for simplicity, reliability, and ease of use.

## Features

- **Robust Authentication**: Handles JWT tokens and automatic refresh.
- **Modern Python**: Built for Python 3.10 through 3.13.
- **Reliability**: Built-in retry strategies for transient network errors.
- **Comprehensive API Support**:
  - User session management (Login, Logoff, Refresh).
  - Data retrieval for Monitored Objects, Locations, Departments, and Policies.
  - Historical data extraction with timestamp adjustment.
- **Developer Friendly**:
  - Managed with `uv`.
  - Comprehensive `pytest` suite.
  - Automated linting and formatting with `prek` (ruff).

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone https://github.com/UMN-ARDL-Biorepository/vt.py.git
cd vt.py

# Create a virtual environment and install dependencies
uv sync
```

## Quick Start

### Basic Usage

```python
from api import VersaTrak
import os

# Initialize the client
# It automatically pulls credentials from environment variables if available
vt = VersaTrak(
    base_url="https://your-instance.versatrak.com/vtwebapi2/api/",
    username="your_username",
    password="your_password"
)

# Fetch current status of monitored objects
status = vt.currentstatus()
print(status)

# Fetch historical data for a specific object
history = vt.gethistorydata(object_id="123", period="1d")
print(history)

# Log off when finished
vt.logoff()
```

## Configuration

The client can be configured via environment variables, constructor arguments, or a `.env` file.

### Environment Configuration

For local development, it is recommended to use a `.env` file. A template is provided in `example.env`.

1. Copy the example file:
   ```bash
   cp example.env .env
   ```
2. Edit `.env` and fill in your VersaTrak credentials:
   ```env
   API_URL=https://your-instance.versatrak.com/vtwebapi2/api/
   USERNAME=your_username
   PASSWORD=your_password
   # INSTANCE_ID is optional; the client will use the first available if omitted
   INSTANCE_ID=your_instance_id
   ```

### Variables reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `API_URL` | The base URL for the VersaTrak API | - |
| `USERNAME` | Your VersaTrak username | - |
| `PASSWORD` | Your VersaTrak password | - |
| `INSTANCE_ID` | Specific instance ID (optional) | First available |

## Development

### Running Tests

We use `pytest` for testing. Ensure your `.env` file is configured with valid test credentials.

```bash
uv run pytest
```

### Pre-commit Hooks

This project uses `prek` to manage hooks.

```bash
# Install hooks
uv run prek install

# Run checks on all files
uv run prek run --all-files
```

## License

Distributed under the MIT License. See `LICENSE` for more information.
