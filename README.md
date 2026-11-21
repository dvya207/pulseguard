<div align="center">

# 🛡️ PulseGuard - DevOps Monitoring & Self-Healing Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.3.1-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### Infrastructure and application monitoring with health alerts and operator-run recovery scripts

PulseGuard is a portfolio project built around FastAPI, Prometheus, Grafana, and a React dashboard. Prometheus collects metrics and evaluates alerts; recovery and rollback scripts are available for an operator to run. Alertmanager currently routes alerts to a null receiver, and alerts do not trigger recovery automatically.

</div>

---

## 🎯 Features

### 🔍 Real-Time Monitoring
- **CPU, Memory, Disk** metrics from Node Exporter
- **Application health gauge** sampled by Prometheus every 15 seconds
- **HTTP request rates** and error tracking
- **Live dashboard** with 10-second auto-refresh

### 🔧 Self-Healing
- **Prometheus alerts** - distinguish an application health failure from a failed metrics scrape
- **Operator-run recovery scripts** - provide restart and rollback paths when deployment state and images are prepared
- **Metrics tracking** - exports recovery counters maintained by the scripts

### 📊 Observability Stack
- **Prometheus** - Time-series metrics database
- **Grafana** - Professional visualization dashboards
- **Node Exporter** - System-level metrics collection
- **Alertmanager** - Alert routing and management

### 🎨 Modern Dashboard
- **React 19** with real-time data fetching
- **Recharts** for beautiful visualizations
- **Tailwind CSS** for responsive design
- **Live metrics** updating every 10 seconds

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 20.19+ or 22.12+ (for the frontend toolchain)

### 1. Clone the Repository
```bash
git clone https://github.com/dvya207/pulseguard.git
cd pulseguard
```

### 2. Start the Infrastructure
```bash
cp .env.example .env
# Set GRAFANA_ADMIN_USER and GRAFANA_ADMIN_PASSWORD in .env (or export them in the shell).
docker compose up -d
```

Grafana credentials are required; Compose intentionally fails if either variable is missing or empty. Keep `.env` local and do not commit it.

This starts:
- PulseGuard FastAPI application
- Prometheus metrics server
- Grafana dashboards
- Node Exporter (system metrics)
- cAdvisor (container metrics)
- Alertmanager

### 3. Start the Frontend in WSL2

From the WSL2 Ubuntu project directory:
```bash
cd frontend
npm ci
npm run dev -- --host 0.0.0.0
```

The Vite development server proxies `/api` requests to the backend on port 8000. Open the dashboard at http://localhost:5173 from Windows or WSL2.

### 4. Access the Services

**Prometheus**: http://localhost:9090
**Grafana**: http://localhost:3000
**API Docs**: http://localhost:8000/docs

---

## 📊 What You'll See

### Live Dashboard
The dashboard displays real-time metrics:

- **Application Health**: Current health gauge from the backend
- **CPU Usage**: Real-time processor utilization
- **Memory Usage**: RAM consumption (used/total)
- **Disk Usage**: Storage utilization percentage
- **Recovery Stats**: Exported recovery counters (zero may mean no metrics file has been initialized)
- **Live Charts**: CPU and memory trends over time

### Sidebar Navigation
- **Overview**: Main dashboard (current page)
- **Monitoring**: Opens Prometheus query interface
- **API Docs**: Opens FastAPI Swagger UI
- **Self-Healing**: Shows recovery statistics
- **Alerts**: Opens Alertmanager
- **Grafana**: Professional dashboards

---

## 🧪 Failure and Recovery Scripts

### Simulate an Application Health Failure
```bash
curl -X POST http://localhost:8000/api/v1/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

The endpoint returns HTTP 500 and exports `pulseguard_health = 0`, which is evaluated by the `PulseGuardHealthCheckFailed` Prometheus alert. A separate `PulseGuardScrapeFailed` alert detects when Prometheus cannot scrape the backend. Neither alert triggers `self_heal.sh`: Alertmanager currently routes to a null receiver, and the recovery script is manual.

### Restore Normal Operation
```bash
curl -X POST http://localhost:8000/api/v1/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Run the Recovery Script Manually
```bash
bash self_heal.sh
```

The script requires a valid `state.json`, the metrics file, Docker Compose, and the relevant image tags. Rollback also requires the prior image to exist locally. These prerequisites and the full recovery/rollback path have not been verified by this documentation; do not treat the scripts as an automatic recovery service.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PulseGuard Stack                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │  React       │───▶│  FastAPI     │                  │
│  │  Dashboard   │    │  Backend     │                  │
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
│  │ (Port    │    │  8080)   │    │          │       │
│  │  9100)   │    └──────────┘    └──────────┘       │
│  └──────────┘                                         │
│       │                                                │
│       ▼                                                │
│  Host Metrics                                          │
│  (CPU, RAM, Disk)                                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Grafana Environment Variables

Create and edit a local `.env` file. Do not put credential values in source control:
```bash
cp .env.example .env
# Set GRAFANA_ADMIN_USER and GRAFANA_ADMIN_PASSWORD in .env.
```

### Prometheus Configuration
Edit `monitoring/prometheus.yml` to add more scrape targets:
```yaml
scrape_configs:
  - job_name: "your-service"
    static_configs:
      - targets: ["your-service:8000"]
```

### Alert Rules
Add custom alerts in `monitoring/alert.rules.yml`:
```yaml
- alert: HighCPUUsage
  expr: node_cpu_usage > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High CPU usage detected"
```

### Alert Behavior and WSL2

