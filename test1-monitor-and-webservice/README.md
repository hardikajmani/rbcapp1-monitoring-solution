# TEST1: Service Status Monitoring - Complete Documentation

## Overview

TEST1 implements a service status monitoring system that monitors the health of multiple Linux services (httpd, rabbitmq, postgresql) and stores their status in Elasticsearch via a REST API. The system generates JSON status files and provides endpoints to query service health in real-time.

If any service is DOWN, the overall rbcapp1 application state is DOWN. If all services are UP, the application is UP.

---

## Project Structure

```
test1-monitor-and-webservice/
├── docker compose.yml              # Service orchestration (API + Elasticsearch only)
├── Dockerfile                       # API container definition
├── run_all_tests.sh                # Automated test suite script
├── README.md                       # This documentation
│
├── api/
│   ├── app.py                      # Flask REST API (Port 5001)
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # API container build
│
├── monitor/
│   ├── monitor-services.py         # Service monitoring daemon
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Monitor container build
│
└── status-files/
    └── [Generated JSON status files stored here]
```

---

## System Requirements

Operating System: Linux (RHEL/CentOS/Ubuntu)
Docker: v20.10 or higher
Docker Compose: v1.29 or higher
Python: 3.8 or higher (for local development)
Memory: Minimum 4GB available
Disk Space: 2GB minimum for containers and data
Ports required: 5001 (API), 9200 (Elasticsearch)

---

## Installation and Setup

### Step 1: Prerequisites

Verify Docker installation:

```bash
docker --version
docker compose --version
```

### Step 2: Clone or Download Project

```bash
git clone https://github.com/your-org/test1-monitor-webservice.git
cd test1-monitor-webservice
```

### Step 3: Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit .env with your settings:

```bash
nano .env
```

Contents of .env:

```
API_HOST=0.0.0.0
API_PORT=5001
FLASK_ENV=production

ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_URL=http://elasticsearch:9200

MONITOR_INTERVAL=60
OUTPUT_DIR=/var/tmp/rbcapp1-status
LOG_DIR=/var/log/rbcapp1
```

---

## Docker Configuration and Build

### Docker Services Overview

The docker compose.yml defines two services:

1. api (Flask application on port 5001)
2. elasticsearch (Data persistence on port 9200)

Note: The monitor runs as a background service checking httpd, rabbitmq, and postgresql status on the host machine.

### Build Docker Images

```bash
docker compose build
```

Expected output:

```
Building api
Building elasticsearch
Successfully built [image_hash]
Successfully tagged test1-api:latest
```

### Start All Services

```bash
docker compose up -d
```

Verify services are running:

```bash
docker compose ps
```

Expected output:

```
CONTAINER ID   IMAGE              COMMAND                PORTS
abc123         test1-api          "python app.py"        0.0.0.0:5001->5001/tcp
def456         elasticsearch:7.17 "/bin/elasticsearch"   9200/tcp
```

### View Service Logs

All services:

```bash
docker compose logs -f
```

Specific service:

```bash
docker compose logs -f api
docker compose logs -f elasticsearch
```

---

## Code Logic Explained

### Monitor Service (monitor-services.py)

Purpose: Continuously monitors Linux services (httpd, rabbitmq, postgresql) and generates JSON status files

Key functionality:

1. ServiceMonitor class initializes monitoring configuration
2. Service status for each: UP or DOWN (configurable)
3. Generates JSON file for each service every 60 seconds
4. Files stored in /var/tmp/rbcapp1-status with naming pattern: {serviceName}-{status}-{timestamp}.json
5. Logs all activity to /var/log/rbcapp1/monitor.log

Sample JSON output:

```json
{
  "service_name": "httpd",
  "service_status": "UP",
  "host_name": "host1",
  "timestamp": "2026-01-30T10:57:26.123456Z",
  "@timestamp": "2026-01-30T10:57:26.123456Z"
}
```

Monitoring cycle:

