<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Projects Overview'" />

    <div class="space-y-6">
      <!-- Header -->
      <div>
        <h2 class="text-xl font-semibold text-gray-800 dark:text-white/90">
          Projects Overview
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Aggregate statistics across all your projects
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
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <!-- Total Projects -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Total Projects</p>
                <p class="mt-1 text-2xl font-semibold text-gray-800 dark:text-white/90">
                  {{ stats?.total_projects || 0 }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-500/10">
                <svg class="w-6 h-6 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Active Projects -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Active Projects</p>
                <p class="mt-1 text-2xl font-semibold text-success-600 dark:text-success-400">
                  {{ stats?.active_projects || 0 }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-success-100 dark:bg-success-500/10">
                <svg class="w-6 h-6 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Paused Projects -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Paused Projects</p>
                <p class="mt-1 text-2xl font-semibold text-warning-600 dark:text-warning-400">
                  {{ stats?.paused_projects || 0 }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-warning-100 dark:bg-warning-500/10">
                <svg class="w-6 h-6 text-warning-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Finished Projects -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Finished Projects</p>
                <p class="mt-1 text-2xl font-semibold text-gray-600 dark:text-gray-400">
                  {{ stats?.finished_projects || 0 }}
                </p>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-700">
                <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Active Projects Progress -->
        <div class="rounded-2xl border border-brand-200 bg-brand-50/50 p-6 dark:border-brand-800 dark:bg-brand-900/10">
          <div class="flex items-center gap-2 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-500/20">
              <svg class="w-4 h-4 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              Active Projects Progress
            </h3>
          </div>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-500 dark:text-gray-400">Features Completed</span>
              <span class="text-lg font-semibold text-gray-800 dark:text-white/90">
                {{ stats?.active_passing || 0 }} / {{ stats?.active_features || 0 }}
              </span>
            </div>
            <div class="h-4 w-full rounded-full bg-gray-200 dark:bg-gray-700">
              <div
                class="h-4 rounded-full bg-brand-500 transition-all duration-500"
                :style="{ width: `${stats?.active_percentage || 0}%` }"
              ></div>
            </div>
            <div class="flex items-center justify-between">
              <p class="text-2xl font-bold text-brand-500">
                {{ stats?.active_percentage?.toFixed(1) || 0 }}%
              </p>
              <div class="text-right">
                <p class="text-sm text-gray-500 dark:text-gray-400">Currently In Progress</p>
                <p class="text-lg font-semibold text-warning-600 dark:text-warning-400">
                  {{ stats?.active_in_progress || 0 }} features
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Overall Progress (All Projects) -->
        <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
          <h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
            All Projects Progress
          </h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-500 dark:text-gray-400">Total Features Completed</span>
              <span class="text-lg font-semibold text-gray-800 dark:text-white/90">
                {{ stats?.total_passing || 0 }} / {{ stats?.total_features || 0 }}
              </span>
            </div>
            <div class="h-3 w-full rounded-full bg-gray-200 dark:bg-gray-700">
              <div
                class="h-3 rounded-full bg-gray-400 dark:bg-gray-500 transition-all duration-500"
                :style="{ width: `${stats?.overall_percentage || 0}%` }"
              ></div>
            </div>
            <p class="text-center text-xl font-semibold text-gray-600 dark:text-gray-400">
              {{ stats?.overall_percentage?.toFixed(1) || 0 }}%
            </p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <router-link
            to="/projects"
            class="flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-5 transition hover:border-brand-300 hover:shadow-md dark:border-gray-800 dark:bg-white/[0.03] dark:hover:border-brand-800"
          >
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-500/10">
              <svg class="w-6 h-6 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-gray-800 dark:text-white/90">All Projects</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">View and manage all projects</p>
            </div>
          </router-link>

          <router-link
            to="/projects/paused"
            class="flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-5 transition hover:border-warning-300 hover:shadow-md dark:border-gray-800 dark:bg-white/[0.03] dark:hover:border-warning-800"
          >
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-warning-100 dark:bg-warning-500/10">
              <svg class="w-6 h-6 text-warning-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-gray-800 dark:text-white/90">Paused Projects</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">Resume paused work</p>
            </div>
          </router-link>

          <router-link
            to="/projects/finished"
            class="flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-5 transition hover:border-success-300 hover:shadow-md dark:border-gray-800 dark:bg-white/[0.03] dark:hover:border-success-800"
          >
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-success-100 dark:bg-success-500/10">
              <svg class="w-6 h-6 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-gray-800 dark:text-white/90">Finished Projects</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">View completed work</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import { projectsAPI, type ProjectOverviewStats } from '@/api/client'

const stats = ref<ProjectOverviewStats | null>(null)
const isLoading = ref(true)

onMounted(async () => {
  await fetchOverview()
})

async function fetchOverview() {
  isLoading.value = true
  try {
    stats.value = await projectsAPI.getOverview()
  } catch (err) {
    console.error('Failed to fetch overview:', err)
  } finally {
    isLoading.value = false
  }
}
</script>
