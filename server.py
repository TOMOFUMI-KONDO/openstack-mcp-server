import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from openstack import connection
from pydantic import BaseModel

logger = logging.getLogger(__name__)

mcp = FastMCP("openstack-mcp-server")

conn: Optional[connection.Connection] = None


class Server(BaseModel):
    """OpenStack server model."""

    id: str
    name: str
    status: str
    flavor: Optional[str] = None
    image: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    addresses: Optional[dict] = None


class ServerList(BaseModel):
    """List of OpenStack servers."""

    servers: List[Server]


class OpenStackMCPServer:
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
        """Initialize OpenStack MCP Server."""
        self.auth_url = auth_url
        self.user_domain_name = user_domain_name
        self.username = username
        self.password = password
        self.project_domain_id = project_domain_id
        self.project_name = project_name
        self.region = region

    def connect(self) -> None:
        """Initialize OpenStack connection."""
        try:
            global conn
            conn = connection.Connection(
                region_name=self.region,
                auth={
                    "auth_url": self.auth_url,
                    "user_domain_name": self.user_domain_name,
                    "username": self.username,
                    "password": self.password,
                    "project_domain_id": self.project_domain_id,
                    "project_name": self.project_name,
                },
            )
            logger.info("Successfully connected to OpenStack")
        except Exception as e:
            logger.error(f"Failed to connect to OpenStack: {e}")
            raise

    def run(self) -> None:
        """Run the OpenStack MCP Server."""
        try:
            logger.info("Connecting to OpenStack...")
            self.connect()

            logger.info("OpenStack MCP Server is running")
            mcp.run()
        except Exception as e:
            logger.error(f"Error running OpenStack MCP Server: {e}")
            raise


@mcp.resource("openstack://servers")
def list_servers() -> ServerList:
    """Get all OpenStack compute servers."""
    if not conn:
        raise Exception("OpenStack connection not initialized")

    try:
        servers = list(conn.compute.servers())
        server_list = []

        for server in servers:
            server_obj = Server(
                id=server.id,
                name=server.name,
                status=server.status,
                flavor=server.flavor.get("id") if server.flavor else None,
                image=server.image.get("id") if server.image else None,
                created=server.created_at,
                updated=server.updated_at,
            )
            server_list.append(server_obj)

        return ServerList(servers=server_list)
    except Exception as e:
        logger.error(f"Failed to get servers: {e}")
        raise


@mcp.resource("openstack://servers/{server_id}")
def get_server(server_id: str) -> Server:
    """Get details of a specific OpenStack server."""
    if not conn:
        raise Exception("OpenStack connection not initialized")

    try:
        server = conn.compute.get_server(server_id)
        if not server:
            raise Exception(f"Server {server_id} not found")

        return Server(
            id=server.id,
            name=server.name,
            status=server.status,
            flavor=server.flavor.get("id") if server.flavor else None,
            image=server.image.get("id") if server.image else None,
            created=server.created_at,
            updated=server.updated_at,
            addresses=server.addresses,
        )
    except Exception as e:
        logger.error(f"Failed to get server {server_id}: {e}")
        raise
