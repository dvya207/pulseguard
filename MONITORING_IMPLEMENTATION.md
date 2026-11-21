# PulseGuard Infrastructure Monitoring Implementation

## Overview

This document details the implementation of real infrastructure monitoring for PulseGuard, including CPU, RAM, disk, and Docker container metrics.

## Changes Made

### 1. Docker Compose Configuration (`docker-compose.yml`)

**Added Services:**

#### Node Exporter (v1.8.2)
- **Purpose**: Collects host-level system metrics (CPU, RAM, disk, filesystem)
- **Port**: 9100
- **Volumes**: 
  - `/proc:/host/proc:ro` - CPU and process information
  - `/sys:/host/sys:ro` - System information
  - `/:/rootfs:ro` - Filesystem information
- **Collectors Enabled**:
  - `cpu` - CPU usage statistics
  - `meminfo` - Memory usage
  - `diskstats` - Disk I/O statistics
  - `filesystem` - Filesystem usage
  - `loadavg` - System load average
  - `uname` - System information

#### cAdvisor (v0.49.1)
- **Purpose**: Collects Docker container resource metrics
- **Port**: 8080
- **Volumes**:
  - `/:/rootfs:ro` - Root filesystem
  - `/var/run:/var/run:ro` - Docker socket
  - `/sys:/sys:ro` - System information
  - `/var/lib/docker:/var/lib/docker:ro` - Docker data
- **Configuration**:
  - Housekeeping interval: 15 seconds
  - Docker-only mode enabled
  - Disabled unnecessary metrics for performance

### 2. Prometheus Configuration (`monitoring/prometheus.yml`)

**Added Scrape Targets:**

```yaml
- job_name: "node-exporter"
  static_configs:
    - targets: ["node-exporter:9100"]
      labels:
        app: "node-exporter"
        env: "local"

- job_name: "cadvisor"
  static_configs:
    - targets: ["cadvisor:8080"]
      labels:
        app: "cadvisor"
        env: "local"
```

### 3. Backend API (`app/main.py`)

**Enhanced `/api/v1/monitoring` Endpoint:**

**New Metrics Returned:**

1. **CPU Metrics**:
   - `cpu_usage_percent` - Overall CPU utilization percentage
   - `load_average_1m` - 1-minute load average

2. **Memory Metrics**:
   - `memory_used_bytes` - Used memory in bytes
   - `memory_total_bytes` - Total memory in bytes
   - `memory_used_percent` - Memory utilization percentage

3. **Disk Metrics**:
   - `disk_used_bytes` - Available disk space in bytes
   - `disk_total_bytes` - Total disk space in bytes
   - `disk_used_percent` - Disk utilization percentage
   - `disk_read_bytes` - Disk read rate
   - `disk_write_bytes` - Disk write rate

4. **Container Metrics**:
   - `container_cpu_usage` - CPU usage per container
   - `container_memory_usage` - Memory usage per container
   - `container_memory_limit` - Memory limit per container
   - `container_status_running` - Container running status

**Error Handling**:
- Timeout protection (5-second timeout per query)
- Partial success handling (returns available metrics even if some fail)
- Graceful degradation for missing metrics

### 4. React Dashboard (`frontend/src/App.jsx`)

**Implemented Features:**

1. **State Management**:
   - `useState` for metrics, loading, and error states
   - `useEffect` for automatic 10-second polling
   - `useCallback` for memoized fetch function

2. **Live Data Display**:
   - Real-time CPU, memory, and disk usage
   - Application health status
   - Recovery metrics (attempts, successes, failures, rollbacks)
   - Container resource usage

3. **Visual Components**:
   - `MetricCard` - Displays key metrics with loading/error states
   - `ResourceBar` - Progress bars for CPU/memory/disk usage
   - `ContainerMetrics` - List of container resource usage
   - Live updating charts with Recharts

4. **User Experience**:
   - Loading spinners during data fetch
   - Error states with visual indicators
   - Manual refresh button
   - Last updated timestamp
   - Status indicator (operational/error)
   - "LIVE DATA" labels when metrics are connected

5. **Chart Integration**:
   - Real-time area chart for CPU and memory
   - Maintains last 20 data points
   - Updates every 10 seconds
   - Domain set to 0-100% for consistency

