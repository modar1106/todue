<template>
  <aside :class="['sidebar', { collapsed: isCollapsed }]">
    <!-- Top Header: User Profile Dropdown & Controls -->
    <div class="sidebar-header">
      <div class="user-menu-wrapper" ref="userMenuRef" v-if="!isCollapsed">
        <button
          class="user-dropdown-btn"
          @click="showUserMenu = !showUserMenu"
          title="Account menu"
        >
          <div class="user-avatar">
            {{ userInitial }}
          </div>
          <span class="user-name">{{ userName }}</span>
          <ChevronDown :size="14" class="chevron-icon" :class="{ rotated: showUserMenu }" />
        </button>

        <!-- Dropdown Menu -->
        <transition name="dropdown">
          <div v-if="showUserMenu" class="user-dropdown-popover">
            <div class="popover-user-info">
              <div class="user-avatar lg">{{ userInitial }}</div>
              <div class="popover-user-details">
                <span class="popover-user-name">{{ userName }}</span>
                <span class="popover-user-email">{{ user?.email || '' }}</span>
              </div>
            </div>

            <div class="popover-divider"></div>

            <button class="popover-item" @click="toggleTheme">
              <Sun v-if="isDark" :size="16" />
              <Moon v-else :size="16" />
              <span>{{ isDark ? 'Light theme' : 'Dark theme' }}</span>
            </button>

            <button
              class="popover-item"
              @click="handleBulkGenerate"
              :disabled="isBulkGenerating"
            >
              <Zap :size="16" class="text-amber" />
              <span>{{ isBulkGenerating ? 'Generating...' : 'Generate 1,000 Tasks' }}</span>
            </button>

            <div class="popover-divider"></div>

            <button class="popover-item logout" @click="handleLogout">
              <LogOut :size="16" />
              <span>Log out</span>
            </button>
          </div>
        </transition>
      </div>

      <!-- Action Buttons (Bell & Sidebar Toggle) -->
      <div class="header-actions">
        <button
          v-if="!isCollapsed"
          class="header-btn"
          @click="$emit('open-notifications')"
          title="Notifications"
        >
          <Bell :size="17" />
        </button>
        <button
          class="header-btn"
          @click="$emit('toggle')"
          :title="isCollapsed ? 'Open sidebar' : 'Close sidebar'"
        >
          <PanelLeftClose v-if="!isCollapsed" :size="18" />
          <PanelLeft v-else :size="18" />
        </button>
      </div>
    </div>

    <!-- Sidebar Scrollable Body -->
    <div class="sidebar-body">
      <!-- Finish Setup Widget Card -->
      <div
        v-if="!isCollapsed && showSetupCard"
        class="setup-card"
      >
        <div class="setup-card-header">
          <span class="setup-card-title">Finish your setup</span>
          <button class="setup-close-btn" @click="showSetupCard = false" title="Dismiss">
            <X :size="14" />
          </button>
        </div>
        <span class="setup-progress-text">{{ setupCompletedCount }}/3 complete</span>
        <div class="setup-progress-bars">
          <div :class="['bar-segment', { filled: setupCompletedCount >= 1 }]"></div>
          <div :class="['bar-segment', { filled: setupCompletedCount >= 2 }]"></div>
          <div :class="['bar-segment', { filled: setupCompletedCount >= 3 }]"></div>
        </div>
      </div>

      <!-- Quick Add Task Button -->
      <div class="quick-add-container">
        <button
          class="quick-add-task-btn"
          @click="$emit('quick-add')"
          title="Add task"
        >
          <div class="add-task-icon-circle">
            <Plus :size="14" />
          </div>
          <span v-if="!isCollapsed" class="add-task-label">Add task</span>
          <div v-if="!isCollapsed" class="add-task-streak" title="Productivity pulse">
            <Flame :size="16" class="streak-icon" />
          </div>
        </button>
      </div>

      <!-- Primary Navigation -->
      <nav class="nav-group">
        <!-- Search -->
        <button
          class="nav-link"
          @click="$emit('open-search')"
          title="Search (Ctrl + K)"
        >
          <Search :size="18" class="link-icon" />
          <span v-if="!isCollapsed" class="link-label">Search</span>
        </button>

        <!-- Inbox -->
        <button
          :class="['nav-link', { active: activeView === 'inbox' }]"
          @click="handleNav('inbox')"
          title="Inbox"
        >
          <Inbox :size="18" class="link-icon inbox-icon" />
          <span v-if="!isCollapsed" class="link-label">Inbox</span>
          <span v-if="!isCollapsed && stats.total > 0" class="link-count">{{ stats.total }}</span>
        </button>

        <!-- Today -->
        <button
          :class="['nav-link', { active: activeView === 'today' }]"
          @click="handleNav('today')"
          title="Today"
        >
          <div class="calendar-icon-wrapper">
            <Calendar :size="18" class="link-icon today-icon" />
            <span class="calendar-today-number">{{ todayDateNumber }}</span>
          </div>
          <span v-if="!isCollapsed" class="link-label">Today</span>
          <span v-if="!isCollapsed && stats.pending > 0" class="link-count">{{ stats.pending }}</span>
        </button>

        <!-- Upcoming -->
        <button
          :class="['nav-link', { active: activeView === 'upcoming' }]"
          @click="handleNav('upcoming')"
          title="Upcoming"
        >
          <CalendarDays :size="18" class="link-icon upcoming-icon" />
          <span v-if="!isCollapsed" class="link-label">Upcoming</span>
          <span v-if="!isCollapsed && stats.progress > 0" class="link-count">{{ stats.progress }}</span>
        </button>

        <!-- Filters & Labels -->
        <button
          :class="['nav-link', { active: isFilterActive }]"
          @click="toggleFiltersSection"
          title="Filters & Labels"
        >
          <SlidersHorizontal :size="18" class="link-icon filters-icon" />
          <span v-if="!isCollapsed" class="link-label">Filters & Labels</span>
          <ChevronRight
            v-if="!isCollapsed"
            :size="14"
            class="expand-icon"
            :class="{ rotated: showFiltersSubmenu }"
          />
        </button>

        <!-- Filters Submenu -->
        <div v-if="!isCollapsed && showFiltersSubmenu" class="sub-nav-group">
          <button
            :class="['sub-nav-link', { active: filters?.priority === 'high' }]"
            @click="handlePriority('high')"
          >
            <span class="color-dot high"></span>
            <span>High Priority</span>
          </button>
          <button
            :class="['sub-nav-link', { active: filters?.priority === 'medium' }]"
            @click="handlePriority('medium')"
          >
            <span class="color-dot medium"></span>
            <span>Medium Priority</span>
          </button>
          <button
            :class="['sub-nav-link', { active: filters?.priority === 'low' }]"
            @click="handlePriority('low')"
          >
            <span class="color-dot low"></span>
            <span>Low Priority</span>
          </button>
          <button
            :class="['sub-nav-link', { active: filters?.status === 'done' }]"
            @click="handleNav('done')"
          >
            <CheckCircle2 :size="14" class="text-green" />
            <span>Completed Tasks</span>
          </button>
        </div>

        <!-- Reporting / Activity -->
        <button
          :class="['nav-link', { active: activeView === 'reporting' }]"
          @click="$emit('open-reporting')"
          title="Reporting & Productivity"
        >
          <TrendingUp :size="18" class="link-icon reporting-icon" />
          <span v-if="!isCollapsed" class="link-label">Reporting</span>
        </button>
      </nav>

      <!-- Projects Section -->
      <div v-if="!isCollapsed" class="projects-section">
        <div class="section-header">
          <button class="section-toggle" @click="showProjects = !showProjects">
            <ChevronRight :size="14" class="section-chevron" :class="{ rotated: showProjects }" />
            <span>My Projects</span>
          </button>
          <button class="add-project-btn" @click="showAddProject = true" title="Add Project">
            <Plus :size="16" />
          </button>
        </div>

        <div v-if="showProjects" class="project-links">
          <button
            v-for="project in projects"
            :key="project.id"
            :class="['nav-link project-link', { active: activeProject === project.name }]"
            @click="selectProject(project.name)"
          >
            <span class="project-dot" :style="{ backgroundColor: project.color }"></span>
            <span class="link-label">{{ project.name }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Footer -->
    <div v-if="!isCollapsed" class="sidebar-footer">
      <button class="footer-link" @click="showAddTeam = true">
        <Plus :size="16" class="footer-icon" />
        <span>Add a team</span>
      </button>
      <button class="footer-link" @click="showHelp = true">
        <HelpCircle :size="16" class="footer-icon help-icon" />
        <span>Help & resources</span>
        <span class="help-badge-dot"></span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import {
  ChevronDown,
  ChevronRight,
  Bell,
  PanelLeftClose,
  PanelLeft,
  Plus,
  Search,
  Inbox,
  Calendar,
  CalendarDays,
  SlidersHorizontal,
  TrendingUp,
  X,
  Flame,
  Zap,
  Sun,
  Moon,
  LogOut,
  HelpCircle,
  CheckCircle2,
} from 'lucide-vue-next'

const props = defineProps({
  user: Object,
  stats: {
    type: Object,
    default: () => ({ total: 0, pending: 0, progress: 0, done: 0 }),
  },
  filters: {
    type: Object,
    default: () => ({ status: '', priority: '', search: '' }),
  },
  isBulkGenerating: Boolean,
  isCollapsed: Boolean,
})

const emit = defineEmits([
  'toggle',
  'quick-add',
  'filter-view',
  'filter-project',
  'filter-status',
  'filter-priority',
  'clear-filters',
  'generate-bulk',
  'logout',
  'open-search',
  'open-notifications',
  'open-reporting',
])

// ── State ────────────────────────────────────────────────
const showUserMenu = ref(false)
const showSetupCard = ref(true)
const showFiltersSubmenu = ref(false)
const showProjects = ref(true)
const showAddProject = ref(false)
const showAddTeam = ref(false)
const showHelp = ref(false)
const isDark = ref(false)
const userMenuRef = ref(null)
const activeProject = ref('')

const projects = ref([
  { id: 1, name: 'Work', color: '#eb8909' },
  { id: 2, name: 'Personal', color: '#246fe0' },
  { id: 3, name: 'Study', color: '#058527' },
])

// ── Computed ─────────────────────────────────────────────
const userName = computed(() => {
  return props.user?.full_name || props.user?.email?.split('@')[0] || 'User'
})

const userInitial = computed(() => {
  return userName.value.charAt(0).toUpperCase()
})

const todayDateNumber = computed(() => {
  return new Date().getDate()
})

const activeView = computed(() => {
  if (props.filters?.project) return props.filters.project
  if (props.filters?.priority) return props.filters.priority
  if (props.filters?.status === 'done') return 'done'
  if (props.filters?.view) return props.filters.view
  if (props.filters?.status === 'pending') return 'today'
  if (props.filters?.status === 'progress') return 'upcoming'
  return 'inbox'
})

const isFilterActive = computed(() => {
  return !!props.filters?.priority || props.filters?.status === 'done' || showFiltersSubmenu.value
})

const setupCompletedCount = computed(() => {
  let count = 0
  if (props.stats.total > 0) count++
  if (props.stats.done > 0) count++
  if (props.user?.full_name) count++
  return count
})

// ── Navigation Handlers ──────────────────────────────────
function handleNav(view) {
  activeProject.value = ''
  emit('filter-view', view)
}

function handlePriority(priority) {
  activeProject.value = ''
  emit('filter-priority', priority)
}

function toggleFiltersSection() {
  showFiltersSubmenu.value = !showFiltersSubmenu.value
}

function selectProject(name) {
  activeProject.value = name
  emit('filter-project', name)
}

// ── Dropdown & Theme ─────────────────────────────────────
function toggleTheme() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
    localStorage.setItem('theme', 'light')
  }
}

