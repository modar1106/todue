<template>
  <div id="app-root">
    <!-- ── 1. Landing Page View (at root '/') ──────────────── -->
    <LandingPage
      v-if="isLandingRoute"
      :is-authenticated="isAuthenticated"
      @navigate-login="router.push('/login')"
      @navigate-register="router.push('/register')"
      @navigate-app="router.push('/app')"
    />

    <!-- ── 2. Auth View (at '/login' or '/register') ────────── -->
    <AuthView
      v-else-if="isAuthRoute"
      @authenticated="handleAuthenticated"
    />

    <!-- ── 3. Main App Dashboard (at '/app') ────────────────── -->
    <div v-else-if="isAuthenticated" class="app-layout">
      <!-- Mobile Backdrop Overlay -->
      <transition name="fade">
        <div
          v-if="!sidebarCollapsed && isMobile"
          class="sidebar-backdrop"
          @click="sidebarCollapsed = true"
        ></div>
      </transition>

      <!-- Sidebar -->
      <Sidebar
        :user="user"
        :stats="stats"
        :filters="filters"
        :is-bulk-generating="isBulkGenerating"
        :is-collapsed="sidebarCollapsed"
        :is-mobile="isMobile"
        @toggle="sidebarCollapsed = !sidebarCollapsed"
        @close-mobile="sidebarCollapsed = true"
        @quick-add="openQuickAdd"
        @filter-view="handleFilterView"
        @filter-project="handleFilterProject"
        @filter-status="handleFilterStatus"
        @filter-priority="handleFilterPriority"
        @clear-filters="handleClearFilters"
        @generate-bulk="handleGenerateBulk"
        @logout="handleLogout"
        @open-search="handleOpenSearch"
        @open-notifications="handleOpenNotifications"
        @open-reporting="handleOpenReporting"
      />

      <!-- Main Content -->
      <main class="main-content">
        <TodoList
          ref="todoListRef"
          :user="user"
          :todos="todos"
          :pagination="pagination"
          :filters="filters"
          :is-loading="isLoading"
          :error="error"
          :upcoming-date-range="upcomingDateRange"
          @create="handleCreate"
          @update="handleUpdate"
          @delete="handleDelete"
          @update-status="handleStatusUpdate"
          @filter="handleFilter"
          @toggle-sort="toggleSortOrder"
          @clear-filters="handleClearFilters"
          @retry="fetchTodos"
          @prev-page="prevPage"
          @next-page="nextPage"
          @go-to-page="goToPage"
          @set-page-size="setPageSize"
          @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
          @date-range-change="handleDateRangeChange"
        />
      </main>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-container">
      <div
        v-for="(toast, i) in toasts"
        :key="i"
        :class="['toast', `toast-${toast.type}`]"
      >
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth'
import { useTodos } from './composables/useTodos'
import LandingPage from './components/LandingPage.vue'
import AuthView from './components/AuthView.vue'
import Sidebar from './components/Sidebar.vue'
import TodoList from './components/TodoList.vue'

// ── Router ───────────────────────────────────────────────
const route = useRoute()
const router = useRouter()

// ── Auth ─────────────────────────────────────────────────
const { user, isAuthenticated, logout } = useAuth()

// ── Computed Routes ──────────────────────────────────────
const isLandingRoute = computed(() => {
  return route.path === '/'
})

const isAuthRoute = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

// ── Todos ────────────────────────────────────────────────
const {
  todos,
  isLoading,
  isBulkGenerating,
  error,
  pagination,
  filters,
  stats,
  upcomingDateRange,
  fetchTodos,
  fetchStats,
  createTodo,
  updateTodo,
  deleteTodo,
  generateBulk,
  resetState,
  goToPage,
  nextPage,
  prevPage,
  setPageSize,
  setFilter,
  clearFilters,
  toggleSortOrder,
} = useTodos()

// ── UI State ─────────────────────────────────────────────
const isMobile = ref(typeof window !== 'undefined' ? window.innerWidth <= 768 : false)
const sidebarCollapsed = ref(isMobile.value)
const todoListRef = ref(null)
const toasts = ref([])

function handleResize() {
  const mobile = window.innerWidth <= 768
  if (mobile !== isMobile.value) {
    isMobile.value = mobile
    if (mobile) {
      sidebarCollapsed.value = true
    }
  }
}