1. Check status of each service (httpd, rabbitmq, postgresql)
2. Generate JSON status file for each service
3. Sleep for configured interval (default 60 seconds)
4. Repeat

### REST API (app.py)

Purpose: Accept JSON status payloads and provide health check endpoints

Port: 5001
Technology: Flask (Python web framework)

Supported services: httpd, rabbitmq, postgresql

Endpoints:

1. GET / (Root)
   Returns API information and available endpoints
   
   Example:
   ```bash
   curl http://localhost:5001/
   ```
   
   Response:
   ```json
   {
     "service": "rbcapp1-api",
     "version": "2.0",
     "description": "Service Status Management API",
     "endpoints": {
       "/health": "GET - API health check",
       "/healthcheck": "GET - Get all services status",
       "/healthcheck/<service>": "GET - Get specific service status",
       "/add": "POST - Add/Insert service status to Elasticsearch"
     },
     "supported_services": ["httpd", "rabbitmq", "postgresql"]
   }
   ```

2. GET /health
   Returns API health status
   Checks Elasticsearch connectivity
   
   Example:
   ```bash
   curl http://localhost:5001/health
   ```
   
   Success response (200):
   ```json
   {
     "status": "healthy"
   }
   ```
   
   Failure response (503):
   ```json
   {
     "status": "unhealthy"
   }
   ```

3. GET /healthcheck
   Returns status of all services
   Queries latest status from Elasticsearch for each service
   
   Example:
   ```bash
   curl http://localhost:5001/healthcheck
   ```
   
   Success response (200):
   ```json
   {
     "timestamp": "2026-01-30T10:57:26.123456Z",
     "services": {
       "httpd": {
         "status": "UP",
         "timestamp": "2026-01-30T10:57:00.000000Z"
       },
       "rabbitmq": {
         "status": "UP",
         "timestamp": "2026-01-30T10:57:00.000000Z"
       },
       "postgresql": {
         "status": "UP",
         "timestamp": "2026-01-30T10:57:00.000000Z"
       }
     }
   }
   ```

4. GET /healthcheck/{serviceName}
   Returns status of specific service
   Queries Elasticsearch for latest status
   
   Example:
   ```bash
   curl http://localhost:5001/healthcheck/httpd
   curl http://localhost:5001/healthcheck/rabbitmq
   curl http://localhost:5001/healthcheck/postgresql
   ```
   
   Success response (200):
   ```json
   {
     "service": "httpd",
     "status": "UP",
     "host_name": "host1",
     "timestamp": "2026-01-30T10:57:00.000000Z"
   }
   ```
   
   Not found response (200):
   ```json
   {
     "service": "httpd",
     "status": "NO_DATA",
     "message": "No status data found for httpd"
   }
   ```
   
   Error response (400):
   ```json
   {
     "error": "Unknown service: invalidservice",
     "available_services": ["httpd", "rabbitmq", "postgresql"]
   }
   ```

5. POST /add
   Accepts JSON status payload
   Stores in Elasticsearch with index naming: rbcapp1-{serviceName}
   
   Example:
   ```bash
   curl -X POST http://localhost:5001/add \
     -H "Content-Type: application/json" \
     -d '{
       "service_name": "httpd",
       "service_status": "UP",
       "host_name": "host1"
     }'
   ```
   
   Success response (201):
   ```json
   {
     "message": "Status for httpd successfully added to Elasticsearch",
     "service": "httpd",
     "status": "UP",
     "host_name": "host1",
     "timestamp": "2026-01-30T10:57:26.123456Z",
     "elasticsearch_id": "abc123def456"
   }
   ```
   
   Missing fields response (400):
   ```json
   {
     "error": "Missing required fields: ['service_status']",
     "required_fields": ["service_name", "service_status", "host_name"]
   }
   ```
   
   Invalid service response (400):
   ```json
   {
     "error": "Unknown service: invalidservice",
     "supported_services": ["httpd", "rabbitmq", "postgresql"]
   }
   ```
   
   Elasticsearch unavailable response (503):
   ```json
   {
     "error": "Elasticsearch unavailable",
     "status": "FAILED"
   }
   ```