- `PulseGuardScrapeFailed` fires when Prometheus cannot scrape the backend metrics endpoint (`up{job="pulseguard"} == 0`).
- `PulseGuardHealthCheckFailed` fires when the backend's `pulseguard_health` gauge reports a failed application health check.
- Alertmanager currently routes to its configured null receiver. Alerts are evaluated and visible in Prometheus/Alertmanager, but no notifications are delivered and alerts do not launch recovery scripts.
- cAdvisor container metrics may be missing in WSL2 because Docker Desktop's container storage metadata is not always visible at the paths cAdvisor expects. Host-level Node Exporter metrics are separate; an empty container panel in WSL2 is a known limitation, not evidence that container metrics were verified.

---

## 📈 Metrics Available

### Application Metrics
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency histogram
- `self_heal_failures_detected_total` - Detected failures
- `self_heal_recovery_attempts_total` - Recovery attempts
- `self_heal_success_total` - Successful recoveries
- `self_heal_failure_total` - Failed recoveries
- `self_heal_rollback_total` - Rollback operations

### Infrastructure Metrics (Node Exporter)
- `node_cpu_seconds_total` - CPU time per core
- `node_memory_MemTotal_bytes` - Total memory
- `node_memory_MemAvailable_bytes` - Available memory
- `node_filesystem_size_bytes` - Filesystem size
- `node_load1` - 1-minute load average

### Query Examples
```promql
# CPU usage percentage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage percentage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk used bytes
node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}

# HTTP error rate
rate(http_requests_total{status=~"5.."}[5m])

# Self-healing success rate
rate(self_heal_success_total[1h]) / rate(self_heal_recovery_attempts_total[1h])
```

---

## 🧪 Testing

### Run Tests
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_health.py -v
pytest tests/test_monitoring.py -v
```

---

## 📚 Documentation

- **[Demo Guide](DEMO_GUIDE.md)** - Interactive hands-on walkthrough
- **[Monitoring Implementation](MONITORING_IMPLEMENTATION.md)** - Technical details
- **[Runtime Verification](RUNTIME_VERIFICATION_REPORT.md)** - Historical runtime notes; not a current verification guarantee
- **[Quick Start](QUICK_START.md)** - Quick reference guide
- **[Sidebar Navigation](SIDEBAR_NAVIGATION_GUIDE.md)** - Dashboard navigation help

---

## 🐳 Docker Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| pulseguard | pulseguard:1.0.0 | 8000 | FastAPI application |
| prometheus | prom/prometheus:v3.16.0 | 9090 | Metrics database |
| grafana | grafana/grafana:13.3.1 | 3000 | Dashboards |
| node-exporter | prom/node-exporter:v1.8.2 | 9100 | System metrics |
| cadvisor | gcr.io/cadvisor/cadvisor:v0.49.1 | 8080 | Container metrics |
| alertmanager | prom/alertmanager:v0.27.0 | 9093 | Alert routing |

---

## 🔒 Security Considerations

### Local Development
- Grafana requires `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`; there are no Compose credential defaults.
- `.env` and `.env.*` are ignored by Git; `.env.example` contains only empty keys.
- Compose service ports bind to localhost by default.
- The API does not provide production-grade authentication or TLS. Do not expose it directly to an untrusted network.

### Network Security
All services are bound to `127.0.0.1` by default. For production:
- Use reverse proxy (Nginx/Traefik)
- Enable TLS/SSL certificates
- Implement authentication
- Use VPN for remote access

---

## 🚀 Deployment Considerations

PulseGuard is a development/portfolio stack. Production suitability, TLS, API authentication, notification delivery, and automated recovery have not been established by the current configuration.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Frontend
cd frontend
npm install
npm run dev

# Run tests
pytest tests/ -v

# Linting
ruff check .
npm run lint
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Prometheus](https://prometheus.io/) - Monitoring and alerting toolkit
- [Grafana](https://grafana.com/) - Observability platform
- [React](https://reactjs.org/) - UI library
- [Docker](https://www.docker.com/) - Containerization platform

---

## 📊 Project Status

The repository includes a React dashboard, FastAPI metrics API, Prometheus rules, Grafana provisioning, and operator-run recovery scripts. Runtime behavior depends on the local Docker/WSL2 environment. Alert delivery and automatic recovery are not wired; see the alert and recovery notes above. Do not infer production readiness from the presence of these components.

### Recommended Dashboard Screenshots

Capture real screens only after starting the stack:
1. PulseGuard overview with live CPU, memory, disk, application health, and update time.
2. Grafana overview showing host CPU, memory, and disk panels with the Prometheus datasource active.
3. Prometheus Targets page showing current scrape health.
4. Prometheus Alerts and Alertmanager page showing alert state and the configured null receiver.
5. Container metrics panel in a native Linux Docker environment; note the WSL2 cAdvisor limitation when capturing from WSL2.

---

## 🎓 Learning Resources

This project demonstrates:
- ✅ Observability (Metrics, Dashboards, Alerts)
- ✅ Self-Healing Systems
- ✅ Site Reliability Engineering (SRE) practices
- ✅ Infrastructure as Code
- ✅ Docker & Container Orchestration
- ✅ REST API Design
- ✅ React & Modern Frontend
- ✅ CI/CD Integration
- ✅ DevOps Best Practices

Perfect for:
- 🎯 DevOps Portfolio Projects
- 🎯 Interview Preparation
- 🎯 Learning SRE Concepts
- 🎯 Production Infrastructure Reference

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ by [Divya Jain](https://github.com/dvya207)

</div>
