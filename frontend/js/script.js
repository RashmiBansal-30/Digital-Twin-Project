const API_BASE = (window.location.protocol.startsWith('http')) ? window.location.origin : 'http://127.0.0.1:8000';

let tempChart = null;
let rpmChart = null;
let pressureChart = null;
let pollInterval = null;
let engine3d = null;
let isSimulationRunning = true;
let currentSpeedMultiplier = 1.0;

const MAX_CHART_POINTS = 20;
const timeLabels = [];
const chtData = [];
const oilTempData = [];
const egtData = [];
const rpmData = [];
const loadData = [];
const oilPressData = [];
const vibData = [];

document.addEventListener('DOMContentLoaded', () => {
  // Initialize 3D Aero Engine
  if (typeof AeroEngine3D !== 'undefined') {
    engine3d = new AeroEngine3D('canvas3d-container', {
      onComponentSelect: (data) => showComponentInspector(data)
    });
  }

  initCharts();
  fetchModelMetrics();
  startPolling();
});

function initCharts() {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    scales: {
      x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: '#1e293b' } },
      y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: '#1e293b' } }
    },
    plugins: { legend: { labels: { color: '#f0f4f8', font: { size: 11 } } } }
  };

  const ctxTemp = document.getElementById('tempChart').getContext('2d');
  tempChart = new Chart(ctxTemp, {
    type: 'line',
    data: {
      labels: timeLabels,
      datasets: [
        { label: 'CHT (°C)', data: chtData, borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', tension: 0.3, fill: true },
        { label: 'Oil Temp (°C)', data: oilTempData, borderColor: '#eab308', backgroundColor: 'rgba(234, 179, 8, 0.1)', tension: 0.3, fill: true },
        { label: 'EGT (°C)', data: egtData, borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', tension: 0.3, fill: false }
      ]
    },
    options: chartOptions
  });

  const ctxRpm = document.getElementById('rpmChart').getContext('2d');
  rpmChart = new Chart(ctxRpm, {
    type: 'line',
    data: {
      labels: timeLabels,
      datasets: [
        { label: 'RPM', data: rpmData, borderColor: '#22c55e', yAxisID: 'y', tension: 0.3 },
        { label: 'Load (%)', data: loadData, borderColor: '#a855f7', yAxisID: 'y1', tension: 0.3 }
      ]
    },
    options: {
      ...chartOptions,
      scales: {
        ...chartOptions.scales,
        y: { type: 'linear', position: 'left', ticks: { color: '#22c55e' }, grid: { color: '#1e293b' } },
        y1: { type: 'linear', position: 'right', min: 0, max: 100, ticks: { color: '#a855f7' }, grid: { drawOnChartArea: false } }
      }
    }
  });

  const ctxPress = document.getElementById('pressureChart').getContext('2d');
  pressureChart = new Chart(ctxPress, {
    type: 'line',
    data: {
      labels: timeLabels,
      datasets: [
        { label: 'Oil Press (bar)', data: oilPressData, borderColor: '#38bdf8', yAxisID: 'y', tension: 0.3 },
        { label: 'Vibration (g)', data: vibData, borderColor: '#f97316', yAxisID: 'y1', tension: 0.3 }
      ]
    },
    options: {
      ...chartOptions,
      scales: {
        ...chartOptions.scales,
        y: { type: 'linear', position: 'left', ticks: { color: '#38bdf8' }, grid: { color: '#1e293b' } },
        y1: { type: 'linear', position: 'right', ticks: { color: '#f97316' }, grid: { drawOnChartArea: false } }
      }
    }
  });
}

function startPolling() {
  if (pollInterval) clearInterval(pollInterval);
  fetchDigitalTwinState();
  pollInterval = setInterval(fetchDigitalTwinState, 1000);
}

async function fetchDigitalTwinState() {
  try {
    const res = await fetch(`${API_BASE}/api/twin/current`);
    if (!res.ok) throw new Error('API server returned error');
    const state = await res.json();

    const healthRes = await fetch(`${API_BASE}/api/health`);
    if (healthRes.ok) {
      const hData = await healthRes.json();
      isSimulationRunning = hData.simulation_running;
      if (hData.speed_multiplier) currentSpeedMultiplier = hData.speed_multiplier;
    }

    updateConnectionStatus(true);
    updateDashboardUI(state);
    fetchAuditLog();
  } catch (err) {
    console.warn('Backend disconnected:', err);
    updateConnectionStatus(false);
  }
}

function updateConnectionStatus(isConnected) {
  const dot = document.getElementById('status-dot');
  const text = document.getElementById('status-text');

  if (isConnected) {
    dot.className = 'dot online';
    text.textContent = 'Backend Online';
  } else {
    dot.className = 'dot offline';
    text.textContent = 'Disconnected';
  }
}

function updateDashboardUI(state) {
  const telemetry = state.telemetry || {};
  const prediction = state.prediction || {};
  const health = state.health || {};
  const reliability = state.reliability || {};

  const currentRpm = telemetry.rpm ? telemetry.rpm : 2800;
  const fault = prediction.predicted_fault || 'Normal';

  // Update Mission Phase Status Banner & Mode Button Highlight
  if (state.mission_phase_text) {
    document.getElementById('mission-phase-text').textContent = state.mission_phase_text;
  }
  if (state.simulation_mode) {
    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
    let id = 'mode-auto';
    if (state.simulation_mode === 'dataset_replay') id = 'mode-dataset';
    else if (state.simulation_mode === 'manual') id = 'mode-manual';
    const activeBtn = document.getElementById(id);
    if (activeBtn) activeBtn.classList.add('active');
  }

  // Update 3D Engine Instance
  if (engine3d) {
    engine3d.updateRPM(currentRpm, isSimulationRunning, currentSpeedMultiplier);
    engine3d.updateFaultState(fault, telemetry, health);
  }

  // Update Subsystem Root-Cause Fault Differentiation Panel
  updateRootCausePanel(fault, telemetry);

  // KPI 1: Health Score
  const healthScore = health.health_score !== undefined ? health.health_score : '--';
  const healthStatus = health.health_status || 'Unknown';
  document.getElementById('kpi-health-score').textContent = healthScore;
  const healthBadge = document.getElementById('kpi-health-status');
  healthBadge.textContent = healthStatus;
  healthBadge.className = `kpi-badge badge-${healthStatus.toLowerCase()}`;

  // KPI 2: Fault Prediction
  const conf = prediction.confidence ? (prediction.confidence * 100).toFixed(1) : '--';
  document.getElementById('kpi-predicted-fault').textContent = fault;
  document.getElementById('kpi-confidence').textContent = `Confidence: ${conf}%`;

  // KPI 3: Mission Risk Level
  const riskLevel = reliability.risk_level || 'Low Risk';
  const riskScore = reliability.risk_score !== undefined ? reliability.risk_score : '--';
  document.getElementById('kpi-risk-level').textContent = riskLevel;
  document.getElementById('kpi-risk-score').textContent = `Risk Index: ${riskScore}/100`;

  // KPI 4: Key Telemetry
  document.getElementById('kpi-rpm').textContent = Math.round(currentRpm);
  document.getElementById('kpi-load').textContent = telemetry.engine_load ? Math.round(telemetry.engine_load) : '--';
  document.getElementById('kpi-vibration').textContent = telemetry.vibration ? telemetry.vibration.toFixed(2) : '--';

  // Subsystem Values
  document.getElementById('val-cht').textContent = telemetry.cylinder_head_temperature ? `${telemetry.cylinder_head_temperature.toFixed(1)} °C` : '--';
  document.getElementById('val-oil').textContent = `${telemetry.oil_pressure ? telemetry.oil_pressure.toFixed(2) : '--'} bar | ${telemetry.oil_temperature ? telemetry.oil_temperature.toFixed(1) : '--'} °C`;
  document.getElementById('val-egt').textContent = telemetry.exhaust_gas_temperature ? `${telemetry.exhaust_gas_temperature.toFixed(1)} °C` : '--';
  document.getElementById('val-fuel').textContent = `${telemetry.fuel_flow ? telemetry.fuel_flow.toFixed(1) : '--'} L/h | ${telemetry.manifold_pressure ? telemetry.manifold_pressure.toFixed(2) : '--'} bar`;
  document.getElementById('val-vib').textContent = telemetry.vibration ? `${telemetry.vibration.toFixed(2)} g` : '--';
  document.getElementById('val-amb').textContent = telemetry.ambient_temperature ? `${telemetry.ambient_temperature.toFixed(1)} °C` : '--';

  // Mission Risk Panel
  const riskBanner = document.getElementById('risk-display-banner');
  riskBanner.textContent = riskLevel.toUpperCase();
  if (riskLevel.includes('High')) {
    riskBanner.className = 'risk-level-display badge-critical';
  } else if (riskLevel.includes('Medium')) {
    riskBanner.className = 'risk-level-display badge-warning';
  } else {
    riskBanner.className = 'risk-level-display badge-healthy';
  }

  document.getElementById('risk-recommendation').textContent = reliability.recommendation || '--';
  document.getElementById('risk-explanation-text').textContent = reliability.explanation || '--';

  // Alerts List
  updateAlertsList(health.alerts || []);

  // Charts update
  if (isSimulationRunning && state.timestamp) {
    const timestamp = state.timestamp.split(' ')[1] || state.timestamp;
    pushChartData(
      timestamp,
      telemetry.cylinder_head_temperature,
      telemetry.oil_temperature,
      telemetry.exhaust_gas_temperature,
      currentRpm,
      telemetry.engine_load,
      telemetry.oil_pressure,
      telemetry.vibration
    );
  }
}

function updateRootCausePanel(fault, telemetry) {
  const badge = document.getElementById('root-cause-badge');
  const sub = document.getElementById('cause-subsystem');
  const mech = document.getElementById('cause-mechanics');
  const telem = document.getElementById('cause-telemetry');
  const act = document.getElementById('cause-action');

  if (fault === 'Overheating') {
    badge.textContent = 'THERMAL OVERHEATING';
    badge.className = 'kpi-badge badge-critical';
    sub.textContent = 'Cylinder Heads, Valves & Cooling Fins';
    mech.textContent = 'Cooling fin airflow restriction or lean combustion causes extreme thermal accumulation inside combustion chambers.';
    telem.textContent = `CHT ${telemetry.cylinder_head_temperature ? telemetry.cylinder_head_temperature.toFixed(1) : 205}°C (Limit 210°C) | EGT ${telemetry.exhaust_gas_temperature ? telemetry.exhaust_gas_temperature.toFixed(1) : 690}°C`;
    act.textContent = 'Enrich fuel mixture, adjust cowl flap opening, or lower engine load % immediately.';

  } else if (fault === 'Lubrication Fault') {
    badge.textContent = 'LUBRICATION FAILURE';
    badge.className = 'kpi-badge badge-critical';
    sub.textContent = 'Oil Sump, Pump & Crankshaft Bearings';
    mech.textContent = 'Oil pump pressure loss causes oil film breakdown between crankshaft journals and main bearing shells.';
    telem.textContent = `Oil Press ${telemetry.oil_pressure ? telemetry.oil_pressure.toFixed(2) : 2.8} bar (Limit 2.2 bar) | Oil Temp ${telemetry.oil_temperature ? telemetry.oil_temperature.toFixed(1) : 100}°C`;
    act.textContent = 'Inspect oil pressure relief valve, check sump fluid level, and reduce flight RPM.';

  } else if (fault === 'Mechanical/Vibration Fault') {
    badge.textContent = 'MECHANICAL VIBRATION';
    badge.className = 'kpi-badge badge-critical';
    sub.textContent = 'Connecting Rod Big-End Caps & Wrist Pins';
    mech.textContent = 'Connecting rod bearing clearance play causes mechanical rod knocking, wrist pin wear, and structural oscillation.';
    telem.textContent = `Vibration ${telemetry.vibration ? telemetry.vibration.toFixed(2) : 0.75}g (Limit 0.70g) | RPM Instability ±120`;
    act.textContent = 'Check propeller dynamic balance and inspect connecting rod journal cap bolts.';

  } else {
    badge.textContent = 'NOMINAL OPERATION';
    badge.className = 'kpi-badge badge-healthy';
    sub.textContent = 'All Subsystems Nominal';
    mech.textContent = 'All mechanical components, fluid pressures, and combustion temperatures operate within baseline tolerances.';
    telem.textContent = `CHT ${telemetry.cylinder_head_temperature ? telemetry.cylinder_head_temperature.toFixed(1) : 170}°C | Oil ${telemetry.oil_pressure ? telemetry.oil_pressure.toFixed(2) : 4.2} bar | Vibration ${telemetry.vibration ? telemetry.vibration.toFixed(2) : 0.25}g`;
    act.textContent = 'Continue standard flight profile automated telemetry logging.';
  }
}

function updateAlertsList(alerts) {
  const container = document.getElementById('alerts-container');
  if (!alerts || alerts.length === 0) {
    container.innerHTML = '<div class="no-alerts"><i class="fa-solid fa-circle-check"></i> All parameters operating within nominal thresholds.</div>';
    return;
  }

  container.innerHTML = alerts.map(a => `
    <div class="alert-item ${a.severity}">
      <i class="fa-solid ${a.severity === 'CRITICAL' ? 'fa-triangle-exclamation' : 'fa-circle-exclamation'}"></i>
      <div>
        <strong>[${a.severity}]</strong> ${a.message}
      </div>
    </div>
  `).join('');
}

function pushChartData(timeStr, cht, oilTemp, egt, rpm, load, oilPress, vib) {
  if (timeLabels.length >= MAX_CHART_POINTS) {
    timeLabels.shift();
    chtData.shift();
    oilTempData.shift();
    egtData.shift();
    rpmData.shift();
    loadData.shift();
    oilPressData.shift();
    vibData.shift();
  }

  timeLabels.push(timeStr);
  chtData.push(cht);
  oilTempData.push(oilTemp);
  egtData.push(egt);
  rpmData.push(rpm);
  loadData.push(load);
  oilPressData.push(oilPress);
  vibData.push(vib);

  tempChart.update();
  rpmChart.update();
  pressureChart.update();
}

async function fetchAuditLog() {
  try {
    const res = await fetch(`${API_BASE}/api/telemetry/history?limit=15`);
    if (!res.ok) return;
    const history = await res.json();

    const tbody = document.getElementById('telemetry-table-body');
    if (!history || history.length === 0) return;

    tbody.innerHTML = history.map(row => {
      const ts = row.timestamp || '--';
      const rpm = row.rpm ? Math.round(row.rpm) : '--';
      const op = row.oil_pressure ? row.oil_pressure.toFixed(2) : '--';
      const ot = row.oil_temperature ? row.oil_temperature.toFixed(1) : '--';
      const cht = row.cylinder_head_temperature ? row.cylinder_head_temperature.toFixed(1) : '--';
      const egt = row.exhaust_gas_temperature ? row.exhaust_gas_temperature.toFixed(1) : '--';
      const vib = row.vibration ? row.vibration.toFixed(2) : '--';
      const fault = row.predicted_fault || '--';
      const health = row.health_score !== undefined ? row.health_score : '--';
      const risk = row.risk_level || '--';

      return `
        <tr>
          <td>${ts}</td>
          <td>${rpm}</td>
          <td>${op}</td>
          <td>${ot}</td>
          <td>${cht}</td>
          <td>${egt}</td>
          <td>${vib}</td>
          <td><strong>${fault}</strong></td>
          <td>${health}</td>
          <td>${risk}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.warn('Error fetching audit log:', err);
  }
}

async function fetchModelMetrics() {
  try {
    const res = await fetch(`${API_BASE}/api/models/metrics`);
    if (!res.ok) return;
    const metrics = await res.json();

    const tbody = document.getElementById('metrics-table-body');
    tbody.innerHTML = Object.keys(metrics).map(modelName => {
      const m = metrics[modelName];
      return `
        <tr>
          <td><strong>${modelName}</strong></td>
          <td>${(m.accuracy * 100).toFixed(2)}%</td>
          <td>${(m.precision_macro * 100).toFixed(2)}%</td>
          <td>${(m.recall_macro * 100).toFixed(2)}%</td>
          <td>${(m.f1_macro * 100).toFixed(2)}%</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.warn('Error fetching model metrics:', err);
  }
}

/* Simulation Controls */
async function startSimulation() {
  await fetch(`${API_BASE}/api/simulation/start`, { method: 'POST' });
  isSimulationRunning = true;
}

async function pauseSimulation() {
  await fetch(`${API_BASE}/api/simulation/pause`, { method: 'POST' });
  isSimulationRunning = false;
  if (engine3d) engine3d.updateRPM(0, false, currentSpeedMultiplier);
}

async function resumeSimulation() {
  await fetch(`${API_BASE}/api/simulation/resume`, { method: 'POST' });
  isSimulationRunning = true;
}

async function resetSimulation() {
  await fetch(`${API_BASE}/api/simulation/reset`, { method: 'POST' });
  isSimulationRunning = true;
  timeLabels.length = 0;
  chtData.length = 0;
  oilTempData.length = 0;
  egtData.length = 0;
  rpmData.length = 0;
  loadData.length = 0;
  oilPressData.length = 0;
  vibData.length = 0;
  tempChart.update();
  rpmChart.update();
  pressureChart.update();
}

async function onRpmSliderInput(val) {
  document.getElementById('rpm-slider-val').textContent = `${val} RPM`;
  await fetch(`${API_BASE}/api/simulation/rpm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rpm: parseFloat(val) })
  });
}

async function setSimulationSpeed(multiplier) {
  currentSpeedMultiplier = multiplier;
  await fetch(`${API_BASE}/api/simulation/speed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ speed: multiplier })
  });

  document.querySelectorAll('.speed-btn').forEach(btn => btn.classList.remove('active'));
  const speedId = 'speed-' + String(multiplier).replace('.', '');
  const activeBtn = document.getElementById(speedId);
  if (activeBtn) activeBtn.classList.add('active');

  if (engine3d) {
    engine3d.updateRPM(engine3d.currentRPM, isSimulationRunning, multiplier);
  }
}

