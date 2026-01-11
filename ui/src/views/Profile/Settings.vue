<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Settings'" />

    <div class="space-y-6">
      <!-- Appearance -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <h3 class="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">
          Appearance
        </h3>

        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-800 dark:text-white/90">Dark Mode</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Switch between light and dark themes
              </p>
            </div>
            <button
              @click="toggleTheme"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                isDark ? 'bg-brand-500' : 'bg-gray-300'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  isDark ? 'translate-x-6' : 'translate-x-1'
                ]"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- Notifications -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <h3 class="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">
          Notifications
        </h3>

        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-800 dark:text-white/90">Email Notifications</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Receive email updates about your projects
              </p>
            </div>
            <button
              @click="toggleSetting('emailNotifications')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                localSettings.emailNotifications ? 'bg-brand-500' : 'bg-gray-300'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  localSettings.emailNotifications ? 'translate-x-6' : 'translate-x-1'
                ]"
              />
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-800 dark:text-white/90">Agent Completion Alerts</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Get notified when an agent completes a task
              </p>
            </div>
            <button
              @click="toggleSetting('agentAlerts')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                localSettings.agentAlerts ? 'bg-brand-500' : 'bg-gray-300'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  localSettings.agentAlerts ? 'translate-x-6' : 'translate-x-1'
                ]"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- Agent Preferences -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <h3 class="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">
          Agent Preferences
        </h3>

        <div class="space-y-5">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Default Session Delay (seconds)
            </label>
            <input
              v-model.number="localSettings.sessionDelay"
              type="number"
              min="1"
              max="60"
              class="h-11 w-32 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Time between agent sessions (1-60 seconds)
            </p>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-800 dark:text-white/90">YOLO Mode Default</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Enable YOLO mode by default for new projects
              </p>
            </div>
            <button
              @click="toggleSetting('yoloMode')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                localSettings.yoloMode ? 'bg-warning-500' : 'bg-gray-300'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  localSettings.yoloMode ? 'translate-x-6' : 'translate-x-1'
                ]"
              />
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-800 dark:text-white/90">Auto-continue Sessions</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Automatically continue to next session after completion
              </p>
            </div>
            <button
              @click="toggleSetting('autoContinue')"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                localSettings.autoContinue ? 'bg-brand-500' : 'bg-gray-300'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  localSettings.autoContinue ? 'translate-x-6' : 'translate-x-1'
                ]"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="flex justify-end gap-3">
        <button
          @click="resetSettings"
          class="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          Reset to Defaults
        </button>
        <button
          @click="saveSettings"
          :disabled="isLoading"
          class="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
        >
          {{ isLoading ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>

      <!-- Success/Error Messages -->
      <div
        v-if="saveSuccess"
        class="rounded-lg bg-success-50 p-4 text-sm text-success-600 dark:bg-success-900/20 dark:text-success-400"
      >
        Settings saved successfully!
      </div>
      <div
        v-if="saveError"
        class="rounded-lg bg-error-50 p-4 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400"
      >
        {{ saveError }}
      </div>

      <!-- Danger Zone -->
      <div
        class="rounded-2xl border border-error-200 bg-error-50/50 p-5 dark:border-error-800 dark:bg-error-900/10 lg:p-6"
      >
        <h3 class="mb-2 text-lg font-semibold text-error-700 dark:text-error-400">
          Danger Zone
        </h3>
        <p class="mb-4 text-sm text-error-600 dark:text-error-400/80">
          These actions are irreversible. Please proceed with caution.
        </p>

        <div class="flex flex-wrap gap-3">
          <button
            @click="handleLogout"
            class="rounded-lg border border-error-300 px-4 py-2 text-sm font-medium text-error-600 transition hover:bg-error-100 dark:border-error-700 dark:text-error-400 dark:hover:bg-error-900/30"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/components/layout/ThemeProvider.vue'

const { settings, updateSettings, isLoading, logout } = useAuth()
const { isDarkMode: isDark, toggleTheme } = useTheme()

const saveSuccess = ref(false)
const saveError = ref('')

const defaultSettings = {
  emailNotifications: true,
  agentAlerts: true,
  sessionDelay: 3,
  yoloMode: false,
  autoContinue: true,
}

const localSettings = reactive({ ...defaultSettings })

onMounted(() => {
  // Load saved settings
  if (settings.value) {
    Object.assign(localSettings, {
      ...defaultSettings,
      ...settings.value,
    })
  }
})

const toggleSetting = (key: keyof typeof localSettings) => {
  if (typeof localSettings[key] === 'boolean') {
    (localSettings[key] as boolean) = !localSettings[key]
  }
}

const saveSettings = async () => {
  saveSuccess.value = false
  saveError.value = ''

  const success = await updateSettings(localSettings)
  if (success) {
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } else {
    saveError.value = 'Failed to save settings'
  }
}

const resetSettings = () => {
  Object.assign(localSettings, defaultSettings)
}

const handleLogout = () => {
  logout()
}
</script>

