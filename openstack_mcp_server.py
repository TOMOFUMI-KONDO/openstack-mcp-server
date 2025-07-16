"""OpenStack MCP Server - Core server implementation."""

import json
import logging
from typing import List

from mcp.types import Resource, TextContent
from openstack import connection

logger = logging.getLogger(__name__)


class OpenStackMCPServer:
    """MCP Server for OpenStack resources."""

    def __init__(
        self,
        auth_url: str,
        user_domain_name: str,
        username: str,
        password: str,
        project_domain_id: str,
        project_name: str,
        region: str,
    ):
        """Initialize OpenStack MCP Server with authentication credentials."""
        self.auth_url = auth_url
        self.user_domain_name = user_domain_name
        self.username = username
        self.password = password
        self.project_domain_id = project_domain_id
        self.project_name = project_name
        self.region = region
        self.conn = None

    def connect(self) -> None:
        """Establish connection to OpenStack."""
        try:
            self.conn = connection.Connection(
                region_name=self.region,
                auth={
                    "auth_url": self.auth_url,
                    "user_domain_name": self.user_domain_name,
                    "username": self.username,
                    "password": self.password,
                    "project_domain_name": self.project_domain_name,
                    "project_name": self.project_name,
                },
            )
            logger.info("Successfully connected to OpenStack")
        except Exception as e:
            logger.error(f"Failed to connect to OpenStack: {e}")
            raise

    def get_instances(self) -> List[Resource]:
        """Get all compute instances."""
        resources = []
        try:
            servers = self.conn.compute.servers()
            for server in servers:
                resource_data = {
                    "id": server.id,
                    "name": server.name,
                    "status": server.status,
                    "flavor": server.flavor.get("id") if server.flavor else None,
                    "image": server.image.get("id") if server.image else None,
                    "created": server.created_at,
                    "updated": server.updated_at,
                }

                resource = Resource(
                    uri=f"openstack://instances/{server.id}",
                    name=f"Instance: {server.name}",
                    description=f"OpenStack instance {server.name} (Status: {server.status})",
                    contents=[TextContent(type="text", text=json.dumps(resource_data, indent=2))],
                )
                resources.append(resource)
        except Exception as e:
            logger.error(f"Failed to get instances: {e}")

        return resources

    def get_networks(self) -> List[Resource]:
        """Get all networks."""
        resources = []
        try:
            networks = self.conn.network.networks()
            for network in networks:
                resource_data = {
                    "id": network.id,
                    "name": network.name,
                    "status": network.status,
                    "admin_state_up": network.is_admin_state_up,
                    "shared": network.is_shared,
                    "tenant_id": network.tenant_id,
                }

                resource = Resource(
                    uri=f"openstack://networks/{network.id}",
                    name=f"Network: {network.name}",
                    description=f"OpenStack network {network.name}",
                    contents=[TextContent(type="text", text=json.dumps(resource_data, indent=2))],
                )
                resources.append(resource)
        except Exception as e:
            logger.error(f"Failed to get networks: {e}")

        return resources
