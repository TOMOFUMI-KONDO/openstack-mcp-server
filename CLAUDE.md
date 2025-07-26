# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an OpenStack Model Context Protocol (MCP) server written in Python. It provides access to OpenStack resources (instances and networks) via the MCP protocol using the official Python SDK.

## Essential Commands

- `make deps` - Install dependencies from requirements.txt
- `make fmt` - Format code using Black and isort
- `make run` - Run the server with default parameters
- `make test` - Run all tests with pytest

## Architecture

The server is implemented in `openstack_mcp_server.py` with the following key components:

1. **OpenStackMCPServer class** - Handles OpenStack connections and resource retrieval
1. **Resource Types**:
   - Instance:
   - list: `openstack://servers`
   - get: `openstack://servers/{server_id}`
1. **Authentication** - Uses openstacksdk for OpenStack API access
1. **CLI** - Uses Click framework for command-line interface

## Coding

- Folow format of PEP8
- Do formatting with `make fmt` after editing code
- Do test with `make test` after editing test code

## Key Design Patterns

- Uses FastMCP of <https://github.com/modelcontextprotocol/python-sdk> to handle MCP requests
- Resources returned as JSON-formatted text content
- Environment variable support for all authentication parameters
- Error handling logs failures but continues operation

## OpenStack Credentials

Required for all operations (via CLI args or environment variables):

- `--auth-url` (or `OS_AUTH_URL`) - OpenStack Identity endpoint
- `--user-domain-name` (or `OS_USER_DOMAIN_NAME`) - OpenStack User Domain Name
- `--username` (or `OS_USERNAME`) - OpenStack Username
- `--password` (or `OS_PASSWORD`) - OpenStack Password
- `--project-domain-id` (or `OS_PROJECT_DOMAIN_ID`) - OpenStack Project Domain ID
- `--project-name` (or `OS_PROJECT_NAME`) - OpenStack Project Name
- `--region` (or `OS_REGION_NAME`) - OpenStack Region

## Dependencies

- `mcp-server-sdk` - MCP server implementation
- `openstacksdk` - OpenStack API client
- `click` - CLI framework

## Important Notes

- Always run `make fmt` after editing code to ensure consistent formatting
- Always run `make test` after editing test code to ensure all tests pass
- Tests use mocking to avoid requiring real OpenStack connections
- Docker container runs as non-root user for security
