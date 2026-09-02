/**
 * app.js
 * ======
 * Water Potability FIS Dashboard — Client-side logic
 *
 * Features:
 *  - Socket.IO real-time sensor updates
 *  - WPI arc gauge (Canvas)
 *  - Chart.js time-series for WPI + sensor params
 *  - Membership degree bars
 *  - Active rule display
 *  - Manual inference via sliders
 *
 * Author: SC_CProject
 */

'use strict';

// ── Socket.IO ─────────────────────────────────────────────────────
const socket = io();

socket.on('connect', () => {
  document.getElementById('conn-badge').querySelector('.conn-dot').classList.add('connected');
  document.getElementById('conn-text').textContent = 'Live';
});
socket.on('disconnect', () => {
  document.getElementById('conn-text').textContent = 'Disconnected';
  document.querySelector('.conn-dot').classList.remove('connected');
});

// Scenario selector
document.getElementById('scenario-select').addEventListener('change', (e) => {
  socket.emit('set_scenario', { scenario: e.target.value });
});

// ── WPI Arc Gauge ─────────────────────────────────────────────────
const gaugeCanvas = document.getElementById('wpi-gauge');
const gCtx        = gaugeCanvas.getContext('2d');
const W = gaugeCanvas.width, H = gaugeCanvas.height;

const GAUGE_START = Math.PI * 0.75;  // 135°
const GAUGE_END   = Math.PI * 2.25;  // 405° (270° arc)
const GAUGE_RANGE = GAUGE_END - GAUGE_START;

let currentWPI = 5.0;
let targetWPI  = 5.0;

function wpiToColor(wpi) {
  if (wpi < 3.5) return '#ef4444';
  if (wpi < 6.5) return '#f59e0b';
  return '#22c55e';
}

function drawGauge(wpi) {
  gCtx.clearRect(0, 0, W, H);

  const cx = W / 2, cy = H / 2 + 10;
  const r  = 105;
  const lw = 14;

  // Track (background arc)
  gCtx.beginPath();
  gCtx.arc(cx, cy, r, GAUGE_START, GAUGE_END);
  gCtx.strokeStyle = 'rgba(255,255,255,0.06)';
  gCtx.lineWidth   = lw;
  gCtx.lineCap     = 'round';
  gCtx.stroke();

  // Zones: NON-POTABLE, MARGINAL, POTABLE
  const zones = [
    { from: 0.0, to: 3.5, color: 'rgba(239,68,68,0.25)' },
    { from: 3.5, to: 6.5, color: 'rgba(245,158,11,0.25)' },
    { from: 6.5, to:10.0, color: 'rgba(34,197,94,0.25)' },
  ];
  zones.forEach(z => {
    const sa = GAUGE_START + (z.from / 10) * GAUGE_RANGE;
    const ea = GAUGE_START + (z.to   / 10) * GAUGE_RANGE;
    gCtx.beginPath();
    gCtx.arc(cx, cy, r, sa, ea);
    gCtx.strokeStyle = z.color;
    gCtx.lineWidth   = lw;
    gCtx.stroke();
  });

  // Value arc
  const fillEnd  = GAUGE_START + (wpi / 10) * GAUGE_RANGE;
  const color    = wpiToColor(wpi);

  // Glow
  gCtx.save();
  gCtx.shadowColor = color;
  gCtx.shadowBlur  = 18;
  gCtx.beginPath();
  gCtx.arc(cx, cy, r, GAUGE_START, fillEnd);
  gCtx.strokeStyle = color;
  gCtx.lineWidth   = lw;
  gCtx.lineCap     = 'round';
  gCtx.stroke();
  gCtx.restore();

  // Needle dot
  const needleAngle = fillEnd;
  const nx = cx + r * Math.cos(needleAngle);
  const ny = cy + r * Math.sin(needleAngle);
  gCtx.beginPath();
  gCtx.arc(nx, ny, 7, 0, Math.PI * 2);
  gCtx.fillStyle = color;
  gCtx.shadowColor = color;
  gCtx.shadowBlur = 12;
  gCtx.fill();

  // Tick marks
  for (let v = 0; v <= 10; v += 2) {
    const angle = GAUGE_START + (v / 10) * GAUGE_RANGE;
    const x1 = cx + (r - 18) * Math.cos(angle);
    const y1 = cy + (r - 18) * Math.sin(angle);
    const x2 = cx + (r - 10) * Math.cos(angle);
    const y2 = cy + (r - 10) * Math.sin(angle);
    gCtx.beginPath();
    gCtx.moveTo(x1, y1);
    gCtx.lineTo(x2, y2);
    gCtx.strokeStyle = 'rgba(255,255,255,0.15)';
    gCtx.lineWidth = 1.5;
    gCtx.shadowBlur = 0;
    gCtx.stroke();

    // Label
    const lx = cx + (r - 30) * Math.cos(angle);
    const ly = cy + (r - 30) * Math.sin(angle);
    gCtx.fillStyle = 'rgba(255,255,255,0.3)';
    gCtx.font = '9px Inter, sans-serif';
    gCtx.textAlign = 'center';
    gCtx.textBaseline = 'middle';
    gCtx.fillText(v, lx, ly);
  }
}

