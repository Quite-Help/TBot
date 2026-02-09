# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

TBot is a Telegram bot service that facilitates anonymous, privacy-preserving conversations between users and counselors. Users receive aliases (nicknames) instead of exposing their real Telegram identities. The bot creates separate Telegram groups for each user-counselor pair and relays messages between them.

## Development Commands

### Run the server
```bash
uvicorn app.main:app --reload
```

### Run tests
```bash
# All tests
pytest

# Single test file
pytest tests/test_handlers_callbacks.py

# Single test function
pytest tests/test_handlers_callbacks.py::test_select_callback

# With coverage
pytest --cov=app
```

### Linting
```bash
# Check linting issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

### Environment Setup
Copy `.env.example` to `.env` and fill in the required values. Required environment variables:
- `TELEGRAM_BOT_TOKEN`, `BOT_USERNAME`, `API_KEY`, `API_HASH` - Telegram credentials
- `WEBHOOK_SECRET`, `PUBLIC_WEBHOOK_BASE` - Webhook configuration
- `CORE_API_BASE`, `CORE_API_SVC_ACCOUNT_USERNAME`, `CORE_API_SVC_ACCOUNT_PASSWORD` - Core API service account
- `HASH_KEY` - Key for hashing user IDs

## Architecture

### Core Flow
1. User starts bot → receives alias, shown counselor list
2. User selects counselor → Telethon creates two supergroups (one for user, one for counselor) with the bot as admin
3. Messages sent to either group are relayed to the other via the `relay_handler`

### Key Components

**`app/main.py`** - FastAPI entrypoint with lifespan management that initializes both the python-telegram-bot Application and Telethon client.

**`app/telegram/`** - Telegram integration layer:
- `app.py` - python-telegram-bot Application instance and webhook setup
- `client.py` - Telethon TelegramClient for advanced operations (group creation, migrations)
- `handlers/start.py` - `/start` command, creates/fetches user alias
- `handlers/callbacks.py` - Inline button callbacks for counselor selection and session creation
- `handlers/relay.py` - Relays messages between user and counselor groups

**`app/services/`** - External service integrations:
- `core/` - Core API client for aliases, counselors, and group records. Uses `auth.py` for bearer token authentication with automatic refresh.
- `taccount/api.py` - Telethon-based Telegram account operations: creates groups, migrates to supergroups, promotes bot to admin, removes service account from groups

### Privacy Design
User Telegram IDs are never stored directly. They're hashed via HMAC-SHA256 (`app/util/hash.py`) using `HASH_KEY` before being sent to the Core API.

### Two Telegram Libraries
The project uses both:
- **python-telegram-bot**: For receiving updates via webhook and sending messages as the bot
- **Telethon**: For account-level operations that require a user session (creating groups, managing permissions)
