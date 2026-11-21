# PulseGuard Live Demo Guide

## 🎯 What You're Actually Monitoring

**PulseGuard monitors ITSELF** - it's a demo application that:
- Runs a FastAPI web service
- Has a `/health` endpoint that can fail
- Monitors its own CPU, RAM, disk usage
- Can simulate failures on command
- Automatically recovers when it detects failures

---

## 📋 Prerequisites - Check Everything is Running

Open a browser and visit these URLs to confirm everything works:

### 1. ✅ PulseGuard API
```
http://localhost:8000/docs
```
**What you should see**: FastAPI Swagger documentation page

### 2. ✅ Health Endpoint
```
http://localhost:8000/health
```
**What you should see**: 
```json
{"status":"healthy","service":"pulseguard","version":"1.0.0"}
```

### 3. ✅ Monitoring Dashboard
```
http://localhost:5173
```
**What you should see**: 
- Dark themed dashboard
- CPU usage showing real percentage (like 50%)
- Memory usage showing real GB (like 2.3 GB / 3.8 GB)
- "SYSTEM OPERATIONAL" green indicator
- Charts updating

### 4. ✅ Prometheus
```
http://localhost:9090
```
**What you should see**: Prometheus query interface

### 5. ✅ Grafana
```
http://localhost:3000
```
**What you should see**: Grafana login page

---

## 🧪 DEMO 1: See Real-Time Metrics

### Step 1: Open the Dashboard
Go to: **http://localhost:5173**

### Step 2: Watch the Live Data
Look at the top cards:
- **Application Health**: Should say "Healthy"
- **Recovery Attempts**: Should show "10"
- **Successful Recoveries**: Should show "10"

### Step 3: Watch the Chart Update
The blue and purple area chart updates every 10 seconds with real CPU and memory data.

**What it's monitoring**: The CPU and memory of your computer right now!

### Step 4: Open Browser Console
1. Press F12 in your browser
2. Go to "Network" tab
3. Filter by "monitoring"
4. Watch the requests every 10 seconds
5. Click on a request to see the JSON response with real values

---

## 🔥 DEMO 2: Simulate a Failure (Watch Self-Healing)

### Step 1: Open Two Browser Tabs
- **Tab 1**: Dashboard → http://localhost:5173
- **Tab 2**: Keep on health endpoint → http://localhost:8000/health

### Step 2: Trigger a Failure
Open a **new terminal/PowerShell** and run:

```bash
wsl curl -X POST http://localhost:8000/api/v1/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

**Response you'll see**:
```json
{
  "simulate_failure": true,
  "message": "Failure simulation ACTIVE. /health will now return HTTP 500."
}
```

### Step 3: Watch What Happens

**Tab 2** (Health endpoint):
Refresh → You'll see:
```json
{
  "status": "degraded",
  "service": "pulseguard",
  "error": "Simulated deployment failure triggered..."
}
```
HTTP Status: **500 Internal Server Error** (red in browser)

**Tab 1** (Dashboard):
- "SYSTEM OPERATIONAL" changes to "CONNECTION ERROR" (red)
- Application Health card turns red
- Charts might pause updating

### Step 4: Watch Self-Healing (Prometheus Detection)

Go to Prometheus: **http://localhost:9090**

1. In the query box, enter: `up{job="pulseguard"}`
2. Click "Execute"
3. You'll see the value is **1** (up)

But health checks are failing! This is what triggers alerts.

### Step 5: Manually Run Self-Healing Script

In PowerShell/Terminal:
```bash
wsl bash /home/administrator/devops-learning/pulseguard/self_heal.sh
```

**You'll see output like**:
```
[watchdog] Health check failed.
[watchdog] Attempting to restart current version: 1.0.0
[watchdog] Current version recovered successfully.
```

### Step 6: Verify Recovery

Refresh **Tab 2** (health endpoint) → Back to:
```json
{"status":"healthy","service":"pulseguard","version":"1.0.0"}
```

Check the dashboard **Tab 1** → Back to green "SYSTEM OPERATIONAL"

### Step 7: See Updated Metrics

Refresh the dashboard and check:
- **Recovery Attempts**: Should increase by 1
- **Successful Recoveries**: Should increase by 1

---

## 📊 DEMO 3: Query Prometheus Directly

### Step 1: Open Prometheus
Go to: **http://localhost:9090**

### Step 2: Try These Queries

#### Query 1: CPU Usage
```promql
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
**Execute** → Shows your real CPU percentage