function handleBulkGenerate() {
  showUserMenu.value = false
  emit('generate-bulk')
}

function handleLogout() {
  showUserMenu.value = false
  emit('logout')
}

// Click outside handler for user menu
function handleClickOutside(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* ── Sidebar Container ──────────────────────────────────── */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100vh;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-slow), min-width var(--transition-slow);
  overflow: hidden;
  position: sticky;
  top: 0;
  z-index: var(--z-sidebar);
  user-select: none;
}

.sidebar.collapsed {
  width: 54px;
  min-width: 54px;
}

/* ── Top Header ─────────────────────────────────────────── */
.sidebar-header {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-bottom: 1px solid transparent;
}

.sidebar.collapsed .sidebar-header {
  padding: 0;
  justify-content: center;
}

.user-menu-wrapper {
  position: relative;
  flex: 1;
  min-width: 0;
}

.user-dropdown-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px 4px 4px;
  border-radius: var(--border-radius-sm);
  background: transparent;
  border: none;
  cursor: pointer;
  max-width: 170px;
  transition: background var(--transition-fast);
}

.user-dropdown-btn:hover {
  background: var(--bg-hover);
}

.user-avatar {
  width: 28px;
  height: 28px;
  min-width: 28px;
  border-radius: 50%;
  background: #00897b;
  color: #ffffff;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar.lg {
  width: 38px;
  height: 38px;
  font-size: 16px;
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chevron-icon {
  color: var(--text-tertiary);
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.header-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.header-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* ── User Popover Menu ──────────────────────────────────── */
.user-dropdown-popover {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  width: 240px;
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: 8px 0;
  z-index: var(--z-dropdown);
}

.popover-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px;
}

.popover-user-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.popover-user-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.popover-user-email {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.popover-divider {
  height: 1px;
  background: var(--border-light);
  margin: 6px 0;
}

.popover-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background var(--transition-fast);
}

.popover-item:hover {
  background: var(--bg-hover);
}

.popover-item.logout {
  color: var(--priority-high);
}

.popover-item.logout:hover {
  background: var(--priority-high-bg);
}

/* ── Sidebar Body ───────────────────────────────────────── */
.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 6px 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar.collapsed .sidebar-body {
  padding: 8px 4px;
}

/* ── Setup Card ─────────────────────────────────────────── */
.setup-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-md);
  padding: 10px 12px;
  margin-bottom: 4px;
  box-shadow: var(--shadow-sm);
}