### 5. CSS Styling (`frontend/src/App.css`)

**Added Styles:**

- `.spinning` - Rotating animation for loading icons
- `.metric-error` / `.resource-error` - Error state styling
- `.last-updated` - Timestamp display
- `.live-label` / `.loading-label` - Status badges
- `.status-error` - Error status indicator
- `.container-*` - Container metrics styling
- Dark theme with cyan/purple accents

### 6. Grafana Dashboard (`monitoring/dashboards/pulseguard-overview.json`)

**New Dashboard Sections:**

1. **Infrastructure Overview** (Row 1):
   - Host CPU Usage panel
   - Host Memory Usage panel
   - Root Disk Usage panel

2. **CPU & Memory Over Time** (Row 2):
   - CPU usage time series
   - Memory usage time series

3. **Docker Container Resources** (Row 3):
   - Container CPU usage by container
   - Container memory usage by container

4. **Application Traffic & Health** (Row 4):
   - HTTP request rate
   - 5xx error rate
   - Request count by route
   - 95th percentile latency

5. **Python Process Runtime** (Row 5):
   - Process CPU usage
   - Process resident memory

**Dashboard Features**:
- 5-second auto-refresh
- 15-minute time window
- Color-coded thresholds
- Proper units and formatting
- Legend placement optimized

### 7. Tests (`tests/test_monitoring.py`)

**New Test Suite:**

- `test_monitoring_endpoint_success` - Mock successful responses
- `test_monitoring_endpoint_structure` - Validate response structure
- `test_monitoring_endpoint_timeout` - Test timeout handling
- `test_monitoring_metrics_types` - Verify data types

### 8. Verification Script (`verify_monitoring.sh`)

**Verification Steps:**

1. Check all Docker services are running
2. Verify Prometheus targets are UP
3. Query infrastructure metrics
4. Test backend monitoring API
5. Run Python test suite

## Prometheus Queries Used

### CPU Usage
```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Memory Usage Percentage
```promql
((node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes) * 100
```

### Disk Usage Percentage
```promql
((node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}) / node_filesystem_size_bytes{mountpoint="/"}) * 100
```

### Container CPU Usage
```promql
sum(rate(container_cpu_usage_seconds_total{image!=""}[5m])) by (container_label_com_docker_compose_project)
```

### Container Memory Usage
```promql
container_memory_usage_bytes{image!=""}
```

## Deployment Instructions

### 1. Start Infrastructure

```bash
docker compose up -d
```

### 2. Verify Services

```bash
# Check all containers are running
docker compose ps

# Verify Prometheus targets
curl http://127.0.0.1:9090/api/v1/targets

# Check Node Exporter
curl http://127.0.0.1:9100/metrics

# Check cAdvisor
curl http://127.0.0.1:8080/metrics
```

### 3. Test Backend API

```bash
# Test monitoring endpoint
curl http://127.0.0.1:8000/api/v1/monitoring | jq

