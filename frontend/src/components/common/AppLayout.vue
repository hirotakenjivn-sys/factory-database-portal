<template>
  <div class="app-wrapper">
    <AppNavigation ref="navRef" />
    <div class="app-content" :class="{ 'sidebar-collapsed': navRef?.isCollapsed }">
      <AppHeader />
      <main class="app-main">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './AppHeader.vue'
import AppNavigation from './AppNavigation.vue'

const navRef = ref(null)
</script>
