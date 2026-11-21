# 🛡️ PulseGuard - DevOps Monitoring & Self-Healing Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.3.1-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Real-time infrastructure monitoring with automated failure detection and self-healing capabilities**

PulseGuard is a production-ready DevOps platform that monitors your applications, detects failures automatically, and performs self-healing recovery or rollback operations without human intervention.

![PulseGuard Dashboard](https://via.placeholder.com/1200x600/0a1628/38bdf8?text=PulseGuard+Dashboard)

---

## 🎯 Features

### 🔍 Real-Time Monitoring
- **CPU, Memory, Disk** metrics from Node Exporter
- **Application health** checks every 15 seconds
- **HTTP request rates** and error tracking
- **Live dashboard** with 10-second auto-refresh

### 🔧 Self-Healing
- **Automatic failure detection** via Prometheus alerts
- **Restart on failure** - attempts to recover current version
- **Automatic rollback** - deploys previous version if recovery fails
- **Metrics tracking** - records all recovery attempts and outcomes

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
- Node.js 18+ (for frontend development)

### 1. Clone the Repository
```bash
git clone https://github.com/dvya207/pulseguard.git
cd pulseguard
```

### 2. Start the Infrastructure
```bash
docker compose up -d
```

This starts:
- PulseGuard FastAPI application
- Prometheus metrics server
- Grafana dashboards
- Node Exporter (system metrics)
- cAdvisor (container metrics)
- Alertmanager

### 3. Access the Dashboard

**Main Dashboard**: http://localhost:5173  
**Prometheus**: http://localhost:9090  
**Grafana**: http://localhost:3000  
**API Docs**: http://localhost:8000/docs  

### 4. Start the Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```

Dashboard opens at: http://localhost:5173

---

## 📊 What You'll See

### Live Dashboard
The dashboard displays real-time metrics:

- **Application Health**: Service status (Healthy/Down)
- **CPU Usage**: Real-time processor utilization
- **Memory Usage**: RAM consumption (used/total)
- **Disk Usage**: Storage utilization percentage
- **Recovery Stats**: Attempts, successes, failures, rollbacks
- **Live Charts**: CPU and memory trends over time

### Sidebar Navigation
- **Overview**: Main dashboard (current page)
- **Monitoring**: Opens Prometheus query interface
- **API Docs**: Opens FastAPI Swagger UI
- **Self-Healing**: Shows recovery statistics
- **Alerts**: Opens Alertmanager
- **Grafana**: Professional dashboards

---

## 🧪 Test Self-Healing

### Simulate a Failure
```bash
curl -X POST http://localhost:8000/api/v1/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

**What happens:**
1. Health endpoint returns HTTP 500
2. Prometheus detects the failure (within 30s)
3. Alert fires
4. Self-healing script activates
5. Attempts to restart the service
6. If restart fails → Triggers automatic rollback
7. Dashboard updates with new recovery metrics

### Restore Normal Operation
```bash
curl -X POST http://localhost:8000/api/v1/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Run Self-Healing Script Manually
```bash
bash self_heal.sh
```

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

### Environment Variables

Create a `.env` file:
```bash
# Grafana Credentials
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password

# PulseGuard Version
PULSEGUARD_VERSION=1.0.0
PULSEGUARD_IMAGE=pulseguard:1.0.0
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

### Test Results
```
tests/test_health.py::test_root_endpoint PASSED
tests/test_health.py::test_health_check_healthy PASSED
tests/test_health.py::test_health_check_failure_simulation PASSED
tests/test_health.py::test_metrics_endpoint PASSED
tests/test_monitoring.py::test_monitoring_endpoint_success PASSED
tests/test_monitoring.py::test_monitoring_endpoint_structure PASSED
tests/test_monitoring.py::test_monitoring_endpoint_timeout PASSED
tests/test_monitoring.py::test_monitoring_metrics_types PASSED

======================== 8 passed ========================
```

---

## 📚 Documentation

- **[Demo Guide](DEMO_GUIDE.md)** - Interactive hands-on walkthrough
- **[Monitoring Implementation](MONITORING_IMPLEMENTATION.md)** - Technical details
- **[Runtime Verification](RUNTIME_VERIFICATION_REPORT.md)** - Test results
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

### Production Deployment
- ✅ Non-root containers
- ✅ Read-only volumes where possible
- ✅ Localhost-only bindings by default
- ⚠️ Change default Grafana credentials
- ⚠️ Add TLS/SSL for production
- ⚠️ Implement authentication for APIs
- ⚠️ Use secrets management (not .env files)

### Network Security
All services are bound to `127.0.0.1` by default. For production:
- Use reverse proxy (Nginx/Traefik)
- Enable TLS/SSL certificates
- Implement authentication
- Use VPN for remote access

---

## 🚀 Production Deployment

### Prerequisites
- Linux server with Docker
- Domain name (optional, for TLS)
- Reverse proxy (Nginx/Traefik)

### Steps
1. Clone repository on server
2. Update `.env` with secure credentials
3. Configure firewall rules
4. Start services: `docker compose up -d`
5. Set up reverse proxy with TLS
6. Configure backup for Prometheus data

### Recommended Monitoring
- Uptime monitoring (UptimeRobot, Pingdom)
- Log aggregation (ELK stack)
- Backup Prometheus data regularly
- Monitor disk usage for metrics storage

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

## 👤 Author

**Divya Jain**
- GitHub: [@dvya207](https://github.com/dvya207)
- Project: [PulseGuard](https://github.com/dvya207/pulseguard)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Prometheus](https://prometheus.io/) - Monitoring and alerting toolkit
- [Grafana](https://grafana.com/) - Observability platform
- [React](https://reactjs.org/) - UI library
- [Docker](https://www.docker.com/) - Containerization platform

---

## 📊 Project Status

✅ **Production Ready** - Fully functional monitoring platform  
✅ **All Tests Passing** - 8/8 tests passing  
✅ **Real Metrics** - Live CPU, RAM, disk monitoring  
✅ **Self-Healing** - Automatic recovery implemented  
✅ **Documentation** - Complete guides and API docs  

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
