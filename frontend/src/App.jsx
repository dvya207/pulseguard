import { useState, useEffect, useCallback } from "react";
import {
  Activity, Server, ShieldCheck, RefreshCw,
  LayoutDashboard, GitBranch, HeartPulse,
  Bell, Settings, Cpu, HardDrive, Zap,
  CheckCircle2, AlertTriangle, Clock, Loader2
} from "lucide-react";

import {
  AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";

import "./App.css";

const deployments = [
  { version: "v1.4.0", description: "Production deployment", time: "Latest", status: "Successful" },
  { version: "v1.2.0", description: "Automatic rollback", time: "Previous", status: "Rolled back" },
  { version: "v1.2.0", description: "Previous release", time: "Earlier", status: "Successful" },
];

function MetricCard({ title, value, detail, icon: Icon, color, loading = false, error = false }) {
  let displayValue = value;
  let displayDetail = detail;
  
  if (loading) {
    displayValue = "—";
    displayDetail = "Loading...";
  } else if (error) {
    displayValue = "N/A";
    displayDetail = "Unable to retrieve";
  } else if (value === undefined || value === null) {
    displayValue = "—";
    displayDetail = "Metric not available";
  }

  return (
    <div className={`metric-card ${error ? 'metric-error' : ''}`}>
      <div className="metric-top">
        <span>{title}</span>
        <div className={`metric-icon ${color}`}>{loading ? <Loader2 size={19} className="spinning" /> : <Icon size={19} />}</div>
      </div>
      <h2>{displayValue}</h2>
      <p>{displayDetail}</p>
    </div>
  );
}

function ResourceBar({ icon: Icon, label, used, total, unit, percent, color = "blue", loading = false, error = false }) {
  let displayPercent = percent;
  let displayUsed = used;
  let displayTotal = total;
  
  if (loading) {
    displayPercent = 0;
    displayUsed = "—";
    displayTotal = "—";
  } else if (error || used === null || total === null || percent === null) {
    displayPercent = 0;
    displayUsed = "N/A";
    displayTotal = "N/A";
  }

  return (
    <div className={`resource-item ${error ? 'resource-error' : ''}`}>
      <div><Icon size={18} /><span>{label}</span><strong>{displayUsed} / {displayTotal} {unit}</strong></div>
      <div className={`progress ${color}`}><span style={{ width: `${Math.min(displayPercent || 0, 100)}%` }} /></div>
    </div>
  );
}

function ContainerMetrics({ containers, loading, error }) {
  if (loading) {
    return <div className="container-loading"><Loader2 size={18} className="spinning" /> Loading container metrics...</div>;
  }
  
  if (error || !containers || containers.length === 0) {
    return <div className="container-error"><AlertTriangle size={17} /> Unable to load container metrics</div>;
  }

  return (
    <div className="container-list">
      {containers.slice(0, 5).map((container, idx) => (
        <div key={idx} className="container-item">
          <div className="container-icon"><Server size={16} /></div>
          <div className="container-info">
            <strong>{container.metric}</strong>
            <span>CPU: {(container.cpu * 100).toFixed(2)}%</span>
          </div>
          <div className="container-memory">
            <span>{(container.memory / 1024 / 1024 / 1024).toFixed(2)} GB</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [chartData, setChartData] = useState([]);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch("/api/v1/monitoring");
      if (!response.ok) throw new Error("Failed to fetch metrics");
      
      const data = await response.json();
      setMetrics(data.metrics);
      setError(false);
      setLastUpdated(new Date());

      // Update chart data with real values
      const now = new Date();
      const timeStr = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
      
      setChartData(prev => {
        const newData = [...prev, { 
          time: timeStr, 
          cpu: data.metrics.cpu_usage_percent || 0, 
          memory: data.metrics.memory_used_percent || 0 
        }];
        // Keep last 20 data points
        return newData.slice(-20);
      });
    } catch (err) {
      console.error("Failed to fetch metrics:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

  const cpuPercent = metrics?.cpu_usage_percent;
  const memoryUsed = metrics?.memory_used_bytes;
  const memoryTotal = metrics?.memory_total_bytes;
  const memoryPercent = metrics?.memory_used_percent;
  const diskUsed = metrics?.disk_used_bytes;
  const diskTotal = metrics?.disk_total_bytes;
  const diskPercent = metrics?.disk_used_percent;
  const containerMetrics = metrics?.container_cpu_usage || [];
  const appHealth = metrics?.application_up === 1;
  const recoveryAttempts = metrics?.recovery_attempts;
  const successfulRecoveries = metrics?.successful_recoveries;
  const failedRecoveries = metrics?.failed_recoveries;
  const rollbacks = metrics?.rollbacks;

  // Format bytes to human readable
  const formatBytes = (bytes) => {
    if (bytes === null || bytes === undefined) return "N/A";
    const gb = bytes / (1024 * 1024 * 1024);
    return gb.toFixed(2);
  };

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={25} /></div>
          <div>
            <h2>PulseGuard</h2>
            <span>DEVOPS CONTROL CENTER</span>
          </div>
        </div>

        <p className="nav-label">WORKSPACE</p>

        <nav>
          <a className="nav-item active" href="#"><LayoutDashboard size={18} /> Overview</a>
          <a className="nav-item" href="http://localhost:9090" target="_blank" title="Open Prometheus"><Activity size={18} /> Monitoring</a>
          <a className="nav-item" href="http://localhost:8000/docs" target="_blank" title="Open API Docs"><GitBranch size={18} /> API Docs</a>
          <a className="nav-item" href="#self-healing" onClick={(e) => { e.preventDefault(); alert('Self-Healing Stats:\n\n✅ Recovery Attempts: 10\n✅ Successful: 10\n⚠️ Failed: 0\n🔄 Rollbacks: 1\n\nCheck metrics.json for details'); }}><HeartPulse size={18} /> Self-Healing</a>
          <a className="nav-item" href="http://localhost:9093" target="_blank" title="Open Alertmanager"><Bell size={18} /> Alerts</a>
        </nav>

        <div className="sidebar-bottom">
          <a className="nav-item" href="http://localhost:3000" target="_blank" title="Open Grafana"><Settings size={18} /> Grafana</a>
          <div className="profile">
            <div className="avatar">PG</div>
            <div><strong>PulseGuard</strong><span>System Admin</span></div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace / Overview</p>
            <h1>System Overview</h1>
            <p className="subtitle">Monitor your infrastructure and deployment health.</p>
          </div>
          <div className="top-actions">
            <span className={`live-status ${error ? 'status-error' : ''}`}>
              <span /> {error ? "CONNECTION ERROR" : "SYSTEM OPERATIONAL"}
            </span>
            <button className="refresh-btn" onClick={fetchMetrics}>
              <RefreshCw size={16} /> Refresh
            </button>
          </div>
        </header>

        <section className="welcome-banner">
          <div>
            <span className="eyebrow">PULSEGUARD MONITORING</span>
            <h2>Your infrastructure is looking healthy.</h2>
            <p>Monitor performance, deployments and automated recovery in one place.</p>
          </div>
          <div className="banner-icon"><ShieldCheck size={65} /></div>
        </section>

        <section className="section-heading">
          <div><h3>System metrics</h3><p>Key infrastructure indicators</p></div>
          {lastUpdated && <span className="last-updated">Updated: {lastUpdated.toLocaleTimeString()}</span>}
        </section>

        <section className="metrics-grid">
          <MetricCard 
            title="Application Health" 
            value={appHealth ? "Healthy" : "Down"} 
            detail={appHealth ? "API health check passed" : "Service unavailable"} 
            icon={HeartPulse} 
            color={appHealth ? "green" : "red"}
            loading={loading}
            error={error && !appHealth}
          />
          <MetricCard title="Current Version" value="1.4.0" detail="Currently deployed" icon={GitBranch} color="blue" />
          <MetricCard 
            title="Recovery Attempts" 
            value={recoveryAttempts !== undefined ? recoveryAttempts : "—"} 
            detail="Recorded recovery attempts" 
            icon={Zap} 
            color="orange"
            loading={loading}
          />
          <MetricCard 
            title="Successful Recoveries" 
            value={successfulRecoveries !== undefined ? successfulRecoveries : "—"} 
            detail="Recorded successful recoveries" 
            icon={CheckCircle2} 
            color="green"
            loading={loading}
          />
        </section>

        <section className="content-grid">
          <div className="panel chart-panel">
            <div className="panel-heading">
              <div><h3>Infrastructure performance</h3><p>CPU and memory utilization over time</p></div>
              {!loading && !error && <span className="live-label">LIVE DATA</span>}
              {loading && <span className="loading-label">LOADING...</span>}
            </div>
            <div className="chart">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="cpuFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="memoryFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#a78bfa" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#263244" strokeDasharray="3 3" />
                  <XAxis dataKey="time" stroke="#8190a5" tickLine={false} />
                  <YAxis stroke="#8190a5" tickLine={false} domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: "#111c2c", border: "1px solid #334155", borderRadius: 10 }} />
                  <Area type="monotone" dataKey="cpu" stroke="#38bdf8" fill="url(#cpuFill)" strokeWidth={2} name="CPU %" />
                  <Area type="monotone" dataKey="memory" stroke="#a78bfa" fill="url(#memoryFill)" strokeWidth={2} name="Memory %" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-legend">
              <span><i className="blue-dot" /> CPU Usage</span>
              <span><i className="purple-dot" /> Memory Usage</span>
            </div>
          </div>

          <div className="panel resource-panel">
            <div className="panel-heading"><div><h3>Resource overview</h3><p>Host system resources</p></div></div>
            <ResourceBar 
              icon={Cpu} 
              label="CPU Usage" 
              used={cpuPercent ? `${cpuPercent.toFixed(1)}%` : "—"}
              total="100"
              unit="%"
              percent={cpuPercent}
              color="blue"
              loading={loading}
              error={error}
            />
            <ResourceBar 
              icon={HardDrive} 
              label="Memory Usage" 
              used={formatBytes(memoryUsed)}
              total={formatBytes(memoryTotal)}
              unit="GB"
              percent={memoryPercent}
              color="purple"
              loading={loading}
              error={error}
            />
            <ResourceBar 
              icon={Activity} 
              label="Disk Usage" 
              used={formatBytes(diskUsed)}
              total={formatBytes(diskTotal)}
              unit="GB"
              percent={diskPercent}
              color="green"
              loading={loading}
              error={error}
            />
            <div className={`resource-note ${loading ? 'resource-note-loading' : ''}`}>
              <Activity size={17} /> 
              {loading ? "Loading live metrics..." : "Live resource metrics from Node Exporter"}
            </div>
          </div>
        </section>

        <section className="content-grid bottom-grid">
          <div className="panel">
            <div className="panel-heading"><div><h3>Container resources</h3><p>Docker container CPU and memory usage</p></div></div>
            <ContainerMetrics containers={containerMetrics} loading={loading} error={error} />
          </div>

          <div className="panel">
            <div className="panel-heading"><div><h3>Recovery summary</h3><p>Self-healing activity</p></div></div>
            <div className="recovery-stat"><CheckCircle2 size={21} /><div><strong>{successfulRecoveries !== undefined ? successfulRecoveries : "—"}</strong><span>Successful recoveries</span></div></div>
            <div className="recovery-stat"><AlertTriangle size={21} /><div><strong>{failedRecoveries !== undefined ? failedRecoveries : "—"}</strong><span>Failed recoveries</span></div></div>
            <div className="recovery-stat"><Clock size={21} /><div><strong>{rollbacks !== undefined ? rollbacks : "—"}</strong><span>Rollback recorded</span></div></div>
          </div>
        </section>

        <footer>PulseGuard <span>•</span> DevOps Monitoring Platform <span>•</span> Real-time monitoring active</footer>
      </main>
    </div>
  );
}