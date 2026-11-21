#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "PulseGuard Infrastructure Monitoring"
echo "Verification Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local name=$1
    local url=$2
    echo -n "Checking $name... "
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ UP${NC}"
        return 0
    else
        echo -e "${RED}✗ DOWN${NC}"
        return 1
    fi
}

check_prometheus_target() {
    local job=$1
    echo -n "Checking Prometheus target '$job'... "
    
    result=$(curl -sf "http://127.0.0.1:9090/api/v1/query?query=up{job=\"$job\"}" | grep -o '"value":\[.*,.*\]' | grep -o ',[0-9.]*' | tr -d ',')
    
    if [ "$result" == "1" ]; then
        echo -e "${GREEN}✓ UP${NC}"
        return 0
    else
        echo -e "${RED}✗ DOWN or NO DATA${NC}"
        return 1
    fi
}

query_prometheus() {
    local query=$1
    local label=$2
    echo -n "Query: $label... "
    
    result=$(curl -sf "http://127.0.0.1:9090/api/v1/query?query=$(echo "$query" | jq -sRr @uri)" 2>/dev/null || echo "")
    
    if [ -n "$result" ] && echo "$result" | grep -q '"status":"success"'; then
        value=$(echo "$result" | grep -o '"value":\[[^]]*\]' | head -1 | grep -o ',[^]]*' | tr -d ',[]" ')
        if [ -n "$value" ]; then
            echo -e "${GREEN}✓ $value${NC}"
            return 0
        fi
    fi
    
    echo -e "${YELLOW}⚠ NO DATA${NC}"
    return 1
}

echo "Step 1: Check Docker Services"
echo "------------------------------"
check_service "PulseGuard App" "http://127.0.0.1:8000/health"
check_service "Prometheus" "http://127.0.0.1:9090/-/healthy"
check_service "Node Exporter" "http://127.0.0.1:9100/metrics"
check_service "cAdvisor" "http://127.0.0.1:8080/metrics"
check_service "Grafana" "http://127.0.0.1:3000/api/health"
echo ""

echo "Step 2: Check Prometheus Targets"
echo "---------------------------------"
check_prometheus_target "pulseguard"
check_prometheus_target "node-exporter"
check_prometheus_target "cadvisor"
check_prometheus_target "prometheus"
echo ""

echo "Step 3: Query Infrastructure Metrics"
echo "-------------------------------------"
query_prometheus '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)' "CPU Usage %"
query_prometheus 'node_memory_MemTotal_bytes / 1024 / 1024 / 1024' "Total Memory (GB)"
query_prometheus '((node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes) * 100' "Memory Usage %"
query_prometheus 'node_filesystem_size_bytes{mountpoint="/"} / 1024 / 1024 / 1024' "Total Disk (GB)"
query_prometheus 'rate(container_cpu_usage_seconds_total{image!=""}[5m])' "Container CPU"
echo ""

echo "Step 4: Test Backend Monitoring API"
echo "------------------------------------"
echo -n "Fetching /api/v1/monitoring... "
response=$(curl -sf "http://127.0.0.1:8000/api/v1/monitoring" 2>/dev/null || echo "")

if [ -n "$response" ] && echo "$response" | grep -q '"status"'; then
    echo -e "${GREEN}✓ SUCCESS${NC}"
    
    # Parse key metrics
    cpu=$(echo "$response" | grep -o '"cpu_usage_percent":[0-9.]*' | cut -d':' -f2 || echo "N/A")
    mem=$(echo "$response" | grep -o '"memory_used_percent":[0-9.]*' | cut -d':' -f2 || echo "N/A")
    disk=$(echo "$response" | grep -o '"disk_used_percent":[0-9.]*' | cut -d':' -f2 || echo "N/A")
    
    echo "  CPU Usage: $cpu%"
    echo "  Memory Usage: $mem%"
    echo "  Disk Usage: $disk%"
else
    echo -e "${RED}✗ FAILED${NC}"
fi
echo ""

echo "Step 5: Run Python Tests"
echo "------------------------"
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short
else
    echo -e "${YELLOW}⚠ pytest not found, skipping tests${NC}"
fi
echo ""

echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
echo ""
echo "Access Points:"
echo "  - Dashboard: http://127.0.0.1:8000 (coming soon)"
echo "  - Prometheus: http://127.0.0.1:9090"
echo "  - Grafana: http://127.0.0.1:3000 (credentials configured locally)"
echo "  - Node Exporter: http://127.0.0.1:9100/metrics"
echo "  - cAdvisor: http://127.0.0.1:8080"
echo "  - Monitoring API: http://127.0.0.1:8000/api/v1/monitoring"
echo ""