async function setSimulationMode(mode) {
  await fetch(`${API_BASE}/api/simulation/mode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: mode })
  });

  document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
  let id = 'mode-auto';
  if (mode === 'dataset_replay') id = 'mode-dataset';
  else if (mode === 'manual') id = 'mode-manual';

  const activeBtn = document.getElementById(id);
  if (activeBtn) activeBtn.classList.add('active');
}

async function setFaultScenario(faultType) {
  await fetch(`${API_BASE}/api/simulation/fault`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fault_type: faultType })
  });

  document.querySelectorAll('.scenario-btn').forEach(btn => btn.classList.remove('active'));
  let id = 'scenario-normal';
  if (faultType === 'Overheating') id = 'scenario-overheating';
  else if (faultType === 'Lubrication Fault') id = 'scenario-lubrication';
  else if (faultType === 'Mechanical/Vibration Fault') id = 'scenario-vibration';

  const btn = document.getElementById(id);
  if (btn) btn.classList.add('active');
}

async function changeModel(modelType) {
  await fetch(`${API_BASE}/api/model/select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_type: modelType })
  });
}

/* 3D Viewport Controls & Component Inspection Overlay */
function toggleCutawayView() {
  if (engine3d) engine3d.toggleExplodedView();
}

function showComponentInspector(data) {
  const overlay = document.getElementById('inspector-overlay');
  const title = document.getElementById('inspector-title');
  const body = document.getElementById('inspector-body');

  overlay.style.display = 'block';
  title.innerHTML = `<i class="fa-solid fa-microscope"></i> ${data.name}`;

  body.innerHTML = `
    <h4>Purpose</h4>
    <p>${data.purpose}</p>
    <h4>Operation Principle</h4>
    <p>${data.operation}</p>
    <h4>Associated Telemetry</h4>
    <p><span class="inspector-tag">${data.telemetry}</span></p>
    <h4>Fault Indication Signal</h4>
    <p style="color: var(--accent-yellow);">${data.faultMeaning}</p>
  `;
}

function toggleInspectorHint() {
  const overlay = document.getElementById('inspector-overlay');
  if (overlay.style.display === 'none' || !overlay.style.display) {
    overlay.style.display = 'block';
  } else {
    overlay.style.display = 'none';
  }
}

function closeInspectorOverlay() {
  document.getElementById('inspector-overlay').style.display = 'none';
}
