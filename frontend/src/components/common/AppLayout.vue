<template>
  <div class="app-wrapper">
    <!-- Mobile Menu Toggle Button -->
    <button class="mobile-menu-toggle" @click="toggleMobileMenu">
      ☰
    </button>

    <!-- Mobile Menu Overlay -->
    <div
      class="mobile-menu-overlay"
      :class="{ active: navRef?.mobileOpen }"
      @click="closeMobileMenu"
    ></div>

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

const toggleMobileMenu = () => {
  navRef.value?.toggleMobileMenu()
}

const closeMobileMenu = () => {
  navRef.value?.closeMobileMenu()
}
</script>
