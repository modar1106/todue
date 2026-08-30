/**
 * Todos composable.
 * Manages todo list state, CRUD, filtering, sorting, pagination, and bulk generation.
 * Routes requests to dedicated backend endpoints per view.
 */

import { ref, reactive, computed } from 'vue'
import api from '../utils/api'

export function useTodos() {
  // ── State ──────────────────────────────────────────────
  const todos = ref([])
  const selectedTodo = ref(null)
  const isLoading = ref(false)
  const isBulkGenerating = ref(false)
  const error = ref(null)

  // Pagination
  const pagination = reactive({
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,
  })

  // Filters & sorting
  const filters = reactive({
    view: 'inbox',
    status: '',
    priority: '',
    project: '',
    search: '',
    sortBy: 'created_at',
    sortOrder: 'desc',
  })

  // Stats
  const stats = reactive({
    total: 0,
    active: 0,
    pending: 0,
    progress: 0,
    done: 0,
  })

  // Helper to compute default current week range (Mon-Sun)
  function getDefaultWeekRange() {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const dayIndex = (today.getDay() + 6) % 7
    const monday = new Date(today)
    monday.setDate(today.getDate() - dayIndex)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)

    const format = (d) => {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    }
    return { startDate: format(monday), endDate: format(sunday) }
  }

  // Upcoming view date range (managed by TodoList.vue)
  const upcomingDateRange = reactive(getDefaultWeekRange())

  // ── Computed ───────────────────────────────────────────
  const hasNextPage = computed(() => pagination.page < pagination.totalPages)
  const hasPrevPage = computed(() => pagination.page > 1)

  let currentRequestId = 0

  // ── Fetch Todos ────────────────────────────────────────
  async function fetchTodos() {
    const requestId = ++currentRequestId
    isLoading.value = true
    error.value = null

    try {
      let response

      if (filters.view === 'upcoming') {
        // Dedicated endpoint: no pagination, date-range based
        response = await api.get('/todos/upcoming', {
          params: {
            start_date: upcomingDateRange.startDate,
            end_date: upcomingDateRange.endDate,
          }
        })
      } else if (filters.view === 'today') {
        // Dedicated endpoint: paginated today + overdue
        response = await api.get('/todos/today', {
          params: {
            page: pagination.page,
            page_size: pagination.pageSize,
          }
        })
      } else if (filters.view === 'done') {
        // Dedicated endpoint: paginated completed tasks
        response = await api.get('/todos/completed', {
          params: {
            page: pagination.page,
            page_size: pagination.pageSize,
          }
        })
      } else {
        // General endpoint: Inbox / Project / Search
        const params = {
          page: pagination.page,
          page_size: pagination.pageSize,
          sort_by: filters.sortBy,
          sort_order: filters.sortOrder,
        }
        if (filters.status && ['pending', 'progress', 'done', 'active', 'all'].includes(filters.status)) {
          params.status = filters.status
        }
        if (filters.priority && ['low', 'medium', 'high'].includes(filters.priority)) {
          params.priority = filters.priority
        }
        if (filters.project && filters.project !== 'Inbox') {
          params.project = filters.project
        }
        if (filters.search) params.search = filters.search

        response = await api.get('/todos', { params })
      }

      const { data } = response

      // Only update state if this request is still the most recent one
      if (requestId === currentRequestId) {
        todos.value = data.data
        pagination.total = data.total ?? data.data?.length ?? 0
        pagination.totalPages = data.total_pages ?? 0
      }
    } catch (err) {
      if (requestId === currentRequestId) {
        error.value = err.response?.data?.detail || 'Failed to load todos.'
      }
    } finally {
      if (requestId === currentRequestId) {
        isLoading.value = false
      }
    }
  }

  // ── Fetch Stats ────────────────────────────────────────
  async function fetchStats() {
    try {
      const { data } = await api.get('/todos/stats')
      stats.total = data.total ?? 0
      stats.active = data.active ?? 0
      stats.pending = data.pending ?? 0
      stats.progress = data.progress ?? 0
      stats.done = data.done ?? 0
    } catch {
      // Silently fail stats — non-critical
    }
  }

  // ── Get Single Todo ────────────────────────────────────
  async function getTodo(id) {
    try {
      const { data } = await api.get(`/todos/${id}`)
      selectedTodo.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load todo.'
      return null
    }
  }

  // ── Create Todo ────────────────────────────────────────
  async function createTodo(todoData) {
    try {
      const { data } = await api.post('/todos', todoData)
      await fetchTodos()
      fetchStats()
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create todo.'
      throw err
    }
  }

  // ── Update Todo (Optimistic) ───────────────────────────
  async function updateTodo(id, updateData) {
    // 1. Optimistic Local Update (0ms latency UI response)
    const index = todos.value.findIndex(t => t.id === id)
    let previousTodo = null
    if (index !== -1) {
      previousTodo = { ...todos.value[index] }
      todos.value[index] = { ...todos.value[index], ...updateData }

      // Optimistically adjust stats count
      if (updateData.status && updateData.status !== previousTodo.status) {
        if (stats[previousTodo.status] > 0) stats[previousTodo.status]--
        if (stats[updateData.status] !== undefined) stats[updateData.status]++
        // Recalculate active
        stats.active = stats.pending + stats.progress
      }
    }

    if (selectedTodo.value?.id === id) {
      selectedTodo.value = { ...selectedTodo.value, ...updateData }
    }

    try {
      // 2. Background Network Sync
      const { data } = await api.put(`/todos/${id}`, updateData)
      if (index !== -1) {
        todos.value[index] = data
      }
      if (selectedTodo.value?.id === id) {
        selectedTodo.value = data
      }
      fetchStats() // Background re-sync
      return data
    } catch (err) {
      // 3. Rollback on failure
      if (index !== -1 && previousTodo) {
        todos.value[index] = previousTodo
        if (updateData.status && updateData.status !== previousTodo.status) {
          if (stats[updateData.status] > 0) stats[updateData.status]--
          if (stats[previousTodo.status] !== undefined) stats[previousTodo.status]++
          stats.active = stats.pending + stats.progress
        }
      }
      error.value = err.response?.data?.detail || 'Failed to update todo.'
      throw err
    }
  }

  // ── Delete Todo (Optimistic) ───────────────────────────
  async function deleteTodo(id) {
    const index = todos.value.findIndex(t => t.id === id)
    let removedTodo = null
    if (index !== -1) {
      removedTodo = todos.value[index]
      todos.value.splice(index, 1)
      pagination.total = Math.max(0, pagination.total - 1)
      if (stats.total > 0) stats.total--
      if (removedTodo.status && stats[removedTodo.status] > 0) {
        stats[removedTodo.status]--
      }
      stats.active = stats.pending + stats.progress
    }

    if (selectedTodo.value?.id === id) {
      selectedTodo.value = null
    }

    try {
      await api.delete(`/todos/${id}`)
      fetchStats()
    } catch (err) {
      // Re-fetch to sync if failed
      await fetchTodos()
      await fetchStats()
      error.value = err.response?.data?.detail || 'Failed to delete todo.'
      throw err
    }
  }

  // ── Generate Bulk Todos ────────────────────────────────
  async function generateBulk(count = 1000) {
    isBulkGenerating.value = true
    error.value = null

    try {
      const { data } = await api.post(`/todos/generate-bulk?count=${count}`)
      await fetchTodos()
      await fetchStats()
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to generate todos.'
      throw err
    } finally {
      isBulkGenerating.value = false
    }
  }

  // ── Pagination Helpers ─────────────────────────────────
  function goToPage(page) {
    pagination.page = page
    fetchTodos()
  }

  function nextPage() {
    if (hasNextPage.value) goToPage(pagination.page + 1)
  }

  function prevPage() {
    if (hasPrevPage.value) goToPage(pagination.page - 1)
  }

  function setPageSize(size) {
    pagination.pageSize = size
    pagination.page = 1
    fetchTodos()
  }

  // ── Filter Helpers ─────────────────────────────────────
  function setFilter(key, value) {
    if (key === 'status') {
      filters.status = ['pending', 'progress', 'done'].includes(value) ? value : ''
    } else if (key === 'priority') {
      filters.priority = ['low', 'medium', 'high'].includes(value) ? value : ''
    } else {
      filters[key] = value
    }
    pagination.page = 1  // Reset to first page on filter change
    fetchTodos()
  }

  function clearFilters(shouldFetch = true) {
    filters.view = 'inbox'
    filters.status = ''
    filters.priority = ''
    filters.project = ''
    filters.search = ''
    filters.sortBy = 'created_at'
    filters.sortOrder = 'desc'
    pagination.page = 1
    if (shouldFetch) {
      fetchTodos()
    }
  }

  function toggleSortOrder() {
    filters.sortOrder = filters.sortOrder === 'desc' ? 'asc' : 'desc'
    fetchTodos()
  }

  function resetState() {
    todos.value = []
    selectedTodo.value = null
    error.value = null
    pagination.page = 1
    pagination.total = 0
    pagination.totalPages = 0
    stats.total = 0
    stats.active = 0
    stats.pending = 0
    stats.progress = 0
    stats.done = 0
    filters.view = 'inbox'
    filters.status = ''
    filters.priority = ''
    filters.project = ''
    filters.search = ''
  }

  return {
    // State
    todos,
    selectedTodo,
    isLoading,
    isBulkGenerating,
    error,
    pagination,
    filters,
    stats,
    upcomingDateRange,

    // Computed
    hasNextPage,
    hasPrevPage,

    // Actions
    fetchTodos,
    fetchStats,
    getTodo,
    createTodo,
    updateTodo,
    deleteTodo,
    generateBulk,
    resetState,

    // Pagination
    goToPage,
    nextPage,
    prevPage,
    setPageSize,

    // Filters
    setFilter,
    clearFilters,
    toggleSortOrder,
  }
}
