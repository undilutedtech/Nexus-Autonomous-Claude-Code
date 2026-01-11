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
          Add Feature
        </h4>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Category -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Category
            </label>
            <input
              v-model="form.category"
              type="text"
              placeholder="e.g., Authentication, UI, API"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              required
            />
          </div>

          <!-- Name -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Feature Name
            </label>
            <input
              v-model="form.name"
              type="text"
              placeholder="e.g., User Login Form"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              required
            />
          </div>

          <!-- Description -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Description
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              placeholder="Describe what this feature should do..."
              class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              required
            ></textarea>
          </div>

          <!-- Steps -->
          <div>
            <div class="mb-1.5 flex items-center justify-between">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-400">
                Verification Steps
              </label>
              <button
                type="button"
                @click="addStep"
                class="text-xs text-brand-500 hover:text-brand-600"
              >
                + Add Step
              </button>
            </div>
            <div class="space-y-2">
              <div
                v-for="(step, index) in form.steps"
                :key="index"
                class="flex items-center gap-2"
              >
                <span class="w-6 text-center text-sm text-gray-400">{{ index + 1 }}.</span>
                <input
                  v-model="form.steps[index]"
                  type="text"
                  :placeholder="`Step ${index + 1}...`"
                  class="h-10 flex-1 rounded-lg border border-gray-300 bg-transparent px-3 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                />
                <button
                  v-if="form.steps.length > 1"
                  type="button"
                  @click="removeStep(index)"
                  class="text-gray-400 hover:text-error-500"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
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
              :disabled="isSubmitting"
              class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
            >
              {{ isSubmitting ? 'Adding...' : 'Add Feature' }}
            </button>
          </div>
        </form>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import Modal from '@/components/profile/Modal.vue'
import { featuresAPI, type FeatureCreate } from '@/api/client'

const props = defineProps<{
  projectName: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'added'): void
}>()

const form = reactive<FeatureCreate>({
  category: '',
  name: '',
  description: '',
  steps: [''],
})

const isSubmitting = ref(false)
const error = ref('')

function addStep() {
  form.steps.push('')
}

function removeStep(index: number) {
  form.steps.splice(index, 1)
}

async function handleSubmit() {
  // Filter out empty steps
  const steps = form.steps.filter(s => s.trim() !== '')
  if (steps.length === 0) {
    error.value = 'Please add at least one verification step'
    return
  }

  isSubmitting.value = true
  error.value = ''

  try {
    await featuresAPI.create(props.projectName, {
      category: form.category,
      name: form.name,
      description: form.description,
      steps,
    })
    emit('added')
    emit('close')
  } catch (err: any) {
    error.value = err.message || 'Failed to add feature'
  } finally {
    isSubmitting.value = false
  }
}
</script>
