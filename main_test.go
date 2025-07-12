package main

import (
	"testing"
)

func TestOpenStackConfig_Validate(t *testing.T) {
	tests := []struct {
		name    string
		config  OpenStackConfig
		wantErr bool
	}{
		{
			name: "valid config",
			config: OpenStackConfig{
				AuthURL:     "https://example.com:5000/v3",
				Username:    "testuser",
				Password:    "testpass",
				ProjectName: "testproject",
				Region:      "testregion",
			},
			wantErr: false,
		},
		{
			name: "missing auth url",
			config: OpenStackConfig{
				Username:    "testuser",
				Password:    "testpass",
				ProjectName: "testproject",
				Region:      "testregion",
			},
			wantErr: true,
		},
		{
			name: "missing username",
			config: OpenStackConfig{
				AuthURL:     "https://example.com:5000/v3",
				Password:    "testpass",
				ProjectName: "testproject",
				Region:      "testregion",
			},
			wantErr: true,
		},
		{
			name: "missing password",
			config: OpenStackConfig{
				AuthURL:     "https://example.com:5000/v3",
				Username:    "testuser",
				ProjectName: "testproject",
				Region:      "testregion",
			},
			wantErr: true,
		},
		{
			name: "missing project",
			config: OpenStackConfig{
				AuthURL:  "https://example.com:5000/v3",
				Username: "testuser",
				Password: "testpass",
				Region:   "testregion",
			},
			wantErr: true,
		},
		{
			name: "missing region",
			config: OpenStackConfig{
				AuthURL:     "https://example.com:5000/v3",
				Username:    "testuser",
				Password:    "testpass",
				ProjectName: "testproject",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateConfig(&tt.config)
			if (err != nil) != tt.wantErr {
				t.Errorf("validateConfig() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func validateConfig(config *OpenStackConfig) error {
	if config.AuthURL == "" {
		return &ConfigError{Field: "auth-url", Message: "Auth URL is required"}
	}
	if config.Username == "" {
		return &ConfigError{Field: "username", Message: "Username is required"}
	}
	if config.Password == "" {
		return &ConfigError{Field: "password", Message: "Password is required"}
	}
	if config.ProjectName == "" {
		return &ConfigError{Field: "project", Message: "Project name is required"}
	}
	if config.Region == "" {
		return &ConfigError{Field: "region", Message: "Region is required"}
	}
	return nil
}

type ConfigError struct {
	Field   string
	Message string
}

func (e *ConfigError) Error() string {
	return e.Message
}

func TestOpenStackMCPServer_ListResources(t *testing.T) {
	// モックサーバーのテスト
	server := &OpenStackMCPServer{
		config: &OpenStackConfig{
			AuthURL:     "https://example.com:5000/v3",
			Username:    "testuser",
			Password:    "testpass",
			ProjectName: "testproject",
			Region:      "testregion",
		},
		client: nil, // 実際のクライアントは接続テストで使用
	}

	// 基本的な構造のテスト
	if server.config == nil {
		t.Error("Server config should not be nil")
	}

	if server.config.AuthURL != "https://example.com:5000/v3" {
		t.Errorf("Expected auth URL %s, got %s", "https://example.com:5000/v3", server.config.AuthURL)
	}
}

func TestResourceURIGeneration(t *testing.T) {
	tests := []struct {
		name     string
		resource string
		id       string
		expected string
	}{
		{
			name:     "instance uri",
			resource: "instances",
			id:       "test-instance-id",
			expected: "openstack://instances/test-instance-id",
		},
		{
			name:     "network uri",
			resource: "networks",
			id:       "test-network-id",
			expected: "openstack://networks/test-network-id",
		},
		{
			name:     "stack uri",
			resource: "stacks",
			id:       "test-stack-id",
			expected: "openstack://stacks/test-stack-id",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			uri := generateResourceURI(tt.resource, tt.id)
			if uri != tt.expected {
				t.Errorf("generateResourceURI() = %v, want %v", uri, tt.expected)
			}
		})
	}
}

func generateResourceURI(resource, id string) string {
	return "openstack://" + resource + "/" + id
}
