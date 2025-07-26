from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
import server
from server import OpenStackMCPServer, Server, ServerList, get_server, list_servers


class TestServerModel:
    def test_server_creation_with_all_fields(self) -> None:
        server_data = {
            "id": "test-id-123",
            "name": "test-server",
            "status": "ACTIVE",
            "flavor": "m1.small",
            "image": "ubuntu-20.04",
            "created": "2023-01-01T00:00:00",
            "updated": "2023-01-02T00:00:00",
            "addresses": {"private": [{"addr": "10.0.0.1"}]},
        }
        server_obj = Server(**server_data)

        assert server_obj.id == "test-id-123"
        assert server_obj.name == "test-server"
        assert server_obj.status == "ACTIVE"
        assert server_obj.flavor == "m1.small"
        assert server_obj.image == "ubuntu-20.04"
        assert server_obj.created == "2023-01-01T00:00:00"
        assert server_obj.updated == "2023-01-02T00:00:00"
        assert server_obj.addresses == {"private": [{"addr": "10.0.0.1"}]}

    def test_server_creation_with_minimal_fields(self) -> None:
        server_data = {"id": "test-id-456", "name": "minimal-server", "status": "BUILDING"}
        server_obj = Server(**server_data)

        assert server_obj.id == "test-id-456"
        assert server_obj.name == "minimal-server"
        assert server_obj.status == "BUILDING"
        assert server_obj.flavor is None
        assert server_obj.image is None
        assert server_obj.created is None
        assert server_obj.updated is None
        assert server_obj.addresses is None


class TestServerListModel:
    def test_server_list_creation(self) -> None:
        servers = [Server(id="server1", name="test1", status="ACTIVE"), Server(id="server2", name="test2", status="STOPPED")]
        server_list = ServerList(servers=servers)

        assert len(server_list.servers) == 2
        assert server_list.servers[0].id == "server1"
        assert server_list.servers[1].id == "server2"

    def test_empty_server_list(self) -> None:
        server_list = ServerList(servers=[])
        assert len(server_list.servers) == 0


class TestOpenStackMCPServer:
    def test_init(self) -> None:
        server = OpenStackMCPServer(
            auth_url="https://openstack.example.com:5000",
            user_domain_name="default",
            username="admin",
            password="secret",
            project_domain_id="default",
            project_name="demo",
            region="RegionOne",
        )

        assert server.auth_url == "https://openstack.example.com:5000"
        assert server.user_domain_name == "default"
        assert server.username == "admin"
        assert server.password == "secret"
        assert server.project_domain_id == "default"
        assert server.project_name == "demo"
        assert server.region == "RegionOne"

    @patch("server.connection.Connection")
    def test_connect_success(self, mock_connection: MagicMock) -> None:
        mock_conn_instance = Mock()
        mock_connection.return_value = mock_conn_instance

        server_instance = OpenStackMCPServer(
            auth_url="https://openstack.example.com:5000",
            user_domain_name="default",
            username="admin",
            password="secret",
            project_domain_id="default",
            project_name="demo",
            region="RegionOne",
        )

        server_instance.connect()

        mock_connection.assert_called_once_with(
            region_name="RegionOne",
            auth={
                "auth_url": "https://openstack.example.com:5000",
                "user_domain_name": "default",
                "username": "admin",
                "password": "secret",
                "project_domain_id": "default",
                "project_name": "demo",
            },
        )
        assert server.conn == mock_conn_instance

    @patch("server.connection.Connection")
    def test_connect_failure(self, mock_connection: MagicMock) -> None:
        mock_connection.side_effect = Exception("Connection failed")

        server_instance = OpenStackMCPServer(
            auth_url="https://openstack.example.com:5000",
            user_domain_name="default",
            username="admin",
            password="secret",
            project_domain_id="default",
            project_name="demo",
            region="RegionOne",
        )

        with pytest.raises(Exception) as exc_info:
            server_instance.connect()

        assert str(exc_info.value) == "Connection failed"

    @patch("server.mcp.run")
    @patch.object(OpenStackMCPServer, "connect")
    def test_run_success(self, mock_connect: MagicMock, mock_mcp_run: MagicMock) -> None:
        server_instance = OpenStackMCPServer(
            auth_url="https://openstack.example.com:5000",
            user_domain_name="default",
            username="admin",
            password="secret",
            project_domain_id="default",
            project_name="demo",
            region="RegionOne",
        )

        server_instance.run()

        mock_connect.assert_called_once()
        mock_mcp_run.assert_called_once()

    @patch.object(OpenStackMCPServer, "connect")
    def test_run_failure(self, mock_connect: MagicMock) -> None:
        mock_connect.side_effect = Exception("Connect failed")

        server_instance = OpenStackMCPServer(
            auth_url="https://openstack.example.com:5000",
            user_domain_name="default",
            username="admin",
            password="secret",
            project_domain_id="default",
            project_name="demo",
            region="RegionOne",
        )

        with pytest.raises(Exception) as exc_info:
            server_instance.run()

        assert str(exc_info.value) == "Connect failed"


