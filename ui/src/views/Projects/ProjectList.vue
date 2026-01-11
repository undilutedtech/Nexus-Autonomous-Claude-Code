<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Projects'" />

    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white/90">
            Your Projects
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Manage your autonomous coding projects
          </p>
        </div>
        <router-link
          to="/projects/new"
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
          class="group relative rounded-2xl border border-gray-200 bg-white p-5 transition hover:border-brand-300 hover:shadow-md dark:border-gray-800 dark:bg-white/[0.03] dark:hover:border-brand-800"
        >
          <!-- Dropdown Menu Button -->
          <div class="absolute right-3 top-3 z-10">
            <button
              @click.stop="toggleDropdown(project.name)"
              class="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 opacity-0 transition hover:bg-gray-100 group-hover:opacity-100 dark:hover:bg-gray-800"
              :class="{ 'opacity-100 bg-gray-100 dark:bg-gray-800': openDropdown === project.name }"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-if="openDropdown === project.name"
              class="absolute right-0 top-full mt-1 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800"
            >
              <router-link
                :to="`/projects/${encodeURIComponent(project.name)}`"
                class="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                View Details
              </router-link>
              <button
                v-if="project.status !== 'paused'"
                @click.stop="pauseProject(project.name)"
                class="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Pause Project
              </button>
              <button
                v-else
                @click.stop="resumeProject(project.name)"
                class="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Resume Project
              </button>
              <hr class="my-1 border-gray-200 dark:border-gray-700" />
              <button
                @click.stop="confirmUnregister(project)"
                class="flex w-full items-center gap-2 px-4 py-2 text-sm text-warning-600 hover:bg-warning-50 dark:text-warning-400 dark:hover:bg-warning-900/20"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                Unregister (Keep Files)
              </button>
              <button
                @click.stop="confirmDelete(project)"
                class="flex w-full items-center gap-2 px-4 py-2 text-sm text-error-600 hover:bg-error-50 dark:text-error-400 dark:hover:bg-error-900/20"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Project
              </button>
            </div>
          </div>

          <!-- Clickable card content -->
          <router-link
            :to="`/projects/${encodeURIComponent(project.name)}`"
            class="block"
          >
            <div class="mb-4 flex items-start justify-between">
              <div
                class="flex h-12 w-12 items-center justify-center rounded-xl"
                :class="getStatusStyles(project.status).iconBg"
              >
                <svg
                  class="w-6 h-6"
                  :class="getStatusStyles(project.status).iconColor"
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
              <div class="flex items-center gap-2">
                <span
                  v-if="project.status && project.status !== 'active'"
                  class="rounded-full px-2 py-0.5 text-xs font-medium"
                  :class="getStatusStyles(project.status).badge"
                >
                  {{ project.status.charAt(0).toUpperCase() + project.status.slice(1) }}
                </span>
                <span
                  v-if="project.has_spec"
                  class="rounded-full bg-success-100 px-2 py-0.5 text-xs font-medium text-success-700 dark:bg-success-500/10 dark:text-success-400"
                >
                  Has Spec
                </span>
              </div>
            </div>

            <h3
              class="mb-1 text-lg font-semibold text-gray-800 group-hover:text-brand-600 dark:text-white/90 dark:group-hover:text-brand-400"
            >
              {{ project.name }}
            </h3>
            <p class="mb-4 text-sm text-gray-500 dark:text-gray-400 truncate">
              {{ project.path }}
            </p>

            <!-- Progress Bar -->
            <div class="mb-2">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-500 dark:text-gray-400">Progress</span>
                <span class="font-medium text-gray-800 dark:text-white/90">
                  {{ project.stats.passing }}/{{ project.stats.total }}
                </span>
              </div>
              <div class="mt-2 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  class="h-2 rounded-full bg-brand-500 transition-all"
                  :style="{ width: `${project.stats.percentage}%` }"
                ></div>
              </div>
            </div>

            <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
              <span class="flex items-center gap-1">
                <span class="h-2 w-2 rounded-full bg-success-500"></span>
                {{ project.stats.passing }} passing
              </span>
              <span class="flex items-center gap-1">
                <span class="h-2 w-2 rounded-full bg-warning-500"></span>
                {{ project.stats.in_progress }} in progress
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!isLoading && projects.length === 0"
        class="rounded-2xl border border-gray-200 bg-white p-12 text-center dark:border-gray-800 dark:bg-white/[0.03]"
      >
        <div
          class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800"
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
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
            />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-semibold text-gray-800 dark:text-white/90">
          No projects yet
        </h3>
        <p class="mb-6 text-gray-500 dark:text-gray-400">
          Create your first project to get started with autonomous coding
        </p>
        <router-link
          to="/projects/new"
          class="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600"
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
          Create Project
        </router-link>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <Modal v-if="confirmModal.show" @close="closeConfirmModal">
      <template #body>
        <div
          class="relative w-full max-w-[400px] rounded-3xl bg-white p-6 dark:bg-gray-900"
        >
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full"
            :class="confirmModal.type === 'delete' ? 'bg-error-100 dark:bg-error-900/20' : 'bg-warning-100 dark:bg-warning-900/20'"
          >
            <svg
              class="w-8 h-8"
              :class="confirmModal.type === 'delete' ? 'text-error-500' : 'text-warning-500'"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          <h4 class="mb-2 text-center text-xl font-semibold text-gray-800 dark:text-white/90">
            {{ confirmModal.title }}
          </h4>
          <p class="mb-6 text-center text-sm text-gray-500 dark:text-gray-400">
            {{ confirmModal.message }}
          </p>

          <div v-if="confirmModal.type === 'delete'" class="mb-6 rounded-lg bg-error-50 p-3 text-sm text-error-700 dark:bg-error-900/20 dark:text-error-400">
            <strong>Warning:</strong> This will permanently delete all project files from disk!
          </div>

          <div v-if="actionError" class="mb-4 rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
            {{ actionError }}
          </div>

          <div class="flex gap-3">
            <button
              type="button"
              @click="closeConfirmModal"
              :disabled="actionLoading"
              class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="executeConfirmAction"
              :disabled="actionLoading"
              class="flex-1 rounded-lg px-4 py-2.5 text-sm font-medium text-white transition disabled:opacity-50"
              :class="confirmModal.type === 'delete' ? 'bg-error-500 hover:bg-error-600' : 'bg-warning-500 hover:bg-warning-600'"
            >
              {{ actionLoading ? 'Processing...' : confirmModal.confirmText }}
            </button>
          </div>
        </div>
      </template>
    </Modal>

    <!-- New Project Modal -->
    <Modal v-if="showNewProject" @close="closeNewProjectModal">
      <template #body>
        <div
          class="relative w-full max-w-[600px] rounded-3xl bg-white p-6 dark:bg-gray-900"
        >
          <button
            @click="closeNewProjectModal"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <h4 class="mb-6 text-xl font-semibold text-gray-800 dark:text-white/90">
            Create New Project
          </h4>

          <form @submit.prevent="handleCreateProject" class="space-y-5">
            <!-- Project Name -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Project Name
              </label>
              <input
                v-model="newProjectForm.name"
                type="text"
                placeholder="my-awesome-project"
                pattern="^[a-zA-Z0-9_-]{1,50}$"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                required
              />
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Letters, numbers, hyphens, and underscores only (1-50 characters)
              </p>
            </div>

            <!-- Project Path -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Project Location
              </label>
              <div class="flex gap-2">
                <input
                  v-model="newProjectForm.path"
                  type="text"
                  placeholder="/home/user/projects/my-project"
                  class="h-11 flex-1 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                  required
                />
                <button
                  type="button"
                  @click="showFolderBrowser = !showFolderBrowser"
                  class="flex h-11 w-11 items-center justify-center rounded-lg border border-gray-300 transition hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800"
                  :class="{ 'bg-brand-50 border-brand-300 dark:bg-brand-900/20 dark:border-brand-700': showFolderBrowser }"
                >
                  <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Folder Browser -->
            <div v-if="showFolderBrowser" class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <!-- Browser Header -->
              <div class="flex items-center gap-2 border-b border-gray-200 bg-gray-50 px-3 py-2 dark:border-gray-700 dark:bg-gray-800">
                <button
                  type="button"
                  @click="navigateToParent"
                  :disabled="!browserData?.parent_path"
                  class="flex h-8 w-8 items-center justify-center rounded transition hover:bg-gray-200 disabled:opacity-50 dark:hover:bg-gray-700"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button
                  type="button"
                  @click="navigateToHome"
                  class="flex h-8 w-8 items-center justify-center rounded transition hover:bg-gray-200 dark:hover:bg-gray-700"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </button>
                <span class="flex-1 truncate text-sm text-gray-600 dark:text-gray-400">
                  {{ browserData?.current_path || 'Loading...' }}
                </span>
                <button
                  type="button"
                  @click="showNewFolderInput = true"
                  class="flex h-8 items-center gap-1 rounded px-2 text-sm text-brand-600 transition hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-brand-900/20"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  New Folder
                </button>
              </div>

              <!-- New Folder Input -->
              <div v-if="showNewFolderInput" class="flex items-center gap-2 border-b border-gray-200 bg-brand-50 px-3 py-2 dark:border-gray-700 dark:bg-brand-900/20">
                <svg class="w-5 h-5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                </svg>
                <input
                  v-model="newFolderName"
                  type="text"
                  placeholder="New folder name"
                  class="h-8 flex-1 rounded border border-gray-300 bg-white px-2 text-sm dark:border-gray-600 dark:bg-gray-800"
                  @keyup.enter="createNewFolder"
                  @keyup.esc="showNewFolderInput = false; newFolderName = ''"
                  ref="newFolderInput"
                />
                <button
                  type="button"
                  @click="createNewFolder"
                  :disabled="!newFolderName.trim()"
                  class="rounded bg-brand-500 px-3 py-1 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
                >
                  Create
                </button>
                <button
                  type="button"
                  @click="showNewFolderInput = false; newFolderName = ''"
                  class="rounded px-2 py-1 text-sm text-gray-600 transition hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
              </div>

              <!-- Folder List -->
              <div class="max-h-60 overflow-y-auto">
                <div v-if="browserLoading" class="flex items-center justify-center py-8">
                  <svg class="animate-spin h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <div v-else-if="browserData?.entries.length === 0" class="py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                  No subdirectories
                </div>
                <div v-else>
                  <button
                    v-for="entry in browserData?.entries"
                    :key="entry.path"
                    type="button"
                    @click="navigateToFolder(entry.path)"
                    @dblclick="selectFolder(entry.path)"
                    class="flex w-full items-center gap-3 px-3 py-2 text-left transition hover:bg-gray-100 dark:hover:bg-gray-800"
                    :class="{ 'bg-brand-50 dark:bg-brand-900/20': newProjectForm.path === entry.path }"
                  >
                    <svg class="w-5 h-5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    <span class="flex-1 truncate text-sm text-gray-800 dark:text-white/90">{{ entry.name }}</span>
                    <svg v-if="entry.has_children" class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Select Current Folder -->
              <div class="border-t border-gray-200 bg-gray-50 px-3 py-2 dark:border-gray-700 dark:bg-gray-800">
                <button
                  type="button"
                  @click="selectCurrentFolder"
                  class="w-full rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600"
                >
                  Select This Folder
                </button>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="createError" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
              {{ createError }}
            </div>

            <!-- Actions -->
            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="closeNewProjectModal"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isCreating || !newProjectForm.name || !newProjectForm.path"
                class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
              >
                {{ isCreating ? 'Creating...' : 'Create Project' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import Modal from '@/components/profile/Modal.vue'
import {
  projectsAPI,
  filesystemAPI,
  type ProjectSummary,
  type DirectoryListResponse,
} from '@/api/client'

const router = useRouter()
const route = useRoute()

// Projects list
const projects = ref<ProjectSummary[]>([])
const isLoading = ref(true)

// Dropdown state
const openDropdown = ref<string | null>(null)

// Confirmation modal state
const confirmModal = ref({
  show: false,
  type: 'delete' as 'delete' | 'unregister',
  title: '',
  message: '',
  confirmText: '',
  projectName: '',
})
const actionLoading = ref(false)
const actionError = ref('')

// New project modal state
const showNewProject = ref(false)
const isCreating = ref(false)
const createError = ref('')
const newProjectForm = ref({
  name: '',
  path: '',
})

// Folder browser state
const showFolderBrowser = ref(false)
const browserLoading = ref(false)
const browserData = ref<DirectoryListResponse | null>(null)
const showNewFolderInput = ref(false)
const newFolderName = ref('')
const newFolderInput = ref<HTMLInputElement | null>(null)

// Click outside handler to close dropdown
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.absolute.right-3')) {
    openDropdown.value = null
  }
}

