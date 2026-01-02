<template>
  <AppLayout>
      <h1 class="page-title">倉庫 - 完成品管理</h1>

      <!-- 完成品登録フォーム -->
      <div class="card" style="margin-bottom: var(--spacing-lg)">
        <h2>完成品登録</h2>
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
            <div style="width: 175px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">ロット番号</label>
              <AutocompleteInput
                v-model="form.lot_id"
                endpoint="/master/autocomplete/lots"
                display-field="number"
                value-field="id"
                placeholder="ロット番号を入力..."
                required
              />
            </div>
            <div style="width: 81px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">完成数量</label>
              <input v-model.number="form.finished_quantity" class="form-input" type="number" required />
            </div>
            <div style="width: 113px; display: flex; flex-direction: column; gap: 2px;">
              <label class="form-label" style="margin-bottom: 0;">完成日</label>
              <input v-model="form.date_finished" class="form-input" type="text" placeholder="DD/MM/YYYY" required />
            </div>
            <div>
              <button type="submit" class="btn btn-primary">登録</button>
            </div>
          </div>
        </form>
      </div>

      <!-- 完成品一覧 -->
      <div class="card">
        <h2>完成品一覧</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>顧客名</th>
              <th>製品コード</th>
              <th>ロット番号</th>
              <th>完成数量</th>
              <th>完成日</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in finishedProducts" :key="item.finished_product_id">
              <td>{{ item.finished_product_id }}</td>
              <td>{{ item.customer_name || '-' }}</td>
              <td>
                <CopyableText v-if="item.product_code" :text="item.product_code" />
                <span v-else>-</span>
              </td>
              <td>{{ item.lot_number || '-' }}</td>
              <td>{{ item.finished_quantity.toLocaleString() }}</td>
              <td>{{ formatDateForDisplay(item.date_finished) }}</td>
              <td>
                <button @click="handleDelete(item.finished_product_id)" class="btn btn-danger btn-sm">
                  削除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="finishedProducts.length === 0" class="empty-state">
          <p>完成品データがありません</p>
        </div>
      </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/common/AppLayout.vue'
import AutocompleteInput from '../components/common/AutocompleteInput.vue'
import CopyableText from '../components/common/CopyableText.vue'
import api from '../utils/api'
import { getTodayFormatted, formatDateForDisplay, formatDateForApi } from '../utils/dateFormat'

const form = ref({
  product_id: null,
  lot_id: null,
  finished_quantity: null,
  date_finished: getTodayFormatted(),
})

const finishedProducts = ref([])

const loadFinishedProducts = async () => {
  try {
    const response = await api.get('/warehouse/finished-products')
    finishedProducts.value = response.data
  } catch (error) {
    console.error('Failed to load finished products:', error)
    alert('完成品の読み込みに失敗しました')
  }
}

const handleSubmit = async () => {
  if (!form.value.product_id || !form.value.lot_id) {
    alert('製品コードとロット番号を選択してください')
    return
  }

  try {
    // DD/MM/YYYY形式をYYYY-MM-DD形式に変換してAPIに送信
    const submitData = {
      ...form.value,
      date_finished: formatDateForApi(form.value.date_finished)
    }

    await api.post('/warehouse/finished-products', submitData)
    alert('完成品登録成功')
    form.value = {
      product_id: null,
      lot_id: null,
      finished_quantity: null,
      date_finished: getTodayFormatted(),
    }
    await loadFinishedProducts()
  } catch (error) {
    console.error('Failed to create finished product:', error)
    alert('完成品登録に失敗しました')
  }
}

const handleDelete = async (id) => {
  if (!confirm('この完成品を削除しますか？')) {
    return
  }

  try {
    await api.delete(`/warehouse/finished-products/${id}`)
    alert('削除成功')
    await loadFinishedProducts()
  } catch (error) {
    console.error('Failed to delete finished product:', error)
    alert('削除に失敗しました')
  }
}

onMounted(() => {
  loadFinishedProducts()
})
</script>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.btn-danger {
  background: var(--error);
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}
</style>
