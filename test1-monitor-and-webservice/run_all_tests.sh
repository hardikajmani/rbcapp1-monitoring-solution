#!/bin/bash

# TEST1: Comprehensive Test Suite
# Runs all tests and displays results
# Port 5001

set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0
TOTAL=0

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED++))
    ((TOTAL++))
}

print_fail() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED++))
    ((TOTAL++))
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================================================
# SECTION 1: SERVICE VERIFICATION
# ============================================================================

section_verify_services() {
    print_header "SECTION 1: SERVICE VERIFICATION"
    
    print_test "Checking Elasticsearch health..."
    ES_STATUS=$(curl -s http://localhost:9200/_cluster/health | jq -r '.status' 2>/dev/null || echo "error")
    if [[ "$ES_STATUS" == "green" || "$ES_STATUS" == "yellow" ]]; then
        print_pass "Elasticsearch is healthy (status: $ES_STATUS)"
    else
        print_fail "Elasticsearch unhealthy (status: $ES_STATUS)"
    fi
    
    print_test "Checking API availability (port 5001)..."
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        print_pass "API is responding on port 5001"
    else
        print_fail "API not responding on port 5001"
    fi
    
    print_test "Checking monitor logs..."
    if docker compose logs monitor | grep -q "Monitor cycle complete"; then
        print_pass "Monitor has generated status updates"
    else
        print_fail "Monitor not generating updates"
    fi
}

# ============================================================================
# SECTION 2: API ENDPOINT TESTS (PORT 5001)
# ============================================================================

section_api_endpoints() {
    print_header "SECTION 2: API ENDPOINT TESTS"
    
    # Test 1: Root endpoint
    print_test "Test: GET / (API info)"
    RESPONSE=$(curl -s http://localhost:5001/)
    if echo "$RESPONSE" | grep -q "rbcapp1-api"; then
        print_pass "Root endpoint returns API info"
    else
        print_fail "Root endpoint failed"
    fi
    
    # Test 2: Health endpoint
    print_test "Test: GET /health"
    HEALTH=$(curl -s http://localhost:5001/health | jq -r '.status' 2>/dev/null)
    if [[ "$HEALTH" == "healthy" ]]; then
        print_pass "Health check returns healthy"
    else
        print_fail "Health check failed (status: $HEALTH)"
    fi
    
    # Test 3: Healthcheck all services
    print_test "Test: GET /healthcheck (all services)"
    RESPONSE=$(curl -s http://localhost:5001/healthcheck)
    if echo "$RESPONSE" | jq '.services' > /dev/null 2>&1; then
        print_pass "All services status retrieved"
    else
        print_fail "All services status failed"
    fi
    
    # Test 4: Healthcheck single service (httpd)
    print_test "Test: GET /healthcheck/httpd"
    HTTPD=$(curl -s http://localhost:5001/healthcheck/httpd | jq -r '.status' 2>/dev/null)
    if [[ -n "$HTTPD" && "$HTTPD" != "null" ]]; then
        print_pass "httpd status retrieved (status: $HTTPD)"
    else
        print_fail "httpd status failed"
    fi
    
    # Test 5: Healthcheck rabbitmq
    print_test "Test: GET /healthcheck/rabbitmq"
    RABBITMQ=$(curl -s http://localhost:5001/healthcheck/rabbitmq | jq -r '.status' 2>/dev/null)
    if [[ -n "$RABBITMQ" && "$RABBITMQ" != "null" ]]; then
        print_pass "rabbitmq status retrieved (status: $RABBITMQ)"
    else
        print_fail "rabbitmq status failed"
    fi
    
    # Test 6: Healthcheck postgresql
    print_test "Test: GET /healthcheck/postgresql"
    POSTGRESQL=$(curl -s http://localhost:5001/healthcheck/postgresql | jq -r '.status' 2>/dev/null)
    if [[ -n "$POSTGRESQL" && "$POSTGRESQL" != "null" ]]; then
        print_pass "postgresql status retrieved (status: $POSTGRESQL)"
    else
        print_fail "postgresql status failed"
    fi
}

# ============================================================================
# SECTION 3: POST/UPDATE TESTS
# ============================================================================

section_post_updates() {
    print_header "SECTION 3: POST/UPDATE TESTS"
    
    # Test 1: Update single service
    print_test "Test: POST /add (update httpd to UP)"
    RESPONSE=$(curl -s -X POST "http://localhost:5001/add" \
        -H "Content-Type: application/json" \
        -d '{"service_name":"httpd","service_status":"UP","host_name":"test"}')
    
    if echo "$RESPONSE" | jq '.elasticsearch_id' > /dev/null 2>&1; then
        print_pass "httpd updated successfully"
        sleep 1
    else
        print_fail "httpd update failed"
    fi
    
    # Test 2: Verify update
    print_test "Test: Verify httpd status changed"
    HTTPD_STATUS=$(curl -s http://localhost:5001/healthcheck/httpd | jq -r '.status' 2>/dev/null)
    if [[ "$HTTPD_STATUS" == "UP" ]]; then
        print_pass "httpd status changed to UP"
    else
        print_fail "httpd status not changed (status: $HTTPD_STATUS)"
    fi
    
    # Test 3: Update rabbitmq
    print_test "Test: POST /add (update rabbitmq to UP)"
    RESPONSE=$(curl -s -X POST "http://localhost:5001/add" \
        -H "Content-Type: application/json" \
        -d '{"service_name":"rabbitmq","service_status":"UP","host_name":"test"}')
    
    if echo "$RESPONSE" | jq '.elasticsearch_id' > /dev/null 2>&1; then
        print_pass "rabbitmq updated successfully"
        sleep 1
    else
        print_fail "rabbitmq update failed"
    fi
    
    # Test 4: Update postgresql
    print_test "Test: POST /add (update postgresql to UP)"
    RESPONSE=$(curl -s -X POST "http://localhost:5001/add" \
        -H "Content-Type: application/json" \
        -d '{"service_name":"postgresql","service_status":"UP","host_name":"test"}')
    
    if echo "$RESPONSE" | jq '.elasticsearch_id' > /dev/null 2>&1; then
        print_pass "postgresql updated successfully"
        sleep 1
    else
        print_fail "postgresql update failed"
    fi
}

# ============================================================================
# SECTION 4: ERROR HANDLING TESTS
# ============================================================================

section_error_handling() {
    print_header "SECTION 4: ERROR HANDLING TESTS"
    
    # Test 1: Invalid service name in GET
    print_test "Test: Invalid service name (GET)"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/healthcheck/invalid)
    if [[ "$HTTP_CODE" == "400" ]]; then
        print_pass "Invalid service returns 400"
    else
        print_fail "Invalid service should return 400 (got $HTTP_CODE)"
    fi
    
    # Test 2: Invalid service name in POST
    print_test "Test: Invalid service name (POST)"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:5001/add" \
        -H "Content-Type: application/json" \
        -d '{"service_name":"invalid","service_status":"UP","host_name":"test"}')
    if [[ "$HTTP_CODE" == "400" ]]; then
        print_pass "Invalid service POST returns 400"
    else
        print_fail "Invalid service POST should return 400 (got $HTTP_CODE)"
    fi
    
    # Test 3: Missing required field
    print_test "Test: Missing required field"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:5001/add" \
        -H "Content-Type: application/json" \
        -d '{"service_name":"httpd","host_name":"test"}')
    if [[ "$HTTP_CODE" == "400" ]]; then
        print_pass "Missing field returns 400"
    else
        print_fail "Missing field should return 400 (got $HTTP_CODE)"
    fi
    
    # Test 4: Non-JSON request
    print_test "Test: Non-JSON content"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:5001/add" \
        -H "Content-Type: text/plain" \
        -d 'not json')
    if [[ "$HTTP_CODE" == "400" ]]; then
        print_pass "Non-JSON request returns 400"
    else
        print_fail "Non-JSON request should return 400 (got $HTTP_CODE)"
    fi
    
    # Test 5: 404 for non-existent endpoint
    print_test "Test: Non-existent endpoint"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/nonexistent)
    if [[ "$HTTP_CODE" == "404" ]]; then
        print_pass "Non-existent endpoint returns 404"
    else
        print_fail "Non-existent endpoint should return 404 (got $HTTP_CODE)"
    fi
}

# ============================================================================
# SECTION 5: MONITOR TESTS
# ============================================================================

section_monitor_tests() {
    print_header "SECTION 5: MONITOR TESTS"
    
    print_test "Checking monitor container status..."
    if docker compose ps monitor | grep -q "Up"; then
        print_pass "Monitor container is running"
    else
        print_fail "Monitor container not running"
    fi
    
    print_test "Checking generated JSON files..."
    FILE_COUNT=$(docker compose exec monitor bash -c "ls /var/tmp/rbcapp1-status/*.json 2>/dev/null | wc -l")
    if [[ $FILE_COUNT -gt 0 ]]; then
        print_pass "Monitor has generated $FILE_COUNT JSON files"
    else
        print_fail "Monitor has not generated any files"
    fi
    
    print_test "Checking monitor log..."
    if docker compose logs monitor | grep -q "Monitor cycle complete"; then
        print_pass "Monitor cycles are executing"
    else
        print_fail "Monitor cycles not found in logs"
    fi
}

# ============================================================================
# SECTION 6: ELASTICSEARCH TESTS
# ============================================================================

section_elasticsearch_tests() {
    print_header "SECTION 6: ELASTICSEARCH TESTS"
    
    print_test "Checking Elasticsearch indices..."
    INDICES=$(curl -s http://localhost:9200/_cat/indices | awk '{print $3}' | grep rbcapp1)
    if [[ -n "$INDICES" ]]; then
        print_pass "Elasticsearch indices found:"
        echo "$INDICES" | sed 's/^/    /'
    else
        print_fail "No Elasticsearch indices found"
    fi
    
    print_test "Checking httpd index..."
    DOC_COUNT=$(curl -s "http://localhost:9200/rbcapp1-httpd/_count" | jq '.count' 2>/dev/null || echo "0")
    if [[ $DOC_COUNT -gt 0 ]]; then
        print_pass "httpd index has $DOC_COUNT documents"
    else
        print_fail "httpd index empty or missing"
    fi
    
    print_test "Checking rabbitmq index..."
    DOC_COUNT=$(curl -s "http://localhost:9200/rbcapp1-rabbitmq/_count" | jq '.count' 2>/dev/null || echo "0")
    if [[ $DOC_COUNT -gt 0 ]]; then
        print_pass "rabbitmq index has $DOC_COUNT documents"
    else
        print_fail "rabbitmq index empty or missing"
    fi
    
    print_test "Checking postgresql index..."
    DOC_COUNT=$(curl -s "http://localhost:9200/rbcapp1-postgresql/_count" | jq '.count' 2>/dev/null || echo "0")
    if [[ $DOC_COUNT -gt 0 ]]; then
        print_pass "postgresql index has $DOC_COUNT documents"
    else
        print_fail "postgresql index empty or missing"
    fi
}

# ============================================================================
# SECTION 7: INTEGRATION TESTS
# ============================================================================

section_integration_tests() {
    print_header "SECTION 7: INTEGRATION TESTS"
    
    print_test "Test: Complete flow - Update all services to DOWN"
    
    for service in httpd rabbitmq postgresql; do
        curl -s -X POST "http://localhost:5001/add" \
            -H "Content-Type: application/json" \
            -d "{\"service_name\":\"$service\",\"service_status\":\"DOWN\",\"host_name\":\"test\"}" > /dev/null
    done
    sleep 1
    
    # Verify all are down
    STATUSES=$(curl -s http://localhost:5001/healthcheck | jq '.services[] | .status' | sort | uniq)
    if [[ "$STATUSES" == '"DOWN"' ]]; then
        print_pass "All services successfully set to DOWN"
    else
        print_fail "Not all services are DOWN: $STATUSES"
    fi
    
    print_test "Test: Complete flow - Recovery (update all to UP)"
    
    for service in httpd rabbitmq postgresql; do
        curl -s -X POST "http://localhost:5001/add" \
            -H "Content-Type: application/json" \
            -d "{\"service_name\":\"$service\",\"service_status\":\"UP\",\"host_name\":\"test\"}" > /dev/null
    done
    sleep 1
    
    # Verify all are up
    STATUSES=$(curl -s http://localhost:5001/healthcheck | jq '.services[] | .status' | sort | uniq)
    if [[ "$STATUSES" == '"UP"' ]]; then
        print_pass "All services successfully recovered to UP"
    else
        print_fail "Not all services are UP: $STATUSES"
    fi
    
    print_test "Test: Partial outage (httpd and postgresql DOWN, rabbitmq UP)"
    
    curl -s -X POST "http://localhost:5001/add" \
        -H "Content-Type: application/json" \
        -d '{"service_name":"httpd","service_status":"DOWN","host_name":"test"}' > /dev/null
    
    curl -s -X POST "http://localhost:5001/add" \
        -H "Content-Type: application/json" \
        -d '{"service_name":"postgresql","service_status":"DOWN","host_name":"test"}' > /dev/null
    
    sleep 1
    
    HTTPD=$(curl -s http://localhost:5001/healthcheck/httpd | jq -r '.status')
    RABBITMQ=$(curl -s http://localhost:5001/healthcheck/rabbitmq | jq -r '.status')
    POSTGRESQL=$(curl -s http://localhost:5001/healthcheck/postgresql | jq -r '.status')
    
    if [[ "$HTTPD" == "DOWN" && "$RABBITMQ" == "UP" && "$POSTGRESQL" == "DOWN" ]]; then
        print_pass "Partial outage scenario working correctly"
    else
        print_fail "Partial outage scenario failed (httpd:$HTTPD, rabbitmq:$RABBITMQ, postgresql:$POSTGRESQL)"
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    clear
    
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   TEST1: COMPREHENSIVE TEST SUITE      ║"
    echo "║   Service Monitor & REST API           ║"
    echo "║   Port: 5001                           ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_info "Starting tests at $(date)"
    print_info "System: $(uname -s) $(uname -m)"
    
    # Run all sections - NO DOCKER STARTUP
    section_verify_services
    section_api_endpoints
    section_post_updates
    section_error_handling
    section_monitor_tests
    section_elasticsearch_tests
    section_integration_tests
    
    # Summary
    print_header "TEST SUMMARY"
    echo -e "Total Tests: ${BLUE}$TOTAL${NC}"
    echo -e "Passed: ${GREEN}$PASSED${NC}"
    echo -e "Failed: ${RED}$FAILED${NC}"
    
    if [[ $FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}════════════════════════════════════════${NC}"
        echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
        echo -e "${GREEN}════════════════════════════════════════${NC}\n"
        exit 0
    else
        echo -e "\n${RED}════════════════════════════════════════${NC}"
        echo -e "${RED}✗ SOME TESTS FAILED${NC}"
        echo -e "${RED}════════════════════════════════════════${NC}\n"
        exit 1
    fi
}

# Run main
main "$@"
