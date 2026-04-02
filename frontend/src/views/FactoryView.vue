<template>
  <div class="factory-fullscreen">
      <div class="factory-header">
        <router-link to="/dashboard" class="back-btn">&larr;</router-link>
        <h1 class="page-title">Factory</h1>
        <div class="header-actions">
          <button
            :class="['header-btn', { active: activeView === 'data' }]"
            @click="activeView = 'data'"
          >Data</button>
          <button
            :class="['header-btn', { active: activeView === 'graph' }]"
            @click="activeView = 'graph'"
          >Graph</button>
          <button
            :class="['header-btn', { active: activeView === 'api' }]"
            @click="activeView = 'api'"
          >API</button>
        </div>
      </div>

      <!-- Machine Status Section -->
      <div class="machine-status-section">
        <div class="layout-container">
          <!-- SVG column (hidden in API view) -->
          <div v-if="activeView !== 'api'" class="svg-column">
          <svg viewBox="0 0 362 432" class="factory-svg" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Factory layout">

            <!-- Areas (static) -->
            <g>
              <rect x="13" y="10" width="179" height="86" class="area" rx="2"/>
              <text x="102.5" y="53.0" class="area-text">MOLD</text>

              <rect x="222" y="10" width="124" height="115" class="area" rx="2"/>
              <text x="284.0" y="67.5" class="area-text">Wire cutting room</text>

              <rect x="13" y="110" width="90" height="15" class="area" rx="2"/>
              <text x="58.0" y="117.5" class="area-text">Milling</text>

              <rect x="13" y="125" width="90" height="31" class="area" rx="2"/>
              <text x="58.0" y="140.5" class="area-text">CNC Toshiba</text>

              <rect x="13" y="155" width="119" height="30" class="area" rx="2"/>
              <text x="72.5" y="170.0" class="area-text">Grinding</text>

              <rect x="132" y="110" width="60" height="60" class="area" rx="2"/>
              <text x="162.0" y="140.0" class="area-text">CNC</text>

              <rect x="132" y="200" width="60" height="45" class="area" rx="2"/>
              <text x="162.0" y="214" class="area-text">
                <tspan x="162.0" y="214">molding</tspan>
                <tspan x="162.0" y="224">work space</tspan>
              </text>

              <rect x="132" y="275" width="60" height="45" class="area" rx="2"/>
              <text x="162.0" y="289" class="area-text">
                <tspan x="162.0" y="289">Mold</tspan>
                <tspan x="162.0" y="299">warehouse</tspan>
              </text>
            </g>

            <!-- Tag (static label) -->
            <g>
              <rect x="162" y="170" width="30" height="15" class="tag" rx="2"/>
              <text x="177.0" y="177.5" class="press-text">Press</text>
            </g>

            <!-- Presses (Vue reactive) -->
            <g>
              <g v-for="p in presses" :key="p.id" @click="selectPress(p.id)" style="cursor:pointer">
                <rect
                  :x="p.x" :y="p.y" :width="p.w" :height="p.h"
                  rx="4"
                  :class="['press-rect', 'status-' + pressStatus[p.id], { selected: selectedPressId === pressIdToNo(p.id) }]"
                />
                <text
                  :x="p.tx" :y="p.ty"
                  class="press-text"
                  :font-size="p.fs"
                >{{ p.label }}</text>
              </g>
            </g>
          </svg>
          <div class="svg-legend">
            <span class="svg-legend-item"><span class="svg-legend-box running"></span> Running</span>
            <span class="svg-legend-item"><span class="svg-legend-box idle"></span> Idle</span>
            <span class="svg-legend-item"><span class="svg-legend-box warning"></span> Warning</span>
            <span class="svg-legend-item"><span class="svg-legend-box error"></span> Error</span>
          </div>
          </div>

          <!-- API Raw Data view -->
          <div v-if="activeView === 'api'" class="api-data-wrapper">
            <div class="api-toolbar">
              <select v-model="apiRaspiFilter" @change="fetchRawEvents" class="api-select">
                <option value="">All Raspi</option>
                <option v-for="m in machineStatus" :key="m.no" :value="m.no">Raspi {{ m.no }}</option>
              </select>
              <button class="api-refresh-btn" @click="fetchRawEvents">Refresh</button>
              <span class="api-count">{{ rawEvents.length }} events</span>
            </div>
            <div class="api-table-scroll">
              <table class="status-table api-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Raspi No</th>
                    <th>Timestamp (ms)</th>
                    <th>Date / Time</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="ev in rawEvents" :key="ev.id">
                    <td>{{ ev.id }}</td>
                    <td>{{ ev.raspi_no }}</td>
                    <td>{{ ev.ts_ms }}</td>
                    <td>{{ formatTs(ev.ts_ms) }}</td>
                  </tr>
                  <tr v-if="!rawEvents.length">
                    <td colspan="4" style="text-align:center; color:#999; padding:20px;">No data</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="activeView !== 'api'" class="status-table-wrapper">
          <table class="status-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Pressure</th>
                <template v-if="activeView === 'data'">
                  <th>Customer</th>
                  <th>Product</th>
                  <th>Process</th>
                  <th>Qty/Total</th>
                  <th>Name</th>
                  <th>LOT, No</th>
                </template>
                <th v-if="activeView === 'graph'" class="th-timeline">
                  <div class="timeline-axis">
                    <span v-for="h in 25" :key="h" class="axis-tick" :style="{ left: ((h - 1) / 24 * 100) + '%' }">
                      {{ String(h - 1).padStart(2, '0') }}
                    </span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="machine in machineStatus"
                :key="machine.no"
                :ref="el => { if (el) rowRefs[machine.no] = el }"
                :class="{ 'row-selected': selectedPressId === machine.no }"
                style="cursor:pointer"
                @click="selectRow(machine.no)"
              >
                <td>{{ machine.no }}</td>
                <td>{{ machine.pressure }}</td>
                <template v-if="activeView === 'data'">
                  <td>{{ machine.customer }}</td>
                  <td>{{ machine.product }}</td>
                  <td>{{ machine.process }}</td>
                  <td>{{ machine.qty }}</td>
                  <td>{{ machine.name }}</td>
                  <td>{{ machine.lot_no }}</td>
                </template>
                <td v-if="activeView === 'graph'" class="td-timeline">
                  <div class="timeline-bar">
                    <template v-if="timelineData[machine.no]">
                      <div
                        v-for="(seg, i) in timelineData[machine.no]"
                        :key="i"
                        class="bar-seg"
                        :style="{ flexBasis: seg.pct + '%', background: seg.color }"
                        :title="seg.label"
                      ></div>
                    </template>
                    <div v-else class="bar-seg" style="flex-basis:100%; background:#BDBDBD" title="データなし"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, watch } from 'vue'