#### Query 2: Memory Usage
```promql
node_memory_MemTotal_bytes / 1024 / 1024 / 1024
```
**Execute** → Shows total RAM in GB

#### Query 3: Self-Healing Metrics
```promql
self_heal_success_total
```
**Execute** → Shows how many successful recoveries

#### Query 4: HTTP Request Rate
```promql
rate(http_requests_total[1m])
```
**Execute** → Shows requests per second

### Step 3: Create a Graph
1. Click the "Graph" tab (next to Table)
2. Enter query: `rate(http_requests_total[5m])`
3. See the request rate over time

---

## 🎨 DEMO 4: Generate Load and Watch Metrics

### Step 1: Open Dashboard
Keep: **http://localhost:5173** open

### Step 2: Generate HTTP Requests

In a terminal, run this to hit the API repeatedly:

**Windows PowerShell**:
```powershell
for ($i=1; $i -le 100; $i++) {
    wsl curl -s http://localhost:8000/health | Out-Null
    Start-Sleep -Milliseconds 100
}
```

**Or Linux/WSL**:
```bash
for i in {1..100}; do
  curl -s http://localhost:8000/health > /dev/null
  sleep 0.1
done
```

### Step 3: Watch the Dashboard
- Request metrics increase
- CPU might spike slightly
- Chart updates with new data

---

## 📈 DEMO 5: Explore Grafana Dashboards

### Step 1: Login to Grafana
Go to: **http://localhost:3000**

