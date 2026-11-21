# PulseGuard Infrastructure Monitoring - Quick Start

## 🚀 Start Infrastructure

```bash
docker compose up -d
```

Wait 30 seconds for services to initialize.

---

## ✅ Verify Deployment

```bash
# Quick check - all should return OK
curl -sf http://127.0.0.1:8000/health && echo "✓ PulseGuard OK"
curl -sf http://127.0.0.1:9090/-/healthy && echo "✓ Prometheus OK"
curl -sf http://127.0.0.1:9100/metrics > /dev/null && echo "✓ Node Exporter OK"
curl -sf http://127.0.0.1:8080/metrics > /dev/null && echo "✓ cAdvisor OK"
curl -sf http://127.0.0.1:3000/api/health && echo "✓ Grafana OK"
```

Or use the verification script:
```bash
bash verify_monitoring.sh
```

---

## 📊 Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Monitoring API** | http://127.0.0.1:8000/api/v1/monitoring | - |
| **API Documentation** | http://127.0.0.1:8000/docs | - |
| **Prometheus** | http://127.0.0.1:9090 | - |
| **Grafana** | http://127.0.0.1:3000 | See .env file |
| **Node Exporter** | http://127.0.0.1:9100/metrics | - |
| **cAdvisor** | http://127.0.0.1:8080 | - |

---

## 🧪 Test Backend API

```bash
# Fetch all metrics
curl http://127.0.0.1:8000/api/v1/monitoring | jq

# Check specific metrics
curl http://127.0.0.1:8000/api/v1/monitoring | jq '.metrics.cpu_usage_percent'
curl http://127.0.0.1:8000/api/v1/monitoring | jq '.metrics.memory_used_percent'
curl http://127.0.0.1:8000/api/v1/monitoring | jq '.metrics.disk_used_percent'
```

---

## 🎨 Build Frontend

```bash
cd frontend
npm install
npm run build
npm run dev  # Development server on http://localhost:5173
```

---

## 🧪 Run Tests

```bash
# Activate virtual environment
source .venv/bin/activate   # or: source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_health.py -v
pytest tests/test_monitoring.py -v
```

---

## 📈 Sample Prometheus Queries

Access Prometheus UI: http://127.0.0.1:9090

**CPU Usage**:
```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memory Usage**:
```promql
((node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes) * 100
```

**Disk Usage**:
```promql
((node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}) / node_filesystem_size_bytes{mountpoint="/"}) * 100
```

**Container CPU**:
```promql
sum(rate(container_cpu_usage_seconds_total{image!=""}[5m])) by (name)
```

**Container Memory**:
```promql
container_memory_usage_bytes{image!=""}
```

---

## 🔧 Troubleshooting

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker logs pulseguard-app -f
docker logs pulseguard-prometheus -f
docker logs pulseguard-node-exporter -f
docker logs pulseguard-cadvisor -f
```

### Restart Services
```bash
# All services
docker compose restart

# Specific service
docker compose restart node-exporter
docker compose restart cadvisor
```

### Check Prometheus Targets
```bash
curl http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

Expected output (all should be "up"):
```json
{"job": "pulseguard", "health": "up"}
{"job": "node-exporter", "health": "up"}
{"job": "cadvisor", "health": "up"}
{"job": "prometheus", "health": "up"}
```

---

## 🛑 Stop Infrastructure

```bash
# Stop containers (preserve data)
docker compose stop

# Stop and remove containers (preserve volumes)
docker compose down

# Remove everything including volumes (⚠️ DESTROYS DATA)
docker compose down -v
```

---

## 📚 Documentation

- **Full Implementation Details**: `MONITORING_IMPLEMENTATION.md`
- **Implementation Report**: `IMPLEMENTATION_REPORT.md`
- **This Quick Start**: `QUICK_START.md`

---

## 🎯 What's Monitoring

✅ **Host Metrics**:
- CPU usage percentage and per-core stats
- Memory usage (total, used, free, cached, buffers)
- Disk usage and I/O rates
- Filesystem usage
- System load average

✅ **Container Metrics**:
- CPU usage per container
- Memory usage and limits per container
- Network I/O per container
- Container status and uptime

✅ **Application Metrics**:
- HTTP request rate and latency
- Error rates (5xx responses)
- Self-healing metrics
- Recovery attempts and success rate
- Rollback events

---

## 🚨 Common Issues

**"No data in Grafana"**
- Wait 1-2 minutes after startup for first scrape
- Check Prometheus targets: http://127.0.0.1:9090/targets

**"Backend API returns empty metrics"**
- Verify Prometheus is accessible: `curl http://127.0.0.1:9090/-/healthy`
- Check metrics exist: `curl 'http://127.0.0.1:9090/api/v1/query?query=up'`

**"cAdvisor shows no containers"**
- Restart cAdvisor: `docker compose restart cadvisor`
- Check logs: `docker logs pulseguard-cadvisor`

**"Frontend not updating"**
- Open browser console for errors
- Verify API responds: `curl http://127.0.0.1:8000/api/v1/monitoring`
- Check CORS configuration

---

## ⚡ Performance Tips

1. **Reduce Scrape Frequency**: Edit `monitoring/prometheus.yml`, change `scrape_interval` to `30s`
2. **Reduce Chart History**: In `App.jsx`, change `.slice(-20)` to `.slice(-10)`
3. **Disable Unused Collectors**: In `docker-compose.yml`, add more `--collector.disable-*` flags
4. **Adjust Retention**: In Prometheus command, change `--storage.tsdb.retention.time=15d` to `7d`

---

## 🎓 Learn More

**Prometheus**:
- Query language: https://prometheus.io/docs/prometheus/latest/querying/basics/
- Node Exporter: https://github.com/prometheus/node_exporter
- cAdvisor: https://github.com/google/cadvisor

**Grafana**:
- Dashboard creation: https://grafana.com/docs/grafana/latest/dashboards/
- PromQL in Grafana: https://grafana.com/docs/grafana/latest/datasources/prometheus/

**FastAPI**:
- Background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Middleware: https://fastapi.tiangolo.com/tutorial/middleware/

---

## ✨ Features

✅ Real-time infrastructure monitoring  
✅ 10-second automatic refresh  
✅ Live CPU, RAM, disk metrics  
✅ Container resource tracking  
✅ Self-healing metrics preserved  
✅ Grafana dashboards configured  
✅ Error handling and graceful degradation  
✅ Test coverage included  
✅ WSL2 compatible  
✅ Production-ready  

---

**Ready to monitor your infrastructure!** 🚀
