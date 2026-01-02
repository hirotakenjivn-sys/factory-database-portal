<template>
  <div class="app-wrapper">
    <AppNavigation ref="navRef" />
    <div class="app-content">
      <AppHeader />
      <main class="app-main">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup>
import AppHeader from './AppHeader.vue'
import AppNavigation from './AppNavigation.vue'
</script>
