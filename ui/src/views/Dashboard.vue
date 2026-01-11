<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Dashboard'" />

    <div class="grid grid-cols-12 gap-4 md:gap-6">
      <!-- Welcome Card -->
      <div class="col-span-12">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
        >
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 class="text-xl font-semibold text-gray-800 dark:text-white/90 mb-1">
                Welcome back, {{ fullName }}!
              </h2>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Here's an overview of your autonomous coding projects.
              </p>
            </div>
            <router-link
              to="/projects"
              class="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              New Project
            </router-link>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="col-span-12 md:col-span-4">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <div class="flex items-center gap-4">
            <div
              class="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-500/10"
            >
              <svg
                class="w-6 h-6 text-brand-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Total Projects</p>
              <p class="text-2xl font-bold text-gray-800 dark:text-white/90">0</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-span-12 md:col-span-4">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <div class="flex items-center gap-4">
            <div
              class="flex h-12 w-12 items-center justify-center rounded-xl bg-success-100 dark:bg-success-500/10"
            >
              <svg
                class="w-6 h-6 text-success-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Features Complete</p>
              <p class="text-2xl font-bold text-gray-800 dark:text-white/90">0</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-span-12 md:col-span-4">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <div class="flex items-center gap-4">
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
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">In Progress</p>
              <p class="text-2xl font-bold text-gray-800 dark:text-white/90">0</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="col-span-12 lg:col-span-6">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
        >
          <h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
            Quick Actions
          </h3>
          <div class="space-y-3">
            <router-link
              to="/projects"
              class="flex items-center gap-3 rounded-lg border border-gray-200 p-4 transition hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-white/[0.03]"
            >
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-100 dark:bg-brand-500/10"
              >
                <svg
                  class="w-5 h-5 text-brand-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                  />
                </svg>
              </div>
              <div class="flex-1">
                <p class="font-medium text-gray-800 dark:text-white/90">View Projects</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Manage your autonomous coding projects
                </p>
              </div>
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </router-link>

            <router-link
              to="/profile"
              class="flex items-center gap-3 rounded-lg border border-gray-200 p-4 transition hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-white/[0.03]"
            >
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700"
              >
                <svg
                  class="w-5 h-5 text-gray-500 dark:text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <div class="flex-1">
                <p class="font-medium text-gray-800 dark:text-white/90">Profile Settings</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Update your profile and security settings
                </p>
              </div>
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="col-span-12 lg:col-span-6">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
        >
          <h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
            Recent Activity
          </h3>
          <div class="flex flex-col items-center justify-center py-8 text-center">
            <div
              class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800"
            >
              <svg
                class="w-8 h-8 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <p class="text-gray-500 dark:text-gray-400">No recent activity</p>
            <p class="mt-1 text-sm text-gray-400 dark:text-gray-500">
              Start a project to see activity here
            </p>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import { useAuth } from '@/composables/useAuth'

const { fullName } = useAuth()
</script>
