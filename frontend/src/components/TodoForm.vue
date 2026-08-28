<template>
  <div class="todo-form-wrapper">
    <form @submit.prevent="handleSubmit" class="todo-form">
      <div class="form-main">
        <input
          ref="titleInput"
          v-model="title"
          type="text"
          placeholder="Task name"
          class="title-input"
          required
          maxlength="255"
          @keydown.esc="$emit('cancel')"
        />
        <textarea
          v-model="description"
          placeholder="Description"
          class="desc-input"
          rows="1"
          maxlength="5000"
        ></textarea>
      </div>

      <!-- Quick Action Badges (Date, Project, Priority) -->
      <div class="form-badge-row">
        <div class="badge-left">
          <!-- Due Date Picker Badge -->
          <div class="badge-item date-badge">
            <button
              type="button"
              class="tag-btn date-tag"
              @click="cycleDueDate"
              title="Set Due Date"
            >
              <Calendar :size="14" class="tag-icon text-green" />
              <span>{{ dueDateLabel }}</span>
              <X v-if="dueDate" :size="12" class="tag-clear" @click.stop="dueDate = ''" />
            </button>
          </div>

          <!-- Project Picker Badge -->
          <div class="badge-item">
            <button
              type="button"
              class="tag-btn project-tag"
              @click="cycleProject"
              title="Select Project"
            >
              <Inbox :size="14" class="tag-icon text-blue" />
              <span>{{ project }}</span>
            </button>
          </div>

          <!-- Priority Picker Badge -->
          <div class="badge-item">
            <button
              type="button"
              class="tag-btn priority-tag"
              @click="cyclePriority"
              title="Set Priority"
            >
              <Flag :size="14" class="tag-icon" :class="`text-${priority}`" />
              <span class="capitalize">{{ priority }}</span>
            </button>
          </div>
        </div>

        <!-- Submit & Cancel Actions -->
        <div class="form-actions">
          <button
            type="button"
            class="cancel-icon-btn"
            @click="$emit('cancel')"
            title="Cancel"
          >
            <X :size="18" />
          </button>
          <button
            type="submit"
            class="submit-task-btn"
            :disabled="!title.trim()"
            title="Add task"
          >
            <ArrowUp v-if="!isEditing" :size="16" :stroke-width="2.5" />
            <span v-else>Save</span>
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Calendar, Inbox, Flag, X, ArrowUp } from 'lucide-vue-next'

const props = defineProps({
  editTodo: {
    type: Object,
    default: null,
  },
  initialDueDate: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['submit', 'cancel'])

const isEditing = ref(!!props.editTodo)
const title = ref(props.editTodo?.title || '')
const description = ref(props.editTodo?.description || '')
const priority = ref(props.editTodo?.priority || 'low')
const status = ref(props.editTodo?.status || 'pending')
const dueDate = ref(props.editTodo?.due_date || props.initialDueDate || todayIsoString())
const project = ref(props.editTodo?.project || 'Inbox')
const titleInput = ref(null)

function todayIsoString() {
  return new Date().toISOString().split('T')[0]
}

function tomorrowIsoString() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

const dueDateLabel = computed(() => {
  if (!dueDate.value) return 'Due date'
  if (dueDate.value === todayIsoString()) return 'Today'
  if (dueDate.value === tomorrowIsoString()) return 'Tomorrow'
  const d = new Date(dueDate.value)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
})

function cycleDueDate() {
  if (!dueDate.value || dueDate.value === tomorrowIsoString()) {
    dueDate.value = todayIsoString()
  } else if (dueDate.value === todayIsoString()) {
    dueDate.value = tomorrowIsoString()
  } else {
    dueDate.value = ''
  }
}

function cycleProject() {
  const projects = ['Inbox', 'Work', 'Personal', 'Study']
  const idx = projects.indexOf(project.value)
  project.value = projects[(idx + 1) % projects.length]
}

function cyclePriority() {
  const pList = ['low', 'medium', 'high']
  const idx = pList.indexOf(priority.value)
  priority.value = pList[(idx + 1) % pList.length]
}

watch(() => props.editTodo, (newVal) => {
  if (newVal) {
    isEditing.value = true
    title.value = newVal.title || ''
    description.value = newVal.description || ''
    priority.value = newVal.priority || 'low'
    status.value = newVal.status || 'pending'
    dueDate.value = newVal.due_date || ''
    project.value = newVal.project || 'Inbox'
  } else {
    isEditing.value = false
    resetForm()
  }
})

onMounted(() => {
  titleInput.value?.focus()
})

function handleSubmit() {
  if (!title.value.trim()) return

  emit('submit', {
    title: title.value.trim(),
    description: description.value.trim(),
    priority: priority.value,
    status: status.value,
    due_date: dueDate.value || null,
    project: project.value || 'Inbox',
  })

  if (!isEditing.value) {
    resetForm()
  }
}

function resetForm() {
  title.value = ''
  description.value = ''
  priority.value = 'low'
  status.value = 'pending'
  dueDate.value = props.initialDueDate || todayIsoString()
  project.value = 'Inbox'
  titleInput.value?.focus()
}
</script>

<style scoped>
.todo-form-wrapper {
  padding: 4px 0 12px;
}

.todo-form {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-lg);
  padding: 12px 14px 10px;
  box-shadow: var(--shadow-sm);
  animation: fadeInUp 0.15s ease forwards;
  transition: border-color var(--transition-fast);
}

.todo-form:focus-within {
  border-color: var(--text-tertiary);
}

.form-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-input {
  width: 100%;
  padding: 2px 0;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
  background: transparent;
  border: none;
  outline: none;
}

.title-input::placeholder {
  color: var(--text-placeholder);
  font-weight: 400;
}

.desc-input {
  width: 100%;
  padding: 2px 0;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  min-height: 22px;
}

.desc-input::placeholder {
  color: var(--text-placeholder);
}

.form-badge-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  gap: 8px;
  flex-wrap: wrap;
}

.badge-left {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tag-btn:hover {
  background: var(--bg-hover);
  border-color: var(--text-tertiary);
  color: var(--text-primary);
}

.tag-clear {
  margin-left: 2px;
  color: var(--text-tertiary);
}

.tag-clear:hover {
  color: var(--priority-high);
}

.text-green { color: #058527; }
.text-blue { color: #246fe0; }
.text-high { color: var(--priority-high); }
.text-medium { color: var(--priority-medium); }
.text-low { color: var(--priority-low); }

.form-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}

.cancel-icon-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--border-radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.cancel-icon-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.submit-task-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  border: none;
  border-radius: var(--border-radius-sm);
  color: #ffffff;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.submit-task-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: scale(1.05);
}

.submit-task-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.capitalize {
  text-transform: capitalize;
}
</style>
