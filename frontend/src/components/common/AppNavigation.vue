<template>
  <nav class="app-sidebar" :class="{ collapsed: isCollapsed, 'mobile-open': mobileOpen }">
    <div class="sidebar-toggle" @click="toggleSidebar">
      <span class="toggle-icon">{{ isCollapsed ? '>' : '<' }}</span>
    </div>

    <div class="sidebar-menu">
      <template v-for="item in navItems" :key="item.name">
        <!-- Items with children: expandable -->
        <template v-if="item.children">
          <div
            class="nav-item"
            :class="{ active: isParentActive(item) }"
            :title="item.label"
            @click="toggleSubmenu(item.name)"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label" v-show="!isCollapsed">{{ item.label }}</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ openSubmenus[item.name] ? '▾' : '▸' }}</span>
          </div>
          <div v-show="openSubmenus[item.name] && !isCollapsed" class="submenu">
            <router-link
              v-for="child in item.children"
              :key="child.name"
              :to="child.path"
              class="nav-item sub-item"
              :class="{ active: $route.path === child.path }"
              :title="child.label"
              @click="closeMobileMenu"
            >
              <span class="nav-label">{{ child.label }}</span>
            </router-link>
          </div>
        </template>

        <!-- Normal items -->
        <router-link
          v-else
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
          :title="item.label"
          @click="closeMobileMenu"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label" v-show="!isCollapsed">{{ item.label }}</span>
        </router-link>
      </template>
    </div>

    <div class="sidebar-footer">
      <div class="user-info" v-if="authStore.user">
        <span class="user-icon">👤</span>
        <span class="user-name" v-show="!isCollapsed">{{ displayName }}</span>
      </div>
      <button @click="handleLogout" class="logout-btn" :title="isCollapsed ? 'Logout' : ''">
        <span class="logout-icon">🚪</span>
        <span class="logout-label" v-show="!isCollapsed">Logout</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter, useRoute } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isCollapsed = ref(false)
const mobileOpen = ref(false)
const openSubmenus = reactive({})

// Display name in format: Name (employee_no)
const displayName = computed(() => {
  const user = authStore.user
  if (!user) return ''
  if (user.name && user.employee_no) {
    return `${user.name} (${user.employee_no})`
  }
  return user.username || ''
})

const navItems = [
  { name: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { name: 'trace', label: 'Trace', path: '/trace', icon: '🔍' },
  { name: 'factory', label: 'Factory', path: '/factory', icon: '🏭' },
  { name: 'process', label: 'Process', path: '/process', icon: '⚙' },
  { name: 'outsource', label: 'Outsource', path: '/outsource', icon: '📤' },
  { name: 'schedule', label: 'Schedule', path: '/schedule', icon: '📅' },
  { name: 'sales', label: 'Sales', icon: '💰', children: [
    { name: 'sales-po', label: 'PO', path: '/sales/po' },
    { name: 'sales-purchase', label: 'Purchase', path: '/sales/purchase' },
  ]},
  { name: 'warehouse', label: 'Warehouse', icon: '📦', children: [
    { name: 'warehouse-finished', label: 'Finished Products', path: '/warehouse/finished-products' },
    { name: 'warehouse-material-import', label: 'Material Import', path: '/warehouse/material-import' },
  ]},
  { name: 'mold', label: 'Mold', path: '/mold', icon: '🔧' },
  { name: 'master', label: 'Master', path: '/master', icon: '⚡' },
]

const isParentActive = (item) => {
  return item.children?.some(child => route.path === child.path)
}

const toggleSubmenu = (name) => {
  openSubmenus[name] = !openSubmenus[name]
}

// Auto-open submenu if current route matches a child
navItems.forEach(item => {
  if (item.children && item.children.some(child => route.path === child.path)) {
    openSubmenus[item.name] = true
  }
})

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleMobileMenu = () => {
  mobileOpen.value = !mobileOpen.value
}

const closeMobileMenu = () => {
  mobileOpen.value = false
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 親コンポーネントから参照できるように公開
defineExpose({
  isCollapsed,
  mobileOpen,
  toggleMobileMenu,
  closeMobileMenu
})
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 200px;
  background: #2c3e50;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 1000;
}

.app-sidebar.collapsed {
  width: 60px;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #34495e;
}

.toggle-icon {
  color: white;
  font-size: 16px;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.toggle-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  text-decoration: none;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  transition: background-color 0.2s;
  margin-bottom: 4px;
  white-space: nowrap;
  cursor: pointer;
}

.nav-item:hover {
  background-color: #34495e;
}

.nav-item.active {
  background-color: var(--primary);
  font-weight: bold;
}

.nav-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

.nav-label {
  overflow: hidden;
}

.nav-arrow {
  margin-left: auto;
  font-size: 12px;
  color: #bdc3c7;
}

.submenu {
  padding-left: 12px;
}

.sub-item {
  padding-left: 36px !important;
  font-size: 13px;
}

.sidebar-footer {
  border-top: 1px solid #34495e;
  padding: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #bdc3c7;
  padding: 12px;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
}

.user-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px;
  background: transparent;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  border-radius: 6px;
  font-size: 14px;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.logout-btn:hover {
  background-color: rgba(231, 76, 60, 0.2);
}

.logout-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    left: -250px;
    top: 0;
    bottom: 0;
    width: 250px;
    transition: left 0.3s ease;
  }

  .app-sidebar.mobile-open {
    left: 0;
  }

  .app-sidebar.collapsed {
    width: 250px;
    left: -250px;
  }

  .app-sidebar.collapsed.mobile-open {
    left: 0;
  }

  .sidebar-toggle {
    display: none;
  }

  .nav-label {
    display: inline !important;
  }

  .user-name {
    display: inline !important;
  }

  .logout-label {
    display: inline !important;
  }
}
</style>