import api from '@/utils/api'

const activeView = ref('data')

// ============================================================
// 24h Timeline bar (Press-raspi style)
// ============================================================
const CHOKO = 30000   // 30s  → チョコ停
const DOKA  = 300000  // 5min → ドカ停
const COLORS = { green: '#4CAF50', yellow: '#FFC107', red: '#F44336', gray: '#BDBDBD' }
const LABELS = { green: '稼働中', yellow: 'チョコ停', red: 'ドカ停', gray: 'データなし' }

const timelineData = reactive({})

function classify(ms) {
  if (ms < CHOKO) return 'green'
  if (ms < DOKA) return 'yellow'
  return 'red'
}

function buildSegments(events, ws, we) {
  if (!events.length) return [{ s: ws, e: we, c: 'gray' }]
  const segs = []
  let cs = ws, cc = classify(events[0] - ws)
  for (let i = 0; i < events.length - 1; i++) {
    const nc = classify(events[i + 1] - events[i])
    if (nc !== cc) {
      segs.push({ s: cs, e: events[i], c: cc })
      cs = events[i]; cc = nc
    }
  }
  const last = events[events.length - 1]
  const tc = classify(we - last)
  if (tc === cc) {
    segs.push({ s: cs, e: we, c: cc })
  } else {
    segs.push({ s: cs, e: last, c: cc })
    segs.push({ s: last, e: we, c: tc })
  }
  return segs
}

