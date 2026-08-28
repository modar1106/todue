<template>
  <div class="pagination-bar" v-if="totalPages > 0">
    <div class="pagination-info">
      <span class="pagination-text">
        Showing {{ startItem }}–{{ endItem }} of {{ total }} tasks
      </span>
    </div>

    <div class="pagination-controls">
      <!-- Page Size -->
      <div class="page-size-group">
        <label class="page-size-label">Per page:</label>
        <select
          :value="pageSize"
          @change="$emit('page-size', Number($event.target.value))"
          class="page-size-select"
        >
          <option :value="10">10</option>
          <option :value="25">25</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
      </div>

      <!-- Page Navigation -->
      <div class="page-nav">
        <button
          class="btn btn-ghost btn-sm page-btn page-arrow-btn"
          :disabled="page <= 1"
          @click="$emit('prev')"
          title="Previous page"
        >
          <ChevronLeft :size="16" />
        </button>

        <template v-for="p in visiblePages" :key="p">
          <button
            v-if="p === '...'"
            class="btn btn-ghost btn-sm page-btn ellipsis"
            disabled
          >
            …
          </button>
          <button
            v-else
            :class="['btn', 'btn-sm', 'page-btn', { 'btn-primary': p === page, 'btn-ghost': p !== page }]"
            @click="$emit('go-to', p)"
          >
            {{ p }}
          </button>
        </template>

        <button
          class="btn btn-ghost btn-sm page-btn page-arrow-btn"
          :disabled="page >= totalPages"
          @click="$emit('next')"
          title="Next page"
        >
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  page: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  total: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})

defineEmits(['prev', 'next', 'go-to', 'page-size'])

const startItem = computed(() => {
  if (props.total === 0) return 0
  return (props.page - 1) * props.pageSize + 1
})

const endItem = computed(() => {
  return Math.min(props.page * props.pageSize, props.total)
})

const visiblePages = computed(() => {
  const total = props.totalPages
  const current = props.page
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }

  // Always show first page
  pages.push(1)

  if (current > 3) {
    pages.push('...')
  }

  // Pages around current
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (current < total - 2) {
    pages.push('...')
  }

  // Always show last page
  pages.push(total)

  return pages
})
</script>

<style scoped>
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-top: 1px solid var(--border-light);
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-text {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-size-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-size-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.page-size-select {
  padding: 3px 26px 3px 8px;
  font-size: var(--font-size-xs);
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
}

.page-nav {
  display: flex;
  align-items: center;
  gap: 2px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--border-radius-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.page-btn.btn-primary {
  pointer-events: none;
}

.page-arrow-btn {
  padding: 0 6px;
}

.ellipsis {
  cursor: default;
  opacity: 0.5;
}

@media (max-width: 600px) {
  .pagination-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-controls {
    justify-content: space-between;
  }
}
</style>
