<template>
  <div class="todo-list-container">
    <!-- ======================================================== -->
    <!-- UPCOMING VIEW                                            -->
    <!-- ======================================================== -->
    <div v-if="isUpcomingView" class="upcoming-view-wrapper">
      <!-- Title & Month Bar -->
      <div class="upcoming-header">
        <h1 class="list-title">Upcoming</h1>
        <div class="upcoming-controls">
          <button class="month-selector-btn">
            <span>{{ currentMonthYearLabel }}</span>
            <ChevronDown :size="14" />
          </button>

          <div class="week-nav-group">
            <button class="week-nav-btn" @click="changeWeek(-1)" title="Previous week">
              <ChevronLeft :size="16" />
            </button>
            <button class="week-today-btn" @click="resetToToday">Today</button>
            <button class="week-nav-btn" @click="changeWeek(1)" title="Next week">
              <ChevronRight :size="16" />
            </button>
          </div>
        </div>
      </div>

      <!-- Week Day Strip -->
      <div class="week-strip">
        <button
          v-for="day in weekDays"
          :key="day.iso"
          :class="['day-pill', { active: day.isToday, selected: selectedDate === day.iso }]"
          @click="selectDay(day.iso)"
        >
          <span class="day-name">{{ day.name }}</span>
          <span :class="['day-number', { 'today-badge': day.isToday }]">{{ day.number }}</span>
        </button>
      </div>

      <!-- Upcoming Grouped Date Sections -->
      <div class="upcoming-timeline">
        <div
          v-for="section in upcomingSections"
          :key="section.iso"
          class="timeline-section"
        >
          <!-- Section Date Header -->
          <div class="timeline-date-header">
            <span class="date-header-text">{{ section.label }}</span>
          </div>

          <!-- Tasks for this date -->
          <div class="timeline-tasks">
            <TodoItem
              v-for="todo in section.tasks"
              :key="todo.id"
              :todo="todo"
              @select="handleSelect"
              @edit="handleEdit"
              @delete="handleDelete"
              @update-status="handleStatusUpdate"
            />
          </div>

          <!-- Inline Task Form for this section -->
          <div v-if="activeSectionForm === section.iso" class="quick-add-section">
            <TodoForm
              :initial-due-date="section.iso"
              @submit="handleCreateWithDate"
              @cancel="activeSectionForm = null"
            />
          </div>

          <!-- Section Add Task Button -->
          <div v-else class="section-add-container">
            <button class="inline-add-btn" @click="openSectionForm(section.iso)">
              <Plus :size="15" class="inline-add-icon" />
              <span>Add task</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- STANDARD / TODAY VIEW                                    -->
    <!-- ======================================================== -->
    <div v-else class="standard-view-wrapper">
      <!-- Header -->
      <div class="list-header">
        <div class="header-left">
          <button
            class="mobile-menu-btn"
            @click="$emit('toggle-sidebar')"
            title="Toggle sidebar"
          >
            <Menu :size="20" />
          </button>
          <div class="title-with-subtitle">
            <h1 class="list-title">{{ pageTitle }}</h1>
            <div class="list-subtitle">
              <CheckCircle2 :size="13" class="subtitle-icon" />
              <span>{{ activeTaskCount }} task{{ activeTaskCount === 1 ? '' : 's' }}</span>
            </div>
          </div>
        </div>

        <div class="header-right">
          <button class="display-btn" @click="showDisplayOptions = !showDisplayOptions" title="View options">
            <SlidersHorizontal :size="15" />
            <span>Display</span>
          </button>
        </div>
      </div>

      <!-- Filter Bar (Search & Quick Sort) -->
      <FilterBar
        v-if="hasFilters || showDisplayOptions"
        :filters="filters"
        @filter="handleFilter"
        @toggle-sort="$emit('toggle-sort')"
        @clear="$emit('clear-filters')"
      />

      <!-- Inline Add Task Trigger Button (Always accessible below title) -->
      <div v-if="!showForm" class="inline-add-task-container">
        <button class="inline-add-btn" @click="showForm = true">
          <Plus :size="16" class="inline-add-icon" />
          <span>Add task</span>
        </button>
      </div>

      <!-- Quick Add Form -->
      <div v-if="showForm" class="quick-add-section">
        <TodoForm
          @submit="handleCreate"
          @cancel="showForm = false"
        />
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner spinner-lg"></div>
        <span class="loading-text">Loading tasks...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <AlertCircle :size="18" class="error-icon" />
        <span>{{ error }}</span>
        <button class="btn btn-ghost btn-sm" @click="$emit('retry')">Retry</button>
      </div>

      <!-- Celebration Empty State -->
      <div v-else-if="todos.length === 0 && !showForm" class="empty-celebration-state">
        <div class="illustration-wrapper">
          <svg class="celebration-illustration" viewBox="0 0 280 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M40 160C45 130 65 110 90 120C100 124 105 135 105 150" stroke="#7ea38b" stroke-width="8" stroke-linecap="round"/>
            <path d="M180 150C185 125 205 105 225 115C235 120 240 135 240 160" stroke="#5d826a" stroke-width="8" stroke-linecap="round"/>
            <circle cx="60" cy="90" r="4" fill="#e65a4c"/>
            <circle cx="215" cy="85" r="5" fill="#e65a4c"/>
            <circle cx="50" cy="120" r="3" fill="#f5a623"/>
            <circle cx="230" cy="115" r="4" fill="#f5a623"/>
            <path d="M95 90C70 65 75 40 100 50C115 56 120 75 118 95" fill="#f7c244" opacity="0.95"/>
            <path d="M165 90C190 65 185 40 160 50C145 56 140 75 142 95" fill="#f7c244" opacity="0.95"/>
            <circle cx="102" cy="65" r="5" fill="#b8831a"/>
            <circle cx="158" cy="65" r="5" fill="#b8831a"/>
            <ellipse cx="130" cy="95" rx="22" ry="24" fill="#e8ded2"/>
            <path d="M110 115C110 130 118 145 130 145C142 145 150 130 150 115" stroke="#d5c8bb" stroke-width="8" stroke-linecap="round" fill="none"/>
            <path d="M112 110L124 96" stroke="#c0b1a2" stroke-width="3" stroke-linecap="round"/>
            <path d="M148 110L136 96" stroke="#c0b1a2" stroke-width="3" stroke-linecap="round"/>
            <path d="M112 115C108 140 105 165 105 170H155C155 165 152 140 148 115Z" fill="#e8ded2"/>
            <ellipse cx="130" cy="172" rx="65" ry="5" fill="#e8e2dc"/>
          </svg>
        </div>

        <div class="empty-celebration-title">
          You're all done for the week, {{ userName }}!
        </div>
        <div class="empty-celebration-subtitle">
          Enjoy your free time or add a task whenever inspiration strikes.
        </div>
      </div>

      <!-- Todo Items List -->
      <div v-else class="todo-items">
        <TodoItem
          v-for="todo in todos"
          :key="todo.id"
          :todo="todo"
          @select="handleSelect"
          @edit="handleEdit"
          @delete="handleDelete"
          @update-status="handleStatusUpdate"
        />
      </div>

      <!-- Pagination Bar -->
      <PaginationBar
        v-if="pagination.totalPages > 1"
        :page="pagination.page"
        :page-size="pagination.pageSize"
        :total="pagination.total"
        :total-pages="pagination.totalPages"
        @prev="$emit('prev-page')"
        @next="$emit('next-page')"
        @go-to="(p) => $emit('go-to-page', p)"
        @page-size="(s) => $emit('set-page-size', s)"
      />
    </div>

    <!-- Detail Modal -->
    <TodoDetail
      v-if="selectedTodo"
      :todo="selectedTodo"
      @close="selectedTodo = null"
      @update="handleUpdate"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Menu,
  Plus,
  AlertCircle,
  SlidersHorizontal,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
} from 'lucide-vue-next'
import FilterBar from './FilterBar.vue'
import TodoItem from './TodoItem.vue'
import TodoForm from './TodoForm.vue'
import TodoDetail from './TodoDetail.vue'
import PaginationBar from './PaginationBar.vue'

