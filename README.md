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
│   └── config.yaml.bak
├── data/                 # Primary data storage
├── logs/                 # System logs
├── requirements.txt      # Project dependencies
├── scripts/              # Utility scripts
│   ├── schedule_updates.sh
│   └── update_wikipedia.sh
├── specs/                # Specification documents
│   ├── 0010-main.md
│   └── 0020-Wikipedia.md
└── src/                  # Source code
    ├── __init__.py
    ├── main.py           # Main application entry point
    ├── core/             # Core functionality
    │   ├── __init__.py
    │   ├── config.py
    │   └── logging_setup.py
    ├── interface/        # User interface components
    │   └── __init__.py
    ├── metrics/          # Metrics collection
    │   ├── __init__.py
    │   └── prometheus_metrics.py
    ├── sources/          # Data source connectors
    │   ├── __init__.py
    │   └── wikipedia/
    │       ├── __init__.py
    │       └── connector.py
    └── storage/          # Storage management
        └── __init__.py
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
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
- Update schedules
- Data sources
- Storage locations
- Logging levels
- Metrics collection settings

## Usage

### Starting the System

To start the knowledge archival system:

```bash
python src/main.py
```

### Manual Updates

You can trigger manual updates using the provided scripts:

```bash
# Update from Wikipedia sources
./scripts/update_wikipedia.sh

# Run scheduled updates
./scripts/schedule_updates.sh
```

## Features

### Automatic Updates
The system can automatically update its knowledge base from configured sources on a schedule.

### Metrics Collection
Prometheus metrics are integrated from the start as first-class citizens. Key metrics are collected to monitor system performance and usage through the metrics module.

### Comprehensive Logging
All system activities are logged according to configured logging levels in the `logs/` directory.

The logging system follows our standardized format:
- '>' for debug messages
- '>>' for info messages
- '>>>' for warning messages
- '>>>>' for error messages

Each log message is prefixed with the class and method name like: `>>>> ClassName::MethodName Error message`

### Data Storage
Knowledge is stored in the `data/` directory with regular backups to the `backup/` directory.

## Metrics

The system uses Prometheus for metrics collection as per our standards. Key metrics include:
- Update success/failure rates
- Storage usage
- Query performance
- System resource utilization

Metric collection is implemented in the `metrics/prometheus_metrics.py` module.

## Maintenance

### Backups
Regular backups are stored in the `backup/` directory.

### Updates
To update the system dependencies:

```bash
pip install -r requirements.txt --upgrade
```

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

## Troubleshooting

Check the logs in the `logs/` directory for detailed information about any issues.

Common problems:
1. Connection failures to sources (e.g., Wikipedia API)
2. Storage space limitations
3. Configuration errors

## Design Principles

This system follows SOLID principles, with particular emphasis on:
1. Single Responsibility Principle - Each module has one responsibility
2. Interface Segregation - Interfaces are client-specific
3. Low coupling between modules
4. High cohesion within modules

Design patterns are used only where they add clear value to the codebase.

## Additional Documentation

Please refer to the specification documents in the `specs/` directory for details on the system architecture and design.