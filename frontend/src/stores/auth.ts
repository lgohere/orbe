/**
 * Authentication store using Pinia
 * Manages user authentication state, tokens, and user data
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'SUPER_ADMIN' | 'BOARD' | 'FISCAL_COUNCIL' | 'MEMBER'
  profile: {
    phone: string
    city: string
    state: string
    country: string
    membership_due_day: number
    theme_preference: 'white' | 'black'
    language_preference: 'pt-BR' | 'en' | 'es'
    is_onboarding_completed: boolean
  }
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  key: string  // DRF auth token
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isBoardMember = computed(() => user.value?.role === 'BOARD')
  const isFiscalCouncilMember = computed(() => user.value?.role === 'FISCAL_COUNCIL')
  const isAdmin = computed(() => user.value?.role === 'SUPER_ADMIN')
  const canCreateCases = computed(() => isBoardMember.value || isAdmin.value)
  const canApproveCases = computed(() => isFiscalCouncilMember.value || isAdmin.value)

  // Actions
  async function login(credentials: LoginCredentials): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      const data = await response.json()

      if (!response.ok) {
        error.value = data.non_field_errors?.[0] || data.detail || 'Login failed'
        return false
      }

      // Store token
      token.value = data.key
      localStorage.setItem('auth_token', data.key)

      // Fetch user data
      await fetchUser()

      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Network error'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser(): Promise<void> {
    if (!token.value) return

    try {
      const response = await fetch('/api/users/me/', {
        headers: {
          Authorization: `Token ${token.value}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user')
      }

      const data = await response.json()
      user.value = data
    } catch (err) {
      console.error('Failed to fetch user:', err)
      // If user fetch fails, logout
      logout()
    }
  }

  async function logout(): Promise<void> {
    try {
      if (token.value) {
        await fetch('/api/auth/logout/', {
          method: 'POST',
          headers: {
            Authorization: `Token ${token.value}`,
          },
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear state regardless of API call success
      token.value = null
      user.value = null
      error.value = null
      localStorage.removeItem('auth_token')
    }
  }

  async function register(data: {
    email: string
    password1: string
    password2: string
  }): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/auth/registration/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const result = await response.json()

      if (!response.ok) {
        error.value = result.email?.[0] || result.password1?.[0] || result.non_field_errors?.[0] || 'Registration failed'
        return false
      }

      // Store token
      token.value = result.key
      localStorage.setItem('auth_token', result.key)

      // Fetch user data
      await fetchUser()

      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Network error'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function setupPassword(data: {
    token: string
    password: string
    password_confirm: string
  }): Promise<{ success: boolean; error?: string }> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/users/invitations/setup-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const result = await response.json()

      if (!response.ok) {
        const errorMsg = result.password?.[0] ||
                        result.password_confirm?.[0] ||
                        result.token?.[0] ||
                        result.non_field_errors?.[0] ||
                        'Erro ao criar conta'
        error.value = errorMsg
        return { success: false, error: errorMsg }
      }

      // Store token from response (auto-login)
      token.value = result.token
      localStorage.setItem('auth_token', result.token)

      // Store user data
      user.value = result.user

      return { success: true }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erro de rede'
      error.value = errorMsg
      return { success: false, error: errorMsg }
    } finally {
      isLoading.value = false
    }
  }

  async function updatePreferences(preferences: {
    theme_preference?: 'white' | 'black'
    language_preference?: 'pt-BR' | 'en' | 'es'
  }): Promise<boolean> {
    if (!token.value) return false

    try {
      const response = await fetch('/api/users/preferences/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token.value}`,
        },
        body: JSON.stringify(preferences),
      })

      if (!response.ok) {
        throw new Error('Failed to update preferences')
      }

      const data = await response.json()
      if (user.value) {
        user.value.profile = { ...user.value.profile, ...data }
      }

      return true
    } catch (err) {
      console.error('Failed to update preferences:', err)
      return false
    }
  }

  // Initialize: Load user if token exists
  async function initialize(): Promise<void> {
    if (token.value) {
      await fetchUser()
    }
  }

  return {
    // State
    token,
    user,
    isLoading,
    error,
    // Computed
    isAuthenticated,
    isBoardMember,
    isFiscalCouncilMember,
    isAdmin,
    canCreateCases,
    canApproveCases,
    // Actions
    login,
    logout,
    register,
    setupPassword,
    fetchUser,
    updatePreferences,
    initialize,
  }
})