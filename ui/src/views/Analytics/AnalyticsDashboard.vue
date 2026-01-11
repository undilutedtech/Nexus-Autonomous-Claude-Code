<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Analytics'" />

    <div class="space-y-6">
      <!-- Header -->
      <div>
        <h2 class="text-xl font-semibold text-gray-800 dark:text-white/90">
          Usage Analytics
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Token usage, costs, and performance metrics across all projects
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <svg class="animate-spin h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <div v-else class="space-y-6">
        <!-- Summary Stats -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <!-- Total Cost -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Total Cost</p>
                <p class="mt-1 text-2xl font-semibold text-gray-800 dark:text-white/90">
                  ${{ stats?.total_cost_usd?.toFixed(2) || '0.00' }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-success-100 dark:bg-success-500/10">
                <svg class="w-6 h-6 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Total Tokens -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Total Tokens</p>
                <p class="mt-1 text-2xl font-semibold text-brand-600 dark:text-brand-400">
                  {{ formatNumber(stats?.total_tokens || 0) }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-500/10">
                <svg class="w-6 h-6 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Total Sessions -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Total Sessions</p>
                <p class="mt-1 text-2xl font-semibold text-warning-600 dark:text-warning-400">
                  {{ stats?.total_sessions || 0 }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-warning-100 dark:bg-warning-500/10">
                <svg class="w-6 h-6 text-warning-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Projects with Usage -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Projects with Usage</p>
                <p class="mt-1 text-2xl font-semibold text-gray-600 dark:text-gray-400">
                  {{ stats?.total_projects_with_usage || 0 }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-700">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Token Breakdown -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <!-- Token Distribution -->
          <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
            <h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
              Token Distribution
            </h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500 dark:text-gray-400">Input Tokens</span>
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ formatNumber(stats?.total_input_tokens || 0) }}
                </span>
              </div>
              <div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  class="h-2 rounded-full bg-brand-500"
                  :style="{ width: `${inputTokenPercentage}%` }"
                ></div>
              </div>

              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500 dark:text-gray-400">Output Tokens</span>
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ formatNumber(stats?.total_output_tokens || 0) }}
                </span>
              </div>
              <div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  class="h-2 rounded-full bg-success-500"
                  :style="{ width: `${outputTokenPercentage}%` }"
                ></div>
              </div>

              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500 dark:text-gray-400">Cache Read Tokens</span>
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ formatNumber(stats?.total_cache_read_tokens || 0) }}
                </span>
              </div>
              <div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  class="h-2 rounded-full bg-warning-500"
                  :style="{ width: `${cacheReadPercentage}%` }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Averages -->
          <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
            <h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
              Averages
            </h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <span class="text-sm text-gray-500 dark:text-gray-400">Avg Cost per Project</span>
                <span class="text-lg font-semibold text-gray-800 dark:text-white/90">
                  ${{ stats?.avg_cost_per_project?.toFixed(2) || '0.00' }}
                </span>
              </div>
              <div class="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <span class="text-sm text-gray-500 dark:text-gray-400">Avg Sessions per Project</span>
                <span class="text-lg font-semibold text-gray-800 dark:text-white/90">
                  {{ stats?.avg_sessions_per_project?.toFixed(1) || '0' }}
                </span>
              </div>
              <div class="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <span class="text-sm text-gray-500 dark:text-gray-400">Total Runtime</span>
                <span class="text-lg font-semibold text-gray-800 dark:text-white/90">
                  {{ formatDuration(stats?.total_duration_ms || 0) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Per-Project Usage -->
        <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
          <h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
            Usage by Project
          </h3>
          <div v-if="stats?.projects?.length === 0" class="py-8 text-center text-gray-500 dark:text-gray-400">
            No usage data available yet. Start running agents to see statistics.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="pb-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">Project</th>
                  <th class="pb-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">Status</th>
                  <th class="pb-3 text-right text-sm font-medium text-gray-500 dark:text-gray-400">Sessions</th>
                  <th class="pb-3 text-right text-sm font-medium text-gray-500 dark:text-gray-400">Tokens</th>
                  <th class="pb-3 text-right text-sm font-medium text-gray-500 dark:text-gray-400">Cost</th>
                  <th class="pb-3 text-right text-sm font-medium text-gray-500 dark:text-gray-400">Runtime</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="project in stats?.projects"
                  :key="project.name"
                  class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                >
                  <td class="py-3">
                    <router-link
                      :to="`/projects/${project.name}`"
                      class="font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
                    >
                      {{ project.name }}
                    </router-link>
                  </td>
                  <td class="py-3">
                    <span
                      :class="[
                        'rounded-full px-2 py-0.5 text-xs font-medium',
                        project.status === 'active' ? 'bg-success-100 text-success-600 dark:bg-success-900/20 dark:text-success-400' :
                        project.status === 'paused' ? 'bg-warning-100 text-warning-600 dark:bg-warning-900/20 dark:text-warning-400' :
                        'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                      ]"
                    >
                      {{ project.status }}
                    </span>
                  </td>
                  <td class="py-3 text-right text-gray-600 dark:text-gray-400">
                    {{ project.sessions }}
                  </td>
                  <td class="py-3 text-right text-gray-600 dark:text-gray-400">
                    {{ formatNumber(project.tokens) }}
                  </td>
                  <td class="py-3 text-right font-medium text-gray-800 dark:text-white/90">
                    ${{ project.cost_usd.toFixed(2) }}
                  </td>
                  <td class="py-3 text-right text-gray-600 dark:text-gray-400">
                    {{ project.duration_hours }}h
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import { analyticsAPI, type AggregateUsageStats } from '@/api/client'

const stats = ref<AggregateUsageStats | null>(null)
const isLoading = ref(true)

onMounted(async () => {
  await fetchStats()
})

async function fetchStats() {
  isLoading.value = true
  try {
    stats.value = await analyticsAPI.getUsage()
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  } finally {
    isLoading.value = false
  }
}

const inputTokenPercentage = computed(() => {
  if (!stats.value?.total_tokens) return 0
  return (stats.value.total_input_tokens / stats.value.total_tokens) * 100
})

const outputTokenPercentage = computed(() => {
  if (!stats.value?.total_tokens) return 0
  return (stats.value.total_output_tokens / stats.value.total_tokens) * 100
})

const cacheReadPercentage = computed(() => {
  if (!stats.value?.total_tokens) return 0
  return (stats.value.total_cache_read_tokens / stats.value.total_tokens) * 100
})

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

function formatDuration(ms: number): string {
  const hours = Math.floor(ms / 3600000)
  const minutes = Math.floor((ms % 3600000) / 60000)
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}
</script>
