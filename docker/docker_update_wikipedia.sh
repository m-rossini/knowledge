#!/usr/bin/env zsh
#
# docker_update_wikipedia.sh - Runs the update_wikipedia.sh script inside the container
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
        echo "Please start the container first with: ./docker/run_knowledge_container.sh"
        exit 1
    fi
}

function run_update_script() {
    log_info "Running update_wikipedia.sh in container"
    
    # Pass all arguments to the script inside the container
    podman exec "${CONTAINER_NAME}" sh -c "cd /app && ./scripts/update_wikipedia.sh $*"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to run update_wikipedia.sh in container"
        return 1
    fi
    
    log_info "update_wikipedia.sh completed successfully"
    return 0
}

# Main execution
function main() {
    log_info "Starting Wikipedia update in container"
    
    # Check if the container is running
    check_container
    
    # Run the update script
    run_update_script "$@"
    
    if [ $? -eq 0 ]; then
        log_info "Wikipedia update in container completed successfully"
        exit 0
    else
        log_error "Wikipedia update in container failed"
        exit 1
    fi
}

# Call the main function with all arguments
main "$@"