<template>
  <Modal @close="$emit('close')" :fullScreenBackdrop="true">
    <template #body>
      <div
        class="relative w-full max-w-[500px] rounded-3xl bg-white p-6 dark:bg-gray-900 shadow-xl"
      >
        <!-- Header with AI Icon -->
        <div class="flex items-start gap-4 mb-6">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-900/30">
            <svg class="w-6 h-6 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1">
            <h4 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              Agent Question
            </h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              The agent needs your input to continue
            </p>
          </div>
        </div>

        <!-- Context (if provided) -->
        <div v-if="question.context" class="mb-4 rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
          <p class="text-sm text-gray-600 dark:text-gray-300">
            {{ question.context }}
          </p>
        </div>

        <!-- Question -->
        <div class="mb-6">
          <p class="text-base font-medium text-gray-800 dark:text-white/90">
            {{ question.question }}
          </p>
        </div>

        <!-- Options (if provided) -->
        <div v-if="question.options && question.options.length > 0" class="mb-6 space-y-2">
          <button
            v-for="(option, index) in question.options"
            :key="index"
            @click="selectOption(option)"
            :class="[
              'w-full rounded-lg border px-4 py-3 text-left text-sm font-medium transition',
              selectedOption === option
                ? 'border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800'
            ]"
          >
            {{ option }}
          </button>
        </div>

        <!-- Free-form input -->
        <div class="mb-6">
          <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            {{ question.options && question.options.length > 0 ? 'Or type a custom response:' : 'Your response:' }}
          </label>
          <textarea
            v-model="customAnswer"
            rows="3"
            :placeholder="question.options && question.options.length > 0 ? 'Type a custom answer...' : 'Type your response...'"
            class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
            @input="selectedOption = ''"
          ></textarea>
        </div>

        <!-- Actions -->
        <div class="flex gap-3">
          <button
            type="button"
            @click="skipQuestion"
            class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Skip
          </button>
          <button
            @click="submitAnswer"
            :disabled="isSubmitting || (!selectedOption && !customAnswer.trim())"
            class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
          >
            {{ isSubmitting ? 'Submitting...' : 'Submit Answer' }}
          </button>
        </div>

        <!-- Error -->
        <div v-if="error" class="mt-4 rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
          {{ error }}
        </div>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Modal from '@/components/profile/Modal.vue'
import { questionsAPI, type AgentQuestion } from '@/api/client'

const props = defineProps<{
  projectName: string
  question: AgentQuestion
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'answered'): void
}>()

const selectedOption = ref('')
const customAnswer = ref('')
const isSubmitting = ref(false)
const error = ref('')

function selectOption(option: string) {
  selectedOption.value = option
  customAnswer.value = ''
}

async function submitAnswer() {
  const answer = selectedOption.value || customAnswer.value.trim()
  if (!answer) return

  isSubmitting.value = true
  error.value = ''

  try {
    await questionsAPI.answer(props.projectName, props.question.id, answer)
    emit('answered')
    emit('close')
  } catch (err: any) {
    error.value = err.message || 'Failed to submit answer'
  } finally {
    isSubmitting.value = false
  }
}

async function skipQuestion() {
  isSubmitting.value = true
  error.value = ''

  try {
    await questionsAPI.answer(props.projectName, props.question.id, '[SKIPPED]')
    emit('answered')
    emit('close')
  } catch (err: any) {
    error.value = err.message || 'Failed to skip question'
  } finally {
    isSubmitting.value = false
  }
}
</script>
