# TEST2: rbcapp1 Monitoring Solution

Ansible playbook for monitoring rbcapp1 application across 3 RHEL servers.

## Files

- `inventory` - Defines hosts (host1, host2, host3) and groups (httpd, rabbitmq, postgresql)
- `ansible.cfg` - Ansible configuration
- `assignment.yml` - Main playbook with 3 actions

## Architecture

- **host1** (group: httpd) → runs `httpd` web server
- **host2** (group: rabbitmq) → runs `rabbitmq-server` message queue
- **host3** (group: postgresql) → runs `postgresql` database

## Three Actions

### 1. `action=verify_install`
Verifies services are installed on correct hosts. If missing, installs them.

```bash
ansible-playbook assignment.yml -e action=verify_install
```

**What it does:**
- On host1: Check and install `httpd`
- On host2: Check and install `rabbitmq-server`
- On host3: Check and install `postgresql-server`

### 2. `action=check-disk`
Monitors disk usage of root partition (`/`). Sends email alert if usage > 80%.

```bash
ansible-playbook assignment.yml -e action=check-disk
```

**What it does:**
- Runs `df -h /` on all hosts
- Parses disk usage percentage
- If > 80%, sends email alert

### 3. `action=check-status`
Queries rbcapp1 REST API to check overall application status.

```bash
ansible-playbook assignment.yml -e action=check-status
```

**What it does:**
- Calls `http://localhost:5001/healthcheck`
- Reports status: UP, DEGRADED, or UNREACHABLE

## Quick Start

### Setup

1. Update `inventory` with your actual host IPs:

```ini
[httpd]
host1 ansible_host=192.168.1.10 ansible_user=your_user ansible_ssh_private_key_file=~/.ssh/id_rsa

[rabbitmq]
host2 ansible_host=192.168.1.20 ansible_user=your_user ansible_ssh_private_key_file=~/.ssh/id_rsa

[postgresql]
host3 ansible_host=192.168.1.30 ansible_user=your_user ansible_ssh_private_key_file=~/.ssh/id_rsa

[app-servers:children]
httpd
rabbitmq
postgresql
```

2. Test connectivity:

```bash
ansible all -i inventory -m ping
```

### Run Actions

```bash
# Verify and install services
ansible-playbook assignment.yml -i inventory -e action=verify_install

# Check disk usage
ansible-playbook assignment.yml -i inventory -e action=check-disk

# Check rbcapp1 status
ansible-playbook assignment.yml -i inventory -e action=check-status
```

## Configuration

Email settings (in `assignment.yml`):

```yaml
email_to: "hardikajmani.public@gmail.com"
email_from: "gunnuhoneywedding2@gmail.com"
smtp_host: "smtp.gmail.com"
smtp_port: 587
smtp_username: "gunnuhoneywedding2@gmail.com"
smtp_password: "dgglxxuijtscqlmn"
```

REST API endpoint:

```yaml
service_rest_base_url: "http://localhost:5001"
```

## Key Features

 **Per-host service targeting** - Each host handles only its service (httpd on host1, etc.)  
 **Block-based conditionals** - Single `when: action == ...` per action block  
 **Production-ready** - Uses real rpm checks, yum install, and systemctl  
 **Email alerts** - Automatically sends disk usage warnings  
 **REST API integration** - Monitors application health status  
 **Handlers** - Automatically starts and enables services after install  

## Troubleshooting

**Package lock error during verify_install:**
- If you get a package lock error, run with sudo:
```bash
sudo ansible-playbook assignment.yml -e action=verify_install
```

**Disk check not sending email:**
- Verify SMTP credentials are correct
- Ensure disk usage is actually > 80%

**Health check shows UNREACHABLE:**
- Verify Flask app is running on host1:5001
- Check firewall allows traffic to port 5001