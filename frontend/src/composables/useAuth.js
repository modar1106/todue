/**
 * Authentication composable.
 * Manages user auth state, login, register, and logout.
 */

import { ref, computed } from 'vue'
import api from '../utils/api'

// ── Global reactive state (shared across components) ───────
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
const isLoading = ref(false)
const error = ref(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value && !!localStorage.getItem('access_token'))

  /**
   * Register a new user account.
   */
  async function register(email, password, fullName) {
    isLoading.value = true
    error.value = null

    try {
      const { data } = await api.post('/auth/register', {
        email,
        password,
        full_name: fullName,
      })

      // Store tokens and user
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      user.value = data.user

      return data
    } catch (err) {
      let message = 'Registration failed. Please try again.'
      const detail = err.response?.data?.detail || err.response?.data?.error
      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail) && detail.length > 0) {
        message = detail.map(d => d.msg || JSON.stringify(d)).join(', ')
      } else if (err.message && !err.response) {
        message = `Cannot connect to server: ${err.message}`
      }
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Login with email and password.
   */
  async function login(email, password) {
    isLoading.value = true
    error.value = null

    try {
      const { data } = await api.post('/auth/login', {
        email,
        password,
      })

      // Store tokens and user
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      user.value = data.user

      return data
    } catch (err) {
      let message = 'Invalid email or password.'
      const detail = err.response?.data?.detail || err.response?.data?.error
      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail) && detail.length > 0) {
        message = detail.map(d => d.msg || JSON.stringify(d)).join(', ')
      } else if (err.message && !err.response) {
        message = `Cannot connect to server: ${err.message}`
      }
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout the current user.
   */
  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    user.value = null
  }

  /**
   * Fetch current user profile from API.
   */
  async function fetchProfile() {
    try {
      const { data } = await api.get('/auth/me')
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    } catch {
      // Token may be expired
      logout()
      return null
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    register,
    login,
    logout,
    fetchProfile,
  }
}