const props = defineProps({
  todos: {
    type: Array,
    default: () => [],
  },
  user: Object,
  pagination: {
    type: Object,
    default: () => ({ page: 1, pageSize: 10, total: 0, totalPages: 0 }),
  },
  filters: {
    type: Object,
    default: () => ({ status: '', priority: '', search: '' }),
  },
  isLoading: Boolean,
  error: String,
})

const emit = defineEmits([
  'create', 'update', 'delete', 'update-status',
  'filter', 'toggle-sort', 'clear-filters', 'retry',
  'prev-page', 'next-page', 'go-to-page', 'set-page-size',
  'toggle-sidebar',
])

const showForm = ref(false)
const showDisplayOptions = ref(false)
const selectedTodo = ref(null)
const activeSectionForm = ref(null)
const weekOffset = ref(0)
const selectedDate = ref('')

const isUpcomingView = computed(() => {
  return props.filters?.status === 'progress'
})

const userName = computed(() => {
  return props.user?.full_name || props.user?.email?.split('@')[0] || 'User'
})

const activeTaskCount = computed(() => {
  return props.todos.filter(t => t.status !== 'done').length || props.pagination?.total || 0
})

const hasFilters = computed(() => {
  return !!(props.filters?.status || props.filters?.priority || props.filters?.search)
})

