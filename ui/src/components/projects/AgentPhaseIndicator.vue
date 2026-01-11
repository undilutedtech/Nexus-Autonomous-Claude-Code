<template>
  <div
    v-if="phase && showIndicator"
    class="rounded-xl border p-4 transition-all"
    :class="containerClass"
  >
    <!-- Phase Header -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <!-- Phase Icon -->
        <div
          class="flex h-8 w-8 items-center justify-center rounded-lg"
          :class="iconClass"
        >
          <svg v-if="phase.phase === 'creating_features'" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else-if="phase.phase === 'implementing'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <svg v-else-if="phase.phase === 'complete'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <h4 class="text-sm font-semibold" :class="titleClass">{{ phaseTitle }}</h4>
          <p class="text-xs text-gray-500 dark:text-gray-400">{{ phase.description }}</p>
        </div>
      </div>

      <!-- Time Estimate Badge -->
      <div
        v-if="timeEstimate"
        class="flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium"
        :class="badgeClass"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ timeEstimate }}
      </div>
    </div>

    <!-- Progress Bar (for implementing phase) -->
    <div v-if="phase.progress !== null" class="mt-3">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs text-gray-500 dark:text-gray-400">Progress</span>
        <span class="text-xs font-medium" :class="progressTextClass">
          {{ phase.features_passing }}/{{ phase.features_total }} features
        </span>
      </div>
      <div class="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="progressBarClass"
          :style="{ width: `${phase.progress}%` }"
        ></div>
      </div>
    </div>

    <!-- Indeterminate Progress (for creating_features phase) -->
    <div v-else-if="phase.phase === 'creating_features'" class="mt-3">
      <div class="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
        <div class="h-full w-1/3 animate-shimmer rounded-full bg-gradient-to-r from-brand-400 via-brand-500 to-brand-400"></div>
      </div>
      <p class="mt-2 text-xs text-center text-gray-500 dark:text-gray-400">
        The agent is analyzing your app specification and generating detailed test cases.
        This process typically takes 10-20 minutes.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentPhaseInfo } from '@/api/client'

const props = defineProps<{
  phase: AgentPhaseInfo | null
  agentStatus: 'stopped' | 'running' | 'paused' | 'crashed'
}>()

const showIndicator = computed(() => {
  if (!props.phase) return false
  // Show for active phases when agent is running
  if (props.agentStatus === 'running') {
    return ['creating_features', 'implementing', 'complete'].includes(props.phase.phase)
  }
  // Show complete phase even when stopped
  return props.phase.phase === 'complete'
})

const phaseTitle = computed(() => {
  if (!props.phase) return ''
  const titles: Record<string, string> = {
    idle: 'Idle',
    initializing: 'Initializing',
    creating_features: 'Creating Features',
    implementing: 'Implementing',
    complete: 'Complete',
  }
  return titles[props.phase.phase] || props.phase.phase
})

const timeEstimate = computed(() => {
  if (!props.phase) return null
  const { estimate_min, estimate_max } = props.phase

  if (estimate_min === null || estimate_max === null) return null
  if (estimate_min === 0 && estimate_max === 0) return null

  if (estimate_min === estimate_max) {
    return `~${estimate_min} min`
  }
  return `${estimate_min}-${estimate_max} min`
})

const containerClass = computed(() => {
  if (!props.phase) return ''
  switch (props.phase.phase) {
    case 'creating_features':
      return 'border-brand-200 bg-brand-50 dark:border-brand-800 dark:bg-brand-900/20'
    case 'implementing':
      return 'border-cyan-200 bg-cyan-50 dark:border-cyan-800 dark:bg-cyan-900/20'
    case 'complete':
      return 'border-success-200 bg-success-50 dark:border-success-800 dark:bg-success-900/20'
    default:
      return 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50'
  }
})

const iconClass = computed(() => {
  if (!props.phase) return ''
  switch (props.phase.phase) {
    case 'creating_features':
      return 'bg-brand-100 text-brand-600 dark:bg-brand-900/50 dark:text-brand-400'
    case 'implementing':
      return 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/50 dark:text-cyan-400'
    case 'complete':
      return 'bg-success-100 text-success-600 dark:bg-success-900/50 dark:text-success-400'
    default:
      return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
  }
})

const titleClass = computed(() => {
  if (!props.phase) return ''
  switch (props.phase.phase) {
    case 'creating_features':
      return 'text-brand-700 dark:text-brand-300'
    case 'implementing':
      return 'text-cyan-700 dark:text-cyan-300'
    case 'complete':
      return 'text-success-700 dark:text-success-300'
    default:
      return 'text-gray-700 dark:text-gray-300'
  }
})

const badgeClass = computed(() => {
  if (!props.phase) return ''
  switch (props.phase.phase) {
    case 'creating_features':
      return 'bg-brand-100 text-brand-700 dark:bg-brand-900/50 dark:text-brand-300'
    case 'implementing':
      return 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/50 dark:text-cyan-300'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  }
})

const progressTextClass = computed(() => {
  if (!props.phase) return ''
  switch (props.phase.phase) {
    case 'implementing':
      return 'text-cyan-600 dark:text-cyan-400'
    case 'complete':
      return 'text-success-600 dark:text-success-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
})

const progressBarClass = computed(() => {
  if (!props.phase) return ''
  if (props.phase.progress === 100) {
    return 'bg-success-500'
  }
  return 'bg-cyan-500'
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(400%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}
</style>
