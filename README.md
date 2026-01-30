# rbcapp1 - Service Monitoring and Testing Suite

This repository contains a comprehensive solution for monitoring the rbcapp1 application and analyzing related data. The project is organized into separate test folders, each with its own documentation.

---

## Project Overview

rbcapp1 is a critical application that depends on three services:
- httpd (Apache Web Server)
- rabbitmq (Message Queue)
- postgresql (Database)

This suite provides tools to monitor these services, automate infrastructure management, and analyze related data.

---

## Repository Structure

```
rbcapp1/
├── test1-monitor-and-webservice/
│   ├── README.md                    # Complete TEST1 documentation
│   ├── docker compose.yml
│   ├── api/
│   ├── monitor/
│   └── run_all_tests.sh
│
├── test2-ansible-orchestration/
│   ├── README.md                    # Complete TEST2 documentation
│   ├── assignment.yml
│   ├── inventory
│   └── ansible.cfg
│
├── test3-data-analysis/
│   ├── README.md                    # Complete TEST3 documentation
│   ├── solution.py
│   ├── requirements.txt
│   └── assignment-data.csv
│
└── README.md                         # This file
```

---

## Quick Navigation

### TEST1: Service Status Monitoring with REST API and Elasticsearch

A real-time service monitoring system that tracks httpd, rabbitmq, and postgresql services.

**Key Features:**
- Python monitoring daemon that checks service status every 60 seconds
- Flask REST API on port 5001 for querying service status
- Elasticsearch for data persistence
- Docker orchestration with docker compose
- Comprehensive test suite with 12+ tests
- JSON status file generation

**Documentation:** See `TEST1/README.md`

**Quick Start:**
```bash
cd TEST1
docker compose build
docker compose up -d
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

### TEST2: Ansible Playbook for Infrastructure Management

Ansible automation for managing three Linux servers (host1, host2, host3) running httpd, rabbitmq, and postgresql.

**Key Features:**
- Service installation verification across multiple hosts
- Disk usage monitoring with email alerts
- REST API integration for application health checks
- Inventory-based host management
- Multiple playbook actions: verify_install, check-disk, check-status

**Documentation:** See `TEST2/README.md`

**Quick Start:**
```bash
cd TEST2
ansible --version
ansible-playbook assignment.yml -e action=verify_install
```

---

### TEST3: Real Estate Price Per Square Foot Analysis

Python data analysis tool for filtering properties sold below average price per square foot.

**Key Features:**
- CSV data processing
- Price per square foot calculation
- Statistical analysis
- Filtered results export
- Virtual environment setup included

**Documentation:** See `TEST3/README.md`

**Quick Start:**
```bash
cd TEST3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python solution.py assignment-data.csv
```

---

## System Requirements

### General Requirements
- Linux operating system (RHEL/CentOS/Ubuntu)
- Python 3.8 or higher
- Git for version control

### For TEST1
- Docker v20.10 or higher
- Docker Compose v1.29 or higher
- 4GB RAM minimum
- 2GB disk space

### For TEST2
- Ansible v2.9 or higher
- SSH access to target hosts
- Host inventory configuration

### For TEST3
- Python 3.8+
- pip package manager
- Virtual environment support

---

## Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/your-org/rbcapp1.git
   cd rbcapp1
   ```

2. Choose a test to run:
   ```bash
   # For test1 monitor-and-webservice
   cd test1-monitor-and-webservice
   
   # For test2 ansible-orchestration
   cd test2-ansible-orchestration
   
   # For test3 data-analysis
   cd test3-data-analysis
   ```

3. Follow the specific README in each test folder

---

## Common Commands

### TEST1 Commands
```bash
docker compose build              # Build images
docker compose up -d              # Start services
docker compose ps                 # View running services
docker compose logs -f            # View logs
./run_all_tests.sh                # Run test suite
curl http://localhost:5001/health # Check API health
docker compose down               # Stop services
```

### TEST2 Commands
```bash
ansible --version                 # Check Ansible version
ansible-playbook assignment.yml -e action=verify_install    # Install services
ansible-playbook assignment.yml -e action=check-disk        # Check disk usage
ansible-playbook assignment.yml -e action=check-status      # Check app status
ansible all -i inventory -m ping  # Test connectivity
```

### TEST3 Commands
```bash
python -m venv venv               # Create virtual environment
source venv/bin/activate          # Activate environment
pip install -r requirements.txt   # Install dependencies
python solution.py <input_csv>    # Run analysis
deactivate                        # Deactivate environment
```

---

## Documentation Index

Each test folder contains a detailed README with:

- Complete overview and functionality description
- System requirements and installation steps
- Docker/Ansible configuration details
- Code logic explanation
- API documentation with request/response examples
- Test suite information
- Troubleshooting guide
- Performance notes
- Quick reference commands

---

## Architecture

The three tests work together to provide:

1. **Real-time Monitoring (TEST1)** - Track service status every 60 seconds
2. **Automated Management (TEST2)** - Manage infrastructure across multiple servers
3. **Data Analysis (TEST3)** - Process and analyze related datasets

---

## Support and Troubleshooting

For issues specific to each test, refer to the troubleshooting section in the respective README:

- TEST1 troubleshooting: `TEST1/README.md#troubleshooting`
- TEST2 troubleshooting: `TEST2/README.md#troubleshooting`
- TEST3 troubleshooting: `TEST3/README.md#troubleshooting`

---

## Next Steps

1. Read the root README (this file) for overview
2. Navigate to your desired test folder
3. Read the test-specific README for detailed documentation
4. Follow the installation and setup steps
5. Run the test suite or deployment commands
6. Refer to troubleshooting if needed

---