onMounted(async () => {
  await fetchProjects()

  // Check for ?new=true query parameter to auto-open the new project modal
  if (route.query.new === 'true') {
    showNewProject.value = true
    // Clear the query parameter from URL without navigation
    router.replace({ path: route.path, query: {} })
  }

  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Dropdown toggle
function toggleDropdown(projectName: string) {
  openDropdown.value = openDropdown.value === projectName ? null : projectName
}

// Get status-based styles
function getStatusStyles(status?: string) {
  switch (status) {
    case 'paused':
      return {
        iconBg: 'bg-warning-100 dark:bg-warning-500/10',
        iconColor: 'text-warning-500',
        badge: 'bg-warning-100 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400',
      }
    case 'finished':
      return {
        iconBg: 'bg-success-100 dark:bg-success-500/10',
        iconColor: 'text-success-500',
        badge: 'bg-success-100 text-success-700 dark:bg-success-500/10 dark:text-success-400',
      }
    case 'archived':
      return {
        iconBg: 'bg-gray-100 dark:bg-gray-500/10',
        iconColor: 'text-gray-500',
        badge: 'bg-gray-100 text-gray-700 dark:bg-gray-500/10 dark:text-gray-400',
      }
    default:
      return {
        iconBg: 'bg-brand-100 dark:bg-brand-500/10',
        iconColor: 'text-brand-500',
        badge: 'bg-brand-100 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400',
      }
  }
}

// Project actions
async function pauseProject(name: string) {
  openDropdown.value = null
  try {
    await projectsAPI.pause(name)
    await fetchProjects()
  } catch (err) {
    console.error('Failed to pause project:', err)
  }
}

async function resumeProject(name: string) {
  openDropdown.value = null
  try {
    await projectsAPI.resume(name)
    await fetchProjects()
  } catch (err) {
    console.error('Failed to resume project:', err)
  }
}

function confirmDelete(project: ProjectSummary) {
  openDropdown.value = null
  confirmModal.value = {
    show: true,
    type: 'delete',
    title: 'Delete Project',
    message: `Are you sure you want to delete "${project.name}"? This action cannot be undone.`,
    confirmText: 'Delete',
    projectName: project.name,
  }
  actionError.value = ''
}

function confirmUnregister(project: ProjectSummary) {
  openDropdown.value = null
  confirmModal.value = {
    show: true,
    type: 'unregister',
    title: 'Unregister Project',
    message: `Remove "${project.name}" from Nexus? The project files at ${project.path} will be kept.`,
    confirmText: 'Unregister',
    projectName: project.name,
  }
  actionError.value = ''
}

function closeConfirmModal() {
  confirmModal.value.show = false
  actionError.value = ''
}

async function executeConfirmAction() {
  actionLoading.value = true
  actionError.value = ''

  try {
    const deleteFiles = confirmModal.value.type === 'delete'
    await projectsAPI.delete(confirmModal.value.projectName, deleteFiles)
    closeConfirmModal()
    await fetchProjects()
  } catch (err: any) {
    actionError.value = err.message || 'Failed to perform action'
  } finally {
    actionLoading.value = false
  }
}

async function fetchProjects() {
  isLoading.value = true
  try {
    projects.value = await projectsAPI.list()
  } catch (err) {
    console.error('Failed to fetch projects:', err)
  } finally {
    isLoading.value = false
  }
}

// Watch for folder browser toggle to load initial data
watch(showFolderBrowser, async (show) => {
  if (show && !browserData.value) {
    await loadBrowserDirectory()
  }
})

// Watch for new folder input to focus
watch(showNewFolderInput, async (show) => {
  if (show) {
    await nextTick()
    newFolderInput.value?.focus()
  }
})

// Modal functions
function closeNewProjectModal() {
  showNewProject.value = false
  showFolderBrowser.value = false
  showNewFolderInput.value = false
  newFolderName.value = ''
  createError.value = ''
  newProjectForm.value = { name: '', path: '' }
  browserData.value = null
}

async function handleCreateProject() {
  if (!newProjectForm.value.name || !newProjectForm.value.path) return

  isCreating.value = true
  createError.value = ''

  try {
    const project = await projectsAPI.create({
      name: newProjectForm.value.name,
      path: newProjectForm.value.path,
    })

    // Refresh projects list
    await fetchProjects()

    // Close modal and navigate to the new project
    closeNewProjectModal()
    router.push(`/projects/${encodeURIComponent(project.name)}`)
  } catch (err: any) {
    createError.value = err.message || 'Failed to create project'
  } finally {
    isCreating.value = false
  }
}

// Folder browser functions
async function loadBrowserDirectory(path?: string) {
  browserLoading.value = true
  try {
    browserData.value = await filesystemAPI.list(path)
  } catch (err: any) {
    console.error('Failed to load directory:', err)
    createError.value = err.message || 'Failed to load directory'
  } finally {
    browserLoading.value = false
  }
}

async function navigateToFolder(path: string) {
  await loadBrowserDirectory(path)
}

async function navigateToParent() {
  if (browserData.value?.parent_path) {
    await loadBrowserDirectory(browserData.value.parent_path)
  }
}

async function navigateToHome() {
  try {
    const home = await filesystemAPI.getHome()
    await loadBrowserDirectory(home.path)
  } catch (err) {
    console.error('Failed to navigate to home:', err)
  }
}

function selectFolder(path: string) {
  newProjectForm.value.path = path
  showFolderBrowser.value = false
}

function selectCurrentFolder() {
  if (browserData.value?.current_path) {
    newProjectForm.value.path = browserData.value.current_path
    showFolderBrowser.value = false
  }
}

async function createNewFolder() {
  if (!newFolderName.value.trim() || !browserData.value?.current_path) return

  try {
    const result = await filesystemAPI.createDirectory(
      browserData.value.current_path,
      newFolderName.value.trim()
    )

    // Navigate to the new folder
    await loadBrowserDirectory(result.path)
    newProjectForm.value.path = result.path

    // Reset input
    showNewFolderInput.value = false
    newFolderName.value = ''
  } catch (err: any) {
    createError.value = err.message || 'Failed to create folder'
  }
}
</script>
