<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">仕入先マスター</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>仕入先登録</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">仕入先名</label>
              <input v-model="form.supplier_name" class="form-input" type="text" required />
            </div>
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">業種</label>
              <input v-model="form.supplier_business" class="form-input" type="text" />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>仕入先一覧</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="仕入先名で検索..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>仕入先ID</th>
              <th>仕入先名</th>
              <th>業種</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="supplier in suppliers" :key="supplier.supplier_id">
              <td>{{ supplier.supplier_id }}</td>
              <td>{{ supplier.supplier_name }}</td>
              <td>{{ supplier.supplier_business || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="suppliers.length === 0" class="empty-state">
          <p>仕入先データがありません</p>
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
  supplier_name: '',
  supplier_business: '',
})

const suppliers = ref([])
const searchQuery = ref('')

const loadSuppliers = async (search = '') => {
  try {
    const response = await api.get('/master/suppliers', {
      params: { search },
    })
    suppliers.value = response.data
  } catch (error) {
    console.error('Failed to load suppliers:', error)
    alert('仕入先の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  try {
    await api.post('/master/suppliers', form.value)
    alert('仕入先の登録に成功しました')
    form.value = {
      supplier_name: '',
      supplier_business: '',
    }
    await loadSuppliers()
  } catch (error) {
    console.error('Failed to create supplier:', error)
    alert('仕入先の登録に失敗しました')
  }
}

const handleSearch = () => {
  loadSuppliers(searchQuery.value)
}

onMounted(() => {
  loadSuppliers()
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

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
