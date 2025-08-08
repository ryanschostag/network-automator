# Network Automation Audit Tool

This project automates configuration backups and compliance checks for network devices using Python.

## Features

- Connects to network devices via SSH (using Netmiko)
- Saves running configuration files
- Compares configs against a golden baseline
- Generates compliance reports (text format)
- Includes unit tests using pytest

## Project Structure

```text
.
├── configs/             # Backed-up device configurations
├── reports/             # Compliance reports
├── templates/
│   └── golden_config.txt # Baseline configuration
├── tests/
│   └── test_audit.py    # Unit tests
├── inventory.yaml       # Device inventory in YAML
├── logging.yaml
├── network_auditor.py
├── network_auditor.yaml
├── __main__.py          # Entry point for program
├── requirements.txt
└── README.md
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run the script
python .  # or python __main__.py

# Run unit tests
pytest tests/
```

## Sample Inventory File

```yaml
- hostname: core-sw1
  ip: 192.168.1.10
  device_type: cisco_ios
  username: admin
  password: admin123
```

## Configuration files

- logging.yaml: For logging configuration. Items must be compatible with logging.config.dictConfig.
- inventory.yaml: Configure the device inventory here.
- network_auditor.yaml: Configure the model-level configuration items here for network_auditor.py

## License

MIT License