// Smooth gauge animation
function animateGauge() {
  currentWPI += (targetWPI - currentWPI) * 0.12;
  drawGauge(currentWPI);

  const scoreEl = document.getElementById('wpi-score');
  const labelEl = document.getElementById('wpi-label');
  const color   = wpiToColor(currentWPI);
  scoreEl.textContent = currentWPI.toFixed(2);
  scoreEl.style.color = color;
  labelEl.style.color = color;

  const heroCard = document.getElementById('wpi-card');
  heroCard.classList.remove('state-marginal','state-danger');
  if (currentWPI < 3.5) heroCard.classList.add('state-danger');
  else if (currentWPI < 6.5) heroCard.classList.add('state-marginal');

  requestAnimationFrame(animateGauge);
}
animateGauge();

// ── Chart.js — WPI Trend ──────────────────────────────────────────
const HISTORY_LEN = 60;
const wpiHistory  = { labels: [], data: [] };

const trendCtx = document.getElementById('trend-chart').getContext('2d');
const trendChart = new Chart(trendCtx, {
  type: 'line',
  data: {
    labels: wpiHistory.labels,
    datasets: [{
      label: 'WPI',
      data:   wpiHistory.data,
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59,130,246,0.08)',
      pointRadius: 0,
      borderWidth: 2,
      fill: true,
      tension: 0.4,
    }]
  },
  options: {
    animation: false,
    scales: {
      x: { ticks: { color: '#4a5a70', maxTicksLimit: 8 }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: {
        min: 0, max: 10,
        ticks: { color: '#4a5a70', stepSize: 2 },
        grid: { color: 'rgba(255,255,255,0.04)' },
      }
    },
    plugins: {
      legend: { display: false },
      annotation: {
        annotations: {
          line35: { type:'line', yMin:3.5, yMax:3.5, borderColor:'rgba(239,68,68,0.3)', borderWidth:1, borderDash:[4,4] },
          line65: { type:'line', yMin:6.5, yMax:6.5, borderColor:'rgba(34,197,94,0.3)',  borderWidth:1, borderDash:[4,4] },
        }
      }
    },
    responsive: true,
    maintainAspectRatio: true,
  }
});

// ── Chart.js — Sensor Param Trends ───────────────────────────────
const paramHistory = { labels:[], ph:[], turbidity:[], tds:[], do:[] };

