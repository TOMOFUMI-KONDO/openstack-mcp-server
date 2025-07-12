package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack"
	"github.com/gophercloud/gophercloud/v2/openstack/compute/v2/servers"
	"github.com/gophercloud/gophercloud/v2/openstack/networking/v2/networks"
	"github.com/gophercloud/gophercloud/v2/openstack/orchestration/v1/stacks"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"github.com/spf13/cobra"
)

type OpenStackConfig struct {
	AuthURL     string
	Username    string
	Password    string
	ProjectName string
	Region      string
}

type OpenStackMCPServer struct {
	config *OpenStackConfig
	client *gophercloud.ServiceClient
}

func main() {
	var config OpenStackConfig

	rootCmd := &cobra.Command{
		Use:   "openstack-mcp-server",
		Short: "OpenStack MCP Server",
		Long:  "Model Context Protocol server for OpenStack cluster information",
		RunE: func(cmd *cobra.Command, args []string) error {
			return runServer(&config)
		},
	}

	rootCmd.Flags().StringVar(&config.AuthURL, "auth-url", "", "OpenStack Auth URL (required)")
	rootCmd.Flags().StringVar(&config.Username, "username", "", "OpenStack Username (required)")
	rootCmd.Flags().StringVar(&config.Password, "password", "", "OpenStack Password (required)")
	rootCmd.Flags().StringVar(&config.ProjectName, "project", "", "OpenStack Project Name (required)")
	rootCmd.Flags().StringVar(&config.Region, "region", "", "OpenStack Region (required)")

	rootCmd.MarkFlagRequired("auth-url")
	rootCmd.MarkFlagRequired("username")
	rootCmd.MarkFlagRequired("password")
	rootCmd.MarkFlagRequired("project")
	rootCmd.MarkFlagRequired("region")

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func runServer(config *OpenStackConfig) error {
	// OpenStackクライアントの初期化
	client, err := initOpenStackClient(config)
	if err != nil {
		return fmt.Errorf("failed to initialize OpenStack client: %w", err)
	}

	s := &OpenStackMCPServer{
		config: config,
		client: client,
	}

	// MCPサーバーの設定
	mcpServer := server.NewMCPServer(
		"openstack-mcp-server",
		mcp.WithDescription("OpenStack cluster information provider"),
	)

	// リソースプロバイダーの登録
	mcpServer.RegisterResourceProvider(s)

	log.Println("Starting OpenStack MCP Server...")
	return mcpServer.ListenAndServe(":8080")
}

func initOpenStackClient(config *OpenStackConfig) (*gophercloud.ServiceClient, error) {
	opts := gophercloud.AuthOptions{
		IdentityEndpoint: config.AuthURL,
		Username:         config.Username,
		Password:         config.Password,
		TenantName:       config.ProjectName,
	}

	provider, err := openstack.AuthenticatedClient(opts)
	if err != nil {
		return nil, fmt.Errorf("failed to authenticate: %w", err)
	}

	client, err := openstack.NewComputeV2(provider, gophercloud.EndpointOpts{
		Region: config.Region,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create compute client: %w", err)
	}

	return client, nil
}

// MCPリソースプロバイダーの実装
func (s *OpenStackMCPServer) ListResources(ctx context.Context, req *mcp.ListResourcesRequest) (*mcp.ListResourcesResponse, error) {
	var resources []*mcp.Resource

	// インスタンス情報の取得
	instances, err := s.getInstances(ctx)
	if err != nil {
		log.Printf("Failed to get instances: %v", err)
	} else {
		resources = append(resources, instances...)
	}

	// ネットワーク情報の取得
	networks, err := s.getNetworks(ctx)
	if err != nil {
		log.Printf("Failed to get networks: %v", err)
	} else {
		resources = append(resources, networks...)
	}

	// スタック情報の取得
	stacks, err := s.getStacks(ctx)
	if err != nil {
		log.Printf("Failed to get stacks: %v", err)
	} else {
		resources = append(resources, stacks...)
	}

	return &mcp.ListResourcesResponse{
		Resources: resources,
	}, nil
}

func (s *OpenStackMCPServer) GetResource(ctx context.Context, req *mcp.GetResourceRequest) (*mcp.GetResourceResponse, error) {
	// 特定のリソースの詳細情報を取得
	// 実装は必要に応じて追加
	return &mcp.GetResourceResponse{
		Resource: &mcp.Resource{},
	}, nil
}

func (s *OpenStackMCPServer) getInstances(ctx context.Context) ([]*mcp.Resource, error) {
	opts := servers.ListOpts{}
	allPages, err := servers.List(s.client, opts).AllPages()
	if err != nil {
		return nil, err
	}

	allServers, err := servers.ExtractServers(allPages)
	if err != nil {
		return nil, err
	}

	var resources []*mcp.Resource
	for _, server := range allServers {
		resource := &mcp.Resource{
			Uri:      fmt.Sprintf("openstack://instances/%s", server.ID),
			MimeType: "application/json",
			Text: fmt.Sprintf(`{
				"id": "%s",
				"name": "%s",
				"status": "%s",
				"flavor": "%s",
				"image": "%s",
				"created": "%s",
				"updated": "%s"
			}`, server.ID, server.Name, server.Status, server.Flavor["id"], server.Image["id"], server.Created, server.Updated),
		}
		resources = append(resources, resource)
	}

	return resources, nil
}

func (s *OpenStackMCPServer) getNetworks(ctx context.Context) ([]*mcp.Resource, error) {
	// ネットワーククライアントの取得
	provider, err := openstack.AuthenticatedClient(gophercloud.AuthOptions{
		IdentityEndpoint: s.config.AuthURL,
		Username:         s.config.Username,
		Password:         s.config.Password,
		TenantName:       s.config.ProjectName,
	})
	if err != nil {
		return nil, err
	}

	networkClient, err := openstack.NewNetworkV2(provider, gophercloud.EndpointOpts{
		Region: s.config.Region,
	})
	if err != nil {
		return nil, err
	}

	opts := networks.ListOpts{}
	allPages, err := networks.List(networkClient, opts).AllPages()
	if err != nil {
		return nil, err
	}

	allNetworks, err := networks.ExtractNetworks(allPages)
	if err != nil {
		return nil, err
	}

	var resources []*mcp.Resource
	for _, network := range allNetworks {
		resource := &mcp.Resource{
			Uri:      fmt.Sprintf("openstack://networks/%s", network.ID),
			MimeType: "application/json",
			Text: fmt.Sprintf(`{
				"id": "%s",
				"name": "%s",
				"status": "%s",
				"admin_state_up": %t,
				"shared": %t,
				"tenant_id": "%s"
			}`, network.ID, network.Name, network.Status, network.AdminStateUp, network.Shared, network.TenantID),
		}
		resources = append(resources, resource)
	}

	return resources, nil
}

func (s *OpenStackMCPServer) getStacks(ctx context.Context) ([]*mcp.Resource, error) {
	// Heatクライアントの取得
	provider, err := openstack.AuthenticatedClient(gophercloud.AuthOptions{
		IdentityEndpoint: s.config.AuthURL,
		Username:         s.config.Username,
		Password:         s.config.Password,
		TenantName:       s.config.ProjectName,
	})
	if err != nil {
		return nil, err
	}

	heatClient, err := openstack.NewOrchestrationV1(provider, gophercloud.EndpointOpts{
		Region: s.config.Region,
	})
	if err != nil {
		return nil, err
	}

	opts := stacks.ListOpts{}
	allPages, err := stacks.List(heatClient, opts).AllPages()
	if err != nil {
		return nil, err
	}

	allStacks, err := stacks.ExtractStacks(allPages)
	if err != nil {
		return nil, err
	}

	var resources []*mcp.Resource
	for _, stack := range allStacks {
		resource := &mcp.Resource{
			Uri:      fmt.Sprintf("openstack://stacks/%s", stack.ID),
			MimeType: "application/json",
			Text: fmt.Sprintf(`{
				"id": "%s",
				"name": "%s",
				"status": "%s",
				"description": "%s",
				"created_at": "%s",
				"updated_at": "%s"
			}`, stack.ID, stack.Name, stack.Status, stack.Description, stack.CreatedAt, stack.UpdatedAt),
		}
		resources = append(resources, resource)
	}

	return resources, nil
}
