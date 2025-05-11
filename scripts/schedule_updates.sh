#!/usr/bin/env zsh
#
# schedule_updates.sh - Schedule periodic Wikipedia update checks
#

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
UPDATE_SCRIPT="./scripts/update_wikipedia.sh"
CRON_JOB="0 0 * * 0 cd $(pwd) && ${UPDATE_SCRIPT} >> logs/cron_wikipedia_update.log 2>&1"

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

function setup_cron() {
    log_info "Setting up cron job for weekly Wikipedia updates"
    
    # Check if crontab exists
    if ! command -v crontab &> /dev/null; then
        log_error "crontab command not found. Please install cron to continue."
        exit 1
    }
    
    # Remove any existing entries with the same script
    (crontab -l 2>/dev/null | grep -v "${UPDATE_SCRIPT}") | crontab -
    
    # Add the new cron job
    (crontab -l 2>/dev/null; echo "${CRON_JOB}") | crontab -
    
    log_info "Cron job installed successfully"
    log_info "Wikipedia will be checked for updates every Sunday at midnight"
}

# Main function
function main() {
    log_info "Setting up scheduled Wikipedia updates"
    
    # Make sure the update script exists and is executable
    if [ ! -f "${UPDATE_SCRIPT}" ]; then
        log_error "Update script not found: ${UPDATE_SCRIPT}"
        exit 1
    fi
    
    if [ ! -x "${UPDATE_SCRIPT}" ]; then
        log_info "Making update script executable"
        chmod +x "${UPDATE_SCRIPT}"
    fi
    
    # Set up the cron job
    setup_cron
    
    log_info "Schedule setup completed successfully"
}

# Call the main function
main