const paramCtx = document.getElementById('param-chart').getContext('2d');
const paramChart = new Chart(paramCtx, {
  type: 'line',
  data: {
    labels: paramHistory.labels,
    datasets: [
      { label:'pH',         data: paramHistory.ph,        borderColor:'#06b6d4', borderWidth:1.5, pointRadius:0, tension:0.4, fill:false },
      { label:'Turbidity/10', data: paramHistory.turbidity, borderColor:'#f59e0b', borderWidth:1.5, pointRadius:0, tension:0.4, fill:false },
      { label:'TDS/100',    data: paramHistory.tds,       borderColor:'#8b5cf6', borderWidth:1.5, pointRadius:0, tension:0.4, fill:false },
      { label:'DO',         data: paramHistory.do,        borderColor:'#22c55e', borderWidth:1.5, pointRadius:0, tension:0.4, fill:false },
    ]
  },
  options: {
    animation: false,
    scales: {
      x: { ticks: { color: '#4a5a70', maxTicksLimit: 8 }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: { min: 0, ticks: { color: '#4a5a70' }, grid: { color: 'rgba(255,255,255,0.04)' } },
    },
    plugins: { legend: { labels: { color: '#8ba0c0', boxWidth: 12, font: { size: 10 } } } },
    responsive: true,
    maintainAspectRatio: true,
  }
});

function pushHistory(ts, wpi, ph, turb, tds, doVal) {
  const label = new Date(ts).toLocaleTimeString('en-GB', { hour:'2-digit', minute:'2-digit', second:'2-digit' });

  const push = (arr, val) => { arr.push(val); if (arr.length > HISTORY_LEN) arr.shift(); };
  push(wpiHistory.labels, label);   push(wpiHistory.data, wpi);
  push(paramHistory.labels, label);
  push(paramHistory.ph,        parseFloat(ph.toFixed(2)));
  push(paramHistory.turbidity, parseFloat((turb / 10).toFixed(2)));
  push(paramHistory.tds,       parseFloat((tds / 100).toFixed(2)));
  push(paramHistory.do,        parseFloat(doVal.toFixed(2)));

  trendChart.update();
  paramChart.update();
}

// ── Sensor Card Updater ───────────────────────────────────────────
const SENSOR_CONFIG = {
  ph:        { id:'ph',   max:14,    safeRange:[6.5,8.5],   warnRange:[5.5,9.5] },
  turbidity: { id:'turb', max:100,   safeRange:[0,1],       warnRange:[0,5] },
  tds:       { id:'tds',  max:1500,  safeRange:[0,500],     warnRange:[0,750] },
  do:        { id:'do',   max:20,    safeRange:[6,20],      warnRange:[4,20], inverted:true },
};

function getSensorStatus(param, value) {
  const cfg = SENSOR_CONFIG[param];
  if (!cfg) return { status:'safe', label:'OK' };
  const [sLo, sHi] = cfg.safeRange;
  const [wLo, wHi] = cfg.warnRange;
  if (value >= sLo && value <= sHi) return { status:'safe',   label:'SAFE' };
  if (value >= wLo && value <= wHi) return { status:'warn',   label:'CAUTION' };
  return                                   { status:'danger', label:'DANGER' };
}

function updateSensorCard(param, value) {
  const cfg    = SENSOR_CONFIG[param];
  const { status, label } = getSensorStatus(param, value);
  const pct    = Math.min(100, (value / cfg.max) * 100);

  const valEl    = document.getElementById(`val-${cfg.id}`);
  const barEl    = document.getElementById(`bar-${cfg.id}`);
  const statEl   = document.getElementById(`status-${cfg.id}`);
  const cardEl   = document.getElementById(`card-${cfg.id}`);

  if (valEl) valEl.textContent = param === 'tds' ? Math.round(value) : value.toFixed(param === 'turbidity' ? 1 : 2);
  if (barEl) {
    barEl.style.width = pct + '%';
    barEl.style.background = status === 'safe' ? 'var(--potable)' : status === 'warn' ? 'var(--marginal)' : 'var(--non-potable)';
  }
  if (statEl) {
    statEl.textContent = label;
    statEl.style.background = status === 'safe' ? 'rgba(34,197,94,0.12)' : status === 'warn' ? 'rgba(245,158,11,0.12)' : 'rgba(239,68,68,0.12)';
    statEl.style.color = status === 'safe' ? 'var(--potable)' : status === 'warn' ? 'var(--marginal)' : 'var(--non-potable)';
  }
  if (cardEl) {
    cardEl.className = `sensor-card status-${status}`;
  }
}

// ── Membership Degree Renderer ────────────────────────────────────
const PARAM_LABELS = {
  ph:        { title:'pH', terms:['ACIDIC','SLIGHTLY_ACIDIC','NEUTRAL','SLIGHTLY_ALKALINE','ALKALINE'] },
  turbidity: { title:'Turbidity', terms:['CLEAR','SLIGHTLY_TURBID','TURBID','VERY_TURBID'] },
  tds:       { title:'TDS', terms:['PURE','ACCEPTABLE','HIGH','VERY_HIGH'] },
  do:        { title:'DO', terms:['VERY_LOW','LOW','ACCEPTABLE','HIGH'] },
};

function renderMembership(membershipMap) {
  const grid = document.getElementById('membership-grid');
  grid.innerHTML = '';

  for (const [param, paramInfo] of Object.entries(PARAM_LABELS)) {
    const mfData = membershipMap[param] || {};
    const div    = document.createElement('div');
    div.className = 'mf-param';
    div.innerHTML = `<div class="mf-param-title">${paramInfo.title}</div>`;

    paramInfo.terms.forEach(term => {
      const mu   = mfData[term] ?? 0;
      const pct  = (mu * 100).toFixed(0);
      const row  = document.createElement('div');
      row.className = 'mf-term-row';
      row.innerHTML = `
        <span class="mf-term-label">${term}</span>
        <div class="mf-bar-bg"><div class="mf-bar-fill" style="width:${pct}%"></div></div>
        <span class="mf-val">${mu.toFixed(3)}</span>
      `;
      div.appendChild(row);
    });
    grid.appendChild(div);
  }
}

// ── Rule Activation Renderer ──────────────────────────────────────
function renderRules(activatedRules) {
  const list = document.getElementById('rules-list');
  if (!activatedRules || activatedRules.length === 0) {
    list.innerHTML = '<div class="rule-placeholder">No rules active.</div>';
    return;
  }
  // Sort by strength desc
  const sorted = [...activatedRules].sort((a, b) => b.strength - a.strength);
  list.innerHTML = sorted.map(r => `
    <div class="rule-item">
      <span class="rule-id">#${r.id}</span>
      <div class="rule-strength-bar">
        <div class="rule-strength-fill" style="width:${(r.strength * 100).toFixed(0)}%"></div>
      </div>
      <span class="mf-val" style="width:42px">${r.strength.toFixed(3)}</span>
      <span class="rule-label label-${r.consequence}">${r.consequence.replace('_','-')}</span>
    </div>
  `).join('');
}

// ── Alert Banner ──────────────────────────────────────────────────
let alertTimeout;
function showAlert(label) {
  const banner  = document.getElementById('alert-banner');
  const classes = { 'NON-POTABLE': 'alert-danger', 'MARGINAL': 'alert-warn', 'POTABLE': 'alert-success' };
  const msgs    = {
    'NON-POTABLE': '⚠️ NON-POTABLE — Water unsafe for consumption!',
    'MARGINAL':    '⚡ MARGINAL — Water treatment recommended.',
    'POTABLE':     '✅ POTABLE — Water meets safety standards.',
  };
  banner.className = `alert-banner ${classes[label] || ''}`;
  banner.textContent = msgs[label] || '';
  banner.style.display = 'block';
  clearTimeout(alertTimeout);
  alertTimeout = setTimeout(() => { banner.style.display = 'none'; }, 4000);
}

// ── Main sensor_update handler ────────────────────────────────────
let lastLabel = null;
socket.on('sensor_update', (data) => {
  const ts = data.timestamp;
  document.getElementById('timestamp').textContent = new Date(ts).toLocaleTimeString();

  const p = data.processed;
  const wpi = data.wpi;

  // Update WPI gauge
  targetWPI = wpi;
  document.getElementById('wpi-label').textContent = data.label;
  document.getElementById('wpi-rules').textContent = `${data.n_rules_fired} rules active`;
  document.getElementById('scenario-badge').textContent = (data.scenario || '').toUpperCase();

  // Sensor cards
  updateSensorCard('ph',        p.ph);
  updateSensorCard('turbidity', p.turbidity);
  updateSensorCard('tds',       p.tds);
  updateSensorCard('do',        p.do);

  // Charts
  pushHistory(ts, wpi, p.ph, p.turbidity, p.tds, p.do);

  // Membership
  if (data.membership_map) renderMembership(data.membership_map);

  // Rules
  if (data.activated_rules) renderRules(data.activated_rules);

  // Alert on class change
  if (data.label !== lastLabel) {
    showAlert(data.label);
    lastLabel = data.label;
  }
});

// ── Manual Inference Sliders ──────────────────────────────────────
const sliders = [
  { id:'sl-ph',   valId:'sl-ph-val',   decimals:1 },
  { id:'sl-turb', valId:'sl-turb-val', decimals:1 },
  { id:'sl-tds',  valId:'sl-tds-val',  decimals:0 },
  { id:'sl-do',   valId:'sl-do-val',   decimals:1 },
];
sliders.forEach(({ id, valId, decimals }) => {
  const el   = document.getElementById(id);
  const disp = document.getElementById(valId);
  el.addEventListener('input', () => {
    disp.textContent = parseFloat(el.value).toFixed(decimals);
  });
});

document.getElementById('infer-btn').addEventListener('click', () => {
  socket.emit('manual_infer', {
    ph:          parseFloat(document.getElementById('sl-ph').value),
    turbidity:   parseFloat(document.getElementById('sl-turb').value),
    tds:         parseFloat(document.getElementById('sl-tds').value),
    do:          parseFloat(document.getElementById('sl-do').value),
    temperature: 25.0,
  });
});

socket.on('manual_result', (res) => {
  const colors = { 'POTABLE':'#22c55e', 'MARGINAL':'#f59e0b', 'NON-POTABLE':'#ef4444' };
  const el = document.getElementById('manual-result');
  el.style.borderColor = colors[res.label] || '#3b82f6';
  el.innerHTML = `
    <strong style="color:${colors[res.label]}">WPI = ${res.wpi}</strong>
    &nbsp;→&nbsp; <strong style="color:${colors[res.label]}">${res.label}</strong>
    &nbsp;&nbsp;<span style="color:#4a5a70;font-size:0.72rem">${res.n_rules_fired} rules fired</span>
  `;
});

// Initial gauge draw
drawGauge(5.0);