function fmtTime(ms) {
  const d = new Date(ms)
  return d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0')
}

function toBarData(segs, ws, we) {
  const total = we - ws
  if (total <= 0) return []
  return segs
    .map(seg => {
      const pct = (seg.e - seg.s) / total * 100
      return pct > 0 ? { pct, color: COLORS[seg.c], label: fmtTime(seg.s) + ' - ' + fmtTime(seg.e) + '  ' + LABELS[seg.c] } : null
    })
    .filter(Boolean)
}

async function fetchTimeline(machineNo) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dayStart = today.getTime()
  const dayEnd = dayStart + 24 * 3600000
  const now = Date.now()
  const effEnd = Math.min(dayEnd, now)

  try {
    const { data } = await api.get('/iot/events', {
      params: { start_ms: dayStart, end_ms: dayEnd, raspi_no: 'raspi_' + machineNo }
    })
    const events = data.events || []
    const segs = buildSegments(events, dayStart, effEnd)
    timelineData[machineNo] = toBarData(segs, dayStart, dayEnd)
  } catch {
    timelineData[machineNo] = toBarData([{ s: dayStart, e: dayEnd, c: 'gray' }], dayStart, dayEnd)
  }
}

// ============================================================
// API Raw Data view
// ============================================================
const rawEvents = ref([])
const apiRaspiFilter = ref('')

async function fetchRawEvents() {
  try {
    const params = { limit: 500 }
    if (apiRaspiFilter.value) params.raspi_no = apiRaspiFilter.value
    console.log('[API] fetching /api/iot/events/raw', params)
    const { data } = await api.get('/iot/events/raw', { params })
    console.log('[API] response:', data)
    rawEvents.value = data
  } catch (err) {
    console.error('[API] fetchRawEvents error:', err?.response?.status, err?.response?.data, err)
    rawEvents.value = []
  }
}

function formatTs(tsMs) {
  const d = new Date(tsMs)
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0') + ' ' +
    String(d.getHours()).padStart(2, '0') + ':' +
    String(d.getMinutes()).padStart(2, '0') + ':' +
    String(d.getSeconds()).padStart(2, '0') + '.' +
    String(d.getMilliseconds()).padStart(3, '0')
}

watch(activeView, (v) => {
  if (v === 'graph') {
    machineStatus.value.forEach(m => fetchTimeline(m.no))
  }
  if (v === 'api') {
    fetchRawEvents()
  }
})

