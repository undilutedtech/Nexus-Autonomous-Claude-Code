<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Paused Projects'" />

    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white/90">
            Paused Projects
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Projects that have been paused and can be resumed
          </p>
        </div>
        <router-link
          to="/projects"
          class="inline-flex items-center gap-2 text-sm text-brand-500 hover:text-brand-600"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to All Projects
        </router-link>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <svg class="animate-spin h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Project Grid -->
      <div v-else-if="projects.length > 0" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="project in projects"
          :key="project.name"
          class="rounded-2xl border border-warning-200 bg-white p-5 dark:border-warning-800 dark:bg-white/[0.03]"
        >
          <div class="mb-4 flex items-start justify-between">
            <div
              class="flex h-12 w-12 items-center justify-center rounded-xl bg-warning-100 dark:bg-warning-500/10"
            >
              <svg
                class="w-6 h-6 text-warning-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <span
              class="rounded-full bg-warning-100 px-2 py-0.5 text-xs font-medium text-warning-700 dark:bg-warning-500/10 dark:text-warning-400"
            >
              Paused
            </span>
          </div>

          <h3 class="mb-1 text-lg font-semibold text-gray-800 dark:text-white/90">
            {{ project.name }}
          </h3>
          <p class="mb-4 text-sm text-gray-500 dark:text-gray-400 truncate">
            {{ project.path }}
          </p>

          <!-- Progress Bar -->
          <div class="mb-4">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">Progress</span>
              <span class="font-medium text-gray-800 dark:text-white/90">
                {{ project.stats.passing }}/{{ project.stats.total }}
              </span>
            </div>
            <div class="mt-2 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
              <div
                class="h-2 rounded-full bg-warning-500 transition-all"
                :style="{ width: `${project.stats.percentage}%` }"
              ></div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button
              @click="resumeProject(project.name)"
              :disabled="actionLoading === project.name"
              class="flex-1 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
            >
              {{ actionLoading === project.name ? 'Resuming...' : 'Resume' }}
            </button>
            <router-link
              :to="`/projects/${encodeURIComponent(project.name)}`"
              class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              View
            </router-link>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!isLoading && projects.length === 0"
        class="rounded-2xl border border-gray-200 bg-white p-12 text-center dark:border-gray-800 dark:bg-white/[0.03]"
      >
        <div
          class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-warning-100 dark:bg-warning-900/20"
        >
          <svg
            class="w-8 h-8 text-warning-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-semibold text-gray-800 dark:text-white/90">
          No paused projects
        </h3>
        <p class="mb-6 text-gray-500 dark:text-gray-400">
          All your projects are either active or finished
        </p>
        <router-link
          to="/projects"
          class="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600"
        >
          View All Projects
        </router-link>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import { projectsAPI, type ProjectSummary } from '@/api/client'

const projects = ref<ProjectSummary[]>([])
const isLoading = ref(true)
const actionLoading = ref<string | null>(null)

onMounted(async () => {
  await fetchProjects()
})

async function fetchProjects() {
  isLoading.value = true
  try {
    projects.value = await projectsAPI.getByStatus('paused')
  } catch (err) {
    console.error('Failed to fetch paused projects:', err)
  } finally {
    isLoading.value = false
  }
}

async function resumeProject(name: string) {
  actionLoading.value = name
  try {
    await projectsAPI.resume(name)
    // Refresh the list
    await fetchProjects()
  } catch (err) {
    console.error('Failed to resume project:', err)
  } finally {
    actionLoading.value = null
  }
}
</script>