.setup-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.setup-card-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.setup-close-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 2px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
}

.setup-close-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.setup-progress-text {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.setup-progress-bars {
  display: flex;
  gap: 4px;
}

.bar-segment {
  flex: 1;
  height: 4px;
  background: var(--border-default);
  border-radius: var(--border-radius-full);
  transition: background var(--transition-base);
}

.bar-segment.filled {
  background: var(--color-primary);
}

/* ── Quick Add Button ───────────────────────────────────── */
.quick-add-container {
  margin: 2px 0 6px;
}

.quick-add-task-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--border-radius-sm);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sidebar.collapsed .quick-add-task-btn {
  justify-content: center;
  padding: 8px 0;
}

.quick-add-task-btn:hover {
  background: var(--bg-hover);
}

.add-task-icon-circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.add-task-label {
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--color-primary);
  flex: 1;
  text-align: left;
}

.add-task-streak {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--priority-medium);
}

/* ── Navigation Links ───────────────────────────────────── */
.nav-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-link {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 10px;
  border-radius: var(--border-radius-sm);
  background: transparent;
  border: none;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 9px 0;
}

.nav-link:hover {
  background: var(--bg-hover);
}

.nav-link.active {
  background: var(--bg-active);
  color: var(--bg-active-text);
  font-weight: 600;
}

