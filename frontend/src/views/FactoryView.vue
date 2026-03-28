<template>
  <div class="factory-fullscreen">
      <div class="factory-header">
        <router-link to="/dashboard" class="back-btn">&larr;</router-link>
        <h1 class="page-title">Factory</h1>
      </div>

      <!-- Machine Status Section -->
      <div class="machine-status-section">
        <div class="layout-container">
          <div class="svg-column">
          <svg viewBox="0 0 362 432" class="factory-svg" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Factory layout">
            <!-- Areas (static) -->
            <g>
              <rect x="13" y="10" width="179" height="86" class="area"/>
              <text x="102.5" y="53.0" class="area-text">MOLD</text>

              <rect x="222" y="10" width="124" height="115" class="area"/>
              <text x="284.0" y="67.5" class="area-text">Wire cutting room</text>

              <rect x="13" y="110" width="90" height="15" class="area"/>
              <text x="58.0" y="117.5" class="area-text">Milling</text>

              <rect x="13" y="125" width="90" height="31" class="area"/>
              <text x="58.0" y="140.5" class="area-text">CNC Toshiba</text>

              <rect x="13" y="155" width="119" height="30" class="area"/>
              <text x="72.5" y="170.0" class="area-text">Grinding</text>

              <rect x="132" y="110" width="60" height="60" class="area"/>
              <text x="162.0" y="140.0" class="area-text">CNC</text>

              <rect x="132" y="200" width="60" height="45" class="area"/>
              <text x="162.0" y="210.9" class="area-text">
                <tspan x="162.0" y="210.9">molding</tspan>
                <tspan x="162.0" y="223.6">work space</tspan>
              </text>

              <rect x="132" y="275" width="60" height="45" class="area"/>
              <text x="162.0" y="285.9" class="area-text">
                <tspan x="162.0" y="285.9">Mold</tspan>
                <tspan x="162.0" y="298.6">warehouse</tspan>
              </text>
            </g>

            <!-- Tag (static label) -->
            <g>
              <rect x="162" y="170" width="30" height="15" class="tag"/>
              <text x="177.0" y="177.5" class="press-text">PRES</text>
            </g>

            <!-- Presses (Vue reactive) -->
            <g>
              <g v-for="p in presses" :key="p.id" @click="selectPress(p.id)" style="cursor:pointer">
                <rect
                  :x="p.x" :y="p.y" :width="p.w" :height="p.h"
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
          <div class="status-table-wrapper">
          <table class="status-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Pressure</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Process</th>
                <th>Qty/Total</th>
                <th>Name</th>
                <th>LOT, No</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="machine in machineStatus"
                :key="machine.no"
                :ref="el => { if (el) rowRefs[machine.no] = el }"
                :class="{ 'row-selected': selectedPressId === machine.no }"
              >
                <td>{{ machine.no }}</td>
                <td>{{ machine.pressure }}</td>
                <td>{{ machine.customer }}</td>
                <td>{{ machine.product }}</td>
                <td>{{ machine.process }}</td>
                <td>{{ machine.qty }}</td>
                <td>{{ machine.name }}</td>
                <td>{{ machine.lot_no }}</td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'

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
  { id: '11',   x: 222, y: 141, w: 30,  h: 15,  tx: 237,   ty: 148.5, fs: 10, label: '11' },
  { id: '18',   x: 252, y: 141, w: 30,  h: 15,  tx: 267,   ty: 148.5, fs: 10, label: '18' },
  { id: '17',   x: 222, y: 170, w: 60,  h: 15,  tx: 252,   ty: 177.5, fs: 10, label: '17' },
  { id: '16',   x: 222, y: 200, w: 60,  h: 15,  tx: 252,   ty: 207.5, fs: 10, label: '16' },
  { id: '15',   x: 222, y: 230, w: 60,  h: 15,  tx: 252,   ty: 237.5, fs: 10, label: '15' },
  { id: '14',   x: 222, y: 260, w: 60,  h: 15,  tx: 252,   ty: 267.5, fs: 10, label: '14' },
  { id: '12-B', x: 222, y: 290, w: 60,  h: 15,  tx: 252,   ty: 297.5, fs: 10, label: '12-B' },
  { id: '12',   x: 222, y: 320, w: 60,  h: 15,  tx: 252,   ty: 327.5, fs: 10, label: '12' },
  { id: '28',   x: 222, y: 348, w: 60,  h: 15,  tx: 252,   ty: 355.5, fs: 10, label: '28' },
  { id: '10',   x: 312, y: 170, w: 34,  h: 15,  tx: 329,   ty: 177.5, fs: 10, label: '10' },
  { id: '9',    x: 312, y: 185, w: 34,  h: 15,  tx: 329,   ty: 192.5, fs: 10, label: '9' },
  { id: '8',    x: 312, y: 200, w: 34,  h: 15,  tx: 329,   ty: 207.5, fs: 10, label: '8' },
  { id: '7',    x: 312, y: 215, w: 34,  h: 15,  tx: 329,   ty: 222.5, fs: 10, label: '7' },
  { id: '6',    x: 312, y: 230, w: 34,  h: 15,  tx: 329,   ty: 237.5, fs: 10, label: '6' },
  { id: '5',    x: 312, y: 260, w: 34,  h: 15,  tx: 329,   ty: 267.5, fs: 10, label: '5' },
  { id: '4',    x: 312, y: 275, w: 34,  h: 15,  tx: 329,   ty: 282.5, fs: 10, label: '4' },
  { id: '3',    x: 312, y: 290, w: 34,  h: 15,  tx: 329,   ty: 297.5, fs: 10, label: '3' },
  { id: '2',    x: 312, y: 320, w: 34,  h: 15,  tx: 329,   ty: 327.5, fs: 10, label: '2' },
  { id: '1',    x: 312, y: 335, w: 34,  h: 13,  tx: 329,   ty: 341.5, fs: 9,  label: '1' },
  { id: '30',   x: 13,  y: 200, w: 30,  h: 60,  tx: 28,    ty: 230,   fs: 13, label: '30' },
  { id: '31',   x: 13,  y: 260, w: 30,  h: 60,  tx: 28,    ty: 290,   fs: 13, label: '31' },
  { id: '24',   x: 13,  y: 320, w: 30,  h: 43,  tx: 28,    ty: 341.5, fs: 13, label: '24' },
  { id: '21',   x: 73,  y: 245, w: 30,  h: 60,  tx: 88,    ty: 275,   fs: 13, label: '21' },
  { id: '25',   x: 73,  y: 305, w: 30,  h: 58,  tx: 88,    ty: 334,   fs: 13, label: '25' },
  { id: '19',   x: 102, y: 215, w: 30,  h: 148, tx: 117,   ty: 289,   fs: 13, label: '19' },
  { id: '23',   x: 132, y: 320, w: 60,  h: 28,  tx: 162,   ty: 334,   fs: 13, label: '23' },
  { id: '22',   x: 102, y: 363, w: 90,  h: 30,  tx: 147,   ty: 378,   fs: 13, label: '22' },
  { id: '27',   x: 222, y: 378, w: 124, h: 15,  tx: 284,   ty: 385.5, fs: 10, label: '27' },
  { id: '26',   x: 222, y: 408, w: 124, h: 15,  tx: 284,   ty: 415.5, fs: 10, label: '26' },
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
</script>

