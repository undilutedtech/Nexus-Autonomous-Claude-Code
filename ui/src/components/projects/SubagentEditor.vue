<template>
  <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-500/20">
          <svg class="w-4 h-4 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
          Custom Subagents
        </h3>
      </div>
      <button
        @click="showAddModal = true"
        class="inline-flex items-center gap-1 rounded-lg bg-brand-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-brand-600"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        Add Subagent
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <svg class="animate-spin h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Subagents List -->
    <div v-else-if="subagents.length > 0" class="space-y-3">
      <div
        v-for="subagent in subagents"
        :key="subagent.name"
        class="flex items-start justify-between rounded-xl border border-gray-200 p-4 dark:border-gray-700"
      >
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <h4 class="font-medium text-gray-800 dark:text-white/90">
              {{ subagent.name }}
            </h4>
            <span
              :class="[
                'rounded-full px-2 py-0.5 text-xs font-medium',
                getTriggerClass(subagent.trigger)
              ]"
            >
              {{ getTriggerLabel(subagent.trigger) }}
            </span>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">
            {{ subagent.description }}
          </p>
          <div v-if="subagent.tools && subagent.tools.length > 0" class="flex flex-wrap gap-1">
            <span
              v-for="tool in subagent.tools"
              :key="tool"
              class="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-400"
            >
              {{ tool }}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2 ml-4">
          <!-- Trigger Button (for manual trigger) -->
          <button
            v-if="subagent.trigger === 'manual'"
            @click="triggerSubagent(subagent.name)"
            :disabled="triggering === subagent.name"
            class="rounded-lg bg-brand-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
          >
            {{ triggering === subagent.name ? 'Running...' : 'Run' }}
          </button>

          <!-- Edit Button -->
          <button
            @click="editSubagent(subagent)"
            class="rounded-lg border border-gray-300 px-2 py-1.5 text-gray-600 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
            title="Edit subagent"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>

          <!-- Delete Button -->
          <button
            @click="deleteSubagent(subagent.name)"
            :disabled="deleting === subagent.name"
            class="rounded-lg border border-error-300 px-2 py-1.5 text-error-600 transition hover:bg-error-50 dark:border-error-700 dark:text-error-400 dark:hover:bg-error-900/20 disabled:opacity-50"
            title="Delete subagent"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="py-8 text-center">
      <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
        <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        No custom subagents configured
      </p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
        Add subagents to automate tasks like testing or code review
      </p>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-4 rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
      {{ error }}
    </div>

    <!-- Add/Edit Modal -->
    <Modal v-if="showAddModal || showEditModal" @close="closeModal">
      <template #body>
        <div class="relative w-full max-w-[500px] rounded-3xl bg-white p-6 dark:bg-gray-900">
          <button
            @click="closeModal"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <h4 class="mb-6 text-xl font-semibold text-gray-800 dark:text-white/90">
            {{ showEditModal ? 'Edit Subagent' : 'Add Subagent' }}
          </h4>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <!-- Name -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Name
              </label>
              <input
                v-model="form.name"
                type="text"
                placeholder="e.g., test-runner"
                :disabled="showEditModal"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:opacity-50"
                required
              />
            </div>

            <!-- Description -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Description
              </label>
              <input
                v-model="form.description"
                type="text"
                placeholder="Brief description of what this subagent does"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required
              />
            </div>

            <!-- Prompt -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Prompt
              </label>
              <textarea
                v-model="form.prompt"
                rows="4"
                placeholder="Instructions for the subagent..."
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required
              ></textarea>
            </div>

            <!-- Trigger -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Trigger
              </label>
              <select
                v-model="form.trigger"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
              >
                <option value="manual">Manual - Run on demand</option>
                <option value="after_feature_complete">After Feature Complete - Run when a feature passes</option>
                <option value="on_error">On Error - Run when agent encounters an error</option>
              </select>
            </div>

            <!-- Tools -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Allowed Tools
              </label>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="tool in availableTools"
                  :key="tool"
                  class="flex items-center gap-2 rounded-lg border px-3 py-2 cursor-pointer transition"
                  :class="form.tools.includes(tool) ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20' : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'"
                >
                  <input
                    type="checkbox"
                    :checked="form.tools.includes(tool)"
                    @change="toggleTool(tool)"
                    class="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ tool }}</span>
                </label>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="modalError" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
              {{ modalError }}
            </div>

            <!-- Actions -->
            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="closeModal"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isSaving"
                class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
              >
                {{ isSaving ? 'Saving...' : (showEditModal ? 'Update' : 'Add') }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import Modal from '@/components/profile/Modal.vue'
import { configAPI, type Subagent } from '@/api/client'

const props = defineProps<{
  projectName: string
}>()

const subagents = ref<Subagent[]>([])
const isLoading = ref(false)
const triggering = ref<string | null>(null)
const deleting = ref<string | null>(null)
const error = ref('')

// Modal state
const showAddModal = ref(false)
const showEditModal = ref(false)
const isSaving = ref(false)
const modalError = ref('')
const editingSubagent = ref<Subagent | null>(null)

const form = reactive({
  name: '',
  description: '',
  prompt: '',
  trigger: 'manual' as 'manual' | 'after_feature_complete' | 'on_error',
  tools: [] as string[],
})

const availableTools = ['bash', 'read', 'write', 'edit', 'glob', 'grep']

onMounted(async () => {
  await fetchSubagents()
})

async function fetchSubagents() {
  isLoading.value = true
  try {
    const config = await configAPI.getSubagents(props.projectName)
    subagents.value = config.subagents || []
  } catch (err) {
    console.error('Failed to fetch subagents:', err)
  } finally {
    isLoading.value = false
  }
}

async function triggerSubagent(name: string) {
  triggering.value = name
  error.value = ''
  try {
    const result = await configAPI.triggerSubagent(props.projectName, name)
    console.log('Subagent triggered:', result)
  } catch (err: any) {
    error.value = err.message || 'Failed to trigger subagent'
  } finally {
    triggering.value = null
  }
}

async function deleteSubagent(name: string) {
  if (!confirm(`Delete subagent "${name}"?`)) return

  deleting.value = name
  error.value = ''
  try {
    await configAPI.deleteSubagent(props.projectName, name)
    await fetchSubagents()
  } catch (err: any) {
    error.value = err.message || 'Failed to delete subagent'
  } finally {
    deleting.value = null
  }
}

function editSubagent(subagent: Subagent) {
  editingSubagent.value = subagent
  form.name = subagent.name
  form.description = subagent.description
  form.prompt = subagent.prompt
  form.trigger = subagent.trigger
  form.tools = [...(subagent.tools || [])]
  showEditModal.value = true
}

function toggleTool(tool: string) {
  const index = form.tools.indexOf(tool)
  if (index >= 0) {
    form.tools.splice(index, 1)
  } else {
    form.tools.push(tool)
  }
}

function closeModal() {
  showAddModal.value = false
  showEditModal.value = false
  editingSubagent.value = null
  modalError.value = ''
  form.name = ''
  form.description = ''
  form.prompt = ''
  form.trigger = 'manual'
  form.tools = []
}

async function handleSubmit() {
  isSaving.value = true
  modalError.value = ''

  try {
    // Get current subagents
    const currentSubagents = [...subagents.value]

    // Create new subagent object
    const newSubagent: Subagent = {
      name: form.name,
      description: form.description,
      prompt: form.prompt,
      trigger: form.trigger,
      tools: form.tools,
    }

    if (showEditModal.value) {
      // Update existing
      const index = currentSubagents.findIndex(s => s.name === form.name)
      if (index >= 0) {
        currentSubagents[index] = newSubagent
      }
    } else {
      // Check for duplicate name
      if (currentSubagents.some(s => s.name === form.name)) {
        modalError.value = 'A subagent with this name already exists'
        isSaving.value = false
        return
      }
      currentSubagents.push(newSubagent)
    }

    // Update all subagents
    await configAPI.updateSubagents(props.projectName, { subagents: currentSubagents })
    await fetchSubagents()
    closeModal()
  } catch (err: any) {
    modalError.value = err.message || 'Failed to save subagent'
  } finally {
    isSaving.value = false
  }
}

function getTriggerLabel(trigger: string): string {
  switch (trigger) {
    case 'manual':
      return 'Manual'
    case 'after_feature_complete':
      return 'After Feature'
    case 'on_error':
      return 'On Error'
    default:
      return trigger
  }
}

function getTriggerClass(trigger: string): string {
  switch (trigger) {
    case 'manual':
      return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
    case 'after_feature_complete':
      return 'bg-success-100 text-success-600 dark:bg-success-900/20 dark:text-success-400'
    case 'on_error':
      return 'bg-error-100 text-error-600 dark:bg-error-900/20 dark:text-error-400'
    default:
      return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
  }
}
</script>
