<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">従業員マスター</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>従業員登録</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">従業員番号</label>
              <input v-model="form.employee_no" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">名前</label>
              <input v-model="form.name" class="form-input" type="text" required />
            </div>
            <div style="display: flex; align-items: center; gap: var(--spacing-sm); height: 34px;">
              <input v-model="form.is_active" type="checkbox" />
              <span>有効</span>
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>従業員一覧</h2>
        <div style="display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); flex-wrap: wrap;">
          <input
            v-model="searchEmployeeNo"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="従業員番号で検索..."
            style="width: 200px;"
          />
          <input
            v-model="searchName"
            @input="handleSearch"
            class="form-input"
            type="text"
            placeholder="名前で検索..."
            style="width: 200px;"
          />
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>従業員ID</th>
              <th>従業員番号</th>
              <th>名前</th>
              <th>ステータス</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employee in employees" :key="employee.employee_id">
              <td>{{ employee.employee_id }}</td>
              <td>{{ employee.employee_no }}</td>
              <td>{{ employee.name }}</td>
              <td>
                <span :class="employee.is_active ? 'status-active' : 'status-inactive'">
                  {{ employee.is_active ? '有効' : '無効' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="employees.length === 0" class="empty-state">
          <p>従業員データがありません</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'
import api from '../../utils/api'

const form = ref({
  employee_no: '',
  name: '',
  is_active: true,
})

const employees = ref([])
const searchEmployeeNo = ref('')
const searchName = ref('')

const loadEmployees = async () => {
  try {
    const params = {}
    if (searchEmployeeNo.value) {
      params.employee_no = searchEmployeeNo.value
    }
    if (searchName.value) {
      params.name = searchName.value
    }
    const response = await api.get('/master/employees', { params })
    employees.value = response.data
  } catch (error) {
    console.error('Failed to load employees:', error)
    alert('従業員の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/employees', form.value)
    alert('従業員の登録に成功しました')
    form.value = {
      employee_no: '',
      name: '',
      is_active: true,
    }
    await loadEmployees()
  } catch (error) {
    console.error('Failed to create employee:', error)
    alert('従業員の登録に失敗しました')
  }
}

const handleSearch = () => {
  loadEmployees()
}

onMounted(() => {
  loadEmployees()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.status-active {
  color: var(--success);
  font-weight: 600;
}

.status-inactive {
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