const pageTitle = computed(() => {
  if (props.filters?.project) return props.filters.project
  if (props.filters?.view === 'inbox') return 'Inbox'
  if (props.filters?.view === 'today') return 'Today'
  if (props.filters?.view === 'upcoming') return 'Upcoming'
  if (props.filters?.status === 'pending') return 'Today'
  if (props.filters?.status === 'progress') return 'Upcoming'
  if (props.filters?.status === 'done') return 'Completed'
  if (props.filters?.priority === 'high') return 'High Priority'
  if (props.filters?.priority === 'medium') return 'Medium Priority'
  if (props.filters?.priority === 'low') return 'Low Priority'
  return 'Inbox'
})

// ── Upcoming Date Calculations ───────────────────────────
const currentMonthYearLabel = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + weekOffset.value * 7)
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const weekDays = computed(() => {
  const days = []
  const today = new Date()
  const startOfWeek = new Date(today)
  const dayIndex = (today.getDay() + 6) % 7 // Monday = 0
  startOfWeek.setDate(today.getDate() - dayIndex + weekOffset.value * 7)

  const names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const todayIso = today.toISOString().split('T')[0]

  for (let i = 0; i < 7; i++) {
    const cur = new Date(startOfWeek)
    cur.setDate(startOfWeek.getDate() + i)
    const iso = cur.toISOString().split('T')[0]
    days.push({
      name: names[i],
      number: cur.getDate(),
      iso,
      isToday: iso === todayIso,
    })
  }
  return days
})

const upcomingSections = computed(() => {
  const sections = []
  const today = new Date()
  const todayIso = today.toISOString().split('T')[0]

  for (let i = 0; i < 5; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    const iso = d.toISOString().split('T')[0]

    let label = ''
    const dayName = d.toLocaleDateString('en-US', { weekday: 'long' })
    const dayDate = d.getDate()
    const monthName = d.toLocaleDateString('en-US', { month: 'short' })

    if (i === 0) {
      label = `${dayDate} ${monthName} · Today · ${dayName}`
    } else if (i === 1) {
      label = `${dayDate} ${monthName} · Tomorrow · ${dayName}`
    } else {
      label = `${dayDate} ${monthName} · ${dayName}`
    }

    // Tasks scheduled for this date or pending
    const tasksForDay = props.todos.filter(t => {
      if (t.due_date) return t.due_date === iso
      return i === 0 // Unscheduled tasks show on Today
    })

    sections.push({
      iso,
      label,
      tasks: tasksForDay,
    })
  }

  return sections
})

function changeWeek(diff) {
  weekOffset.value += diff
}

function resetToToday() {
  weekOffset.value = 0
  selectedDate.value = ''
}

function selectDay(iso) {
  selectedDate.value = iso
}

function openSectionForm(iso) {
  activeSectionForm.value = iso
}