<style scoped>
.factory-fullscreen {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: var(--background, #f5f6fa);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.factory-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md, 12px);
  padding: 8px 16px;
  background: #2c3e50;
  color: white;
  flex-shrink: 0;
}

.factory-header .page-title {
  margin: 0;
  font-size: var(--font-size-lg, 18px);
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
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

/* Factory SVG */
.factory-svg {
  width: 100%;
  flex: 1;
  min-height: 0;
  background: #fff;
}

.area {
  shape-rendering: crispEdges;
  vector-effect: non-scaling-stroke;
  fill: rgb(183,183,183);
  stroke: rgb(120,120,120);
  stroke-width: 2;
}

.area-text {
  font-family: Arial, sans-serif;
  font-size: 11px;
  fill: #222;
  text-anchor: middle;
  dominant-baseline: middle;
}

.press-rect {
  shape-rendering: crispEdges;
  vector-effect: non-scaling-stroke;
  stroke: rgb(120,120,120);
  stroke-width: 2;
  cursor: pointer;
  transition: fill 0.2s;
}

.press-rect:hover {
  stroke: #0055ff;
  stroke-width: 3;
}

.press-rect.selected {
  stroke: #0055ff;
  stroke-width: 3;
}

.tag {
  shape-rendering: crispEdges;
  vector-effect: non-scaling-stroke;
  fill: rgb(207,226,243);
  stroke: rgb(120,120,120);
  stroke-width: 2;
}

.press-text {
  font-family: Arial, sans-serif;
  font-size: 11px;
  fill: #222;
  text-anchor: middle;
  dominant-baseline: middle;
  pointer-events: none;
}

/* Status colors */
.status-running { fill: #6abf69; }
.status-idle    { fill: rgb(207,226,243); }
.status-error   { fill: #e74c3c; }
.status-warning { fill: #f4d03f; }

/* SVG legend */
.svg-legend {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 11px;
  color: #555;
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

.svg-legend-box.running { background: #6abf69; }
.svg-legend-box.idle    { background: rgb(207,226,243); }
.svg-legend-box.warning { background: #f4d03f; }
.svg-legend-box.error   { background: #e74c3c; }

.selected-press-info {
  margin-top: 4px;
  font-size: 12px;
  color: #333;
  background: #f0f4f8;
  padding: 4px 10px;
  border-radius: 4px;
}

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
}

.status-table th,
.status-table td {
  padding: 5px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.status-table th {
  background-color: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 1;
}

.status-table tr:hover {
  background-color: #f5f5f5;
}

.status-table tr.row-selected {
  background-color: #d6eaf8;
}
</style>
