<template>
  <div>
    <AppHeader />
    <AppNavigation />
    <main class="app-main">
      <h1 class="page-title">マスターデータ管理</h1>

      <div class="grid grid-auto">
        <router-link
          v-for="menu in masterMenus"
          :key="menu.path"
          :to="menu.path"
          class="card master-menu-card"
        >
          <h3>{{ menu.label }}</h3>
          <p>{{ menu.description }}</p>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
import AppHeader from '../../components/common/AppHeader.vue'
import AppNavigation from '../../components/common/AppNavigation.vue'

const masterMenus = [
  { path: '/master/customers', label: '顧客マスター', description: '顧客情報を管理' },
  { path: '/master/products', label: '製品コードマスター', description: '製品コードを管理' },
  { path: '/master/employees', label: '従業員マスター', description: '従業員情報を管理' },
  { path: '/master/suppliers', label: '仕入先マスター', description: '仕入先情報を管理' },
  { path: '/master/process-names', label: '工程名マスター', description: '工程名と種別を管理' },
  { path: '/master/material-rates', label: '材料仕様マスター', description: '材料仕様を管理' },
  { path: '/master/machines', label: '機械リストマスター', description: '機械設備を管理' },
  { path: '/master/spm', label: '生産プレス機設定マスター', description: '生産プレス機設定を管理' },
  { path: '/master/holidays', label: '休日マスター', description: '休日・祝日を管理' },
]
</script>

<style scoped>
.page-title {
  margin-bottom: var(--spacing-lg);
}

.master-menu-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.master-menu-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.master-menu-card h3 {
  color: var(--primary);
  margin-bottom: var(--spacing-sm);
}

.master-menu-card p {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}
</style>
