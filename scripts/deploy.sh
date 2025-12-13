#!/bin/bash
# =============================================================================
# Analytics Hub Platform - Deployment Script
# Sustainable Economic Development Analytics Hub
# Ministry of Economy and Planning
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"

# Default values
VERSION="${VERSION:-latest}"
ENVIRONMENT="${ENVIRONMENT:-production}"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "All requirements met"
}

create_env_file() {
    if [[ ! -f "$ENV_FILE" ]]; then
        log_info "Creating .env file..."
        cat > "$ENV_FILE" << EOF
# Analytics Hub Platform Environment Configuration
# Generated on $(date)

# Version
VERSION=${VERSION}

# Ports
STREAMLIT_PORT=8501
API_PORT=8000
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# API Workers
API_WORKERS=2

# Build metadata
BUILD_DATE=${BUILD_DATE}
VCS_REF=${VCS_REF}

# Environment
ANALYTICS_HUB_ENV=${ENVIRONMENT}
LOG_LEVEL=INFO
EOF
        log_success ".env file created"
    else
        log_info ".env file already exists, skipping creation"
    fi
}

# =============================================================================
# Commands
# =============================================================================

cmd_build() {
    log_info "Building Docker images..."
    
    export BUILD_DATE VCS_REF VERSION
    
    docker compose -f "$COMPOSE_FILE" build \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg VCS_REF="$VCS_REF"
    
    log_success "Docker images built successfully"
}

cmd_up() {
    local profile="${1:-}"
    
    log_info "Starting services..."
    
    if [[ "$profile" == "production" ]]; then
        docker compose -f "$COMPOSE_FILE" --profile production up -d
    else
        docker compose -f "$COMPOSE_FILE" up -d
    fi
    
    log_success "Services started"
    cmd_status
}

cmd_down() {
    log_info "Stopping services..."
    docker compose -f "$COMPOSE_FILE" --profile production down
    log_success "Services stopped"
}

cmd_restart() {
    log_info "Restarting services..."
    cmd_down
    cmd_up "$@"
}

cmd_status() {
    log_info "Service status:"
    docker compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Health check:"
    
    # Check Streamlit
    if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        log_success "Streamlit Dashboard: Healthy (http://localhost:8501)"
    else
        log_warning "Streamlit Dashboard: Not responding"
    fi
    
    # Check API
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        log_success "FastAPI Backend: Healthy (http://localhost:8000)"
    else
        log_warning "FastAPI Backend: Not responding"
    fi
}

cmd_logs() {
    local service="${1:-}"
    
    if [[ -n "$service" ]]; then
        docker compose -f "$COMPOSE_FILE" logs -f "$service"
    else
        docker compose -f "$COMPOSE_FILE" logs -f
    fi
}

cmd_shell() {
    local service="${1:-dashboard}"
    log_info "Opening shell in $service container..."
    docker compose -f "$COMPOSE_FILE" exec "$service" /bin/bash
}

cmd_test() {
    log_info "Running tests in container..."
    docker compose -f "$COMPOSE_FILE" run --rm dashboard \
        pytest tests/ -v --tb=short
}

cmd_clean() {
    log_warning "This will remove all containers, volumes, and images"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker compose -f "$COMPOSE_FILE" --profile production down -v --rmi local
        docker system prune -f
        log_success "Cleanup complete"
    else
        log_info "Cleanup cancelled"
    fi
}

cmd_backup() {
    local backup_dir="${PROJECT_ROOT}/backups/$(date +%Y%m%d_%H%M%S)"
    
    log_info "Creating backup in $backup_dir..."
    mkdir -p "$backup_dir"
    
    # Backup data volume
    docker run --rm \
        -v analytics-hub-platform_app-data:/data \
        -v "$backup_dir":/backup \
        alpine tar czf /backup/data.tar.gz -C /data .
    
    log_success "Backup created: $backup_dir/data.tar.gz"
}

cmd_help() {
    cat << EOF
Analytics Hub Platform - Deployment Script

Usage: $0 <command> [options]

Commands:
    build       Build Docker images
    up          Start all services (add 'production' for nginx)
    down        Stop all services
    restart     Restart all services
    status      Show service status and health
    logs        View logs (optionally specify service: dashboard, api, nginx)
    shell       Open shell in container (default: dashboard)
    test        Run tests in container
    clean       Remove all containers, volumes, and images
    backup      Backup data volume
    help        Show this help message

Examples:
    $0 build                    # Build images
    $0 up                       # Start dashboard and API
    $0 up production            # Start with nginx reverse proxy
    $0 logs api                 # View API logs
    $0 shell dashboard          # Open shell in dashboard container

Environment Variables:
    VERSION         Image version tag (default: latest)
    ENVIRONMENT     Environment name (default: production)

EOF
}

# =============================================================================
# Main
# =============================================================================

main() {
    cd "$PROJECT_ROOT"
    
    check_requirements
    create_env_file
    
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        build)      cmd_build "$@" ;;
        up)         cmd_up "$@" ;;
        down)       cmd_down "$@" ;;
        restart)    cmd_restart "$@" ;;
        status)     cmd_status "$@" ;;
        logs)       cmd_logs "$@" ;;
        shell)      cmd_shell "$@" ;;
        test)       cmd_test "$@" ;;
        clean)      cmd_clean "$@" ;;
        backup)     cmd_backup "$@" ;;
        help|--help|-h)  cmd_help ;;
        *)
            log_error "Unknown command: $command"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
