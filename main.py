#!/usr/bin/env python3
"""OpenStack MCP Server - Main entry point."""

import logging
import sys

import click
from mcp.server.fastmcp import FastMCP
from openstack_mcp_server import OpenStackMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global OpenStack server instance
os_server = None

# Create MCP server
mcp = FastMCP("openstack-mcp-server")


@mcp.resource("openstack://instances")
async def list_instances():
    """List all OpenStack compute instances."""
    if not os_server:
        return "OpenStack server not initialized"

    instances = os_server.get_instances()
    logger.info(f"Listed {len(instances)} instances")
    return instances


@mcp.resource("openstack://networks")
async def list_networks():
    """List all OpenStack networks."""
    if not os_server:
        return "OpenStack server not initialized"

    networks = os_server.get_networks()
    logger.info(f"Listed {len(networks)} networks")
    return networks


@mcp.tool()
async def get_instance_details(instance_id: str) -> str:
    """Get detailed information about a specific OpenStack instance."""
    if not os_server:
        return "OpenStack server not initialized"

    # This would fetch detailed instance information
    return f"Detailed information for instance {instance_id} not yet implemented"


@mcp.tool()
async def get_network_details(network_id: str) -> str:
    """Get detailed information about a specific OpenStack network."""
    if not os_server:
        return "OpenStack server not initialized"

    # This would fetch detailed network information
    return f"Detailed information for network {network_id} not yet implemented"


@click.command()
@click.option("--auth-url", required=True, envvar="OS_AUTH_URL", help="OpenStack Auth URL")
@click.option("--user-domain-name", required=True, envvar="OS_USER_DOMAIN_NAME", help="OpenStack User Domain Name")
@click.option("--username", required=True, envvar="OS_USERNAME", help="OpenStack Username")
@click.option("--password", required=True, envvar="OS_PASSWORD", help="OpenStack Password")
@click.option("--project-domain-id", required=True, envvar="OS_PROJECT_DOMAIN_ID", help="OpenStack Project Domain ID")
@click.option("--project", required=True, envvar="OS_PROJECT_NAME", help="OpenStack Project Name")
@click.option("--region", required=True, envvar="OS_REGION_NAME", help="OpenStack Region")
def main(auth_url: str, username: str, password: str, project: str, region: str):
    """OpenStack MCP Server - Model Context Protocol server for OpenStack cluster information."""
    global os_server

    # Create OpenStack server instance
    os_server = OpenStackMCPServer(
        auth_url=auth_url,
        username=username,
        password=password,
        project_name=project,
        region=region,
    )

    # Connect to OpenStack
    try:
        os_server.connect()
    except Exception as e:
        logger.error(f"Failed to initialize OpenStack connection: {e}")
        sys.exit(1)

    # Run the server
    logger.info("Starting OpenStack MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
