# Knowledge Archival System

A comprehensive system for offline knowledge storage and management with automatic updates from various sources.

## System Overview

This knowledge archival system is designed to collect, store, and manage information from various sources (primarily Wikipedia) for offline access. The system follows SOLID principles with high cohesion and low coupling between modules, making components replaceable and maintainable.

## Directory Structure

```
knowledge/
├── backup/               # Backup storage for archived data
├── config/               # Configuration files
│   ├── config.json
│   ├── config.yaml
├── container/            # Container-related files
│   ├── container_schedule_updates.sh
│   ├── container_update_wikipedia.sh
│   ├── Dockerfile
│   └── run_knowledge_container.sh
├── data/                 # Primary data storage
│   └── wikipedia/        # Wikipedia ZIM files
├── logs/                 # System logs
├── requirements.txt      # Project dependencies
├── scripts/              # Utility scripts
│   ├── schedule_updates.sh
│   └── update_wikipedia.sh
├── specs/                # Specification documents
└── src/                  # Source code
    ├── main.py           # Main application entry point
    ├── core/             # Core functionality
    │   ├── application_manager.py  # Application lifecycle manager
    │   ├── command_executor.py     # Command execution
    │   ├── config.py               # Configuration management
    │   └── logging_setup.py        # Logging configuration
    ├── metrics/          # Metrics collection
    │   └── prometheus_metrics.py
    └── sources/          # Data source connectors
        ├── interfaces/   # Source connector interfaces
        │   ├── backup_manager.py
        │   ├── download_manager.py
        │   ├── metadata_manager.py
        │   ├── source_connector.py
        │   └── verification_service.py
        └── wikipedia/    # Wikipedia-specific implementations
            ├── connector.py
            ├── wikipedia_factory.py
            └── implementations/
                ├── wikipedia_backup_manager.py
                ├── wikipedia_download_manager.py
                ├── wikipedia_metadata_manager.py
                └── wikipedia_verification_service.py
```

## Architecture

The system is designed following SOLID principles:

1. **Single Responsibility Principle (SRP)**: Each class has a single responsibility
2. **Open/Closed Principle (OCP)**: Components are open for extension but closed for modification
3. **Liskov Substitution Principle (LSP)**: Interface implementations can be substituted without affecting behavior
4. **Interface Segregation Principle (ISP)**: Clients only depend on interfaces they use
5. **Dependency Inversion Principle (DIP)**: High-level modules depend on abstractions, not implementations

### Key Components

- **ApplicationManager**: Manages application lifecycle (initialization, configuration, command routing)
- **CommandExecutor**: Executes specific commands requested by the user
- **Source Connectors**: Interface-based design with specific implementations for each knowledge source
  - **ISourceConnector**: Base interface for all knowledge source connectors
  - **IMetadataManager**: Interface for metadata operations
  - **IDownloadManager**: Interface for downloading operations
  - **IBackupManager**: Interface for backup operations
  - **IVerificationService**: Interface for verification operations

Each knowledge source implements these interfaces with source-specific logic, allowing for multiple knowledge sources with consistent behavior.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/knowledge.git
   cd knowledge
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

All dependencies are managed through the requirements.txt file. Never install individual packages using pip directly.

## Configuration

The system can be configured using the files in the `config/` directory:

- `config.yaml`: Main configuration file (YAML format)
- `config.json`: Alternative configuration file (JSON format)

Configuration parameters include:
- Wikipedia ZIM file pattern and source URL
- Storage and backup paths
- Logging settings
- Metrics collection settings (port, path)

Example configuration (JSON):
```json
{
  "wikipedia": {
    "zim_source_url": "https://download.kiwix.org/zim/wikipedia/",
    "file_pattern": "wikipedia_en_all_maxi_[0-9]{4}-[0-9]{2}.zim",
    "storage_path": "/path/to/knowledge/data/wikipedia",
    "backup_path": "/path/to/knowledge/backup/wikipedia",
    "check_interval": 30,
    "max_backups": 3
  },
  "metrics": {
    "enabled": true,
    "port": 9091,
    "path": "/metrics"
  }
}
```

## Usage

### Starting the System

To start the knowledge archival system with default settings:

```bash
python src/main.py --config config/config.yaml --update-wikipedia
```

### Command-line Arguments

The application supports the following command-line arguments:

```
--config PATH             Path to configuration file
--log-dir PATH            Directory for log files
--log-level LEVEL         Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
--update-wikipedia        Check for Wikipedia updates and download if available
--force-download          Force download even if the file exists or is not newer
```

### Manual Updates

You can trigger manual updates using the provided scripts:

```bash
# Regular update (only newer versions)
./scripts/update_wikipedia.sh

# Force update (even if you have the latest version)
./scripts/update_wikipedia.sh --force

# Schedule automatic updates
./scripts/schedule_updates.sh
```

## Container Support

The system is designed to run in a container environment using Podman (preferred over Docker). The container setup provides isolated execution with data persistence through volumes.

### Container Structure

```
container/
├── Dockerfile                     # Container definition
├── run_knowledge_container.sh     # Script to run the container
├── container_update_wikipedia.sh  # Script to trigger Wikipedia updates
└── container_schedule_updates.sh  # Script for scheduled updates
```

### Dockerfile Details

The Dockerfile includes:
- Python 3.13 slim base image
- Required system dependencies including libzim-dev
- Volume mounts for data, logs, backups, and config
- Exposed port 9091 for Prometheus metrics
- Proper environment variable configuration
- Standardized logging format matching our Python standards

### Container Management

To work with the containerized application:

