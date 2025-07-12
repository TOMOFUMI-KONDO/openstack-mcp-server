# OpenStack MCP Server

OpenStackクラスタの情報を提供するModel Context Protocol (MCP) サーバーです。

## 概要

このMCPサーバーは、OpenStackクラスタから以下の情報を取得して提供します：

- インスタンス（仮想マシン）の情報
- ネットワークの情報
- Heatスタックの情報

## インストール

### 前提条件

- Go 1.21以上
- OpenStackクラスタへのアクセス権限

### ビルド

```bash
git clone <repository-url>
cd openstack-mcp-server
go build -o openstack-mcp-server
```

## 使用方法

### コマンドライン引数

```bash
./openstack-mcp-server \
  --auth-url "https://your-openstack-controller:5000/v3" \
  --username "your-username" \
  --password "your-password" \
  --project "your-project" \
  --region "your-region"
```

### 必須パラメータ

- `--auth-url`: OpenStack IdentityサービスのエンドポイントURL
- `--username`: OpenStackユーザー名
- `--password`: OpenStackパスワード
- `--project`: OpenStackプロジェクト名（テナント名）
- `--region`: OpenStackリージョン名

### 環境変数での設定

セキュリティ上の理由から、パスワードは環境変数で設定することを推奨します：

```bash
export OS_PASSWORD="your-password"
./openstack-mcp-server \
  --auth-url "https://your-openstack-controller:5000/v3" \
  --username "your-username" \
  --project "your-project" \
  --region "your-region"
```

## 提供されるリソース

### インスタンス情報

URI: `openstack://instances/{instance-id}`

```json
{
  "id": "instance-uuid",
  "name": "instance-name",
  "status": "ACTIVE",
  "flavor": "flavor-id",
  "image": "image-id",
  "created": "2024-01-01T00:00:00Z",
  "updated": "2024-01-01T00:00:00Z"
}
```

### ネットワーク情報

URI: `openstack://networks/{network-id}`

```json
{
  "id": "network-uuid",
  "name": "network-name",
  "status": "ACTIVE",
  "admin_state_up": true,
  "shared": false,
  "tenant_id": "tenant-uuid"
}
```

### スタック情報

URI: `openstack://stacks/{stack-id}`

```json
{
  "id": "stack-uuid",
  "name": "stack-name",
  "status": "CREATE_COMPLETE",
  "description": "Stack description",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 設定例

### DevStack環境

```bash
./openstack-mcp-server \
  --auth-url "http://localhost:5000/v3" \
  --username "admin" \
  --password "admin" \
  --project "admin" \
  --region "RegionOne"
```

### 本番環境

```bash
./openstack-mcp-server \
  --auth-url "https://openstack.example.com:5000/v3" \
  --username "service-account" \
  --password "$OS_PASSWORD" \
  --project "production-project" \
  --region "us-west-1"
```

## セキュリティ考慮事項

- パスワードは環境変数で設定することを推奨
- 本番環境では適切なIAMロールとポリシーを設定
- ネットワークアクセス制御を適切に設定
- 定期的な認証情報のローテーション

## トラブルシューティング

### 認証エラー

```
Error: failed to initialize OpenStack client: failed to authenticate: 401 Unauthorized
```

- 認証情報が正しいか確認
- プロジェクト名が正しいか確認
- ユーザーに適切な権限があるか確認

### 接続エラー

```
Error: failed to initialize OpenStack client: failed to create compute client: connection refused
```

- 認証URLが正しいか確認
- ネットワーク接続が可能か確認
- ファイアウォール設定を確認

## 開発

### 依存関係

- [mark3labs/mcp-go](https://github.com/mark3labs/mcp-go) - MCPフレームワーク
- [gophercloud/gophercloud](https://github.com/gophercloud/gophercloud) - OpenStack Go SDK
- [spf13/cobra](https://github.com/spf13/cobra) - CLIフレームワーク

### ローカル開発

```bash
go mod tidy
go run main.go --help
```

## ライセンス

MIT License 