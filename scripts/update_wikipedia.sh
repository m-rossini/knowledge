#!/usr/bin/env zsh
#
# update_wikipedia.sh - Checks for Wikipedia updates and downloads if necessary
#

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set error handling
set -e

# Configuration
CONFIG_FILE="config/config.json"
LOG_DIR="logs"

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

function check_dependencies() {
    log_info "Checking dependencies"
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3 to continue."
        exit 1
    fi
    
    # Check if required Python packages are installed
    if ! python3 -c "import requests" &> /dev/null; then
        log_error "Required Python packages are not installed. Please run: pip install -r requirements.txt"
        exit 1
    fi
}

function create_directories() {
    log_info "Ensuring required directories exist"
    
    # Create directories if they don't exist
    mkdir -p "${LOG_DIR}"
    mkdir -p "data/wikipedia"
    mkdir -p "backup/wikipedia"
}

function run_update() {
    log_info "Running Wikipedia update check"
    
    # Run the Python application (Wikipedia update is now the default behavior)
    python3 src/main.py --config "${CONFIG_FILE}" --log-dir "${LOG_DIR}"
    
    if [ $? -ne 0 ]; then
        log_error "Wikipedia update failed"
        return 1
    fi
    
    log_info "Wikipedia update process completed"
    return 0
}

# Main execution
function main() {
    log_info "Starting Wikipedia update process"
    
    # Make sure we're in the project root directory
    SCRIPT_DIR=$(dirname "$0")
    cd "${SCRIPT_DIR}/.." || exit 1
    
    # Run the update process
    check_dependencies
    create_directories
    run_update
    
    if [ $? -eq 0 ]; then
        log_info "Wikipedia update completed successfully"
        exit 0
    else
        log_error "Wikipedia update process failed"
        exit 1
    fi
}

# Call the main function
main
