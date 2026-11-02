# ☀️ HelioOps™ Copilot

> **Autonomous Industrial Telemetry & Anomaly Analysis Suite for Solar PV + BESS (Battery Energy Storage Systems)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-emerald.svg)]()
[![Zero Cloud Cost](https://img.shields.io/badge/Compute-Edge%20%2F%20Client--Side-orange.svg)]()

---

## ⚡ Overview

**HelioOps™ Copilot** is a high-throughput, physics-informed telemetry analytics engine engineered for solar asset managers, battery test benches, and renewable microgrid operators. 

It eliminates hours of manual spreadsheet processing by automating data ingestion, electrical compliance verification, failure-mode clustering, and client-ready executive PDF report generation.

### 🎯 Key Capabilities

* **Sub-Second Telemetry Ingestion:** Processes 100,000+ multi-channel data points (1-second to 1-minute interval logs) directly in memory or client-side browser with zero latency.
* **Physics-Informed Compliance Verification:**
  * **IEEE 1547 / EN 50160 Grid Standards:** Real-time detection of grid voltage sags ($V < 207\text{V}$) and overvoltage surges ($V > 253\text{V}$).
  * **Inverter Trip Detection:** Flags unscheduled midday inverter lockouts ($P = 0\text{ kW}$ under daylight conditions) with energy-loss estimation.
  * **Inverter Power Clipping:** Quantifies generation curtailment and inverter saturation plateaus during peak irradiance.
  * **BESS Thermal Safety:** Continuous thermal runaway monitoring ($T > 45^\circ\text{C}$) and charging rate tracking.
* **Zero-Leak Data Privacy:** Full client-side JavaScript engine option ensures sensitive commercial generation data **never leaves the user's browser**.
* **1-Click Executive PDF Export:** Built-in clean print formatting designed for asset managers and compliance audits.

---

## 🛠️ Architecture

```
Raw Telemetry CSV (10k - 500k rows)
                │
                ├───> [Browser / Edge Engine] (index.html)
                │         ├── 60 FPS WebGL Multi-Trace Charts (Plotly)
                │         ├── Fast Client-Side Physics Verification
                │         └── 1-Click Printable Compliance PDF
                │
                └───> [Python High-Throughput Engine] (helio_engine.py / server.py)
                          ├── Trapezoidal Energy Yield Integration (∫ P dt)
                          ├── Moving-window Signal Filtering & Anomaly Clustering
                          └── JSON Schema Payload for Claude / GPT-4o Diagnostics
```

---

## 🚀 Quickstart

### Option 1: Zero-Installation Web Version
Open `index.html` directly in any web browser, or access the live deployment:
👉 **[Live HelioOps Web App](https://dbaigara.github.io/helioops/)**

### Option 2: Run Local Python Server (Zero Dependencies)
```bash
# Clone the repository
git clone https://github.com/dbaigara/helioops.git
cd helioops

# Run with standard Python (no pip packages strictly required!)
python3 server.py
```
Open **http://localhost:8765** in your browser.

---

## 📊 Supported Telemetry Schema

HelioOps automatically detects and handles multi-parameter CSV logs with standard headers:

| Parameter | Unit | Description |
| :--- | :--- | :--- |
| `timestamp` | ISO 8601 | Standard date-time format (`YYYY-MM-DD HH:MM:SS`) |
| `grid_voltage_v` | Volts (V) | AC grid feed voltage (230V / 400V nominal) |
| `pv_power_kw` | Kilowatts (kW) | Solar array active power output |
| `battery_soc_pct` | % | Battery Energy Storage System State of Charge |
| `battery_temp_c` | °C | Rack / module temperature sensor feed |
| `inverter_efficiency_pct` | % | Inverter instantaneous conversion efficiency |

---

## 📄 License
MIT License. Created by [D. Baigara](https://github.com/dbaigara).
