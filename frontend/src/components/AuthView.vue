<template>
  <div class="auth-view">
    <div class="auth-container">
      <!-- Logo / Brand -->
      <div class="auth-brand" @click="router.push('/')" style="cursor: pointer" title="Back to home">
        <div class="auth-logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="#dc4c3e"/>
            <path d="M8 16.5L13 21.5L24 10.5" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="auth-title">Todue </h1>
        <p class="auth-subtitle">Organize your work and life, finally.</p>
      </div>

      <!-- Auth Card -->
      <div class="auth-card">
        <div class="auth-tabs">
          <button
            :class="['auth-tab', { active: mode === 'login' }]"
            @click="switchMode('login')"
          >
            Log in
          </button>
          <button
            :class="['auth-tab', { active: mode === 'register' }]"
            @click="switchMode('register')"
          >
            Sign up
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <!-- Full Name (Register only) -->
          <div v-if="mode === 'register'" class="form-group fade-in-up">
            <label for="fullName">Full Name</label>
            <input
              id="fullName"
              v-model="fullName"
              type="text"
              placeholder="Enter your name"
              autocomplete="name"
            />
          </div>

          <!-- Email -->
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="Enter your email..."
              required
              autocomplete="email"
            />
          </div>

          <!-- Password -->
          <div class="form-group">
            <label for="password">Password</label>
            <div class="password-wrapper">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password..."
                required
                minlength="6"
                autocomplete="current-password"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                tabindex="-1"
                :title="showPassword ? 'Hide password' : 'Show password'"
              >
                <EyeOff v-if="showPassword" :size="18" />
                <Eye v-else :size="18" />
              </button>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="authError" class="auth-error fade-in">
            <AlertCircle :size="16" class="error-icon" />
            {{ authError }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="btn btn-primary btn-lg auth-submit"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="spinner"></span>
            <span v-else>
              {{ mode === 'login' ? 'Log in' : 'Sign up' }}
            </span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Eye, EyeOff, AlertCircle } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'

const props = defineProps({
  initialMode: {
    type: String,
    default: 'login',
  },
})

const emit = defineEmits(['authenticated'])
const route = useRoute()
const router = useRouter()

const { login, register, isLoading, error: authError } = useAuth()

const mode = ref(route?.path === '/register' ? 'register' : (props.initialMode || 'login'))
const email = ref('')
const password = ref('')
const fullName = ref('')
const showPassword = ref(false)

watch(() => route?.path, (newPath) => {
  if (newPath === '/register') mode.value = 'register'
  else if (newPath === '/login') mode.value = 'login'
})

function switchMode(newMode) {
  mode.value = newMode
  if (router) {
    router.replace(`/${newMode}`)
  }
}

async function handleSubmit() {
  try {
    if (mode.value === 'login') {
      await login(email.value, password.value)
    } else {
      await register(email.value, password.value, fullName.value)
    }
    emit('authenticated')
  } catch {
    // Error is already set in the composable
  }
}
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 400px;
  animation: fadeInUp var(--transition-slow) forwards;
}

.auth-brand {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  display: inline-flex;
  margin-bottom: 12px;
}

.auth-title {
  font-size: var(--font-size-2xl);
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.auth-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin-top: 4px;
}

.auth-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-lg);
  padding: 28px;
  box-shadow: var(--shadow-lg);
}

.auth-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-default);
}

.auth-tab {
  flex: 1;
  padding: 10px 0;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  background: transparent;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.auth-tab:hover {
  color: var(--text-secondary);
}

.auth-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input {
  width: 100%;
  padding: 10px 14px;
  font-size: var(--font-size-base);
}

.password-wrapper {
  position: relative;
}

.password-wrapper input {
  width: 100%;
  padding-right: 44px;
}

.password-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  cursor: pointer;
  background: none;
  border: none;
  padding: 4px;
}

.auth-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--priority-high-bg);
  color: var(--priority-high);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.error-icon {
  flex-shrink: 0;
}

.auth-submit {
  width: 100%;
  margin-top: 4px;
  padding: 12px;
  font-size: var(--font-size-md);
}
</style>
