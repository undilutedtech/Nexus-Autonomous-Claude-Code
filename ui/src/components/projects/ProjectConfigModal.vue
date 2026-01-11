<template>
  <Modal @close="$emit('close')">
    <template #body>
      <div
        class="relative w-full max-w-[500px] rounded-3xl bg-white p-6 dark:bg-gray-900"
      >
        <button
          @click="$emit('close')"
          class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <h4 class="mb-6 text-xl font-semibold text-gray-800 dark:text-white/90">
          Project Configuration
        </h4>

        <!-- Loading State -->
        <div v-if="isLoading" class="flex items-center justify-center py-12">
          <svg class="animate-spin h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <form v-else @submit.prevent="handleSubmit" class="space-y-5">
          <!-- Max Parallel Agents -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Max Parallel Agents
            </label>
            <select
              v-model.number="form.max_parallel_agents"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
            >
              <option v-for="n in 10" :key="n" :value="n">{{ n }} agent{{ n > 1 ? 's' : '' }}</option>
            </select>
            <p class="mt-1 text-xs text-gray-500">Maximum number of agents that can work simultaneously</p>
          </div>

          <!-- Default Mode -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Default Agent Mode
            </label>
            <div class="space-y-2">
              <label class="flex items-center gap-3 rounded-lg border border-gray-200 p-3 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800" :class="{ 'border-brand-500 bg-brand-50 dark:bg-brand-900/20': form.default_mode === 'separate' }">
                <input type="radio" v-model="form.default_mode" value="separate" class="h-4 w-4 text-brand-500" />
                <div>
                  <p class="text-sm font-medium text-gray-800 dark:text-white/90">Separate</p>
                  <p class="text-xs text-gray-500">Each agent works on different features</p>
                </div>
              </label>
              <label class="flex items-center gap-3 rounded-lg border border-gray-200 p-3 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800" :class="{ 'border-brand-500 bg-brand-50 dark:bg-brand-900/20': form.default_mode === 'collaborative' }">
                <input type="radio" v-model="form.default_mode" value="collaborative" class="h-4 w-4 text-brand-500" />
                <div>
                  <p class="text-sm font-medium text-gray-800 dark:text-white/90">Collaborative</p>
                  <p class="text-xs text-gray-500">Agents can work on the same feature together</p>
                </div>
              </label>
              <label class="flex items-center gap-3 rounded-lg border border-gray-200 p-3 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800" :class="{ 'border-brand-500 bg-brand-50 dark:bg-brand-900/20': form.default_mode === 'worktree' }">
                <input type="radio" v-model="form.default_mode" value="worktree" class="h-4 w-4 text-brand-500" />
                <div>
                  <p class="text-sm font-medium text-gray-800 dark:text-white/90">Worktree</p>
                  <p class="text-xs text-gray-500">Each agent works in its own git worktree</p>
                </div>
              </label>
            </div>
          </div>

          <!-- Use Worktrees -->
          <div class="flex items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">Use Git Worktrees</p>
              <p class="text-xs text-gray-500">Create isolated git worktrees for parallel agents</p>
            </div>
            <button
              type="button"
              @click="form.use_worktrees = !form.use_worktrees"
              class="relative h-6 w-11 rounded-full transition-colors"
              :class="form.use_worktrees ? 'bg-brand-500' : 'bg-gray-300 dark:bg-gray-600'"
            >
              <span
                class="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition-transform"
                :class="{ 'translate-x-5': form.use_worktrees }"
              ></span>
            </button>
          </div>

          <!-- Auto-stop on Completion -->
          <div class="flex items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">Auto-stop on Completion</p>
              <p class="text-xs text-gray-500">Stop agents when all features pass</p>
            </div>
            <button
              type="button"
              @click="form.auto_stop_on_completion = !form.auto_stop_on_completion"
              class="relative h-6 w-11 rounded-full transition-colors"
              :class="form.auto_stop_on_completion ? 'bg-brand-500' : 'bg-gray-300 dark:bg-gray-600'"
            >
              <span
                class="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition-transform"
                :class="{ 'translate-x-5': form.auto_stop_on_completion }"
              ></span>
            </button>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
            {{ error }}
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="$emit('close')"
              class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isSaving"
              class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
            >
              {{ isSaving ? 'Saving...' : 'Save Configuration' }}
            </button>
          </div>
        </form>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import Modal from '@/components/profile/Modal.vue'
import { configAPI, type ProjectConfigUpdate } from '@/api/client'

const props = defineProps<{
  projectName: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const form = reactive<ProjectConfigUpdate>({
  max_parallel_agents: 1,
  default_mode: 'separate',
  use_worktrees: false,
  auto_stop_on_completion: true,
})

const isLoading = ref(true)
const isSaving = ref(false)
const error = ref('')

onMounted(async () => {
  await loadConfig()
})

async function loadConfig() {
  isLoading.value = true
  try {
    const config = await configAPI.get(props.projectName)
    form.max_parallel_agents = config.max_parallel_agents
    form.default_mode = config.default_mode
    form.use_worktrees = config.use_worktrees
    form.auto_stop_on_completion = config.auto_stop_on_completion
  } catch (err) {
    console.error('Failed to load config:', err)
  } finally {
    isLoading.value = false
  }
}

async function handleSubmit() {
  isSaving.value = true
  error.value = ''

  try {
    await configAPI.update(props.projectName, form)
    emit('saved')
    emit('close')
  } catch (err: any) {
    error.value = err.message || 'Failed to save configuration'
  } finally {
    isSaving.value = false
  }
}
</script>
