# PowerShell Deployment Script for Analytics Hub Platform
# Sustainable Economic Development Analytics Hub
# Ministry of Economy and Planning

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "up", "down", "restart", "status", "logs", "shell", "test", "clean", "backup", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$ServiceOrProfile = ""
)

$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectRoot "docker-compose.yml"
$EnvFile = Join-Path $ProjectRoot ".env"

# Default values
$Version = if ($env:VERSION) { $env:VERSION } else { "latest" }
$Environment = if ($env:ENVIRONMENT) { $env:ENVIRONMENT } else { "production" }
$BuildDate = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
try {
    $VcsRef = (git rev-parse --short HEAD 2>$null)
} catch {
    $VcsRef = "unknown"
}

# Colors
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Blue }
function Write-Success { Write-Host "[SUCCESS] $args" -ForegroundColor Green }
function Write-Warning { Write-Host "[WARNING] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

function Test-Requirements {
    Write-Info "Checking requirements..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed"
        exit 1
    }
    
    try {
        docker info 2>$null | Out-Null
    } catch {
        Write-Error "Docker daemon is not running"
        exit 1
    }
    
    Write-Success "All requirements met"
}

function Initialize-EnvFile {
    if (-not (Test-Path $EnvFile)) {
        Write-Info "Creating .env file..."
        @"
# Analytics Hub Platform Environment Configuration
# Generated on $(Get-Date)

# Version
VERSION=$Version

# Ports
STREAMLIT_PORT=8501
API_PORT=8000
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# API Workers
API_WORKERS=2

# Build metadata
BUILD_DATE=$BuildDate
VCS_REF=$VcsRef

# Environment
ANALYTICS_HUB_ENV=$Environment
LOG_LEVEL=INFO
"@ | Out-File -FilePath $EnvFile -Encoding utf8
        Write-Success ".env file created"
    } else {
        Write-Info ".env file already exists, skipping creation"
    }
}

function Invoke-Build {
    Write-Info "Building Docker images..."
    
    $env:BUILD_DATE = $BuildDate
    $env:VCS_REF = $VcsRef
    $env:VERSION = $Version
    
    docker compose -f $ComposeFile build `
        --build-arg BUILD_DATE="$BuildDate" `
        --build-arg VCS_REF="$VcsRef"
    
    Write-Success "Docker images built successfully"
}

function Invoke-Up {
    param([string]$DeployProfile = "")
    
    Write-Info "Starting services..."
    
    if ($DeployProfile -eq "production") {
        docker compose -f $ComposeFile --profile production up -d
    } else {
        docker compose -f $ComposeFile up -d
    }
    
    Write-Success "Services started"
    Invoke-Status
}

function Invoke-Down {
    Write-Info "Stopping services..."
    docker compose -f $ComposeFile --profile production down
    Write-Success "Services stopped"
}

function Invoke-Restart {
    param([string]$DeployProfile = "")
    
    Write-Info "Restarting services..."
    Invoke-Down
    Invoke-Up -DeployProfile $DeployProfile
}

function Invoke-Status {
    Write-Info "Service status:"
    docker compose -f $ComposeFile ps
    
    Write-Host ""
    Write-Info "Health check:"
    
    # Check Streamlit
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Success "Streamlit Dashboard: Healthy (http://localhost:8501)"
    } catch {
        Write-Warning "Streamlit Dashboard: Not responding"
    }
    
    # Check API
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Success "FastAPI Backend: Healthy (http://localhost:8000)"
    } catch {
        Write-Warning "FastAPI Backend: Not responding"
    }
}

function Invoke-Logs {
    param([string]$Service = "")
    
    if ($Service) {
        docker compose -f $ComposeFile logs -f $Service
    } else {
        docker compose -f $ComposeFile logs -f
    }
}

function Invoke-Shell {
    param([string]$Service = "dashboard")
    
    Write-Info "Opening shell in $Service container..."
    docker compose -f $ComposeFile exec $Service /bin/bash
}

function Invoke-Test {
    Write-Info "Running tests in container..."
    docker compose -f $ComposeFile run --rm dashboard pytest tests/ -v --tb=short
}

function Invoke-Clean {
    Write-Warning "This will remove all containers, volumes, and images"
    $confirmation = Read-Host "Are you sure? (y/N)"
    
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Write-Info "Cleaning up..."
        docker compose -f $ComposeFile --profile production down -v --rmi local
        docker system prune -f
        Write-Success "Cleanup complete"
    } else {
        Write-Info "Cleanup cancelled"
    }
}

function Invoke-Backup {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $ProjectRoot "backups\$timestamp"
    
    Write-Info "Creating backup in $backupDir..."
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    docker run --rm `
        -v analytics-hub-platform_app-data:/data `
        -v "${backupDir}:/backup" `
        alpine tar czf /backup/data.tar.gz -C /data .
    
    Write-Success "Backup created: $backupDir\data.tar.gz"
}

function Show-Help {
    @"
Analytics Hub Platform - Deployment Script

Usage: .\deploy.ps1 <command> [options]

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
    .\deploy.ps1 build                  # Build images
    .\deploy.ps1 up                     # Start dashboard and API
    .\deploy.ps1 up production          # Start with nginx reverse proxy
    .\deploy.ps1 logs api               # View API logs
    .\deploy.ps1 shell dashboard        # Open shell in dashboard container

Environment Variables:
    `$env:VERSION         Image version tag (default: latest)
    `$env:ENVIRONMENT     Environment name (default: production)

"@
}

# Main execution
Set-Location $ProjectRoot

Test-Requirements
Initialize-EnvFile

switch ($Command) {
    "build"   { Invoke-Build }
    "up"      { Invoke-Up -DeployProfile $ServiceOrProfile }
    "down"    { Invoke-Down }
    "restart" { Invoke-Restart -DeployProfile $ServiceOrProfile }
    "status"  { Invoke-Status }
    "logs"    { Invoke-Logs -Service $ServiceOrProfile }
    "shell"   { Invoke-Shell -Service $(if ($ServiceOrProfile) { $ServiceOrProfile } else { "dashboard" }) }
    "test"    { Invoke-Test }
    "clean"   { Invoke-Clean }
    "backup"  { Invoke-Backup }
    "help"    { Show-Help }
    default   { 
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}
