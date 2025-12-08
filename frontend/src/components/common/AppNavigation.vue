<template>
  <nav class="app-navigation">
    <router-link
      v-for="item in navItems"
      :key="item.name"
      :to="item.path"
      class="nav-item"
      :class="{ active: $route.path === item.path }"
    >
      {{ item.label }}
    </router-link>
  </nav>
</template>

<script setup>
const navItems = [
  { name: 'dashboard', label: 'ダッシュボード', path: '/dashboard' },
  { name: 'trace', label: 'トレース', path: '/trace' },
  { name: 'outsource', label: '委託', path: '/outsource' },
  { name: 'schedule', label: 'スケジュール', path: '/schedule' },
  { name: 'sales', label: '販売', path: '/sales' },
  { name: 'press', label: 'プレス', path: '/press' },
  { name: 'warehouse', label: '倉庫', path: '/warehouse' },
  { name: 'mold', label: '金型', path: '/mold' },
  { name: 'master', label: 'マスター', path: '/master' },
]
</script>
