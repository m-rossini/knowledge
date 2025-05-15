#!/usr/bin/env zsh
#
# container_update_zim.sh - Runs the update_zim.sh script inside the container
#

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="knowledge-container"

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

function check_container() {
    log_info "Checking if container is running"
    
    # Check if container exists and is running
    if ! podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_error "Container ${CONTAINER_NAME} is not running"
        echo "Please start the container first with: ./container/run_knowledge_container.sh"
        exit 1
    fi
}

function run_update_script() {
    log_info "Running container-compatible update script in container"
    
    # Pass all arguments to the container-compatible script inside the container
    podman exec "${CONTAINER_NAME}" sh -c "cd /app && ./container/container_update_script.sh $*"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to run update script in container"
        return 1
    fi
    
    log_info "Update script completed successfully"
    return 0
}

# Main execution
function main() {
    log_info "Starting ZIM update in container"
    
    # Check if the container is running
    check_container
    
    # Run the update script
    run_update_script "$@"
    
    if [ $? -eq 0 ]; then
        log_info "ZIM update in container completed successfully"
        exit 0
    else
        log_error "ZIM update in container failed"
        exit 1
    fi
}

# Call the main function with all arguments
main "$@"