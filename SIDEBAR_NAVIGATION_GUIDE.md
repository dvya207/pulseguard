# 🧭 PulseGuard Sidebar Navigation - Now Functional!

## ✅ Updated Sidebar Links

The sidebar now links to **real monitoring tools**. Here's what each option does:

---

## 📊 Navigation Options

### 1. **Overview** (Current Page)
- **Status**: ✅ Active
- **Action**: You're here - main dashboard
- **Shows**: Live metrics, charts, recovery stats

---

### 2. **Monitoring** → Opens Prometheus
- **Link**: http://localhost:9090
- **Opens in**: New tab
- **What it is**: Prometheus query interface
- **Use it for**: 
  - Run custom PromQL queries
  - See all available metrics
  - Check target health
  - Create graphs

**Try this query in Prometheus**:
```promql
rate(http_requests_total[5m])
```

---

### 3. **API Docs** → Opens FastAPI Swagger
- **Link**: http://localhost:8000/docs
- **Opens in**: New tab
- **What it is**: Interactive API documentation
- **Use it for**:
  - Test API endpoints directly
  - See request/response schemas
  - Try the failure simulation endpoint
  - View all available APIs

**Try this**: Click "POST /api/v1/simulate-failure" → Try it out → Execute

---

### 4. **Self-Healing** → Shows Stats Alert
- **Action**: Shows popup with current stats
- **What you'll see**:
  ```
  ✅ Recovery Attempts: 10
  ✅ Successful: 10
  ⚠️ Failed: 0
  🔄 Rollbacks: 1
  ```
- **Use it for**: Quick view of self-healing history

---

### 5. **Alerts** → Opens Alertmanager
- **Link**: http://localhost:9093
- **Opens in**: New tab
- **What it is**: Prometheus Alertmanager UI
- **Use it for**:
  - View active alerts
  - See silenced alerts
  - Configure alert routing
  - Check alert history

---

### 6. **Grafana** (Bottom - was "Settings")
- **Link**: http://localhost:3000
- **Opens in**: New tab
- **What it is**: Professional dashboarding tool
- **Use it for**:
  - Advanced visualization
  - Pre-built PulseGuard dashboard
  - Historical data analysis
  - Custom dashboard creation

**Login**: Check `.env` file for credentials

---

## 🎯 Quick Navigation Workflow

### Scenario 1: Investigating High CPU
```
1. See high CPU on Overview dashboard
2. Click "Monitoring" → Opens Prometheus
3. Run query: rate(node_cpu_seconds_total[5m])
4. Analyze which process is consuming CPU
```

### Scenario 2: Testing API Endpoints
```
1. Click "API Docs" → Opens Swagger UI
2. Find endpoint you want to test
3. Click "Try it out"
4. Enter parameters
5. Execute and see live response
```

### Scenario 3: Viewing Self-Healing History
```
1. Click "Self-Healing" → See popup stats
2. For details: Click "Monitoring" → Prometheus
3. Query: self_heal_success_total
4. See time-series of successful recoveries
```

### Scenario 4: Advanced Visualization
```
1. Click "Grafana" → Opens Grafana
2. Navigate to "PulseGuard Overview" dashboard
3. See professional panels with:
   - CPU usage over time
   - Memory trends
   - Request rates
   - Error rates
```

---

## 🔗 All Links at a Glance

| Sidebar Item | URL | Purpose |
|--------------|-----|---------|
| Overview | Current page | Main dashboard |
| Monitoring | http://localhost:9090 | Prometheus queries |
| API Docs | http://localhost:8000/docs | API testing |
| Self-Healing | Alert popup | Quick stats |
| Alerts | http://localhost:9093 | Alert management |
| Grafana | http://localhost:3000 | Advanced dashboards |

---

## 💡 Pro Tips

### Bookmark These Pages
Create a browser bookmark folder with all these links for quick access:
```
📁 PulseGuard
  ├─ Dashboard (localhost:5173)
  ├─ Prometheus (localhost:9090)
  ├─ Grafana (localhost:3000)
  ├─ API Docs (localhost:8000/docs)
  └─ Alertmanager (localhost:9093)
```

### Multi-Monitor Setup
Open each tool in a separate window:
- **Monitor 1**: Dashboard (localhost:5173)
- **Monitor 2**: Prometheus (localhost:9090)
- **Monitor 3**: Grafana (localhost:3000)

Watch metrics flow through the entire stack in real-time!

### Keyboard Shortcuts
- **Ctrl+Click** on any link → Open in new tab
- **Shift+Click** on any link → Open in new window

---

## 🎨 What Changed

### Before:
```
Sidebar links were non-functional placeholders
Clicking them did nothing
```

### After:
```
✅ Monitoring → Opens Prometheus
✅ API Docs → Opens FastAPI Swagger
✅ Self-Healing → Shows stats popup
✅ Alerts → Opens Alertmanager
✅ Grafana → Opens Grafana dashboards
```

---

## 🧪 Test the Links Now

1. **Refresh your dashboard**: http://localhost:5173
2. **Click "Monitoring"** → Prometheus should open
3. **Click "API Docs"** → Swagger UI should open
4. **Click "Self-Healing"** → Popup should appear
5. **Click "Alerts"** → Alertmanager should open
6. **Click "Grafana"** → Grafana should open

All links open in **new tabs** so you don't lose your dashboard!

---

## ❓ Why Not Full Pages?

Building full pages for each section would require:
- React Router setup
- 5+ additional page components
- State management across pages
- More complex navigation

**Instead**, we're linking to the **actual professional tools** (Prometheus, Grafana) which are:
- ✅ More powerful
- ✅ Industry standard
- ✅ Already running
- ✅ Better for learning real DevOps tools

This gives you the **best of both worlds**:
- Simple dashboard for quick overview
- Professional tools for deep analysis

---

## 🚀 Next Steps

1. **Refresh the dashboard** (Ctrl+R or F5)
2. **Try clicking each sidebar link**
3. **Explore Prometheus queries**
4. **Check out Grafana dashboards**
5. **Test API endpoints in Swagger**

**All sidebar navigation is now functional!** 🎉