.link-icon {
  flex-shrink: 0;
  color: var(--text-secondary);
}

.nav-link.active .link-icon {
  color: var(--color-primary);
}

.inbox-icon { color: #246fe0; }
.today-icon { color: #058527; }
.upcoming-icon { color: #692fc2; }
.filters-icon { color: #eb8909; }
.reporting-icon { color: #dc4c3e; }

.calendar-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
}

.calendar-today-number {
  position: absolute;
  top: 5px;
  font-size: 8px;
  font-weight: 800;
  color: #058527;
}

.link-label {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.link-count {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-weight: 600;
  padding: 0 4px;
}

.expand-icon {
  color: var(--text-tertiary);
  transition: transform var(--transition-fast);
}

.expand-icon.rotated {
  transform: rotate(90deg);
}

/* ── Sub Navigation (Filters) ───────────────────────────── */
.sub-nav-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-left: 20px;
  margin: 2px 0 4px;
}

.sub-nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  border-radius: var(--border-radius-sm);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sub-nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sub-nav-link.active {
  background: var(--bg-active);
  color: var(--bg-active-text);
  font-weight: 600;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.color-dot.high { background: var(--priority-high); }
.color-dot.medium { background: var(--priority-medium); }
.color-dot.low { background: var(--priority-low); }

/* ── Projects Section ───────────────────────────────────── */
.projects-section {
  margin-top: 8px;
  border-top: 1px solid var(--border-light);
  padding-top: 10px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 6px;
}

.section-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
}

.section-toggle:hover {
  color: var(--text-primary);
}

.section-chevron {
  transition: transform var(--transition-fast);
}

.section-chevron.rotated {
  transform: rotate(90deg);
}

.add-project-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 2px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
}

.add-project-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.project-links {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
}

.project-link {
  font-size: var(--font-size-sm);
}

.project-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ── Sidebar Footer ─────────────────────────────────────── */
.sidebar-footer {
  padding: 8px 10px;
  border-top: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  border-radius: var(--border-radius-sm);
  background: transparent;
  border: none;
  cursor: pointer;
  position: relative;
  transition: all var(--transition-fast);
}

.footer-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.footer-icon {
  color: var(--text-tertiary);
}

.help-icon {
  color: var(--priority-medium);
}

.help-badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--priority-medium);
  margin-left: auto;
}

/* ── Transitions ────────────────────────────────────────── */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 150ms ease, transform 150ms ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
