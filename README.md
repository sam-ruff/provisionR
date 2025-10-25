# provisionR

Generate Kickstart files on the fly with automatic password management and templating.

## Features

- FastAPI-based REST API for kickstart file generation
- SQLite database for configuration and password storage
- Automatic password generation using memorable passphrases (e.g. `vastly-caring-filly-111`)
- Password persistence - machines get the same passwords on subsequent requests
- Jinja2 templating for flexible kickstart customization
- CSV export of machine credentials
- Static file serving for web frontend

## Quick Start

### Using Docker Compose (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/yourusername/provisionR.git
cd provisionR

# Build and run with Docker Compose
docker-compose up

# Access at http://localhost:8000
```

### Using Docker

```bash
# Build and run with Docker
docker build -t provisionr .
docker run -p 8000:8000 provisionr
```

### Fast Development Workflow

**Prerequisites:** Python 3.14+, [uv](https://github.com/astral-sh/uv), and [pnpm](https://pnpm.io/)

This setup allows hot-reloading for both frontend and backend:

```bash
# Terminal 1 - Run the backend
uv sync
uv run uvicorn provisionR.app:create_app --factory --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Run the frontend dev server
cd gui
pnpm install
pnpm dev
# Frontend dev server runs on http://localhost:5173
# API calls are proxied to http://localhost:8000
```

With this setup:
- Backend runs on `localhost:8000` with auto-reload on code changes
- Frontend runs on `localhost:5173` with hot module replacement
- Frontend proxies `/api` requests to the backend
- Changes to React components update instantly
- Changes to Python code trigger backend reload

### Production Build (Local)

```bash
# Install dependencies
uv sync

# Build the frontend
cd gui && pnpm install && pnpm generate && cd ..

# Run the application
uv run provisionr
# Access at http://localhost:8000
```

### Running Tests

```bash
uv run pytest
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Configuration Management

**Get Configuration:**
```bash
GET /api/v1/config
```

**Update Configuration:**
```bash
PUT /api/v1/config
Content-Type: application/json

{
  "target_os": "Rocky9",
  "generate_passwords": true,
  "values": {
    "hostname_prefix": "prod",
    "timezone": "America/New_York",
    "custom_key": "custom_value"
  }
}
```

### Kickstart Generation

```bash
GET /api/v1/ks?mac=AA:BB:CC:DD:EE:FF&uuid=machine-uuid&serial=SN12345

# With custom template
GET /api/v1/ks?mac=AA:BB:CC:DD:EE:FF&uuid=machine-uuid&serial=SN12345&template_name=rhel9

# With additional variables
GET /api/v1/ks?mac=AA:BB:CC:DD:EE:FF&uuid=machine-uuid&serial=SN12345&hostname=webserver01
```

**Parameters:**
- `mac` (required) - MAC address of the machine
- `uuid` (required) - UUID of the machine
- `serial` (required) - Serial number of the machine
- `template_name` (optional) - Template to use (default: "default")
- Any additional query parameters are passed to the template

### Export Machine Passwords

```bash
GET /api/v1/machines/export
```

Downloads a CSV file with all machine credentials.

## Configuration

### Global Configuration

Configuration is stored in the SQLite database and can be updated via the API:

- **target_os**: Target operating system (Rocky9 or Ubuntu25.04)
- **generate_passwords**: Enable/disable automatic password generation
- **values**: Custom key-value pairs available in templates

### Templates

Templates are stored in `provisionR/templates/` as `.ks.j2` files and have access to:

- Machine identifiers: `mac`, `uuid`, `serial`
- Configuration: `target_os` and custom `values`
- Passwords (if enabled): `root_password`, `user_password`, `luks_password`
- Any additional query parameters

Example template:
```jinja2
# Kickstart for {{ mac }}
timezone {{ timezone | default('UTC') }}
rootpw --iscrypted {{ root_password }}
```

## Password Generation

Passwords are generated in the format `word-word-word-123` (e.g. `vastly-caring-filly-111`). Machines are identified by their MAC address, UUID, and serial number combination. The same machine will always receive the same passwords across requests.

Password generation can be disabled through the configuration API.

## Database

The application uses SQLite (`provisionr.db`) for storing configuration and machine passwords. Tests use an in-memory database when `PROVISIONR_TEST_MODE=true` is set.

## Development

### Running in Development Mode

```bash
# Install dev dependencies
uv sync --dev

# Run with auto-reload (using uvicorn directly)
uv run uvicorn provisionR.app:create_app --factory --reload
```

### Pre-commit Hooks

The project uses pre-commit hooks with ruff for code quality:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually on all files
uv run pre-commit run --all-files

# Run hooks on staged files only
uv run pre-commit run
```

The pre-commit hook will:
- Run ruff linting with auto-fix
- Run ruff formatting
- Check code before every commit

### Code Quality

The project uses ruff for linting and formatting. Pre-commit hooks automatically check code before commits.

### Adding a New Template

Create a `.ks.j2` file in `provisionR/templates/` and use the `template_name` parameter when requesting a kickstart:

```bash
curl "http://localhost:8000/api/v1/ks?mac=AA:BB:CC&uuid=123&serial=SN1&template_name=rhel9"
```

## API Documentation

Interactive API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running the application.