function handleCreateWithDate(data) {
  emit('create', data)
  activeSectionForm.value = null
}

function handleFilter(key, value) {
  emit('filter', key, value)
}

function handleCreate(data) {
  emit('create', data)
  showForm.value = false
}

function handleSelect(todo) {
  selectedTodo.value = todo
}

function handleEdit(todo) {
  selectedTodo.value = todo
}

function handleUpdate(id, data) {
  emit('update', id, data)
  if (selectedTodo.value?.id === id) {
    selectedTodo.value = { ...selectedTodo.value, ...data }
  }
}

function handleStatusUpdate(id, status) {
  emit('update-status', id, status)
}

function handleDelete(todo) {
  if (confirm(`Delete "${todo.title}"?`)) {
    emit('delete', todo.id)
    selectedTodo.value = null
  }
}

function openForm() {
  showForm.value = true
}

defineExpose({ openForm })
</script>

<style scoped>
.todo-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
  padding: 28px 40px 60px;
}

/* ── Standard Header ────────────────────────────────────── */
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.title-with-subtitle {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.list-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.list-subtitle {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.subtitle-icon {
  color: var(--text-tertiary);
}

.display-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.display-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.mobile-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
}

/* ── Upcoming View Header ───────────────────────────────── */
.upcoming-view-wrapper {
  display: flex;
  flex-direction: column;
}

.upcoming-header {
  margin-bottom: 12px;
}

.upcoming-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.month-selector-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: var(--border-radius-sm);
}

.month-selector-btn:hover {
  background: var(--bg-hover);
}

.week-nav-group {
  display: flex;
  align-items: center;
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

.week-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.week-nav-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.week-today-btn {
  padding: 4px 10px;
  font-size: var(--font-size-xs);
  font-weight: 500;
  background: transparent;
  border: none;
  border-left: 1px solid var(--border-default);
  border-right: 1px solid var(--border-default);
  color: var(--text-primary);
  cursor: pointer;
}

.week-today-btn:hover {
  background: var(--bg-hover);
}

/* ── Week Day Strip ─────────────────────────────────────── */
.week-strip {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
  margin: 12px 0 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.day-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 4px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.day-pill:hover {
  background: var(--bg-hover);
}

.day-pill.selected {
  background: var(--bg-active);
}

.day-name {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-weight: 500;
}

.day-number {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.day-number.today-badge {
  background: var(--color-primary);
  color: #ffffff;
  font-weight: 700;
}

/* ── Upcoming Timeline Sections ─────────────────────────── */
.upcoming-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.timeline-section {
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.timeline-date-header {
  padding: 6px 0;
  margin-bottom: 6px;
}

.date-header-text {
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--text-primary);
}

.section-add-container {
  margin-top: 6px;
}

/* ── Inline Add Task ────────────────────────────────────── */
.inline-add-task-container {
  margin: 12px 0 16px;
}

.inline-add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}

.inline-add-icon {
  color: var(--color-primary);
}

.inline-add-btn:hover {
  color: var(--color-primary-hover);
}

.inline-add-btn:hover .inline-add-icon {
  transform: scale(1.15);
}

/* ── Quick Add Section ──────────────────────────────────── */
.quick-add-section {
  padding: 8px 0 16px;
}

/* ── Loading / Error ────────────────────────────────────── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
}

.loading-text {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  background: var(--priority-high-bg);
  border-radius: var(--border-radius-md);
  margin: 20px 0;
  color: var(--priority-high);
  font-size: var(--font-size-sm);
}

/* ── Celebration Empty State ────────────────────────────── */
.empty-celebration-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px 60px;
  text-align: center;
}

.illustration-wrapper {
  width: 240px;
  height: 170px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.celebration-illustration {
  width: 100%;
  height: 100%;
}

.empty-celebration-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.empty-celebration-subtitle {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  max-width: 320px;
}

/* ── Todo Items List ────────────────────────────────────── */
.todo-items {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

@media (max-width: 768px) {
  .todo-list-container {
    padding: 16px 14px;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .week-strip {
    gap: 2px;
  }
}
</style>
