<template>
  <div class="filter-bar">
    <!-- Search -->
    <div class="filter-search">
      <Search :size="16" class="search-icon" />
      <input
        v-model="searchInput"
        type="text"
        placeholder="Search tasks..."
        class="search-input"
        @input="debouncedSearch"
      />
      <button
        v-if="searchInput"
        class="search-clear"
        @click="clearSearch"
        title="Clear search"
      >
        <X :size="14" />
      </button>
    </div>

    <!-- Filter Controls -->
    <div class="filter-controls">
      <!-- Status Filter -->
      <div class="filter-group">
        <select
          :value="filters.status"
          @change="$emit('filter', 'status', $event.target.value)"
          class="filter-select"
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="progress">In Progress</option>
          <option value="done">Done</option>
        </select>
      </div>

      <!-- Priority Filter -->
      <div class="filter-group">
        <select
          :value="filters.priority"
          @change="$emit('filter', 'priority', $event.target.value)"
          class="filter-select"
        >
          <option value="">All Priority</option>
          <option value="high">High Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="low">Low Priority</option>
        </select>
      </div>

      <!-- Sort By -->
      <div class="filter-group">
        <select
          :value="filters.sortBy"
          @change="$emit('filter', 'sortBy', $event.target.value)"
          class="filter-select"
        >
          <option value="created_at">Date Created</option>
          <option value="updated_at">Last Updated</option>
          <option value="title">Title</option>
          <option value="priority">Priority</option>
          <option value="status">Status</option>
        </select>
      </div>

      <!-- Sort Order Toggle -->
      <button
        class="btn btn-ghost btn-icon sort-toggle"
        @click="$emit('toggle-sort')"
        :title="filters.sortOrder === 'desc' ? 'Descending' : 'Ascending'"
      >
        <ArrowDown v-if="filters.sortOrder === 'desc'" :size="16" />
        <ArrowUp v-else :size="16" />
      </button>

      <!-- Clear Filters -->
      <button
        v-if="hasActiveFilters"
        class="btn btn-ghost btn-sm clear-btn"
        @click="handleClear"
      >
        Clear filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, X, ArrowDown, ArrowUp } from 'lucide-vue-next'

const props = defineProps({
  filters: Object,
})

const emit = defineEmits(['filter', 'toggle-sort', 'clear'])

const searchInput = ref(props.filters?.search || '')
let debounceTimer = null

const hasActiveFilters = computed(() => {
  return props.filters?.status || props.filters?.priority || props.filters?.search
})

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('filter', 'search', searchInput.value)
  }, 350)
}

function clearSearch() {
  searchInput.value = ''
  emit('filter', 'search', '')
}

function handleClear() {
  searchInput.value = ''
  emit('clear')
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-light);
}

.filter-search {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-tertiary);
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-input {
  width: 100%;
  padding: 10px 36px 10px 36px;
  background: var(--bg-input);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.search-input:focus {
  border-color: var(--color-primary);
  background: var(--bg-elevated);
}

.search-clear {
  position: absolute;
  right: 10px;
  color: var(--text-tertiary);
  cursor: pointer;
  background: none;
  border: none;
  padding: 4px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-clear:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 6px 30px 6px 10px;
  font-size: var(--font-size-xs);
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  min-width: 120px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-select:hover {
  border-color: var(--text-tertiary);
}

.filter-select:focus {
  border-color: var(--color-primary);
}

.sort-toggle {
  width: 34px;
  height: 34px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn {
  color: var(--color-primary);
  font-size: var(--font-size-xs);
}

.clear-btn:hover {
  background: var(--color-primary-light);
}

@media (max-width: 600px) {
  .filter-controls {
    gap: 6px;
  }

  .filter-select {
    min-width: 100px;
    font-size: 11px;
  }
}
</style>