**Credentials**: Check the `.env` file or try:
- Username: `admin`
- Password: `admin` (or what's in your `.env`)

### Step 2: Open PulseGuard Dashboard
1. Click on the menu (☰) → "Dashboards"
2. Find "PulseGuard Overview"
3. Click to open

### Step 3: Explore Panels
You'll see:
- **Host CPU Usage**: Real-time CPU percentage
- **Host Memory Usage**: Real-time memory percentage  
- **Root Disk Usage**: Disk utilization
- **HTTP Request Rate**: API traffic
- **95th Percentile Latency**: Response times

### Step 4: Change Time Range
- Top right corner → Click time range (e.g., "Last 15 minutes")
- Change to "Last 1 hour" or "Last 6 hours"
- See historical trends

---

## 🔄 DEMO 6: Full Rollback Simulation

### Step 1: Check Current State
```bash
wsl cat /home/administrator/devops-learning/pulseguard/state.json
```

You'll see:
```json
{
  "current_version": "1.0.0",
  "previous_version": "0.9.0",
  "status": "deployed",
  "last_deploy_time": "..."
}
```

### Step 2: Simulate Failed Deployment
```bash
# Enable failure
wsl curl -X POST http://localhost:8000/api/v1/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### Step 3: Run Self-Heal (Will Detect Failure)
```bash
wsl bash /home/administrator/devops-learning/pulseguard/self_heal.sh
```

### Step 4: If Recovery Fails, Trigger Rollback
```bash
wsl bash /home/administrator/devops-learning/pulseguard/rollback.sh
```

### Step 5: Check Metrics File
```bash
wsl cat /home/administrator/devops-learning/pulseguard/self_heal/metrics.json
```

You'll see counts increase:
```json
{
  "self_heal_failures_detected_total": 11,
  "self_heal_recovery_attempts_total": 11,
  "self_heal_success_total": 10,
  "self_heal_failure_total": 0,
  "self_heal_rollback_total": 2
}
```

---

## 🔍 DEMO 7: Check All Metrics Endpoints

### Terminal Commands to Test Everything

```bash
# 1. Health check
wsl curl http://localhost:8000/health

# 2. Full monitoring API
wsl curl http://localhost:8000/api/v1/monitoring | jq

# 3. Prometheus metrics (raw)
wsl curl http://localhost:8000/metrics/ | grep http_requests

# 4. Node Exporter metrics
wsl curl http://localhost:9100/metrics | grep node_cpu

# 5. Check all Prometheus targets
wsl curl -s http://localhost:9090/api/v1/targets | grep '"health":"up"'
```

---

## 📸 Expected Screenshots

### Dashboard (http://localhost:5173)
You should see:
```
┌─────────────────────────────────────────┐
│  PULSEGUARD DEVOPS CONTROL CENTER       │
├─────────────────────────────────────────┤
│                                         │
│  ● SYSTEM OPERATIONAL                   │
│                                         │
│  [Application Health]  [Current Ver]    │
│  Healthy              1.4.0            │
│                                         │
│  [CPU Usage: 45.2%  ████████░░]        │
│  [Memory: 2.3/3.8 GB ███████░░░]       │
│                                         │
│  [📈 Live updating chart]               │
│                                         │
└─────────────────────────────────────────┘
```

### Health Endpoint (http://localhost:8000/health)
```json
{
  "status": "healthy",
  "service": "pulseguard",
  "version": "1.0.0"
}
```

### Monitoring API (http://localhost:8000/api/v1/monitoring)
```json
{
  "status": "success",
  "metrics": {
    "cpu_usage_percent": 45.23,
    "memory_used_percent": 60.45,
    "disk_used_percent": 5.79,
    "recovery_attempts": 10,
    ...
  }
}
```

---

## 🎓 What Each Component Does

### Your Computer → Node Exporter
- Reads `/proc/cpuinfo` → CPU usage
- Reads `/proc/meminfo` → Memory usage
- Reads filesystem stats → Disk usage

### Node Exporter → Prometheus
- Every 15 seconds, Prometheus scrapes metrics
- Stores as time-series data

### PulseGuard App → Prometheus
- Exposes `/metrics/` endpoint
- Tracks HTTP requests, response times
- Custom self-healing metrics

### Prometheus → Dashboard Backend
- Backend queries Prometheus
- Aggregates metrics
- Returns JSON

### Dashboard Backend → Dashboard Frontend
- Frontend fetches `/api/v1/monitoring`
- Every 10 seconds
- Updates UI with real values

### Self-Heal Script → PulseGuard
- Checks `/health` endpoint
- If failing: restarts container
- If still failing: triggers rollback
- Updates metrics file

---

## 🐛 Troubleshooting

### Dashboard shows "CONNECTION ERROR"
**Fix**: The failure simulation might be on. Turn it off:
```bash
wsl curl -X POST http://localhost:8000/api/v1/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Dashboard shows "—" or "N/A"
**Fix**: Wait 10 seconds for next poll, or click "Refresh" button

### Charts not updating
**Check**: Open browser console (F12) and look for errors in Network tab

### "Cannot connect to backend"
**Check services are running**:
```bash
wsl docker compose ps
```

All should show "Up" status.

---

## ✅ Success Checklist

After completing all demos, you should have seen:

- [x] Dashboard displaying real CPU percentage
- [x] Dashboard displaying real memory usage
- [x] Live charts updating every 10 seconds
- [x] Health endpoint returning healthy status
- [x] Simulated failure making health return 500 error
- [x] Self-healing script detecting and fixing the failure
- [x] Metrics increasing (recovery attempts +1)
- [x] Prometheus showing target health
- [x] Grafana dashboards with real data
- [x] Load generation affecting metrics

---

## 🎯 Key Takeaways

**What PulseGuard Monitors**: Itself (a demo FastAPI application) + your computer's resources

**What Failures It Detects**: When `/health` returns HTTP 500 instead of 200

**What It Self-Heals**: Restarts the PulseGuard container when health checks fail

**What It Rolls Back**: If restart fails, it deploys the previous version from `state.json`

**What the Dashboard Shows**: Real CPU, RAM, disk metrics from your computer + PulseGuard's self-healing statistics

---

## 🚀 Next Steps

1. Leave everything running
2. Open the dashboard and Prometheus side by side
3. Trigger failures and watch the automatic recovery
4. Check Grafana for historical trends
5. Try the load generation script and watch metrics spike

**You now have a complete DevOps monitoring and self-healing platform running!**