# Expected output includes:
# - cpu_usage_percent
# - memory_used_percent
# - disk_used_percent
# - container metrics
```

### 4. Build Frontend

```bash
cd frontend
npm install
npm run build
```

### 5. Run Verification Script

```bash
bash verify_monitoring.sh
```

### 6. Run Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_monitoring.py -v
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| PulseGuard API | http://127.0.0.1:8000 | N/A |
| Monitoring Endpoint | http://127.0.0.1:8000/api/v1/monitoring | N/A |
| API Docs | http://127.0.0.1:8000/docs | N/A |
| Prometheus | http://127.0.0.1:9090 | N/A |
| Grafana | http://127.0.0.1:3000 | Configure via .env |
| Node Exporter | http://127.0.0.1:9100/metrics | N/A |
| cAdvisor | http://127.0.0.1:8080 | N/A |
| Alertmanager | http://127.0.0.1:9093 | N/A |

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PulseGuard Stack                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │  React       │    │  FastAPI     │                  │
│  │  Dashboard   │───▶│  Backend     │                  │
│  │  (Port 5173) │    │  (Port 8000) │                  │
│  └──────────────┘    └──────┬───────┘                  │
│                              │                          │
│                              ▼                          │
│                      ┌──────────────┐                  │
│                      │  Prometheus  │                  │
│                      │  (Port 9090) │                  │
│                      └───┬──────────┘                  │
│                          │                              │
│         ┌────────────────┼────────────────┐           │
│         ▼                ▼                ▼           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │   Node   │    │ cAdvisor │    │PulseGuard│       │
│  │ Exporter │    │ (Port    │    │  Metrics │       │
│  │ (Port    │    │  8080)   │    │ (Port    │       │
│  │  9100)   │    └──────────┘    │  8000)   │       │
│  └──────────┘                     └──────────┘       │
│       │                                  │             │
│       ▼                                  ▼             │
│  Host Metrics                    App Metrics          │
│  (CPU, RAM,                      (HTTP, latency,      │
│   Disk, I/O)                      self-healing)       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Files Modified

1. `docker-compose.yml` - Added node-exporter and cadvisor services
2. `monitoring/prometheus.yml` - Added scrape configs for exporters
3. `app/main.py` - Enhanced monitoring endpoint with infrastructure metrics
4. `frontend/src/App.jsx` - Complete rewrite with live data fetching
5. `frontend/src/App.css` - Added loading/error state styles
6. `monitoring/dashboards/pulseguard-overview.json` - Enhanced with infrastructure panels

## Files Created

1. `tests/test_monitoring.py` - Test suite for monitoring endpoint
2. `verify_monitoring.sh` - Verification script for infrastructure
3. `MONITORING_IMPLEMENTATION.md` - This documentation file

## Compatibility Notes

### WSL2 Environment
- Node Exporter works in WSL2 with host volume mounts
- cAdvisor requires Docker socket access
- All metrics accessible from Windows host via `127.0.0.1`

### Resource Requirements
- Node Exporter: ~10MB RAM
- cAdvisor: ~100MB RAM
- Additional Prometheus storage: ~50MB per day

### Security Considerations
- All services bound to `127.0.0.1` (localhost only)
- Read-only volume mounts where possible
- No privileged containers required
- cAdvisor limited to Docker-only metrics

## Known Limitations

1. **Container Metrics**: Some container labels may vary based on Docker Compose version
2. **Disk Metrics**: Only root filesystem (`/`) monitored by default
3. **Network Metrics**: Not yet implemented (future enhancement)
4. **Historical Data**: Limited to Prometheus retention period (15 days)
5. **Frontend Build**: Requires Node.js environment to rebuild

## Troubleshooting

### Node Exporter Not Showing Data
```bash
# Check if Node Exporter is running
docker logs pulseguard-node-exporter

# Verify metrics endpoint
curl http://127.0.0.1:9100/metrics | grep node_cpu
```

### cAdvisor Not Showing Containers
```bash
# Check cAdvisor logs
docker logs pulseguard-cadvisor

# Verify Docker socket access
docker exec pulseguard-cadvisor ls -la /var/run/docker.sock
```

### Prometheus Not Scraping Targets
```bash
# Check Prometheus config
docker exec pulseguard-prometheus cat /etc/prometheus/prometheus.yml

# Check targets status
curl http://127.0.0.1:9090/api/v1/targets | jq
```

### Backend API Returns Empty Metrics
```bash
# Test Prometheus connectivity from backend
docker exec pulseguard-app curl http://prometheus:9090/-/healthy

# Check Prometheus has data
curl 'http://127.0.0.1:9090/api/v1/query?query=node_cpu_seconds_total'
```

## Future Enhancements

1. **Network Metrics**: Add network I/O monitoring
2. **Process Metrics**: Track individual process resource usage
3. **Alerts**: Configure Alertmanager rules for threshold violations
4. **Historical Analysis**: Add long-term trend analysis
5. **Export Functionality**: Export metrics data as CSV/JSON
6. **Custom Dashboards**: Allow users to create custom metric views
7. **Multi-Host Support**: Support monitoring multiple hosts
8. **Authentication**: Add API authentication for production use

## Conclusion

The infrastructure monitoring implementation provides:
- ✅ Real-time CPU, RAM, and disk metrics
- ✅ Docker container resource monitoring
- ✅ Live dashboard with 10-second refresh
- ✅ Comprehensive Grafana dashboards
- ✅ Robust error handling and graceful degradation
- ✅ Test coverage for monitoring endpoints
- ✅ Verification script for deployment validation

All existing self-healing and chaos engineering functionality has been preserved.