// ── Lifecycle ────────────────────────────────────────────
onMounted(() => {
  if (isMobile.value) {
    sidebarCollapsed.value = true
  }
  window.addEventListener('resize', handleResize)

  if (route.path === '/app') {
    const newView = route.query.view || 'inbox'
    filters.view = newView
    filters.status = ['pending', 'progress', 'done', 'active', 'all'].includes(route.query.status) ? route.query.status : ''
    filters.project = route.query.project || ''
    filters.priority = ['low', 'medium', 'high'].includes(route.query.priority) ? route.query.priority : ''
    filters.search = route.query.search || ''

    if (isAuthenticated.value) {
      loadData()
    } else {
      router.replace('/login')
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// Watch route queries for browser back/forward and external navigation
watch(() => route.path, (newPath, oldPath) => {
  if (newPath === '/app' && oldPath !== '/app' && isAuthenticated.value) {
    loadData()
  }
})

watch(() => route.query, (newQuery) => {
  if (route.path === '/app' && isAuthenticated.value) {
    const newView = newQuery.view || 'inbox'
    filters.view = newView
    filters.status = ['pending', 'progress', 'done', 'active', 'all'].includes(newQuery.status) ? newQuery.status : ''
    filters.project = newQuery.project || ''
    filters.priority = ['low', 'medium', 'high'].includes(newQuery.priority) ? newQuery.priority : ''
    filters.search = newQuery.search || ''
    pagination.page = 1
    fetchTodos()
  }
})

function loadData() {
  fetchTodos()
  fetchStats()
}

// ── Auth Handlers ────────────────────────────────────────
function handleAuthenticated() {
  resetState()
  router.push('/app')
  loadData()
}

function handleLogout() {
  resetState()
  logout()
  router.push('/')
  showToast('Logged out successfully', 'success')
}

// ── CRUD Handlers ────────────────────────────────────────
async function handleCreate(data) {
  try {
    await createTodo(data)
    showToast('Task added successfully!', 'success')
  } catch {
    showToast('Failed to create task', 'error')
  }
}

async function handleUpdate(id, data) {
  try {
    await updateTodo(id, data)
    showToast('Task updated', 'success')
  } catch {
    showToast('Failed to update task', 'error')
  }
}

async function handleDelete(id) {
  try {
    await deleteTodo(id)
    showToast('Task deleted', 'success')
  } catch {
    showToast('Failed to delete task', 'error')
  }
}

async function handleStatusUpdate(id, status) {
  try {
    await updateTodo(id, { status })
    const label = status === 'done' ? 'completed' : 'reopened'
    showToast(`Task ${label}!`, 'success')
  } catch {
    showToast('Failed to update status', 'error')
  }
}

// ── Filter Handlers ──────────────────────────────────────
function handleFilterView(view) {
  clearFilters(false)
  if (view === 'today') {
    router.replace({ path: '/app', query: { view: 'today' } })
  } else if (view === 'upcoming') {
    router.replace({ path: '/app', query: { view: 'upcoming' } })
  } else if (view === 'done') {
    router.replace({ path: '/app', query: { view: 'done' } })
  } else {
    router.replace({ path: '/app', query: {} })
  }
}

function handleFilterProject(project) {
  clearFilters(false)
  router.replace({ path: '/app', query: { project } })
}

function handleFilter(key, value) {
  setFilter(key, value)
  const query = { ...route.query }
  if (value) {
    query[key] = value
  } else {
    delete query[key]
  }
  router.replace({ path: '/app', query })
}

function handleFilterStatus(status) {
  clearFilters(false)
  if (status && status !== 'all') {
    router.replace({ path: '/app', query: { status } })
  } else {
    router.replace({ path: '/app', query: {} })
  }
}

function handleFilterPriority(priority) {
  clearFilters(false)
  router.replace({ path: '/app', query: { priority } })
}

function handleClearFilters() {
  clearFilters(false)
  router.replace({ path: '/app', query: {} })
}

// ── Upcoming Date Range ─────────────────────────────────
function handleDateRangeChange({ startDate, endDate }) {
  upcomingDateRange.startDate = startDate
  upcomingDateRange.endDate = endDate
  fetchTodos()
}

// ── Bulk Generate ────────────────────────────────────────
async function handleGenerateBulk() {
  try {
    const result = await generateBulk(1000)
    showToast(result.message, 'success')
  } catch {
    showToast('Failed to generate todos', 'error')
  }
}

// ── Quick Add (from sidebar) ─────────────────────────────
function openQuickAdd() {
  todoListRef.value?.openForm()
}

function handleOpenSearch() {
  const searchInput = document.querySelector('.search-input')
  if (searchInput) {
    searchInput.focus()
  } else {
    showToast('Use search in the filter bar or press Ctrl + K', 'info')
  }
}

function handleOpenNotifications() {
  showToast('You are all caught up! No new notifications.', 'info')
}

function handleOpenReporting() {
  showToast(`Productivity summary: ${stats.done} completed tasks, ${stats.pending} pending.`, 'info')
}

// ── Toast Helper ─────────────────────────────────────────
function showToast(message, type = 'success') {
  toasts.value.push({ message, type })
  setTimeout(() => {
    toasts.value.shift()
  }, 3500)
}
</script>

<style scoped>
#app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background: var(--bg-surface);
}

.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  padding: 10px 16px;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  animation: slideInRight 0.25s ease forwards;
  pointer-events: auto;
}

.toast-success {
  background: var(--status-done);
  color: #ffffff;
}

.toast-error {
  background: var(--priority-high);
  color: #ffffff;
}

.toast-info {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ── Mobile Sidebar Backdrop ────────────────────────────── */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  z-index: 1040;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.22s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