class TestMCPToolFunctions:
    def test_list_servers_no_connection(self) -> None:
        server.conn = None

        with pytest.raises(Exception) as exc_info:
            list_servers()

        assert str(exc_info.value) == "OpenStack connection not initialized"

    @patch("server.conn")
    def test_list_servers_success(self, mock_conn: MagicMock) -> None:
        mock_server1 = Mock()
        mock_server1.id = "server1"
        mock_server1.name = "test-server-1"
        mock_server1.status = "ACTIVE"
        mock_server1.flavor = {"id": "m1.small"}
        mock_server1.image = {"id": "ubuntu-20.04"}
        mock_server1.created_at = "2023-01-01T00:00:00"
        mock_server1.updated_at = "2023-01-02T00:00:00"

        mock_server2 = Mock()
        mock_server2.id = "server2"
        mock_server2.name = "test-server-2"
        mock_server2.status = "STOPPED"
        mock_server2.flavor = None
        mock_server2.image = None
        mock_server2.created_at = "2023-01-03T00:00:00"
        mock_server2.updated_at = "2023-01-04T00:00:00"

        mock_conn.compute.servers.return_value = [mock_server1, mock_server2]
        server.conn = mock_conn

        result = list_servers()

        assert isinstance(result, ServerList)
        assert len(result.servers) == 2

        # Test first server - all fields populated
        assert result.servers[0].id == "server1"
        assert result.servers[0].name == "test-server-1"
        assert result.servers[0].status == "ACTIVE"
        assert result.servers[0].flavor == "m1.small"
        assert result.servers[0].image == "ubuntu-20.04"
        assert result.servers[0].created == "2023-01-01T00:00:00"
        assert result.servers[0].updated == "2023-01-02T00:00:00"

        # Test second server - minimal fields
        assert result.servers[1].id == "server2"
        assert result.servers[1].name == "test-server-2"
        assert result.servers[1].status == "STOPPED"
        assert result.servers[1].flavor is None
        assert result.servers[1].image is None
        assert result.servers[1].created == "2023-01-03T00:00:00"
        assert result.servers[1].updated == "2023-01-04T00:00:00"

    @patch("server.conn")
    def test_list_servers_api_error(self, mock_conn: MagicMock) -> None:
        mock_conn.compute.servers.side_effect = Exception("API Error")
        server.conn = mock_conn

        with pytest.raises(Exception) as exc_info:
            list_servers()

        assert str(exc_info.value) == "API Error"

    def test_get_server_no_connection(self) -> None:
        server.conn = None

        with pytest.raises(Exception) as exc_info:
            get_server("test-id")

        assert str(exc_info.value) == "OpenStack connection not initialized"

    @patch("server.conn")
    def test_get_server_success(self, mock_conn: MagicMock) -> None:
        mock_server = Mock()
        mock_server.id = "server1"
        mock_server.name = "test-server-1"
        mock_server.status = "ACTIVE"
        mock_server.flavor = {"id": "m1.small"}
        mock_server.image = {"id": "ubuntu-20.04"}
        mock_server.created_at = "2023-01-01T00:00:00"
        mock_server.updated_at = "2023-01-02T00:00:00"
        mock_server.addresses = {"private": [{"addr": "10.0.0.1"}]}

        mock_conn.compute.get_server.return_value = mock_server
        server.conn = mock_conn

        result = get_server("server1")

        assert isinstance(result, Server)
        # Test all fields are properly mapped
        assert result.id == "server1"
        assert result.name == "test-server-1"
        assert result.status == "ACTIVE"
        assert result.flavor == "m1.small"
        assert result.image == "ubuntu-20.04"
        assert result.created == "2023-01-01T00:00:00"
        assert result.updated == "2023-01-02T00:00:00"
        assert result.addresses == {"private": [{"addr": "10.0.0.1"}]}

    @patch("server.conn")
    def test_get_server_not_found(self, mock_conn: MagicMock) -> None:
        mock_conn.compute.get_server.return_value = None
        server.conn = mock_conn

        with pytest.raises(Exception) as exc_info:
            get_server("nonexistent")

        assert str(exc_info.value) == "Server (id:nonexistent) not found"

    @patch("server.conn")
    def test_get_server_api_error(self, mock_conn: MagicMock) -> None:
        mock_conn.compute.get_server.side_effect = Exception("API Error")
        server.conn = mock_conn

        with pytest.raises(Exception) as exc_info:
            get_server("server1")

        assert str(exc_info.value) == "API Error"