API Logic Flow:

1. Request received at Flask endpoint
2. Validate request format (JSON for POST)
3. Extract and validate required fields
4. Check Elasticsearch connectivity
5. Query or insert data into appropriate index
6. Return response with status code

---

## Running the Complete Test Suite

### Make Test Script Executable

```bash
chmod +x run_all_tests.sh
```

### Run All Tests

```bash
./run_all_tests.sh
```

The test suite runs comprehensive tests and takes approximately 1-2 minutes.

Test sections executed:
- Service Verification
- API Endpoint Tests
- POST/Update Tests
- Error Handling Tests

### Success Output

```
════════════════════════════════════════
SECTION 1: SERVICE VERIFICATION
════════════════════════════════════════
→ Checking Elasticsearch health...
✓ Elasticsearch is healthy (status: yellow)
→ Checking API availability (port 5001)...
✓ API is responding on port 5001

[... more test results ...]

════════════════════════════════════════
TEST SUMMARY
════════════════════════════════════════
Total Tests: 12
Passed: 12
Failed: 0
════════════════════════════════════════
✓ ALL TESTS PASSED!
════════════════════════════════════════
```

### Failure Output

```
✗ API not responding on port 5001
✗ Elasticsearch unhealthy (status: error)

════════════════════════════════════════
TEST SUMMARY
════════════════════════════════════════
Total Tests: 12
Passed: 10
Failed: 2
════════════════════════════════════════
✗ SOME TESTS FAILED
════════════════════════════════════════
```

### Run Individual Tests Manually

Test Elasticsearch connectivity:

```bash
curl -s http://localhost:9200/_cluster/health | jq .
```

Test API is responding:

```bash
curl -s http://localhost:5001/health | jq .
```

Test all services status:

```bash
curl -s http://localhost:5001/healthcheck | jq .
```

Add status via POST:

```bash
curl -X POST http://localhost:5001/add \
  -H "Content-Type: application/json" \
  -d '{"service_name":"httpd","service_status":"UP","host_name":"host1"}'
```

View monitor logs:

```bash
docker compose logs monitor
```

Check generated JSON files:

```bash
ls -la /var/tmp/rbcapp1-status/
```

---

## Port Configuration

API Port: 5001
- Flask REST API listens on this port
- Change in .env: API_PORT=5001
- Change in docker compose.yml: ports: - "5001:5001"

Elasticsearch Port: 9200
- Elasticsearch cluster communication
- Internal to Docker network (not exposed to host by default)
- Access via: http://localhost:9200 (from host)

---

## Troubleshooting

### Issue 1: Port 5001 Already in Use

Error: "Address already in use"

Solution:

Check what is using port 5001:
```bash
lsof -i :5001
```

Kill the process:
```bash
kill -9 <PID>
```

Or use different port in .env:
```
API_PORT=5002
```

Then rebuild and restart:
```bash
docker compose down
docker compose build
docker compose up -d
```

### Issue 2: Services Not Starting

Error: "service unhealthy" or "exited with code 1"

Solution:

Check logs:
```bash
docker compose logs
```

Restart services:
```bash
docker compose restart
```

Full rebuild:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

Wait for initialization:
```bash
sleep 30
docker compose logs
```

### Issue 3: Elasticsearch Connection Failed

Error: "Failed to connect to Elasticsearch"

Solution:

Check Elasticsearch health:
```bash
curl -s http://localhost:9200/_cluster/health | jq .
```

View Elasticsearch logs:
```bash
docker compose logs elasticsearch
```

Restart Elasticsearch:
```bash
docker compose restart elasticsearch
sleep 30
./run_all_tests.sh
```

### Issue 4: API Returns 503 Service Unavailable

Error: "HTTP 503" or "Elasticsearch unavailable"

Solution:

Verify Elasticsearch is running and responding:
```bash
curl -s http://localhost:9200/_cluster/health
```

Check API logs:
```bash
docker compose logs api
```

