#!/usr/bin/env zsh
#
# download_sources.sh - Downloads configured knowledge sources as needed
#

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set error handling
set -e

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

# Configuration - use BASE_PATH from environment or set default
if [ -z "${BASE_PATH}" ]; then
    # BASE_PATH not provided, use default
    export BASE_PATH="${HOME}/projetos/knowledge"
    log_info "Using default BASE_PATH: ${BASE_PATH}"
else
    log_info "Using provided BASE_PATH: ${BASE_PATH}"
fi

CONFIG_FILE="${BASE_PATH}/config/config.json"
LOG_DIR="${BASE_PATH}/logs"
FORCE_DOWNLOAD=false
SOURCE_NAME=""

# Functions
function parse_arguments() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --force|-f)
                FORCE_DOWNLOAD=true
                log_info "Force download enabled"
                shift
                ;;
            --source|-s)
                SOURCE_NAME="$2"
                log_info "Using source name: ${SOURCE_NAME}"
                shift 2
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
    
    # Create log directory
    mkdir -p "${LOG_DIR}"
    
    # Note: We don't need to create source-specific directories anymore
    # as they'll be created automatically based on the configuration
}

function download_source() {
    log_info "Downloading knowledge sources"
    log_info "Using config file: ${CONFIG_FILE}"
    log_info "Log directory: ${LOG_DIR}"
    if [ -n "${SOURCE_NAME}" ]; then
        log_info "Requested source: ${SOURCE_NAME}"
    else
        log_info "No specific source requested; all sources in config will be processed"
    fi
    
    # Build command based on arguments
    local cmd="cd \"${BASE_PATH}\" && PYTHONPATH=\"${BASE_PATH}\" python3 \"${BASE_PATH}/src/main.py\" --config \"${CONFIG_FILE}\" --log-dir \"${LOG_DIR}\" --log-level DEBUG"
    
    # If a specific source is requested, pass it as a generic --source argument
    if [ -n "${SOURCE_NAME}" ]; then
        cmd="${cmd} --source \"${SOURCE_NAME}\""
    fi
    
    if [ "${FORCE_DOWNLOAD}" = true ]; then
        log_info "Force download is enabled"
        cmd="${cmd} --force-download"
    fi
    
    # Run the Python application
    eval "${cmd}"
    
    if [ $? -ne 0 ]; then
        log_error "Source download failed"
        return 1
    fi
    
    log_info "Download process completed"
    return 0
}

# Main execution
function main() {
    log_info "Starting knowledge sources download process"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Run the download process
    check_dependencies
    create_directories
    download_source
    
    if [ $? -eq 0 ]; then
        log_info "Knowledge sources download completed successfully"
        exit 0
    else
        log_error "Knowledge sources download process failed"
        exit 1
    fi
}

# Call the main function with all arguments
main "$@"