#!/usr/bin/env zsh
#
# run_knowledge_container.sh - Starts the knowledge container with all necessary volumes
#

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="knowledge-container"
IMAGE_NAME="knowledge-project:latest"
PROJECT_ROOT="${HOME}/projetos/knowledge"
METRICS_PORT=9091

# Functions
function log_info() {
    echo -e "${GREEN}>> ShellScript::${FUNCNAME[1]} $1${NC}"
}

function log_warn() {
    echo -e "${YELLOW}>>> ShellScript::${FUNCNAME[1]} $1${NC}"
}

function log_error() {
    echo -e "${RED}>>>> ShellScript::${FUNCNAME[1]} $1${NC}"
}

function parse_arguments() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --metrics-port)
                METRICS_PORT="$2"
                log_info "Using custom metrics endpoint port: $METRICS_PORT"
                shift 2
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --metrics-port PORT     Set custom port for metrics endpoint (default: 9091)"
                echo "  --help, -h              Show this help message"
                exit 0
                ;;
            *)
                log_warn "Unknown option: $1"
                shift
                ;;
        esac
    done
}

function check_dependencies() {
    log_info "Checking dependencies"
    
    # Check if Podman is installed
    if ! command -v podman &> /dev/null; then
        log_error "Podman is not installed. Please install Podman to continue."
        exit 1
    fi
    
    # Check if image exists
    if ! podman image exists "${IMAGE_NAME}"; then
        log_error "Image ${IMAGE_NAME} does not exist. Please build it first with: podman build -t ${IMAGE_NAME} -f ${PROJECT_ROOT}/container/Dockerfile ${PROJECT_ROOT}"
        exit 1
    fi
}

function check_existing_container() {
    log_info "Checking for existing container"
    
    # Check if container already exists and is running
    if podman container exists "${CONTAINER_NAME}" &> /dev/null; then
        if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
            log_warn "Container ${CONTAINER_NAME} is already running"
            read -p "Do you want to stop and remove it? (y/n): " -r REPLY
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                podman stop "${CONTAINER_NAME}"
                podman rm "${CONTAINER_NAME}"
                log_info "Container ${CONTAINER_NAME} stopped and removed"
            else
                log_info "Exiting without starting a new container"
                exit 0
            fi
        else
            log_warn "Container ${CONTAINER_NAME} exists but is not running"
            read -p "Do you want to remove it? (y/n): " -r REPLY
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                podman rm "${CONTAINER_NAME}"
                log_info "Container ${CONTAINER_NAME} removed"
            fi
        fi
    fi
}

function run_container() {
    log_info "Starting container ${CONTAINER_NAME}"
    
    # Run the container with volume mounts
    podman run -d \
        --name "${CONTAINER_NAME}" \
        -v "${PROJECT_ROOT}/data:/app/data:Z" \
        -v "${PROJECT_ROOT}/logs:/app/logs:Z" \
        -v "${PROJECT_ROOT}/backup:/app/backup:Z" \
        -v "${PROJECT_ROOT}/config:/app/config:Z" \
        -p "${METRICS_PORT}:9091" \
        "${IMAGE_NAME}"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to start container"
        exit 1
    fi
    
    log_info "Container ${CONTAINER_NAME} started successfully"
    log_info "Metrics endpoint available at http://localhost:${METRICS_PORT} for Prometheus scraping"
}

# Main execution
function main() {
    log_info "Starting knowledge container setup"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Check for dependencies
    check_dependencies
    
    # Check for existing container
    check_existing_container
    
    # Run the container
    run_container
    
    log_info "Container setup completed"
}

# Call the main function with all arguments
main "$@"