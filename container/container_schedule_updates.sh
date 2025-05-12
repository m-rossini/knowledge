#!/usr/bin/env zsh
#
# container_schedule_updates.sh - Runs the schedule_updates.sh script inside the container
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

function run_schedule_script() {
    log_info "Running schedule_updates.sh in container"
    
    # Pass all arguments to the script inside the container
    podman exec "${CONTAINER_NAME}" sh -c "cd /app && ./scripts/schedule_updates.sh $*"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to run schedule_updates.sh in container"
        return 1
    fi
    
    log_info "schedule_updates.sh completed successfully"
    return 0
}

# Main execution
function main() {
    log_info "Starting scheduled updates setup in container"
    
    # Check if the container is running
    check_container
    
    # Run the schedule script
    run_schedule_script "$@"
    
    if [ $? -eq 0 ]; then
        log_info "Scheduled updates setup in container completed successfully"
        exit 0
    else
        log_error "Scheduled updates setup in container failed"
        exit 1
    fi
}

# Call the main function with all arguments
main "$@"