Restart API:
```bash
docker compose restart api
```

Wait longer for services to initialize:
```bash
sleep 60
./run_all_tests.sh
```

### Issue 5: Test Script Fails

Error: "run_all_tests.sh: command not found" or "Permission denied"

Solution:

Make script executable:
```bash
chmod +x run_all_tests.sh
```

Run with bash explicitly:
```bash
bash run_all_tests.sh
```

### Issue 6: Monitor Not Generating JSON Files

Error: "Monitor has not generated any files"

Solution:

Check monitor container status:
```bash
docker compose ps monitor
```

View monitor logs:
```bash
docker compose logs monitor
```

Check output directory:
```bash
ls -la /var/tmp/rbcapp1-status/
```

Restart monitor:
```bash
docker compose restart monitor
sleep 30
ls -la /var/tmp/rbcapp1-status/
```

### General Debug Commands

View all running containers:
```bash
docker ps -a
```

View specific service logs:
```bash
docker compose logs api
docker compose logs elasticsearch
```

Execute command in container:
```bash
docker compose exec api bash
```

Check network connectivity:
```bash
docker network ls
```

Test API directly:
```bash
curl -v http://localhost:5001/health
```

Monitor resource usage:
```bash
docker stats
```

---

## Expected Behavior

### Startup Sequence

1. Docker containers are built (30-60 seconds)
2. Elasticsearch initializes (20-30 seconds)
3. Monitor starts and begins monitoring all services
4. API starts and listens on port 5001
5. Monitor generates first JSON status file after 60 seconds
6. All tests pass when services are ready (may take 1-2 minutes)

### Monitor Behavior

1. Runs continuously in background
2. Checks service status every 60 seconds
3. Generates JSON file for each service with timestamp
4. Files saved to /var/tmp/rbcapp1-status/
5. Logs activity to /var/log/rbcapp1/monitor.log
6. Configuration supports simulating service status (UP/DOWN) for all three services: httpd, rabbitmq, postgresql

### API Behavior

1. Accepts POST requests with JSON payloads
2. Stores data in Elasticsearch with index names: rbcapp1-httpd, rbcapp1-rabbitmq, rbcapp1-postgresql
3. Returns latest status on GET requests
4. Returns 400 for invalid requests
5. Returns 503 if Elasticsearch is unavailable
6. Logs all requests for debugging

### Service Status Rules

httpd status: UP or DOWN (configurable in monitor)
rabbitmq status: UP or DOWN (configurable in monitor)
postgresql status: UP or DOWN (configurable in monitor)

Overall rbcapp1 status:
- UP: All three services are UP
- DOWN: Any service is DOWN
- UNKNOWN: No status data available

---

## Verification Checklist

After startup, verify:

1. Docker containers running
   ```bash
   docker compose ps
   ```

2. Elasticsearch responding
   ```bash
   curl http://localhost:9200/_cluster/health
   ```

3. API is accessible
   ```bash
   curl http://localhost:5001/health
   ```

4. Monitor generating files
   ```bash
   ls /var/tmp/rbcapp1-status/
   ```

5. Test suite passes
   ```bash
   ./run_all_tests.sh
   ```

6. API can retrieve status
   ```bash
   curl http://localhost:5001/healthcheck
   ```


## Quick Reference Commands

Start services:
```bash
docker compose up -d
```

Stop services:
```bash
docker compose stop
```

View logs:
```bash
docker compose logs -f
```

Run tests:
```bash
./run_all_tests.sh
```

Check health:
```bash
curl http://localhost:5001/health
```

Check all service statuses:
```bash
curl http://localhost:5001/healthcheck
```

Clean up:
```bash
docker compose down
```

---

## Support

For issues or questions:

1. Check logs: docker compose logs -f
2. Verify port availability: lsof -i :5001
3. Test Elasticsearch: curl http://localhost:9200/_cluster/health
4. Test API: curl http://localhost:5001/health
5. Run full test suite: ./run_all_tests.sh

---