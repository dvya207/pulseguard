#!/bin/bash
# PulseGuard Quick Demo Test Script

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   PulseGuard Interactive Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

step=1

print_step() {
    echo ""
    echo -e "${BLUE}━━━ Step $step: $1 ━━━${NC}"
    ((step++))
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

pause() {
    echo ""
    read -p "Press Enter to continue..."
}

# Step 1: Check Services
print_step "Checking all services are running"
print_info "Running: docker compose ps"
docker compose ps
pause

# Step 2: Test Health Endpoint
print_step "Testing PulseGuard Health Endpoint"
print_info "GET http://localhost:8000/health"
health_response=$(curl -s http://localhost:8000/health)
echo "$health_response" | jq .
if echo "$health_response" | grep -q "healthy"; then
    print_success "PulseGuard is healthy!"
else
    print_error "PulseGuard is not healthy"
fi
pause

# Step 3: Get Current Metrics
print_step "Fetching real-time infrastructure metrics"
print_info "GET http://localhost:8000/api/v1/monitoring"
metrics=$(curl -s http://localhost:8000/api/v1/monitoring)
echo "$metrics" | jq .

cpu=$(echo "$metrics" | jq -r '.metrics.cpu_usage_percent')
memory=$(echo "$metrics" | jq -r '.metrics.memory_used_percent')
disk=$(echo "$metrics" | jq -r '.metrics.disk_used_percent')

echo ""
print_success "Current CPU Usage: $cpu%"
print_success "Current Memory Usage: $memory%"
print_success "Current Disk Usage: $disk%"
pause

# Step 4: Check Prometheus Targets
print_step "Checking Prometheus is scraping all targets"
print_info "Querying Prometheus targets..."
targets=$(curl -s http://localhost:9090/api/v1/targets)
up_count=$(echo "$targets" | grep -o '"health":"up"' | wc -l)
print_success "Found $up_count targets in UP state"
pause

# Step 5: Test Dashboard
print_step "Testing Dashboard (Frontend)"
print_info "GET http://localhost:5173/"
dashboard_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
if [ "$dashboard_status" = "200" ]; then
    print_success "Dashboard is accessible at http://localhost:5173"
    print_info "Open in browser: http://localhost:5173"
else
    print_error "Dashboard returned HTTP $dashboard_status"
fi
pause

# Step 6: Simulate Failure
print_step "🔥 DEMO: Simulating Application Failure"
print_info "This will make the health endpoint return 500 errors"
echo ""
read -p "Do you want to simulate a failure? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Enabling failure simulation..."
    curl -X POST http://localhost:8000/api/v1/simulate-failure \
      -H "Content-Type: application/json" \
      -d '{"enabled": true}' | jq .
    
    echo ""
    print_error "Health endpoint is now failing!"
    print_info "Testing health endpoint..."
    curl -s http://localhost:8000/health | jq .
    
    echo ""
    print_info "Check the dashboard at http://localhost:5173"
    print_info "You should see 'CONNECTION ERROR' in red"
    pause
    
    # Step 7: Run Self-Healing
    print_step "🔧 DEMO: Running Self-Healing Script"
    print_info "This will detect the failure and attempt recovery..."
    ./self_heal.sh
    
    echo ""
    print_info "Self-healing completed!"
    print_info "Testing health endpoint again..."
    curl -s http://localhost:8000/health | jq .
    
    echo ""
    print_success "Application should be healthy again!"
    print_info "Check updated metrics..."
    curl -s http://localhost:8000/api/v1/monitoring | jq '.metrics | {recovery_attempts, successful_recoveries, rollbacks}'
else
    print_info "Skipping failure simulation"
fi

pause

# Step 8: Check Self-Healing Metrics File
print_step "Checking Self-Healing Metrics"
print_info "Reading: self_heal/metrics.json"
cat self_heal/metrics.json | jq .
pause

# Step 9: Summary
print_step "Demo Complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   🎯 Access Points"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard:      http://localhost:5173"
echo "🏥 Health Check:   http://localhost:8000/health"
echo "📈 Monitoring API: http://localhost:8000/api/v1/monitoring"
echo "📚 API Docs:       http://localhost:8000/docs"
echo "🔍 Prometheus:     http://localhost:9090"
echo "📉 Grafana:        http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "All demos completed successfully!"
echo ""
echo "💡 Tips:"
echo "  • Open the dashboard in your browser"
echo "  • Watch metrics update every 10 seconds"
echo "  • Try simulating failures and watch auto-recovery"
echo "  • Explore Grafana dashboards for historical data"
echo ""
