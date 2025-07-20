#!/usr/bin/env python3
"""OpenStack MCP Server - Main entry point."""

import logging
import sys

import click
import server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--auth-url", required=True, envvar="OS_AUTH_URL", help="OpenStack Auth URL")
@click.option("--user-domain-name", required=True, envvar="OS_USER_DOMAIN_NAME", help="OpenStack User Domain Name")
@click.option("--username", required=True, envvar="OS_USERNAME", help="OpenStack Username")
@click.option("--password", required=True, envvar="OS_PASSWORD", help="OpenStack Password")
@click.option("--project-domain-id", required=True, envvar="OS_PROJECT_DOMAIN_ID", help="OpenStack Project Domain ID")
@click.option("--project-name", required=True, envvar="OS_PROJECT_NAME", help="OpenStack Project Name")
@click.option("--region", required=True, envvar="OS_REGION_NAME", help="OpenStack Region")
def main(
    auth_url: str,
    user_domain_name: str,
    username: str,
    password: str,
    project_domain_id: str,
    project_name: str,
    region: str,
):
    """
    OpenStack MCP Server

    Model Context Protocol server for OpenStack cluster information.
    """
    try:
        s = server.OpenStackMCPServer(
            auth_url=auth_url,
            user_domain_name=user_domain_name,
            username=username,
            password=password,
            project_domain_id=project_domain_id,
            project_name=project_name,
            region=region,
        )
    except Exception as e:
        logger.error(f"Failed to initialize OpenStack connection: {e}")
        sys.exit(1)

    # Run the MCP server
    logger.info("Starting OpenStack MCP Server...")
    s.run()


if __name__ == "__main__":
    main()
