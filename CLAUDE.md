# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Microsoft SQL Server MCP (Model Context Protocol) server that enables secure interaction with SQL Server databases. It's a Python package that provides tools for listing tables and executing SQL queries through Claude Desktop.

## Key Commands

### Development Setup
```bash
# Create virtual environment and install dependencies
make install-dev

# Run the server locally
make run
# or
python -m mssql_mcp_server
```

### Testing
```bash
# Run all tests
make test

# Run specific test files
venv/bin/pytest tests/test_server.py -v

# Test database connection
make test-connection
```

### Code Quality
```bash
# Check code formatting and types
make lint

# Auto-format code
make format
```

### Docker Development
```bash
# Build and start Docker environment
make docker-build
make docker-up

# Run tests in Docker
make docker-test

# Access Docker container
make docker-exec
```

## Architecture

The codebase follows a simple MCP server architecture:

1. **Entry Points**: 
   - `src/mssql_mcp_server/__main__.py` - Module entry point
   - `src/mssql_mcp_server/__init__.py` - Package initialization with `main()` function

2. **Core Server**: 
   - `src/mssql_mcp_server/server.py` - Main server implementation containing:
     - Database configuration from environment variables
     - Connection handling for SQL Server, Windows Auth, and Azure SQL
     - SQL query execution with security validations
     - MCP protocol implementation for tools and resources

3. **Configuration**: 
   - Supports multiple authentication methods (SQL, Windows, Azure AD)
   - Environment variables: `MSSQL_SERVER`, `MSSQL_DATABASE`, `MSSQL_USER`, `MSSQL_PASSWORD`
   - Optional: `MSSQL_PORT`, `MSSQL_ENCRYPT`, `MSSQL_WINDOWS_AUTH`

4. **Testing Structure**:
   - Unit tests for server functionality
   - Integration tests for database operations
   - Security and performance test suites
   - Configuration via `pytest.ini` with async support

## Key Technical Details

- Uses `pymssql` for SQL Server connectivity
- Implements MCP protocol for tool-based database interaction
- Supports LocalDB connections with special formatting
- Automatic encryption for Azure SQL connections
- SQL injection prevention through table name validation
- Async implementation using asyncio

## Smithery Deployment

The server includes HTTP wrapper for deployment on Smithery:

### HTTP Server
- `src/mssql_mcp_server/http_server.py` - Streamable HTTP implementation
- Listens on `/mcp` endpoint (GET, POST, DELETE)
- Handles configuration via query parameters with dot notation
- Maps query params to environment variables for the MCP server

### Deployment Files
- `smithery.yaml` - Defines container runtime and configuration schema
- Modified `Dockerfile` to run HTTP server instead of stdio server

### Testing HTTP Mode
```bash
# Run HTTP server locally
python -m mssql_mcp_server.http_server

# Test endpoints
python test_http_server.py
```