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
  { name: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { name: 'trace', label: 'Trace', path: '/trace' },
  { name: 'outsource', label: 'Outsource', path: '/outsource' },
  { name: 'schedule', label: 'Schedule', path: '/schedule' },
  { name: 'sales', label: 'Sales', path: '/sales' },
  { name: 'press', label: 'Press', path: '/press' },
  { name: 'warehouse', label: 'Warehouse', path: '/warehouse' },
  { name: 'mold', label: 'Mold', path: '/mold' },
  { name: 'master', label: 'Master', path: '/master' },
]
</script>
