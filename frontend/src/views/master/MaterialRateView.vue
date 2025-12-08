<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <div style="margin-bottom: var(--spacing-lg)">
        <router-link to="/master" class="btn btn-secondary">← マスターメニューに戻る</router-link>
      </div>

      <h1 class="page-title">材料仕様マスター</h1>

      <!-- Registration Form -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>材料仕様登録</h2>
        <form @submit.prevent="handleSubmit">
          <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end;">
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">製品コード</label>
              <AutocompleteInput
                v-model="form.product_id"
                endpoint="/master/autocomplete/products"
                display-field="code"
                value-field="id"
                placeholder="製品コードを入力..."
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">厚さ</label>
              <input v-model.number="form.thickness" class="form-input" type="number" step="0.01" required />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">幅</label>
              <input v-model.number="form.width" class="form-input" type="number" step="0.01" required />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">ピッチ</label>
              <input v-model.number="form.pitch" class="form-input" type="number" step="0.01" required />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">H (高さ)</label>
              <input v-model.number="form.h" class="form-input" type="number" step="0.01" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </div>
        </form>
      </div>

      <!-- List -->
      <div class="card">
        <h2>材料仕様一覧</h2>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          class="form-input"
          type="text"
          placeholder="製品コードで検索..."
          style="margin-bottom: var(--spacing-md); max-width: 175px;"
        />
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>製品コード</th>
              <th>厚さ</th>
              <th>幅</th>
              <th>ピッチ</th>
              <th>H</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in materialRates" :key="item.material_rate_id">
              <td>{{ item.material_rate_id }}</td>
              <td>
                <CopyableText v-if="item.product_code" :text="item.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ item.thickness }}</td>
              <td>{{ item.width }}</td>
              <td>{{ item.pitch }}</td>
              <td>{{ item.h }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="materialRates.length === 0" class="empty-state">
          <p>材料仕様データがありません</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'
import AutocompleteInput from '../../components/common/AutocompleteInput.vue'
import CopyableText from '../../components/common/CopyableText.vue'
import api from '../../utils/api'

const form = ref({
  product_id: null,
  thickness: null,
  width: null,
  pitch: null,
  h: null,
})

const materialRates = ref([])
const searchQuery = ref('')

const loadMaterialRates = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await api.get('/master/material-rates', { params })
    materialRates.value = response.data
  } catch (error) {
    console.error('Failed to load material rates:', error)
    alert('材料仕様の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id) {
    alert('製品を選択してください')
    return
  }

  try {
    await api.post('/master/material-rates', form.value)
    alert('材料仕様の登録に成功しました')
    form.value = {
      product_id: null,
      thickness: null,
      width: null,
      pitch: null,
      h: null,
    }
    await loadMaterialRates()
  } catch (error) {
    console.error('Failed to create material rate:', error)
    alert('材料仕様の登録に失敗しました')
  }
}

const handleSearch = () => {
  loadMaterialRates(searchQuery.value)
}

onMounted(() => {
  loadMaterialRates()
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
</style>
