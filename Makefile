.PHONY: build test run clean docker-build docker-run help

# デフォルトターゲット
.DEFAULT_GOAL := help

# 変数
BINARY_NAME=openstack-mcp-server
DOCKER_IMAGE=openstack-mcp-server
DOCKER_TAG=latest

# ビルド
build:
	@echo "Building $(BINARY_NAME)..."
	go build -o $(BINARY_NAME) .

# テスト
test:
	@echo "Running tests..."
	go test -v ./...

# 実行（ヘルプ表示）
run:
	@echo "Running $(BINARY_NAME)..."
	./$(BINARY_NAME) --help

# クリーン
clean:
	@echo "Cleaning..."
	rm -f $(BINARY_NAME)
	go clean

# Dockerビルド
docker-build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

# Docker実行
docker-run:
	@echo "Running Docker container..."
	docker run -p 8080:8080 \
		-e OS_AUTH_URL=$(OS_AUTH_URL) \
		-e OS_USERNAME=$(OS_USERNAME) \
		-e OS_PASSWORD=$(OS_PASSWORD) \
		-e OS_PROJECT_NAME=$(OS_PROJECT_NAME) \
		-e OS_REGION_NAME=$(OS_REGION_NAME) \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		--auth-url $(OS_AUTH_URL) \
		--username $(OS_USERNAME) \
		--password $(OS_PASSWORD) \
		--project $(OS_PROJECT_NAME) \
		--region $(OS_REGION_NAME)

# Docker Compose起動
docker-compose-up:
	@echo "Starting with Docker Compose..."
	docker-compose up -d

# Docker Compose停止
docker-compose-down:
	@echo "Stopping Docker Compose..."
	docker-compose down

# 依存関係の整理
deps:
	@echo "Tidying dependencies..."
	go mod tidy
	go mod download

# フォーマット
fmt:
	@echo "Formatting code..."
	go fmt ./...

# リント
lint:
	@echo "Linting code..."
	golangci-lint run

# ヘルプ
help:
	@echo "Available targets:"
	@echo "  build              - Build the binary"
	@echo "  test               - Run tests"
	@echo "  run                - Run the binary with help"
	@echo "  clean              - Clean build artifacts"
	@echo "  docker-build       - Build Docker image"
	@echo "  docker-run         - Run Docker container"
	@echo "  docker-compose-up  - Start with Docker Compose"
	@echo "  docker-compose-down- Stop Docker Compose"
	@echo "  deps               - Tidy dependencies"
	@echo "  fmt                - Format code"
	@echo "  lint               - Lint code"
	@echo "  help               - Show this help"
	@echo ""
	@echo "Environment variables for Docker:"
	@echo "  OS_AUTH_URL        - OpenStack Auth URL"
	@echo "  OS_USERNAME        - OpenStack Username"
	@echo "  OS_PASSWORD        - OpenStack Password"
	@echo "  OS_PROJECT_NAME    - OpenStack Project Name"
	@echo "  OS_REGION_NAME     - OpenStack Region Name" 