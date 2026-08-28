<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content todo-detail">
      <!-- Header -->
      <div class="detail-header">
        <h3 class="detail-title-label">Task Details</h3>
        <button class="btn btn-icon btn-ghost detail-close-btn" @click="$emit('close')" title="Close">
          <X :size="18" />
        </button>
      </div>

      <!-- Body -->
      <div v-if="isEditing" class="detail-body">
        <TodoForm
          :edit-todo="todo"
          @submit="handleUpdate"
          @cancel="isEditing = false"
        />
      </div>

      <div v-else class="detail-body">
        <!-- Status Checkbox + Title -->
        <div class="detail-title-row">
          <button
            :class="['todo-checkbox', `priority-${todo.priority}`, { checked: todo.status === 'done' }]"
            @click="toggleStatus"
          >
            <Check v-if="todo.status === 'done'" :size="12" class="check-icon" :stroke-width="3" />
          </button>
          <h2 class="detail-title" :class="{ 'is-done': todo.status === 'done' }">
            {{ todo.title }}
          </h2>
        </div>

        <!-- Description -->
        <div class="detail-section">
          <div class="section-label">Description</div>
          <p class="detail-description" v-if="todo.description">{{ todo.description }}</p>
          <p class="detail-description empty" v-else>No description</p>
        </div>

        <!-- Meta Info -->
        <div class="detail-meta-grid">
          <div class="meta-item">
            <span class="meta-label">Status</span>
            <span :class="['badge', `badge-status-${todo.status}`]">
              {{ formatStatus(todo.status) }}
            </span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Priority</span>
            <span :class="['badge', `badge-priority-${todo.priority}`]">
              {{ todo.priority }}
            </span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Created</span>
            <span class="meta-value">{{ formatFullDate(todo.created_at) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Updated</span>
            <span class="meta-value">{{ formatFullDate(todo.updated_at) }}</span>
          </div>
          <div class="meta-item full-width">
            <span class="meta-label">ID</span>
            <span class="meta-value id-value">{{ todo.id }}</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="detail-footer">
        <button class="btn btn-ghost btn-sm detail-btn" @click="isEditing = !isEditing">
          <template v-if="isEditing">
            <ArrowLeft :size="15" />
            <span>Back</span>
          </template>
          <template v-else>
            <Pencil :size="15" />
            <span>Edit</span>
          </template>
        </button>
        <button class="btn btn-danger btn-sm detail-btn" @click="$emit('delete', todo)">
          <Trash2 :size="15" />
          <span>Delete</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { X, Check, Pencil, ArrowLeft, Trash2 } from 'lucide-vue-next'
import TodoForm from './TodoForm.vue'

const props = defineProps({
  todo: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'update', 'delete'])

const isEditing = ref(false)

function toggleStatus() {
  const newStatus = props.todo.status === 'done' ? 'pending' : 'done'
  emit('update', props.todo.id, { status: newStatus })
}

function handleUpdate(data) {
  emit('update', props.todo.id, data)
  isEditing.value = false
}

function formatStatus(status) {
  const map = {
    pending: 'Pending',
    progress: 'In Progress',
    done: 'Done',
  }
  return map[status] || status
}

function formatFullDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.todo-detail {
  width: 540px;
  max-width: 95vw;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid var(--border-light);
}

.detail-title-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
}

.detail-body {
  padding: 22px;
}

.detail-title-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 20px;
}

.todo-checkbox {
  width: 22px;
  height: 22px;
  min-width: 22px;
  border-radius: 50%;
  border: 2px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-top: 3px;
  background: transparent;
}

.todo-checkbox.priority-high { border-color: var(--priority-high); }
.todo-checkbox.priority-medium { border-color: var(--priority-medium); }
.todo-checkbox.priority-low { border-color: var(--priority-low); }

.todo-checkbox:hover { transform: scale(1.1); }

.todo-checkbox.checked {
  background: var(--status-done);
  border-color: var(--status-done);
}

.check-icon {
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.detail-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  word-break: break-word;
}

.detail-title.is-done {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.detail-section {
  margin-bottom: 20px;
}

.section-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.detail-description {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-description.empty {
  color: var(--text-tertiary);
  font-style: italic;
}

.detail-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-item.full-width {
  grid-column: 1 / -1;
}

.meta-label {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-tertiary);
}

.meta-value {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.id-value {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  word-break: break-all;
}

.detail-footer {
  display: flex;
  justify-content: space-between;
  padding: 14px 22px;
  border-top: 1px solid var(--border-light);
}

.detail-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.detail-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
