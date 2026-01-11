/**
 * Auth Composable
 * ================
 *
 * Vue composable for authentication state management.
 */

import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  authAPI,
  setAuthToken,
  clearAuthToken,
  getAuthToken,
  type UserResponse,
  type LoginData,
  type RegisterData,
  type ProfileUpdate,
  type PasswordChange,
  type MFAEnableData,
  type MFAVerifyData,
} from '@/api/client'

// Global state (shared across components)
const user = ref<UserResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const isInitialized = ref(false)

export function useAuth() {
  const router = useRouter()

  // Computed
  const isAuthenticated = computed(() => !!user.value)
  const username = computed(() => user.value?.username ?? '')
  const email = computed(() => user.value?.email ?? '')
  const fullName = computed(() => user.value?.full_name ?? user.value?.username ?? '')
  const avatarUrl = computed(() => user.value?.avatar_url)
  const mfaEnabled = computed(() => user.value?.mfa_enabled ?? false)
  const settings = computed(() => user.value?.settings ?? {})

  /**
   * Initialize auth state from stored token.
   */
  async function initialize(): Promise<void> {
    if (isInitialized.value) return

    const token = getAuthToken()
    if (!token) {
      isInitialized.value = true
      return
    }

    try {
      isLoading.value = true
      const userData = await authAPI.getMe()
      user.value = userData
    } catch (err) {
      // Token is invalid, clear it
      clearAuthToken()
      user.value = null
    } finally {
      isLoading.value = false
      isInitialized.value = true
    }
  }

  /**
   * Register a new user.
   */
  async function register(data: RegisterData): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      const response = await authAPI.register(data)
      setAuthToken(response.access_token)
      user.value = response.user

      return true
    } catch (err: any) {
      error.value = err.message || 'Registration failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Login with email/username and password.
   */
  async function login(data: LoginData): Promise<{ success: boolean; mfaRequired?: boolean }> {
    try {
      isLoading.value = true
      error.value = null

      const response = await authAPI.login(data)
      setAuthToken(response.access_token)
      user.value = response.user

      return { success: true }
    } catch (err: any) {
      if (err.mfaRequired) {
        return { success: false, mfaRequired: true }
      }
      error.value = err.message || 'Login failed'
      return { success: false }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout the current user.
   */
  function logout(): void {
    clearAuthToken()
    user.value = null
    router.push('/signin')
  }

  /**
   * Update user profile.
   */
  async function updateProfile(data: ProfileUpdate): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      const updatedUser = await authAPI.updateProfile(data)
      user.value = updatedUser

      return true
    } catch (err: any) {
      error.value = err.message || 'Profile update failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Change password.
   */
  async function changePassword(data: PasswordChange): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      await authAPI.changePassword(data)
      return true
    } catch (err: any) {
      error.value = err.message || 'Password change failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update user settings.
   */
  async function updateSettings(newSettings: Record<string, unknown>): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      const updatedUser = await authAPI.updateSettings(newSettings)
      user.value = updatedUser

      return true
    } catch (err: any) {
      error.value = err.message || 'Settings update failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Setup MFA - returns secret and QR code.
   */
  async function setupMFA(): Promise<{ secret: string; qrCode: string } | null> {
    try {
      isLoading.value = true
      error.value = null

      const response = await authAPI.setupMFA()
      return {
        secret: response.secret,
        qrCode: response.qr_code,
      }
    } catch (err: any) {
      error.value = err.message || 'MFA setup failed'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Enable MFA after verifying code.
   */
  async function enableMFA(data: MFAEnableData): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      await authAPI.enableMFA(data)

      // Refresh user data to get updated mfa_enabled status
      const updatedUser = await authAPI.getMe()
      user.value = updatedUser

      return true
    } catch (err: any) {
      error.value = err.message || 'MFA enable failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Disable MFA.
   */
  async function disableMFA(data: MFAVerifyData): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      await authAPI.disableMFA(data)

      // Refresh user data
      const updatedUser = await authAPI.getMe()
      user.value = updatedUser

      return true
    } catch (err: any) {
      error.value = err.message || 'MFA disable failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear error state.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    // State
    user,
    isLoading,
    error,
    isInitialized,

    // Computed
    isAuthenticated,
    username,
    email,
    fullName,
    avatarUrl,
    mfaEnabled,
    settings,

    // Methods
    initialize,
    register,
    login,
    logout,
    updateProfile,
    changePassword,
    updateSettings,
    setupMFA,
    enableMFA,
    disableMFA,
    clearError,
  }
}
