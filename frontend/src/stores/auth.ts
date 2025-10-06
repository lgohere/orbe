/**
 * Authentication store using Pinia
 * Manages user authentication state, tokens, and user data
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  apiService,
  type User,
  type LoginCredentials,
  type RegistrationPayload,
  type SetupPasswordPayload,
  type UpdatePreferencesPayload,
} from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(apiService.getAuthToken())
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const fullName = computed(() => user.value ? `${user.value.first_name} ${user.value.last_name}`.trim() : '')
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
      const { data, error: apiError } = await apiService.login(credentials)

      if (!data) {
        error.value = apiError || 'Login failed'
        return false
      }

      apiService.setAuthToken(data.key)
      token.value = data.key

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
      const { data, error: apiError } = await apiService.currentUser()

      if (!data) {
        throw new Error(apiError || 'Failed to fetch user')
      }

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
        await apiService.logout()
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear state regardless of API call success
      apiService.setAuthToken(null)
      token.value = null
      user.value = null
      error.value = null
    }
  }

  async function register(data: RegistrationPayload): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const { data: result, error: apiError } = await apiService.register(data)

      if (!result) {
        error.value = apiError || 'Registration failed'
        return false
      }

      apiService.setAuthToken(result.key)
      token.value = result.key

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

  async function setupPassword(data: SetupPasswordPayload): Promise<{ success: boolean; error?: string }> {
    isLoading.value = true
    error.value = null

    try {
      const { data: result, error: apiError } = await apiService.setupPassword(data)

      if (!result) {
        const errorMsg = apiError || 'Erro ao criar conta'
        error.value = errorMsg
        return { success: false, error: errorMsg }
      }

      apiService.setAuthToken(result.token)
      token.value = result.token
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

  async function updatePreferences(preferences: UpdatePreferencesPayload): Promise<boolean> {
    if (!token.value) return false

    try {
      const { data, error: apiError } = await apiService.updatePreferences(preferences)
      if (!data) {
        throw new Error(apiError || 'Failed to update preferences')
      }
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
    fullName,
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