```bash
# Build the container
podman build -t knowledge-project:latest -f container/Dockerfile .

# Run the container with default settings
./container/run_knowledge_container.sh

# Run with custom metrics port
./container/run_knowledge_container.sh --metrics-port 9095

# View container logs
podman logs knowledge-container

# Stop the container
podman stop knowledge-container
```

The `run_knowledge_container.sh` script provides:
- Automatic detection of existing containers
- Interactive prompts for stopping/removing existing containers
- Volume mounting for persistent data
- Metrics port configuration
- Comprehensive error handling and logging
- Dependency verification

### Container Update Scripts

```bash
# Trigger a Wikipedia update in the container
./container/container_update_wikipedia.sh

# Force an update regardless of version
./container/container_update_wikipedia.sh --force

# Set up scheduled updates in the container
./container/container_schedule_updates.sh
```

## Scripts

The system includes several utility scripts to manage operations:

### Local Scripts

```
scripts/
├── update_wikipedia.sh    # Updates Wikipedia data
└── schedule_updates.sh    # Sets up scheduled updates
```

These scripts follow our Shell Script Standards:
- Clear color-coded log messages (green for info, yellow for warnings, red for errors)
- Consistent logging format matching Python standards ('>>' for info, etc.)
- Proper error handling
- Command-line argument parsing
- Small, focused functions

### Usage Examples

```bash
# Update Wikipedia data
./scripts/update_wikipedia.sh

# Force download even if you have the latest version
./scripts/update_wikipedia.sh --force

# Schedule automatic updates (creates a cron job)
./scripts/schedule_updates.sh --interval daily

# Remove scheduled updates
./scripts/schedule_updates.sh --remove
```

## Features

### Extensible Architecture
The system uses interface-based design, making it easy to add new knowledge sources beyond Wikipedia:

1. Implement the required interfaces for your new knowledge source
2. Add the source to the CommandExecutor's update_knowledge_source method
3. Update the command-line arguments to include the new source

### Automatic Updates
The system can automatically update its knowledge base from configured sources on a schedule.

### Version Tracking and Metadata
- Tracks all downloaded versions in a metadata file
- Only downloads newer versions when they become available
- Supports forced downloads via command-line flag
- Maintains version history with timestamps and file sizes

### Metrics Collection
Prometheus metrics are integrated from the start as first-class citizens. Key metrics are collected to monitor system performance and usage through the metrics module.

Available metrics include:
- `wikipedia_check_count`: Number of times Wikipedia update was checked
- `wikipedia_download_count`: Number of Wikipedia downloads
- `wikipedia_last_download_size_bytes`: Size of last Wikipedia download in bytes
- `wikipedia_last_download_time_seconds`: Time taken for last Wikipedia download in seconds
- `wikipedia_download_failures`: Number of Wikipedia download failures

### Comprehensive Logging
All system activities are logged according to configured logging levels in the `logs/` directory.

The logging system follows our standardized format:
- '>' for debug messages
- '>>' for info messages
- '>>>' for warning messages
- '>>>>' for error messages

Each log message is prefixed with the class and method name like: `>>>> ClassName::MethodName Error message`

### Data Storage
Knowledge is stored in the `data/` directory with regular backups to the `backup/` directory. The system:
- Maintains a configurable number of backups
- Creates timestamped backups before updates
- Automatically cleans up old backups

## Metrics

The system exposes Prometheus metrics on port 9091 (configurable). The metrics can be accessed at:
```
http://localhost:9091/metrics
```

## Wikipedia ZIM Files

This system uses ZIM files from the Kiwix project for Wikipedia content. These files follow a specific naming pattern:
```
wikipedia_en_all_maxi_YYYY-MM.zim
```

The system will automatically:
1. Check for new versions on the Kiwix server
2. Compare with locally downloaded versions
3. Download only if a newer version is available
4. Maintain metadata about all downloaded versions

## Troubleshooting

### Common Issues

1. **404 Errors**: Check that the file pattern in your configuration matches what's available on the Kiwix server.
2. **Address Already in Use**: If the Prometheus server fails to start with "Address already in use" errors, change the metrics port in the configuration file.
3. **Space Issues**: The full Wikipedia ZIM files are very large (>100GB). Ensure you have sufficient disk space.

### Checking Status

To check the status of the system, examine the log files in the `logs/` directory. The JSON metadata file in `data/wikipedia/downloads_metadata.json` provides information about downloaded versions.

## Development Standards

### Python Standards
- No global variables
- SOLID principles are followed
- Logging is used instead of print statements
- Standard log format: '>' for debug, '>>' for info, '>>>' for warn, '>>>>' for error followed by ClassName::MethodName
- PEP8 formatting
- Meaningful variable names with limited scope
- Modular design with low coupling and high cohesion
- Approved libraries: pydantic, dataclasses, pandas, numpy

### Shell Script Standards
- Clear info, warn, and error messages with semaphore colors
- Small, focused functions
- Consistent message formatting aligned with Python logging

### Environment
- Linux operating system
- ZSH shell
- PODMAN for containerization (preferred over Docker)
- Prometheus for metrics
- Promtail and Loki for log collection

## Extending the System

To add a new knowledge source (e.g., Project Gutenberg):

1. Create a new directory structure in `src/sources/gutenberg/`
2. Implement the interfaces defined in `src/sources/interfaces/`
3. Create a factory class similar to `WikipediaFactory`
4. Update the `CommandExecutor.update_knowledge_source()` method to handle the new source type
5. Add command-line arguments to `main.py` for the new source

## Additional Documentation

Please refer to the specification documents in the `specs/` directory for details on the system architecture and design.