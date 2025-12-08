<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master/products" class="btn btn-secondary">← 製品一覧に戻る</router-link>
      </div>

      <h1 class="page-title">製品詳細</h1>

      <div v-if="loading" class="empty-state">
        <p>読み込み中...</p>
      </div>

      <div v-else-if="product">
        <!-- 製品基本情報 -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>基本情報</h2>
          <form @submit.prevent="handleUpdateProduct">
            <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
              <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
                <label class="form-label" style="margin-bottom: 0;">製品コード</label>
                <input v-model="product.product_code" class="form-input" type="text" required />
              </div>
              <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
                <label class="form-label" style="margin-bottom: 0;">顧客ID</label>
                <input v-model.number="product.customer_id" class="form-input" type="number" required />
              </div>
              <div style="display: flex; align-items: center; gap: var(--spacing-sm); height: 34px;">
                <input v-model="product.is_active" type="checkbox" />
                <span>有効</span>
              </div>
              <div>
                <button type="submit" class="btn btn-primary">更新</button>
              </div>
            </div>
          </form>
        </div>

        <!-- 材料仕様 -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>材料仕様</h2>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>厚さ</th>
                <th>幅</th>
                <th>ピッチ</th>
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
            <p>材料仕様データがありません</p>
          </div>
        </div>

        <!-- 工程管理 -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-md);">
            <h2 style="margin-bottom: 0;">工程管理</h2>
            <button @click="showAddProcessForm = !showAddProcessForm" class="btn btn-primary">
              {{ showAddProcessForm ? 'キャンセル' : '+ 工程を追加' }}
            </button>
          </div>

          <!-- 新規工程追加フォーム -->
          <div v-if="showAddProcessForm" class="form-card" style="margin-bottom: var(--spacing-md); padding: var(--spacing-md); background: #f9fafb; border-radius: 8px;">
            <form @submit.prevent="handleAddProcess">
              <div style="display: flex; flex-wrap: wrap; gap: var(--spacing-sm); align-items: flex-end;">
                <div style="width: 100px;">
                  <label class="form-label">工程番号</label>
                  <input v-model.number="newProcess.process_no" class="form-input" type="number" required />
                </div>
                <div style="width: 150px;">
                  <label class="form-label">工程名</label>
                  <input v-model="newProcess.process_name" class="form-input" type="text" required />
                </div>
                <div style="width: 120px;">
                  <label class="form-label">DAY</label>
                  <input v-model.number="newProcess.rough_cycletime" class="form-input" type="number" step="0.01" placeholder="日数" />
                </div>
                <div style="width: 150px;">
                  <label class="form-label">生産限界 (pcs)</label>
                  <input v-model.number="newProcess.production_limit" class="form-input" type="number" placeholder="個数" />
                </div>
                <div style="width: 120px;">
                  <label class="form-label">段取時間 (分)</label>
                  <input v-model.number="newProcess.setup_time" class="form-input" type="number" step="0.01" placeholder="分" />
                </div>
                <div>
                  <button type="submit" class="btn btn-success">追加</button>
                </div>
              </div>
            </form>
          </div>

          <!-- 工程一覧テーブル -->
          <table class="table">
            <thead>
              <tr>
                <th style="width: 80px;">工程番号</th>
                <th style="width: 150px;">工程名</th>
                <th style="width: 100px;">DAY</th>
                <th style="width: 120px;">生産限界 (pcs)</th>
                <th style="width: 120px;">段取時間 (分)</th>
                <th style="width: 100px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="process in processes" :key="process.process_id">
                <template v-if="editingProcessId === process.process_id">
                  <!-- 編集モード -->
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
                    <button @click="handleSaveProcess(process.process_id)" class="btn btn-success btn-sm" style="margin-right: 4px;">保存</button>
                    <button @click="cancelEdit" class="btn btn-secondary btn-sm">キャンセル</button>
                  </td>
                </template>
                <template v-else>
                  <!-- 表示モード -->
                  <td>{{ process.process_no }}</td>
                  <td>{{ process.process_name }}</td>
                  <td>{{ process.rough_cycletime || '-' }}</td>
                  <td>{{ process.production_limit ? process.production_limit.toLocaleString() : '-' }}</td>
                  <td>{{ process.setup_time || '-' }}</td>
                  <td>
                    <button @click="startEdit(process)" class="btn btn-primary btn-sm" style="margin-right: 4px;">編集</button>
                    <button @click="handleDeleteProcess(process.process_id)" class="btn btn-danger btn-sm">削除</button>
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
          <div v-if="processes.length === 0" class="empty-state">
            <p>工程データがありません</p>
          </div>
        </div>

        <!-- SPM設定 -->
        <div class="card" style="margin-bottom: var(--spacing-lg)">
          <h2>SPM設定</h2>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>工程番号</th>
                <th>プレス番号</th>
                <th>サイクルタイム</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="spm in spmSettings" :key="spm.spm_id">
                <td>{{ spm.spm_id }}</td>
                <td>{{ spm.process_no }}</td>
                <td>{{ spm.press_no }}</td>
                <td>{{ spm.cycle_time }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="spmSettings.length === 0" class="empty-state">
            <p>SPM設定データがありません</p>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>製品が見つかりません</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'
import api from '../../utils/api'

const route = useRoute()
const productId = parseInt(route.params.id)

const loading = ref(true)
const product = ref(null)
const materialRates = ref([])
const spmSettings = ref([])
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
    alert('製品の読み込みに失敗しました')
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

const loadSpmSettings = async () => {
  try {
    const response = await api.get('/master/spm')
    spmSettings.value = response.data.filter(s => s.product_id === productId)
  } catch (error) {
    console.error('Failed to load SPM settings:', error)
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
    alert('工程を追加しました')
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
    alert('工程の追加に失敗しました: ' + (error.response?.data?.detail || error.message))
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
    alert('工程を更新しました')
    cancelEdit()
    await loadProcesses()
  } catch (error) {
    console.error('Failed to update process:', error)
    alert('工程の更新に失敗しました: ' + (error.response?.data?.detail || error.message))
  }
}

const handleDeleteProcess = async (processId) => {
  if (!confirm('この工程を削除してもよろしいですか？')) {
    return
  }
  try {
    await api.delete(`/process/processes/${processId}`)
    alert('工程を削除しました')
    await loadProcesses()
  } catch (error) {
    console.error('Failed to delete process:', error)
    alert('工程の削除に失敗しました: ' + (error.response?.data?.detail || error.message))
  }
}

const handleUpdateProduct = async () => {
  try {
    await api.put(`/master/products/${productId}`, {
      product_code: product.value.product_code,
      customer_id: product.value.customer_id,
      is_active: product.value.is_active,
    })
    alert('製品情報を更新しました')
  } catch (error) {
    console.error('Failed to update product:', error)
    alert('製品情報の更新に失敗しました')
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    loadProduct(),
    loadMaterialRates(),
    loadSpmSettings(),
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
</style>
