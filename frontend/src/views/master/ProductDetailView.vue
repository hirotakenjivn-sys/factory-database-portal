<template>
  <AppLayout>
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master/products" class="btn btn-secondary">← Back to Product List</router-link>
      </div>

      <h1 class="page-title">Product Details</h1>

      <div v-if="loading" class="empty-state">
        <p>Loading...</p>
      </div>

      <div v-else-if="product">
        <!-- Basic Info -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>Basic Info</h2>
          <form @submit.prevent="handleUpdateProduct">
            <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
              <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
                <label class="form-label" style="margin-bottom: 0;">Product Code</label>
                <input v-model="product.product_code" class="form-input" type="text" required />
              </div>
              <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
                <label class="form-label" style="margin-bottom: 0;">Customer ID</label>
                <input v-model.number="product.customer_id" class="form-input" type="number" required />
              </div>
              <div style="display: flex; align-items: center; gap: var(--spacing-sm); height: 34px;">
                <input v-model="product.is_active" type="checkbox" />
                <span>Active</span>
              </div>
              <div>
                <button type="submit" class="btn btn-primary">Update</button>
              </div>
            </div>
          </form>
        </div>

        <!-- Material Specs -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>Material Specs</h2>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Thickness</th>
                <th>Width</th>
                <th>Pitch</th>
                <th>H</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="material in materialRates" :key="material.material_rate_id">
                <td>{{ material.material_rate_id }}</td>
                <td>{{ material.thickness }}</td>
                <td>{{ material.width }}</td>
                <td>{{ material.pitch }}</td>
                <td>{{ material.h }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="materialRates.length === 0" class="empty-state">
            <p>No material spec data found</p>
          </div>
        </div>

        <!-- Process Management -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-md);">
            <h2 style="margin-bottom: 0;">Process Management</h2>
            <button @click="showAddProcessForm = !showAddProcessForm" class="btn btn-primary">
              {{ showAddProcessForm ? 'Cancel' : '+ Add Process' }}
            </button>
          </div>

          <!-- Add Process Form -->
          <div v-if="showAddProcessForm" class="form-card" style="margin-bottom: var(--spacing-md); padding: var(--spacing-md); background: #f9fafb; border-radius: 8px;">
            <form @submit.prevent="handleAddProcess">
              <div style="display: flex; flex-wrap: wrap; gap: var(--spacing-sm); align-items: flex-end;">
                <div style="width: 100px;">
                  <label class="form-label">Process No</label>
                  <input v-model.number="newProcess.process_no" class="form-input" type="number" required />
                </div>
                <div style="width: 150px;">
                  <label class="form-label">Process Name</label>
                  <input v-model="newProcess.process_name" class="form-input" type="text" required />
                </div>
                <div style="width: 120px;">
                  <label class="form-label">DAY</label>
                  <input v-model.number="newProcess.rough_cycletime" class="form-input" type="number" step="0.01" placeholder="Days" />
                </div>
                <div style="width: 150px;">
                  <label class="form-label">Prod. Limit (pcs)</label>
                  <input v-model.number="newProcess.production_limit" class="form-input" type="number" placeholder="Pcs" />
                </div>
                <div style="width: 120px;">
                  <label class="form-label">Setup Time (min)</label>
                  <input v-model.number="newProcess.setup_time" class="form-input" type="number" step="0.01" placeholder="Min" />
                </div>
                <div>
                  <button type="submit" class="btn btn-success">Add</button>
                </div>
              </div>
            </form>
          </div>

          <!-- Process List Table -->
          <table class="table">
            <thead>
              <tr>
                <th style="width: 80px;">Process No</th>
                <th style="width: 150px;">Process Name</th>
                <th style="width: 100px;">DAY</th>
                <th style="width: 120px;">Prod. Limit (pcs)</th>
                <th style="width: 120px;">Setup Time (min)</th>
                <th style="width: 100px;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="process in processes" :key="process.process_id">
                <template v-if="editingProcessId === process.process_id">
                  <!-- Edit Mode -->
                  <td>
                    <input v-model.number="editingProcess.process_no" class="form-input" type="number" style="width: 70px;" required />
                  </td>
                  <td>
                    <input v-model="editingProcess.process_name" class="form-input" type="text" style="width: 140px;" required />
                  </td>
                  <td>
                    <input v-model.number="editingProcess.rough_cycletime" class="form-input" type="number" step="0.01" style="width: 90px;" />
                  </td>
                  <td>
                    <input v-model.number="editingProcess.production_limit" class="form-input" type="number" style="width: 110px;" />
                  </td>
                  <td>
                    <input v-model.number="editingProcess.setup_time" class="form-input" type="number" step="0.01" style="width: 110px;" />
                  </td>
                  <td>
                    <button @click="handleSaveProcess(process.process_id)" class="btn btn-success btn-sm" style="margin-right: 4px;">Save</button>
                    <button @click="cancelEdit" class="btn btn-secondary btn-sm">Cancel</button>
                  </td>
                </template>
                <template v-else>
                  <!-- View Mode -->
                  <td>{{ process.process_no }}</td>
                  <td>{{ process.process_name }}</td>
                  <td :class="{ 'highlight-zero-cycletime': Number(process.rough_cycletime) === 0 }">{{ process.rough_cycletime || '-' }}</td>
                  <td>{{ process.production_limit ? process.production_limit.toLocaleString() : '-' }}</td>
                  <td>{{ process.setup_time || '-' }}</td>
                  <td>
                    <button @click="startEdit(process)" class="btn btn-primary btn-sm" style="margin-right: 4px;">Edit</button>
                    <button @click="handleDeleteProcess(process.process_id)" class="btn btn-danger btn-sm">Delete</button>
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
          <div v-if="processes.length === 0" class="empty-state">
            <p>No process data found</p>
          </div>
        </div>

        <!-- Cycletime Settings -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>Cycletime Settings</h2>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Process Name</th>
                <th>Press No</th>
                <th>Cycle Time</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ct in cycletimeSettings" :key="ct.cycletime_id">
                <td>{{ ct.cycletime_id }}</td>
                <td>{{ ct.process_name }}</td>
                <td>{{ ct.press_no }}</td>
                <td>{{ ct.cycle_time }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="cycletimeSettings.length === 0" class="empty-state">
            <p>No cycletime setting data found</p>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>Product not found</p>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../../components/common/AppLayout.vue'
import api from '../../utils/api'

const route = useRoute()
const productId = parseInt(route.params.id)

const loading = ref(true)
const product = ref(null)
const materialRates = ref([])
const cycletimeSettings = ref([])
const processes = ref([])

// 工程追加フォーム
const showAddProcessForm = ref(false)
const newProcess = ref({
  process_no: null,
  process_name: '',
  rough_cycletime: null,
  production_limit: null,
  setup_time: null
})

// 工程編集
const editingProcessId = ref(null)
const editingProcess = ref({})

const loadProduct = async () => {
  try {
    const response = await api.get(`/master/products?search=`)
    const allProducts = response.data
    product.value = allProducts.find(p => p.product_id === productId)

    if (!product.value) {
      console.error('Product not found')
    }
  } catch (error) {
    console.error('Failed to load product:', error)
    alert('Failed to load product')
  }
}

const loadMaterialRates = async () => {
  try {
    const response = await api.get('/master/material-rates')
    materialRates.value = response.data.filter(m => m.product_id === productId)
  } catch (error) {
    console.error('Failed to load material rates:', error)
  }
}

const loadCycletimeSettings = async () => {
  try {
    const response = await api.get('/master/cycletimes')
    cycletimeSettings.value = response.data.filter(c => c.product_id === productId)
  } catch (error) {
    console.error('Failed to load cycletime settings:', error)
  }
}

const loadProcesses = async () => {
  try {
    const response = await api.get(`/process/products/${productId}/processes`)
    processes.value = response.data
  } catch (error) {
    console.error('Failed to load processes:', error)
  }
}

const handleAddProcess = async () => {
  try {
    await api.post('/process/processes', {
      product_id: productId,
      process_no: newProcess.value.process_no,
      process_name: newProcess.value.process_name,
      rough_cycletime: newProcess.value.rough_cycletime,
      production_limit: newProcess.value.production_limit,
      setup_time: newProcess.value.setup_time
    })
    alert('Process added successfully')
    showAddProcessForm.value = false
    newProcess.value = {
      process_no: null,
      process_name: '',
      rough_cycletime: null,
      production_limit: null,
      setup_time: null
    }
    await loadProcesses()
  } catch (error) {
    console.error('Failed to add process:', error)
    alert('Failed to add process: ' + (error.response?.data?.detail || error.message))
  }
}

const startEdit = (process) => {
  editingProcessId.value = process.process_id
  editingProcess.value = { ...process }
}

const cancelEdit = () => {
  editingProcessId.value = null
  editingProcess.value = {}
}

const handleSaveProcess = async (processId) => {
  try {
    await api.put(`/process/processes/${processId}`, {
      process_no: editingProcess.value.process_no,
      process_name: editingProcess.value.process_name,
      rough_cycletime: editingProcess.value.rough_cycletime,
      production_limit: editingProcess.value.production_limit,
      setup_time: editingProcess.value.setup_time
    })
    alert('Process updated successfully')
    cancelEdit()
    await loadProcesses()
  } catch (error) {
    console.error('Failed to update process:', error)
    alert('Failed to update process: ' + (error.response?.data?.detail || error.message))
  }
}

const handleDeleteProcess = async (processId) => {
  if (!confirm('Are you sure you want to delete this process?')) {
    return
  }
  try {
    await api.delete(`/process/processes/${processId}`)
    alert('Process deleted successfully')
    await loadProcesses()
  } catch (error) {
    console.error('Failed to delete process:', error)
    alert('Failed to delete process: ' + (error.response?.data?.detail || error.message))
  }
}

const handleUpdateProduct = async () => {
  try {
    await api.put(`/master/products/${productId}`, {
      product_code: product.value.product_code,
      customer_id: product.value.customer_id,
      is_active: product.value.is_active,
    })
    alert('Product updated successfully')
  } catch (error) {
    console.error('Failed to update product:', error)
    alert('Failed to update product')
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    loadProduct(),
    loadMaterialRates(),
    loadCycletimeSettings(),
    loadProcesses(),
  ])
  loading.value = false
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.status-active {
  color: var(--success);
  font-weight: 600;
}

.status-inactive {
  color: var(--text-secondary);
}

.highlight-zero-cycletime {
  background-color: rgba(255, 235, 59, 0.3) !important;
}
</style>
