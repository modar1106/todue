<template>
  <div class="todo-item" :class="{ 'is-done': todo.status === 'done' }">
    <!-- Drag Handle Dots -->
    <div class="drag-handle" title="Drag to reorder">
      <GripVertical :size="14" />
    </div>

    <!-- Circle Checkbox -->
    <button
      class="todo-checkbox"
      :class="[`priority-${todo.priority}`, { checked: todo.status === 'done' }]"
      @click="toggleStatus"
      :title="todo.status === 'done' ? 'Mark as pending' : 'Mark as done'"
    >
      <Check v-if="todo.status === 'done'" :size="12" class="check-icon" :stroke-width="3" />
    </button>

    <!-- Content -->
    <div class="todo-content" @click="$emit('select', todo)">
      <div class="todo-title">{{ todo.title }}</div>
      <div v-if="todo.description" class="todo-description">
        {{ truncateDescription(todo.description) }}
      </div>
      <div v-if="todo.due_date" class="todo-due-meta">
        <Calendar :size="12" class="due-icon" />
        <span>{{ formatDue(todo.due_date) }}</span>
      </div>
    </div>

    <!-- Project Tag / Meta -->
    <div class="todo-project-tag" @click="$emit('select', todo)">
      <span class="project-name">{{ todo.project || 'Inbox' }}</span>
      <Inbox v-if="!todo.project || todo.project === 'Inbox'" :size="13" class="project-icon" />
      <span v-else class="project-dot"></span>
    </div>

    <!-- Actions on Hover -->
    <div class="todo-actions">
      <button
        class="action-btn"
        @click="$emit('edit', todo)"
        title="Edit task"
      >
        <Pencil :size="14" />
      </button>
      <button
        class="action-btn delete-btn"
        @click="$emit('delete', todo)"
        title="Delete task"
      >
        <Trash2 :size="14" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { Check, Pencil, Trash2, GripVertical, Inbox, Calendar } from 'lucide-vue-next'

const props = defineProps({
  todo: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['select', 'edit', 'delete', 'update-status'])

function toggleStatus() {
  const newStatus = props.todo.status === 'done' ? 'pending' : 'done'
  emit('update-status', props.todo.id, newStatus)
}

function formatDue(dateStr) {
  if (!dateStr) return ''
  const today = new Date().toISOString().split('T')[0]
  if (dateStr === today) return 'Today'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function truncateDescription(desc) {
  if (!desc) return ''
  return desc.length > 80 ? desc.substring(0, 80) + '...' : desc
}
</script>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-light);
  transition: background var(--transition-fast);
  cursor: default;
  position: relative;
  border-radius: var(--border-radius-sm);
}

.todo-item:hover {
  background: var(--bg-hover);
}

/* Drag handle */
.drag-handle {
  width: 14px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  opacity: 0;
  cursor: grab;
  transition: opacity var(--transition-fast);
  margin-left: -6px;
}

.todo-item:hover .drag-handle {
  opacity: 1;
}

/* Checkbox */
.todo-checkbox {
  width: 18px;
  height: 18px;
  min-width: 18px;
  border-radius: 50%;
  border: 1.5px solid var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: transparent;
  padding: 0;
}

.todo-checkbox.priority-high {
  border-color: var(--priority-high);
}

.todo-checkbox.priority-medium {
  border-color: var(--priority-medium);
}

.todo-checkbox.priority-low {
  border-color: var(--priority-low);
}

.todo-checkbox:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: scale(1.08);
}

.todo-checkbox.checked {
  background: var(--status-done);
  border-color: var(--status-done);
}

.check-icon {
  color: #fff;
}

/* Content */
.todo-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
  padding: 0 4px;
}

.todo-title {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  line-height: 1.4;
  word-break: break-word;
}

.todo-item.is-done .todo-title {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.todo-description {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-top: 2px;
}

.todo-due-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--status-done);
  margin-top: 3px;
  font-weight: 500;
}

/* Project Tag */
.todo-project-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  padding: 2px 6px;
  cursor: pointer;
}

.todo-project-tag:hover {
  color: var(--text-secondary);
}

.project-icon {
  color: var(--text-tertiary);
}

.project-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--priority-medium);
}

/* Actions */
.todo-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.todo-item:hover .todo-actions {
  opacity: 1;
}

.action-btn {
  width: 26px;
  height: 26px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--border-light);
  color: var(--text-primary);
}

.delete-btn:hover {
  color: var(--priority-high);
}
</style>
