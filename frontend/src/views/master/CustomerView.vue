<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">顧客マスター</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>顧客登録</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">顧客名</label>
              <input v-model="form.customer_name" class="form-input" type="text" required />
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
        <h2>顧客一覧</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="顧客名で検索..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>顧客ID</th>
              <th>顧客名</th>
              <th>ステータス</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in customers" :key="customer.customer_id">
              <td>{{ customer.customer_id }}</td>
              <td>{{ customer.customer_name }}</td>
              <td>
                <span :class="customer.is_active ? 'status-active' : 'status-inactive'">
                  {{ customer.is_active ? '有効' : '無効' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
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
  customer_name: '',
  is_active: true,
})

const customers = ref([])
const searchQuery = ref('')

const loadCustomers = async (search = '') => {
  try {
    const response = await api.get('/master/customers', {
      params: { search },
    })
    customers.value = response.data
  } catch (error) {
    console.error('Failed to load customers:', error)
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/customers', form.value)
    alert('顧客の登録に成功しました')
    form.value = { customer_name: '', is_active: true }
    loadCustomers()
  } catch (error) {
    console.error('Failed to create customer:', error)
    alert('顧客の登録に失敗しました')
  }
}

const handleSearch = () => {
  loadCustomers(searchQuery.value)
}

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

h2 {
  margin-bottom: var(--spacing-md);
}

.status-active {
  color: var(--success);
  font-weight: 600;
}

.status-inactive {
  color: var(--text-secondary);
}
</style>
