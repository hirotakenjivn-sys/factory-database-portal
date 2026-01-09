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

<style scoped>
/* Mobile Menu Toggle - hidden on desktop */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 1001;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 12px;
  cursor: pointer;
  font-size: 20px;
}

.mobile-menu-toggle:hover {
  background: #34495e;
}

/* Mobile Overlay - hidden by default */
.mobile-menu-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.mobile-menu-overlay.active {
  display: block;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }
}
</style>