// Machine list — No & Pressure populated, others blank
const machineStatus = ref([
  { no: "01",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "02",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "03",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "04",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "05",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "06",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "07",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "08",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "09",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "10",   pressure: 35,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "11",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "12",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "12-B", pressure: 150, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "14",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "15",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "16",   pressure: 25,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "17",   pressure: 35,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "18",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "19",   pressure: 200, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "21",   pressure: 45,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "22",   pressure: 200, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "23",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "24",   pressure: 20,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "25",   pressure: 35,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "26",   pressure: 80,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "27",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "28",   pressure: 110, lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "30",   pressure: 30,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
  { no: "31",   pressure: 60,  lot_no: "", customer: "", product: "", process: "", qty: "", name: "" },
])

// Factory SVG layout — presses
const presses = [
  { id: '11',   x: 222, y: 141, w: 30,  h: 15,  tx: 237,   ty: 148.5, fs: 8,  label: '11' },
  { id: '18',   x: 252, y: 141, w: 30,  h: 15,  tx: 267,   ty: 148.5, fs: 8,  label: '18' },
  { id: '17',   x: 222, y: 170, w: 60,  h: 15,  tx: 252,   ty: 177.5, fs: 8,  label: '17' },
  { id: '16',   x: 222, y: 200, w: 60,  h: 15,  tx: 252,   ty: 207.5, fs: 8,  label: '16' },
  { id: '15',   x: 222, y: 230, w: 60,  h: 15,  tx: 252,   ty: 237.5, fs: 8,  label: '15' },
  { id: '14',   x: 222, y: 260, w: 60,  h: 15,  tx: 252,   ty: 267.5, fs: 8,  label: '14' },
  { id: '12-B', x: 222, y: 290, w: 60,  h: 15,  tx: 252,   ty: 297.5, fs: 8,  label: '12-B' },
  { id: '12',   x: 222, y: 320, w: 60,  h: 15,  tx: 252,   ty: 327.5, fs: 8,  label: '12' },
  { id: '28',   x: 222, y: 348, w: 60,  h: 15,  tx: 252,   ty: 355.5, fs: 8,  label: '28' },
  { id: '10',   x: 312, y: 170, w: 34,  h: 15,  tx: 329,   ty: 177.5, fs: 8,  label: '10' },
  { id: '9',    x: 312, y: 185, w: 34,  h: 15,  tx: 329,   ty: 192.5, fs: 8,  label: '9' },
  { id: '8',    x: 312, y: 200, w: 34,  h: 15,  tx: 329,   ty: 207.5, fs: 8,  label: '8' },
  { id: '7',    x: 312, y: 215, w: 34,  h: 15,  tx: 329,   ty: 222.5, fs: 8,  label: '7' },
  { id: '6',    x: 312, y: 230, w: 34,  h: 15,  tx: 329,   ty: 237.5, fs: 8,  label: '6' },
  { id: '5',    x: 312, y: 260, w: 34,  h: 15,  tx: 329,   ty: 267.5, fs: 8,  label: '5' },
  { id: '4',    x: 312, y: 275, w: 34,  h: 15,  tx: 329,   ty: 282.5, fs: 8,  label: '4' },
  { id: '3',    x: 312, y: 290, w: 34,  h: 15,  tx: 329,   ty: 297.5, fs: 8,  label: '3' },
  { id: '2',    x: 312, y: 320, w: 34,  h: 15,  tx: 329,   ty: 327.5, fs: 8,  label: '2' },
  { id: '1',    x: 312, y: 335, w: 34,  h: 13,  tx: 329,   ty: 341.5, fs: 7,  label: '1' },
  { id: '30',   x: 13,  y: 200, w: 30,  h: 60,  tx: 28,    ty: 230,   fs: 10, label: '30' },
  { id: '31',   x: 13,  y: 260, w: 30,  h: 60,  tx: 28,    ty: 290,   fs: 10, label: '31' },
  { id: '24',   x: 13,  y: 320, w: 30,  h: 43,  tx: 28,    ty: 341.5, fs: 10, label: '24' },
  { id: '21',   x: 73,  y: 245, w: 30,  h: 60,  tx: 88,    ty: 275,   fs: 10, label: '21' },
  { id: '25',   x: 73,  y: 305, w: 30,  h: 58,  tx: 88,    ty: 334,   fs: 10, label: '25' },
  { id: '19',   x: 102, y: 215, w: 30,  h: 148, tx: 117,   ty: 289,   fs: 10, label: '19' },
  { id: '23',   x: 132, y: 320, w: 60,  h: 28,  tx: 162,   ty: 334,   fs: 10, label: '23' },
  { id: '22',   x: 102, y: 363, w: 90,  h: 30,  tx: 147,   ty: 378,   fs: 10, label: '22' },
  { id: '27',   x: 222, y: 378, w: 124, h: 15,  tx: 284,   ty: 385.5, fs: 8,  label: '27' },
  { id: '26',   x: 222, y: 408, w: 124, h: 15,  tx: 284,   ty: 415.5, fs: 8,  label: '26' },
]

// Press status (default all idle)
const pressStatus = reactive(
  Object.fromEntries(presses.map(p => [p.id, 'idle']))
)

const selectedPressId = ref(null)
const rowRefs = reactive({})

// Map SVG press id to table no (e.g. '1' -> '01', '12-B' -> '12-B')
function pressIdToNo(id) {
  if (id.includes('-')) return id
  return id.padStart(2, '0')
}

function selectPress(id) {
  const no = pressIdToNo(id)
  selectedPressId.value = selectedPressId.value === no ? null : no
  if (selectedPressId.value && rowRefs[selectedPressId.value]) {
    nextTick(() => {
      rowRefs[selectedPressId.value]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
  }
}

function selectRow(no) {
  selectedPressId.value = selectedPressId.value === no ? null : no
}
</script>

<style scoped>
/* ============================================================
   Header action buttons
   ============================================================ */
.header-actions {
  margin-left: auto;
  display: flex;
  gap: 6px;
}

.header-btn {
  padding: 3px 12px;
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 14px;
  background: transparent;
  color: rgba(255,255,255,0.75);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.header-btn:hover {
  background: rgba(255,255,255,0.12);
  color: #fff;
}

.header-btn.active {
  background: rgba(255,255,255,0.22);
  color: #fff;
  border-color: rgba(255,255,255,0.6);
}

/* ============================================================
   Base layout (shared across themes)
   ============================================================ */
.factory-fullscreen {
  /* Design tokens */
  --bg: #f5f6fa;
  --header-bg: #2c3e50;
  --card-bg: #ffffff;
  --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
  --svg-bg: #ffffff;
  --area-fill: rgb(183,183,183);
  --area-stroke: rgb(120,120,120);
  --area-text-fill: #222;
  --press-stroke: rgb(120,120,120);
  --press-stroke-w: 2;
  --press-text-fill: #222;
  --tag-fill: rgb(207,226,243);
  --color-running: #6abf69;
  --color-idle: rgb(207,226,243);
  --color-warning: #f4d03f;
  --color-error: #e74c3c;
  --select-stroke: #0055ff;
  --legend-color: #555;
  --table-head-bg: #f8f9fa;
  --table-border: #eee;
  --table-hover: #f5f5f5;
  --table-selected: #d6eaf8;
  --table-text: inherit;
  --font: 'Consolas', 'SF Mono', 'Fira Code', monospace;

  position: fixed;
  inset: 0;
  z-index: 2000;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.factory-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: var(--header-bg);
  color: white;
  flex-shrink: 0;
}

.factory-header .page-title {
  margin: 0;
  font-size: 18px;
  font-family: var(--font);
}

.back-btn {
  color: white;
  text-decoration: none;
  font-size: 20px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.machine-status-section {
  flex: 1;
  padding: 12px;
  overflow: hidden;
  display: flex;
}

.layout-container {
  flex: 1;
  background: var(--card-bg);
  padding: 12px 16px;
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  display: flex;
  gap: 12px;
  overflow: hidden;
  min-height: 0;
}

.svg-column {
  width: 40%;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 0;
}

/* ============================================================
   SVG elements — driven by CSS vars
   ============================================================ */
.factory-svg {
  width: 100%;
  flex: 1;
  min-height: 0;
  background: var(--svg-bg);
  border-radius: 8px;
}

.area {
  shape-rendering: auto;
  vector-effect: non-scaling-stroke;
  fill: var(--area-fill);
  stroke: var(--area-stroke);
  stroke-width: 2;
}

.area-text {
  font-family: var(--font);
  font-size: 8.5px;
  fill: var(--area-text-fill);
  text-anchor: middle;
  dominant-baseline: middle;
}

.press-rect {
  shape-rendering: auto;
  vector-effect: non-scaling-stroke;
  stroke: var(--press-stroke);
  stroke-width: var(--press-stroke-w);
  cursor: pointer;
  transition: fill 0.2s, stroke 0.2s;
}

.press-rect:hover {
  stroke: var(--select-stroke);
  stroke-width: 3;
}

.press-rect.selected {
  stroke: var(--select-stroke);
  stroke-width: 3;
}

.tag {
  vector-effect: non-scaling-stroke;
  fill: var(--tag-fill);
  stroke: var(--area-stroke);
  stroke-width: 1.5;
}

.press-text {
  font-family: var(--font);
  font-size: 8.5px;
  fill: var(--press-text-fill);
  text-anchor: middle;
  dominant-baseline: middle;
  pointer-events: none;
}

/* Status colors */
.status-running { fill: var(--color-running); }
.status-idle    { fill: var(--color-idle); }
.status-error   { fill: var(--color-error); }
.status-warning { fill: var(--color-warning); }

/* ============================================================
   Legend
   ============================================================ */
.svg-legend {
  display: flex;
  gap: 12px;
  margin-top: 6px;
  font-size: 11px;
  font-family: var(--font);
  color: var(--legend-color);
  flex-shrink: 0;
}

.svg-legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.svg-legend-box {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  display: inline-block;
}

.svg-legend-box.running { background: var(--color-running); }
.svg-legend-box.idle    { background: var(--color-idle); }
.svg-legend-box.warning { background: var(--color-warning); }
.svg-legend-box.error   { background: var(--color-error); }

/* ============================================================
   Status table
   ============================================================ */
.status-table-wrapper {
  flex: 1;
  overflow: auto;
  min-width: 0;
}

.status-table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
  font-size: 13px;
  font-family: var(--font);
  color: var(--table-text);
}

.status-table th,
.status-table td {
  padding: 5px 10px;
  text-align: left;
  border-bottom: 1px solid var(--table-border);
}

.status-table th {
  background-color: var(--table-head-bg);
  position: sticky;
  top: 0;
  z-index: 1;
}

.status-table tr:hover {
  background-color: var(--table-hover);
}

.status-table tr.row-selected {
  background-color: var(--table-selected);
}

/* ============================================================
   24h Timeline bar (Graph view)
   ============================================================ */
.th-timeline {
  min-width: 600px;
  padding-bottom: 0 !important;
}

.timeline-axis {
  position: relative;
  height: 18px;
  font-size: 9px;
  color: #888;
}

.axis-tick {
  position: absolute;
  transform: translateX(-50%);
  white-space: nowrap;
}

.axis-tick:first-child {
  transform: translateX(0);
}

.axis-tick:last-child {
  transform: translateX(-100%);
}

.td-timeline {
  padding: 4px 10px !important;
  min-width: 600px;
}

.timeline-bar {
  display: flex;
  width: 100%;
  height: 22px;
  border-radius: 3px;
  overflow: hidden;
  background: #eee;
  border: 1px solid #ddd;
}

.bar-seg {
  height: 100%;
  min-width: 0;
  transition: opacity 0.15s;
}

.bar-seg:hover {
  opacity: 0.75;
}

/* ============================================================
   API Raw Data view
   ============================================================ */
.api-data-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.api-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
  flex-shrink: 0;
}

.api-select {
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: var(--font);
  font-size: 12px;
}

.api-refresh-btn {
  padding: 4px 12px;
  border: 1px solid #3498db;
  border-radius: 4px;
  background: #3498db;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  font-family: var(--font);
}

.api-refresh-btn:hover {
  background: #2980b9;
}

.api-count {
  font-size: 12px;
  color: #888;
  font-family: var(--font);
}

.api-table-scroll {
  flex: 1;
  overflow: auto;
  min-height: 0;
}

.api-table {
  font-size: 12px;
}

.api-table td {
  font-variant-numeric: tabular-nums;
}
</style>
