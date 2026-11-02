#!/usr/bin/env python3
"""
HelioOps Local SaaS Server - Zero external dependencies.
Binds to http://localhost:8765 and provides interactive UI + REST API.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from helio_engine import generate_industrial_solar_dataset, HelioAnalytics

PORT = int(os.environ.get("PORT", 8765))

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HelioOps™ - Solar & Battery Telemetry Copilot</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #090d16;
      --card: #111827;
      --border: #1f293d;
      --text: #f9fafb;
      --text-muted: #9ca3af;
      --primary: #3b82f6;
      --red: #ef4444;
      --amber: #f59e0b;
      --green: #10b981;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 24px; }
    .container { max-width: 1360px; margin: 0 auto; }
    
    /* Top Bar */
    .top-bar { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 24px; }
    .brand { display: flex; align-items: center; gap: 12px; }
    .brand-icon { font-size: 26px; }
    .brand-title { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }
    .brand-subtitle { font-size: 12px; color: var(--primary); background: #3b82f615; padding: 2px 8px; border-radius: 4px; border: 1px solid #3b82f640; font-weight: 600; }
    .btn-group { display: flex; gap: 10px; }
    button { cursor: pointer; border-radius: 6px; font-weight: 600; font-size: 13px; padding: 9px 16px; border: none; transition: 0.15s; }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: #2563eb; }
    .btn-secondary { background: #1f293d; color: var(--text); border: 1px solid var(--border); }
    .btn-secondary:hover { background: #374151; }

    /* Drag & Drop Hero Box */
    .dropzone {
      border: 2px dashed #2d3748;
      background: #0f172a80;
      border-radius: 12px;
      padding: 32px 20px;
      text-align: center;
      margin-bottom: 24px;
      cursor: pointer;
      transition: 0.2s;
    }
    .dropzone:hover, .dropzone.dragover { border-color: var(--primary); background: #1e293b60; }
    .drop-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
    .drop-desc { font-size: 13px; color: var(--text-muted); }

    /* KPI Grid */
    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }
    .kpi-label { font-size: 11px; text-transform: uppercase; font-weight: 700; color: var(--text-muted); letter-spacing: 0.5px; margin-bottom: 6px; }
    .kpi-val { font-size: 26px; font-weight: 800; }
    .kpi-sub { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

    /* AI Copilot Box */
    .ai-box {
      background: linear-gradient(135deg, #172554 0%, #0f172a 100%);
      border: 1px solid #3b82f660;
      border-radius: 10px;
      padding: 22px;
      margin-bottom: 24px;
    }
    .ai-badge { background: #38bdf8; color: #082f49; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 20px; text-transform: uppercase; }
    .ai-title { font-size: 17px; font-weight: 700; color: #93c5fd; margin: 10px 0; }
    .ai-bullets { list-style: none; margin: 12px 0; }
    .ai-bullets li { font-size: 13px; line-height: 1.6; margin-bottom: 6px; color: #e2e8f0; }
    .ai-actions-wrap { background: rgba(0, 0, 0, 0.35); border-radius: 8px; padding: 14px; margin-top: 14px; }
    .ai-actions-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-bottom: 6px; }
    .ai-actions-list li { margin-left: 18px; font-size: 13px; color: #cbd5e1; margin-bottom: 4px; }

    /* Chart Box */
    .chart-box { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 24px; }
    .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .chart-title { font-size: 14px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }

    /* Incidents Table */
    .table-box { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }
    th { text-align: left; padding: 10px 12px; color: var(--text-muted); font-size: 11px; text-transform: uppercase; border-bottom: 1px solid var(--border); }
    td { padding: 12px; border-bottom: 1px solid #1a2333; }
    .badge-crit { background: #ef444420; color: #f87171; border: 1px solid #ef444450; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-warn { background: #f59e0b20; color: #fbbf24; border: 1px solid #f59e0b50; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }
    .badge-info { background: #3b82f620; color: #60a5fa; border: 1px solid #3b82f650; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }

    /* Print Styles */
    @media print {
      body { background: white; color: black; padding: 0; }
      .dropzone, .btn-group, .top-bar button { display: none !important; }
      .kpi-card, .table-box, .chart-box { border: 1px solid #ccc; background: white; color: black; }
      .ai-box { background: #f1f5f9; color: black; border: 1px solid #cbd5e1; }
      .ai-title { color: #1e3a8a; }
      .ai-bullets li, .ai-actions-list li { color: black; }
      .top-bar { border-bottom: 2px solid #000; }
      .brand-title { color: black; }
    }
  </style>
</head>
<body>
  <div class="container">
    
    <!-- Top Header -->
    <div class="top-bar">
      <div class="brand">
        <span class="brand-icon">☀️</span>
        <div>
          <span class="brand-title">HelioOps™ Copilot</span>
          <span class="brand-subtitle">Industrial Solar & BESS Telemetry</span>
        </div>
      </div>
      <div class="btn-group">
        <button class="btn-secondary" onclick="loadSampleData()">⚡ Load Sample 24h Telemetry</button>
        <button class="btn-primary" onclick="window.print()">📥 Print Executive Report</button>
      </div>
    </div>

    <!-- Drag & Drop Upload Zone -->
    <div class="dropzone" id="drop-area" onclick="document.getElementById('file-input').click()">
      <input type="file" id="file-input" accept=".csv" style="display:none;" onchange="handleFileSelect(event)">
      <div style="font-size:32px; margin-bottom:8px;">📁</div>
      <div class="drop-title">Drop raw solar/battery telemetry CSV here, or click to browse</div>
      <div class="drop-desc">Supports 1-sec to 1-min logs with columns: timestamp, grid_voltage_v, pv_power_kw, battery_soc_pct, battery_temp_c, inverter_efficiency_pct</div>
    </div>

    <!-- KPI Summary Row -->
    <div class="kpi-row" id="kpi-section" style="display:none;">
      <div class="kpi-card">
        <div class="kpi-label">Plant Status</div>
        <div class="kpi-val" id="kpi-status" style="font-size:16px;">-</div>
        <div class="kpi-sub" id="kpi-incidents-count">-</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Daily Yield (kWh)</div>
        <div class="kpi-val" id="kpi-yield" style="color:var(--primary);">-</div>
        <div class="kpi-sub">Total energy generated</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Peak Array Power</div>
        <div class="kpi-val" id="kpi-peak">-</div>
        <div class="kpi-sub">Active peak output</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Inverter Eff / Max Temp</div>
        <div class="kpi-val" id="kpi-eff-temp">-</div>
        <div class="kpi-sub">Thermal & efficiency metrics</div>
      </div>
    </div>

    <!-- AI Diagnostic Card -->
    <div class="ai-box" id="ai-section" style="display:none;">
      <span class="ai-badge">AI Root-Cause Diagnostic</span>
      <h3 class="ai-title" id="ai-headline">-</h3>
      <ul class="ai-bullets" id="ai-observations"></ul>
      <div class="ai-actions-wrap">
        <div class="ai-actions-title">Prescribed Engineering Interventions:</div>
        <ul class="ai-actions-list" id="ai-actions"></ul>
      </div>
    </div>

    <!-- Synchronized 4-Channel Chart -->
    <div class="chart-box" id="chart-section" style="display:none;">
      <div class="chart-header">
        <div class="chart-title">Synchronized 24h Multi-Parameter Telemetry</div>
      </div>
      <div id="plotly-chart" style="height: 560px;"></div>
    </div>

    <!-- Incidents Table -->
    <div class="table-box" id="table-section" style="display:none;">
      <h3 style="font-size:15px; font-weight:700;">Recorded Compliance & Hardware Events</h3>
      <table>
        <thead>
          <tr>
            <th>Severity</th>
            <th>Event Description</th>
            <th>Start Time</th>
            <th>Duration</th>
            <th>Critical Value</th>
          </tr>
        </thead>
        <tbody id="incidents-body"></tbody>
      </table>
    </div>

  </div>

  <script>
    // Drag & drop handlers
    const dropArea = document.getElementById('drop-area');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, e => { e.preventDefault(); e.stopPropagation(); }, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
      dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });
    dropArea.addEventListener('drop', e => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) processFile(files[0]);
    });

    function handleFileSelect(e) {
      if (e.target.files.length > 0) processFile(e.target.files[0]);
    }

    function processFile(file) {
      const reader = new FileReader();
      reader.onload = function(evt) {
        sendCSVForAnalysis(evt.target.result);
      };
      reader.readAsText(file);
    }

    async function loadSampleData() {
      dropArea.innerHTML = '<div style="font-size:24px;">⏳ Generating & analyzing 86,400 solar telemetry records...</div>';
      try {
        const res = await fetch('/api/sample');
        const data = await res.json();
        renderDashboard(data);
        dropArea.innerHTML = '<div style="font-size:32px; margin-bottom:8px;">✅</div><div class="drop-title">Loaded Sample 24-Hour Telemetry Dataset</div><div class="drop-desc">Click to load another file or drop new CSV anytime</div>';
      } catch (err) {
        alert('Error loading sample data: ' + err);
      }
    }

    async function sendCSVForAnalysis(csvContent) {
      dropArea.innerHTML = '<div style="font-size:24px;">⚙️ Parsing and extracting anomalies...</div>';
      try {
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain' },
          body: csvContent
        });
        const data = await res.json();
        renderDashboard(data);
        dropArea.innerHTML = '<div style="font-size:32px; margin-bottom:8px;">✅</div><div class="drop-title">Telemetry Analyzed Successfully</div><div class="drop-desc">Drop another CSV to re-run</div>';
      } catch (err) {
        alert('Analysis error: ' + err);
      }
    }

    function renderDashboard(res) {
      document.getElementById('kpi-section').style.display = 'grid';
      document.getElementById('ai-section').style.display = 'block';
      document.getElementById('chart-section').style.display = 'block';
      document.getElementById('table-section').style.display = 'block';

      // KPIs
      const s = res.summary;
      const statusEl = document.getElementById('kpi-status');
      statusEl.innerText = s.status;
      statusEl.style.color = s.status_color === 'red' ? 'var(--red)' : (s.status_color === 'amber' ? 'var(--amber)' : 'var(--green)');
      document.getElementById('kpi-incidents-count').innerText = `${s.incidents_count} fault events detected across ${s.total_samples.toLocaleString()} rows`;
      document.getElementById('kpi-yield').innerText = s.daily_yield_kwh.toLocaleString() + ' kWh';
      document.getElementById('kpi-peak').innerText = s.peak_power_kw + ' kW';
      document.getElementById('kpi-eff-temp').innerText = `${s.inverter_eff_avg}% / ${s.max_battery_temp_c}°C`;

      // AI Box
      const ai = res.ai_diagnosis;
      document.getElementById('ai-headline').innerText = ai.headline;
      document.getElementById('ai-observations').innerHTML = ai.observations.map(o => `<li>${o}</li>`).join('');
      document.getElementById('ai-actions').innerHTML = ai.prescribed_actions.map(a => `<li>${a}</li>`).join('');

      // Plotly Multi-trace Chart
      const p = res.plot_data;
      const tracePV = {
        x: p.ts, y: p.p_pv, name: "Solar PV Output (kW)",
        type: "scattergl", mode: "lines",
        line: { color: "#f59e0b", width: 1.8 }
      };
      const traceV = {
        x: p.ts, y: p.v_grid, name: "Grid Voltage (V)",
        yaxis: "y2", type: "scattergl", mode: "lines",
        line: { color: "#38bdf8", width: 1.5 }
      };
      const traceSoC = {
        x: p.ts, y: p.soc, name: "Battery SoC (%)",
        yaxis: "y3", type: "scattergl", mode: "lines",
        line: { color: "#10b981", width: 1.5 }
      };
      const traceTemp = {
        x: p.ts, y: p.temp, name: "Battery Temp (°C)",
        yaxis: "y4", type: "scattergl", mode: "lines",
        line: { color: "#ef4444", width: 1.5 }
      };

      const layout = {
        paper_bgcolor: "transparent",
        plot_bgcolor: "#0d1424",
        grid: { rows: 4, columns: 1, pattern: "coupled", roworder: "top to bottom" },
        margin: { l: 60, r: 20, t: 20, b: 40 },
        showlegend: true,
        legend: { orientation: "h", y: 1.08, font: { color: "#9ca3af" } },
        xaxis: { title: "Time of Day", color: "#64748b", gridcolor: "#1e293b" },
        yaxis: { title: "PV (kW)", color: "#f59e0b", gridcolor: "#1e293b" },
        yaxis2: { title: "Grid (V)", color: "#38bdf8", gridcolor: "#1e293b" },
        yaxis3: { title: "SoC (%)", color: "#10b981", gridcolor: "#1e293b" },
        yaxis4: { title: "Temp (°C)", color: "#ef4444", gridcolor: "#1e293b" }
      };

      Plotly.newPlot("plotly-chart", [tracePV, traceV, traceSoC, traceTemp], layout, { responsive: true });

      // Table
      const tb = document.getElementById('incidents-body');
      tb.innerHTML = res.incidents.map(inc => {
        const badgeClass = inc.severity === 'CRITICAL' ? 'badge-crit' : (inc.severity === 'WARNING' ? 'badge-warn' : 'badge-info');
        return `
          <tr>
            <td><span class="${badgeClass}">${inc.severity}</span></td>
            <td><strong>${inc.title}</strong></td>
            <td>${inc.start_time}</td>
            <td>${inc.duration_min} min</td>
            <td>${inc.metric_label}: <strong>${inc.metric_val}</strong></td>
          </tr>
        `;
      }).join('');
    }
  </script>
</body>
</html>
"""

class HelioHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif url.path == "/api/sample":
            csv_data = generate_industrial_solar_dataset(num_points=86400)
            analytics = HelioAnalytics(csv_data)
            result = analytics.process()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/api/analyze":
            content_length = int(self.headers.get("Content-Length", 0))
            csv_body = self.rfile.read(content_length).decode("utf-8", errors="ignore")
            analytics = HelioAnalytics(csv_body)
            result = analytics.process()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def run():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, HelioHandler)
    print(f"\n[🚀] HelioOps Server is running at: http://localhost:{PORT}")
    print(f"[*] Serving interactive UI and REST API. Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    run()
