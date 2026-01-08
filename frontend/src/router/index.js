import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import SalesView from '../views/SalesView.vue'
import PressView from '../views/PressView.vue'
import WarehouseView from '../views/WarehouseView.vue'
import MoldView from '../views/MoldView.vue'
import ScheduleView from '../views/ScheduleView.vue'
import TraceView from '../views/TraceView.vue'
import OutsourceView from '../views/OutsourceView.vue'
import MasterMenuView from '../views/master/MasterMenuView.vue'
import CustomerView from '../views/master/CustomerView.vue'
import ProductView from '../views/master/ProductView.vue'
import ProductDetailView from '../views/master/ProductDetailView.vue'
import EmployeeView from '../views/master/EmployeeView.vue'
import SupplierView from '../views/master/SupplierView.vue'
import ProcessNameView from '../views/master/ProcessNameView.vue'
import MaterialRateView from '../views/master/MaterialRateView.vue'
import MachineView from '../views/master/MachineView.vue'
import CycletimeView from '../views/master/CycletimeView.vue'
import HolidayView from '../views/master/HolidayView.vue'
import MaterialMasterView from '../views/master/MaterialMasterView.vue'
import MaterialSpecView from '../views/master/MaterialSpecView.vue'
import MaterialItemView from '../views/master/MaterialItemView.vue'
import MaterialLotView from '../views/master/MaterialLotView.vue'
import MaterialTransactionView from '../views/master/MaterialTransactionView.vue'
import MaterialStockView from '../views/master/MaterialStockView.vue'
import MaterialTraceView from '../views/master/MaterialTraceView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: '/sales',
      name: 'Sales',
      component: SalesView,
      meta: { requiresAuth: true },
    },
    {
      path: '/press',
      name: 'Press',
      component: PressView,
      meta: { requiresAuth: true },
    },
    {
      path: '/warehouse',
      name: 'Warehouse',
      component: WarehouseView,
      meta: { requiresAuth: true },
    },
    {
      path: '/mold',
      name: 'Mold',
      component: MoldView,
      meta: { requiresAuth: true },
    },
    {
      path: '/schedule',
      name: 'Schedule',
      component: ScheduleView,
      meta: { requiresAuth: true },
    },
    {
      path: '/trace',
      name: 'Trace',
      component: TraceView,
      meta: { requiresAuth: true },
    },
    {
      path: '/outsource',
      name: 'Outsource',
      component: OutsourceView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master',
      name: 'MasterMenu',
      component: MasterMenuView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/customers',
      name: 'Customers',
      component: CustomerView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/products',
      name: 'Products',
      component: ProductView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/products/:id',
      name: 'ProductDetail',
      component: ProductDetailView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/employees',
      name: 'Employees',
      component: EmployeeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/suppliers',
      name: 'Suppliers',
      component: SupplierView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/process-names',
      name: 'ProcessNames',
      component: ProcessNameView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-rates',
      name: 'MaterialRates',
      component: MaterialRateView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/machines',
      name: 'Machines',
      component: MachineView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/cycletimes',
      name: 'Cycletimes',
      component: CycletimeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/holidays',
      name: 'Holidays',
      component: HolidayView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-types',
      name: 'MaterialTypes',
      component: MaterialMasterView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-specs',
      name: 'MaterialSpecs',
      component: MaterialSpecView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-items',
      name: 'MaterialItems',
      component: MaterialItemView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-lots',
      name: 'MaterialLots',
      component: MaterialLotView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-transactions',
      name: 'MaterialTransactions',
      component: MaterialTransactionView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-stock',
      name: 'MaterialStock',
      component: MaterialStockView,
      meta: { requiresAuth: true },
    },
    {
      path: '/master/material-trace',
      name: 'MaterialTrace',
      component: MaterialTraceView,
      meta: { requiresAuth: true },
    },
  ],
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
