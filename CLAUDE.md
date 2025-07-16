# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an OpenStack Model Context Protocol (MCP) server written in Python. It provides access to OpenStack resources (instances and networks) via the MCP protocol using the official Python SDK.

## Essential Commands

### Development
- `make deps` - Install dependencies from requirements.txt
- `make dev` - Install development dependencies (black, flake8, mypy, pytest)
- `make test` - Run all tests with pytest
- `make fmt` - Format code with black (required before commits)
- `make lint` - Run flake8 and mypy linting
- `make clean` - Clean up Python cache files

### Running
- `make run` - Show help for the CLI
- `python openstack_mcp_server.py --auth-url <URL> --username <USER> --password <PASS> --project <PROJECT> --region <REGION>`
- `make docker-build` - Build Docker image
- `make docker-compose-up` - Run with Docker Compose

### Testing a single test
- `pytest -v -k test_function_name`
- `pytest -v test_openstack_mcp_server.py::TestOpenStackMCPServer::test_connect`

## Architecture

The server is implemented in `openstack_mcp_server.py` with the following key components:

1. **OpenStackMCPServer class** - Handles OpenStack connections and resource retrieval
2. **MCP Server integration** - Uses mcp-server-sdk to expose resources
3. **Resource Types**:
   - Instances: `openstack://instances/{id}`
   - Networks: `openstack://networks/{id}`
4. **Authentication** - Uses openstacksdk for OpenStack API access
5. **CLI** - Uses Click framework for command-line interface

## Coding

- Folow format of PEP8

## Key Design Patterns

- Uses async handlers for MCP server endpoints
- Single connection instance reused for all resource queries
- Resources returned as JSON-formatted text content
- Environment variable support for all authentication parameters
- Error handling logs failures but continues operation

## OpenStack Credentials

Required for all operations (via CLI args or environment variables):
- `--auth-url` (or `OS_AUTH_URL`) - OpenStack Identity endpoint
- `--username` (or `OS_USERNAME`)
- `--password` (or `OS_PASSWORD`)
- `--project` (or `OS_PROJECT_NAME`)
- `--region` (or `OS_REGION_NAME`)

## Dependencies

- `mcp-server-sdk` - MCP server implementation
- `openstacksdk` - OpenStack API client
- `click` - CLI framework

## Important Notes

- The MCP server runs on stdio, not HTTP (unlike the Go version)
- Always run `make fmt` before committing code changes
- The `read_resource` method is currently a stub
- Tests use mocking to avoid requiring real OpenStack connections
- Docker container runs as non-root user for security
