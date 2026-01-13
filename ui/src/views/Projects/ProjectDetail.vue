<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="projectName" />

    <div class="space-y-6">
      <!-- Project Header -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div class="flex items-center gap-4">
            <div
              class="flex h-14 w-14 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-500/10"
            >
              <svg
                class="w-7 h-7 text-brand-500"
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
              <h2 class="text-xl font-semibold text-gray-800 dark:text-white/90">
                {{ projectName }}
              </h2>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ project?.path || 'Loading...' }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <!-- Project Status Badge -->
            <span
              v-if="project?.status && project.status !== 'active'"
              :class="[
                'rounded-full px-2.5 py-0.5 text-xs font-medium',
                project.status === 'paused' ? 'bg-warning-100 text-warning-600 dark:bg-warning-900/20 dark:text-warning-400' :
                project.status === 'finished' ? 'bg-success-100 text-success-600 dark:bg-success-900/20 dark:text-success-400' :
                'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
              ]"
            >
              {{ project.status }}
            </span>

            <!-- Agent Status Indicator -->
            <div class="flex items-center gap-2">
              <span
                :class="[
                  'flex h-2.5 w-2.5 rounded-full',
                  isAgentRunning ? 'bg-success-500 animate-pulse' :
                  isAgentPaused ? 'bg-warning-500' :
                  'bg-gray-400'
                ]"
              ></span>
              <span class="text-sm text-gray-600 dark:text-gray-400 capitalize">
                {{ displayedAgentStatus }}
              </span>
              <span v-if="isConnected" class="text-xs text-success-500" title="WebSocket connected">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.05 3.636a1 1 0 010 1.414 7 7 0 000 9.9 1 1 0 11-1.414 1.414 9 9 0 010-12.728 1 1 0 011.414 0zm9.9 0a1 1 0 011.414 0 9 9 0 010 12.728 1 1 0 11-1.414-1.414 7 7 0 000-9.9 1 1 0 010-1.414zM7.879 6.464a1 1 0 010 1.414 3 3 0 000 4.243 1 1 0 11-1.415 1.414 5 5 0 010-7.07 1 1 0 011.415 0zm4.242 0a1 1 0 011.415 0 5 5 0 010 7.072 1 1 0 01-1.415-1.415 3 3 0 000-4.242 1 1 0 010-1.415zM10 9a1 1 0 011 1v.01a1 1 0 11-2 0V10a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
              </span>
            </div>

            <!-- Settings Button -->
            <button
              @click="showConfigModal = true"
              class="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 text-gray-600 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
              title="Project Settings"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>

            <!-- Project Lifecycle Dropdown -->
            <div class="relative" ref="projectMenuRef">
              <button
                @click="showProjectMenu = !showProjectMenu"
                :disabled="projectActionLoading"
                class="flex h-9 items-center gap-1 rounded-lg border border-gray-300 px-3 text-sm text-gray-600 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800 disabled:opacity-50"
              >
                <span>Actions</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div
                v-if="showProjectMenu"
                class="absolute right-0 top-full mt-1 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800 z-50"
              >
                <button
                  v-if="project?.status === 'active'"
                  @click="handlePauseProject(); showProjectMenu = false"
                  class="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  <svg class="w-4 h-4 text-warning-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Pause Project
                </button>
                <button
                  v-if="project?.status === 'paused'"
                  @click="handleResumeProject(); showProjectMenu = false"
                  class="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  <svg class="w-4 h-4 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Resume Project
                </button>
                <button
                  v-if="project?.status !== 'finished'"
                  @click="handleFinishProject(); showProjectMenu = false"
                  class="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  <svg class="w-4 h-4 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Mark as Finished
                </button>
                <div class="my-1 border-t border-gray-200 dark:border-gray-700"></div>
                <button
                  @click="handleResetProject(); showProjectMenu = false"
                  class="flex w-full items-center gap-2 px-4 py-2 text-sm text-warning-600 hover:bg-warning-50 dark:text-warning-400 dark:hover:bg-warning-900/20"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Reset Progress
                </button>
                <button
                  @click="handleRestartProject(); showProjectMenu = false"
                  class="flex w-full items-center gap-2 px-4 py-2 text-sm text-error-600 hover:bg-error-50 dark:text-error-400 dark:hover:bg-error-900/20"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Restart Project
                </button>
              </div>
            </div>

            <!-- YOLO Mode Toggle -->
            <label
              v-if="isAgentStopped"
              class="flex items-center gap-2 cursor-pointer"
              title="YOLO Mode: Skip testing for faster prototyping"
            >
              <input
                type="checkbox"
                v-model="yoloMode"
                class="sr-only peer"
              />
              <div class="relative w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-brand-300 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-600 peer-checked:bg-warning-500"></div>
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">YOLO</span>
            </label>

            <!-- Assistant Button -->
            <button
              @click="toggleAssistant"
              :class="[
                'inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition',
                showAssistant
                  ? 'border-brand-500 bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:border-brand-400 dark:text-brand-400'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800'
              ]"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              Assistant
            </button>

            <!-- Agent Control Buttons -->
            <template v-if="isAgentStopped">
              <button
                @click="handleStartAgent"
                :disabled="agentActionLoading"
                class="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="agentActionLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Start Agent
              </button>
            </template>

            <template v-else-if="isAgentRunning">
              <button
                @click="handlePauseAgent"
                :disabled="agentActionLoading"
                class="inline-flex items-center gap-2 rounded-lg border border-warning-300 bg-warning-50 px-4 py-2 text-sm font-medium text-warning-600 transition hover:bg-warning-100 dark:border-warning-700 dark:bg-warning-900/20 dark:text-warning-400 dark:hover:bg-warning-900/30 disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Pause
              </button>
              <button
                @click="handleStopAgent"
                :disabled="agentActionLoading"
                class="inline-flex items-center gap-2 rounded-lg border border-error-300 bg-error-50 px-4 py-2 text-sm font-medium text-error-600 transition hover:bg-error-100 dark:border-error-700 dark:bg-error-900/20 dark:text-error-400 dark:hover:bg-error-900/30 disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
                Stop
              </button>
            </template>

            <template v-else-if="isAgentPaused">
              <button
                @click="handleResumeAgent"
                :disabled="agentActionLoading"
                class="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Resume
              </button>
              <button
                @click="handleStopAgent"
                :disabled="agentActionLoading"
                class="inline-flex items-center gap-2 rounded-lg border border-error-300 bg-error-50 px-4 py-2 text-sm font-medium text-error-600 transition hover:bg-error-100 dark:border-error-700 dark:bg-error-900/20 dark:text-error-400 dark:hover:bg-error-900/30 disabled:opacity-50"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
                Stop
              </button>
            </template>
          </div>
        </div>
      </div>

      <!-- Stats Cards (use WebSocket progress for real-time updates) -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Features</p>
          <p class="text-2xl font-bold text-gray-800 dark:text-white/90">
            {{ liveStats.total }}
          </p>
        </div>
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <p class="text-sm text-gray-500 dark:text-gray-400">Passing</p>
          <p class="text-2xl font-bold text-success-600">
            {{ liveStats.passing }}
          </p>
        </div>
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <p class="text-sm text-gray-500 dark:text-gray-400">In Progress</p>
          <p class="text-2xl font-bold text-warning-600">
            {{ liveStats.in_progress }}
          </p>
        </div>
        <div
          class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
        >
          <p class="text-sm text-gray-500 dark:text-gray-400">Completion</p>
          <p class="text-2xl font-bold text-brand-600">
            {{ liveStats.percentage }}%
          </p>
        </div>
      </div>

      <!-- Agent Phase Indicator -->
      <AgentPhaseIndicator
        :phase="agentStatusData?.phase || null"
        :agent-status="displayedAgentStatus"
      />

      <!-- Multi-Agent Panel and Assets Grid -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <!-- Multi-Agent Panel -->
        <MultiAgentPanel
          :project-name="projectName"
          :max-agents="projectConfig?.max_parallel_agents || 5"
          @agent-started="fetchFeatures"
          @agent-stopped="fetchFeatures"
        />

        <!-- Asset Uploader -->
        <AssetUploader :project-name="projectName" />
      </div>

      <!-- Custom Subagents -->
      <SubagentEditor :project-name="projectName" />

      <!-- Features Kanban Board -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
            Features
          </h3>
          <div class="flex items-center gap-2">
            <button
              @click="showAddFeatureModal = true"
              class="inline-flex items-center gap-1 rounded-lg bg-brand-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-brand-600"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Feature
            </button>
            <button
              @click="fetchFeatures"
              class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
            >
              <svg class="w-4 h-4" :class="{ 'animate-spin': featuresLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="featuresLoading && !features" class="flex items-center justify-center py-12">
          <svg class="animate-spin h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- Empty State -->
        <div v-else-if="!features || totalFeatures === 0" class="flex flex-col items-center justify-center py-12 text-center">
          <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <p class="text-gray-500 dark:text-gray-400">No features yet</p>
          <p class="mt-1 text-sm text-gray-400 dark:text-gray-500">
            Run the initializer agent to create features from your app spec
          </p>
        </div>

        <!-- Kanban Board -->
        <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <!-- Pending Column -->
          <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-800/50">
            <div class="mb-3 flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded-full bg-warning-100 text-xs font-medium text-warning-600 dark:bg-warning-500/20 dark:text-warning-400">
                {{ features.pending.length }}
              </span>
              <h4 class="font-medium text-gray-700 dark:text-gray-300">Pending</h4>
            </div>
            <div class="space-y-2 max-h-96 overflow-y-auto">
              <div
                v-for="feature in features.pending"
                :key="feature.id"
                @click="selectedFeature = feature"
                class="cursor-pointer rounded-lg border border-gray-200 bg-white p-3 transition hover:border-warning-300 hover:shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:hover:border-warning-600"
              >
                <div class="flex items-start justify-between gap-2">
                  <span class="text-xs font-medium text-warning-600 dark:text-warning-400">{{ feature.category }}</span>
                  <span class="text-xs text-gray-400">#{{ feature.priority }}</span>
                </div>
                <p class="mt-1 text-sm font-medium text-gray-800 dark:text-white/90 line-clamp-2">{{ feature.name }}</p>
              </div>
              <div v-if="features.pending.length === 0" class="py-4 text-center text-sm text-gray-400">
                No pending features
              </div>
            </div>
          </div>

          <!-- In Progress Column -->
          <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-800/50">
            <div class="mb-3 flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded-full bg-brand-100 text-xs font-medium text-brand-600 dark:bg-brand-500/20 dark:text-brand-400">
                {{ features.in_progress.length }}
              </span>
              <h4 class="font-medium text-gray-700 dark:text-gray-300">In Progress</h4>
            </div>
            <div class="space-y-2 max-h-96 overflow-y-auto">
              <div
                v-for="feature in features.in_progress"
                :key="feature.id"
                @click="selectedFeature = feature"
                class="cursor-pointer rounded-lg border border-brand-200 bg-white p-3 shadow-sm dark:border-brand-700 dark:bg-gray-800"
              >
                <div class="flex items-start justify-between gap-2">
                  <span class="text-xs font-medium text-brand-600 dark:text-brand-400">{{ feature.category }}</span>
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
                  </span>
                </div>
                <p class="mt-1 text-sm font-medium text-gray-800 dark:text-white/90 line-clamp-2">{{ feature.name }}</p>
              </div>
              <div v-if="features.in_progress.length === 0" class="py-4 text-center text-sm text-gray-400">
                No features in progress
              </div>
            </div>
          </div>

          <!-- Done Column -->
          <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-800/50">
            <div class="mb-3 flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded-full bg-success-100 text-xs font-medium text-success-600 dark:bg-success-500/20 dark:text-success-400">
                {{ features.done.length }}
              </span>
              <h4 class="font-medium text-gray-700 dark:text-gray-300">Done</h4>
            </div>
            <div class="space-y-2 max-h-96 overflow-y-auto">
              <div
                v-for="feature in features.done"
                :key="feature.id"
                @click="selectedFeature = feature"
                class="cursor-pointer rounded-lg border border-gray-200 bg-white p-3 transition hover:border-success-300 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-success-600"
              >
                <div class="flex items-start justify-between gap-2">
                  <span class="text-xs font-medium text-success-600 dark:text-success-400">{{ feature.category }}</span>
                  <svg class="w-4 h-4 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p class="mt-1 text-sm font-medium text-gray-800 dark:text-white/90 line-clamp-2">{{ feature.name }}</p>
              </div>
              <div v-if="features.done.length === 0" class="py-4 text-center text-sm text-gray-400">
                No completed features
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature Detail Modal -->
      <Modal v-if="selectedFeature" @close="selectedFeature = null">
        <template #body>
          <div class="relative w-full max-w-[600px] rounded-3xl bg-white p-6 dark:bg-gray-900">
            <button
              @click="selectedFeature = null"
              class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div class="mb-4">
              <div class="flex items-center gap-2 mb-2">
                <span
                  :class="[
                    'rounded-full px-2 py-0.5 text-xs font-medium',
                    selectedFeature.passes
                      ? 'bg-success-100 text-success-600 dark:bg-success-500/20 dark:text-success-400'
                      : selectedFeature.in_progress
                        ? 'bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400'
                        : 'bg-warning-100 text-warning-600 dark:bg-warning-500/20 dark:text-warning-400'
                  ]"
                >
                  {{ selectedFeature.passes ? 'Done' : selectedFeature.in_progress ? 'In Progress' : 'Pending' }}
                </span>
                <span class="text-xs text-gray-400">Priority #{{ selectedFeature.priority }}</span>
              </div>
              <h4 class="text-xl font-semibold text-gray-800 dark:text-white/90">
                {{ selectedFeature.name }}
              </h4>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ selectedFeature.category }}
              </p>
            </div>

            <div class="mb-4">
              <h5 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Description</h5>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ selectedFeature.description }}</p>
            </div>

            <div v-if="selectedFeature.steps && selectedFeature.steps.length > 0" class="mb-4">
              <h5 class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">Test Steps</h5>
              <ol class="space-y-2">
                <li
                  v-for="(step, index) in selectedFeature.steps"
                  :key="index"
                  class="flex gap-2 text-sm text-gray-600 dark:text-gray-400"
                >
                  <span class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                    {{ index + 1 }}
                  </span>
                  <span>{{ step }}</span>
                </li>
              </ol>
            </div>

            <div class="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                @click="openEditFeature(selectedFeature)"
                class="flex-1 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600"
              >
                Edit Feature
              </button>
              <button
                v-if="selectedFeature.in_progress && !selectedFeature.passes"
                @click="handleClearInProgress(selectedFeature.id)"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                Clear In Progress
              </button>
              <button
                v-if="!selectedFeature.passes"
                @click="handleSkipFeature(selectedFeature.id)"
                class="flex-1 rounded-lg border border-warning-300 px-4 py-2 text-sm font-medium text-warning-600 transition hover:bg-warning-50 dark:border-warning-700 dark:text-warning-400 dark:hover:bg-warning-900/20"
              >
                Skip Feature
              </button>
            </div>
          </div>
        </template>
      </Modal>

      <!-- Agent Logs -->
      <div
        class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
            Agent Activity
          </h3>
          <div class="flex items-center gap-2">
            <label class="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400 cursor-pointer">
              <input
                type="checkbox"
                v-model="autoScroll"
                class="w-4 h-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
              />
              Auto-scroll
            </label>
            <button
              @click="clearLogs"
              class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Clear
            </button>
          </div>
        </div>

        <div
          ref="logsContainer"
          class="rounded-lg bg-gray-900 p-4 font-mono text-sm text-gray-300 h-80 overflow-y-auto"
        >
          <div v-if="logs.length === 0" class="text-gray-500">
            No agent activity yet. Start the agent to see logs here.
          </div>
          <div v-else class="space-y-0.5">
            <div
              v-for="(log, index) in logs"
              :key="index"
              class="flex gap-3 hover:bg-gray-800/50 px-1 -mx-1 rounded"
            >
              <span class="text-gray-600 flex-shrink-0 select-none text-xs pt-0.5">
                {{ new Date(log.timestamp).toLocaleTimeString() }}
              </span>
              <span
                :class="[
                  'break-all',
                  log.line.includes('Error') || log.line.includes('ERROR') ? 'text-error-400' :
                  log.line.includes('Warning') || log.line.includes('WARN') ? 'text-warning-400' :
                  log.line.includes('Success') || log.line.includes('PASS') ? 'text-success-400' :
                  'text-gray-300'
                ]"
              >{{ log.line }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Assistant Chat Panel - Fixed Sidebar with Backdrop -->
      <Transition name="slide">
        <div v-if="showAssistant" class="fixed inset-0 z-50 flex justify-end">
          <!-- Backdrop -->
          <div
            class="absolute inset-0 bg-black/20"
            @click="showAssistant = false; disconnectAssistant()"
          ></div>
          <!-- Sidebar -->
          <div class="relative w-96 h-full bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 shadow-2xl flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-500/20">
              <svg class="w-4 h-4 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 class="text-base font-semibold text-gray-800 dark:text-white/90">
                Project Assistant
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Ask questions about this project
              </p>
            </div>
          </div>
          <button
            @click="showAssistant = false; disconnectAssistant()"
            class="flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Chat Messages -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 dark:bg-gray-800/50">
          <div v-if="assistantMessages.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8">
            <svg class="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <p>Start a conversation with the assistant</p>
            <p class="text-sm mt-1">Ask about features, code, or project status</p>
          </div>
          <div
            v-for="(msg, index) in assistantMessages"
            :key="index"
            :class="[
              'rounded-lg p-3 max-w-[85%]',
              msg.role === 'user'
                ? 'ml-auto bg-brand-500 text-white'
                : 'mr-auto bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600'
            ]"
          >
            <p class="text-sm whitespace-pre-wrap">{{ msg.content }}</p>
          </div>
          <div v-if="assistantLoading" class="mr-auto flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <span class="text-sm">Thinking...</span>
          </div>
        </div>

        <!-- Chat Input -->
        <form @submit.prevent="sendAssistantMessage" class="p-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
          <div class="flex gap-2">
            <input
              v-model="assistantInput"
              type="text"
              placeholder="Ask about your project..."
              :disabled="assistantLoading"
              class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white disabled:opacity-50"
            />
            <button
              type="submit"
              :disabled="assistantLoading || !assistantInput.trim()"
              class="inline-flex items-center justify-center rounded-lg bg-brand-500 px-3 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Add Feature Modal -->
    <AddFeatureModal
      v-if="showAddFeatureModal"
      :project-name="projectName"
      @close="showAddFeatureModal = false"
      @added="handleFeatureAdded"
    />

    <!-- Edit Feature Modal -->
    <Modal v-if="editingFeature" @close="editingFeature = null">
      <template #body>
        <div class="relative w-full max-w-[500px] rounded-3xl bg-white p-6 dark:bg-gray-900">
          <button
            @click="editingFeature = null"
            class="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <h4 class="mb-6 text-xl font-semibold text-gray-800 dark:text-white/90">
            Edit Feature
          </h4>

          <form @submit.prevent="handleSaveFeature" class="space-y-4">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Category
              </label>
              <input
                v-model="editForm.category"
                type="text"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Feature Name
              </label>
              <input
                v-model="editForm.name"
                type="text"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Description
              </label>
              <textarea
                v-model="editForm.description"
                rows="3"
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-hidden dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required
              ></textarea>
            </div>

            <div>
              <div class="mb-1.5 flex items-center justify-between">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Verification Steps
                </label>
                <button
                  type="button"
                  @click="editForm.steps.push('')"
                  class="text-xs text-brand-500 hover:text-brand-600"
                >
                  + Add Step
                </button>
              </div>
              <div class="space-y-2">
                <div
                  v-for="(step, index) in editForm.steps"
                  :key="index"
                  class="flex items-center gap-2"
                >
                  <span class="w-6 text-center text-sm text-gray-400">{{ index + 1 }}.</span>
                  <input
                    v-model="editForm.steps[index]"
                    type="text"
                    class="h-10 flex-1 rounded-lg border border-gray-300 bg-transparent px-3 py-2 text-sm text-gray-800 focus:border-brand-300 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                  />
                  <button
                    v-if="editForm.steps.length > 1"
                    type="button"
                    @click="editForm.steps.splice(index, 1)"
                    class="text-gray-400 hover:text-error-500"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="editingFeature = null"
                class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isEditingSaving"
                class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
              >
                {{ isEditingSaving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>

    <!-- Project Config Modal -->
    <ProjectConfigModal
      v-if="showConfigModal"
      :project-name="projectName"
      @close="showConfigModal = false"
      @saved="handleConfigSaved"
    />

    <!-- Agent Question Modal -->
    <AgentQuestionModal
      v-if="pendingQuestion"
      :project-name="projectName"
      :question="pendingQuestion"
      @close="clearPendingQuestion"
      @answered="handleQuestionAnswered"
    />
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import Modal from '@/components/profile/Modal.vue'
import MultiAgentPanel from '@/components/projects/MultiAgentPanel.vue'
import AssetUploader from '@/components/projects/AssetUploader.vue'
import AddFeatureModal from '@/components/projects/AddFeatureModal.vue'
import ProjectConfigModal from '@/components/projects/ProjectConfigModal.vue'
import SubagentEditor from '@/components/projects/SubagentEditor.vue'
import AgentPhaseIndicator from '@/components/projects/AgentPhaseIndicator.vue'
import AgentQuestionModal from '@/components/projects/AgentQuestionModal.vue'
import {
  projectsAPI,
  featuresAPI,
  agentAPI,
  configAPI,
  type ProjectSummary,
  type FeatureListResponse,
  type FeatureResponse,
  type AgentStatus,
  type ProjectConfig,
} from '@/api/client'
import { useProjectWebSocket } from '@/composables/useProjectWebSocket'

const route = useRoute()
const router = useRouter()
const project = ref<ProjectSummary | null>(null)
const isLoading = ref(false)

// Project config state
const projectConfig = ref<ProjectConfig | null>(null)
const showConfigModal = ref(false)
const showAddFeatureModal = ref(false)
const projectActionLoading = ref(false)
const showProjectMenu = ref(false)

// Features state
const features = ref<FeatureListResponse | null>(null)
const featuresLoading = ref(false)
const selectedFeature = ref<FeatureResponse | null>(null)
const editingFeature = ref<FeatureResponse | null>(null)
const editForm = ref({
  category: '',
  name: '',
  description: '',
  steps: [''] as string[],
})
const isEditingSaving = ref(false)

// Agent state
const agentStatusData = ref<AgentStatus | null>(null)
const agentActionLoading = ref(false)
const yoloMode = ref(false)
const logsContainer = ref<HTMLElement | null>(null)
const autoScroll = ref(true)
const projectMenuRef = ref<HTMLElement | null>(null)

// Assistant chat state
const showAssistant = ref(false)
const assistantMessages = ref<Array<{ role: 'user' | 'assistant'; content: string }>>([])
const assistantInput = ref('')
const assistantLoading = ref(false)
let assistantWs: WebSocket | null = null

const projectName = computed(() => {
  return (route.params.name as string) || 'Project'
})

// WebSocket for real-time updates
const { isConnected, agentStatus, progress, logs, pendingQuestion, clearLogs, clearPendingQuestion } = useProjectWebSocket(projectName)

// Watch for progress updates to refresh features
watch(progress, () => {
  if (progress.value) {
    fetchFeatures()
  }
})

// Watch for agent status changes to refresh features when agent stops
watch(agentStatus, (newStatus, oldStatus) => {
  // Refresh features and project when agent stops or crashes
  if ((newStatus === 'stopped' || newStatus === 'crashed') &&
      (oldStatus === 'running' || oldStatus === 'paused')) {
    fetchFeatures()
    fetchProject()
    fetchAgentStatus()
  }
})

// Auto-scroll logs
watch(logs, async () => {
  if (autoScroll.value && logsContainer.value) {
    await nextTick()
    logsContainer.value.scrollTop = logsContainer.value.scrollHeight
  }
}, { deep: true })

const totalFeatures = computed(() => {
  if (!features.value) return 0
  return features.value.pending.length + features.value.in_progress.length + features.value.done.length
})

// Live stats - prefer WebSocket progress data for real-time updates
const liveStats = computed(() => {
  // Use WebSocket progress if available (real-time during agent execution)
  if (progress.value) {
    return {
      total: progress.value.total,
      passing: progress.value.passing,
      in_progress: progress.value.in_progress,
      percentage: progress.value.percentage,
    }
  }
  // Fall back to project stats from initial fetch
  return {
    total: project.value?.stats.total || 0,
    passing: project.value?.stats.passing || 0,
    in_progress: project.value?.stats.in_progress || 0,
    percentage: project.value?.stats.percentage || 0,
  }
})

const displayedAgentStatus = computed(() => {
  return agentStatus.value || agentStatusData.value?.status || 'stopped'
})

const isAgentRunning = computed(() => displayedAgentStatus.value === 'running')
const isAgentPaused = computed(() => displayedAgentStatus.value === 'paused')
const isAgentStopped = computed(() => displayedAgentStatus.value === 'stopped' || displayedAgentStatus.value === 'crashed')

// Click outside handler for dropdown
function handleClickOutside(event: MouseEvent) {
  if (projectMenuRef.value && !projectMenuRef.value.contains(event.target as Node)) {
    showProjectMenu.value = false
  }
}

// Auto-refresh interval for live updates
let refreshInterval: ReturnType<typeof setInterval> | null = null

function startAutoRefresh() {
  if (refreshInterval) return
  refreshInterval = setInterval(async () => {
    // Refresh features, project status, and agent phase every 5 seconds while agent is running
    if (isAgentRunning.value) {
      await Promise.all([fetchFeatures(), fetchProject(), fetchAgentStatus()])
    }
  }, 5000)
}

function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Watch agent status to start/stop auto-refresh
watch(isAgentRunning, (running) => {
  if (running) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  await Promise.all([fetchProject(), fetchFeatures(), fetchAgentStatus(), fetchProjectConfig()])
  // Start auto-refresh if agent is already running
  if (isAgentRunning.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  disconnectAssistant()
  stopAutoRefresh()
})

async function fetchProject() {
  isLoading.value = true
  try {
    project.value = await projectsAPI.get(projectName.value)
  } catch (err) {
    console.error('Failed to fetch project:', err)
  } finally {
    isLoading.value = false
  }
}

async function fetchFeatures() {
  featuresLoading.value = true
  try {
    features.value = await featuresAPI.list(projectName.value)
  } catch (err) {
    console.error('Failed to fetch features:', err)
  } finally {
    featuresLoading.value = false
  }
}

async function fetchAgentStatus() {
  try {
    agentStatusData.value = await agentAPI.getStatus(projectName.value)
    yoloMode.value = agentStatusData.value.yolo_mode
  } catch (err) {
    console.error('Failed to fetch agent status:', err)
  }
}

async function fetchProjectConfig() {
  try {
    projectConfig.value = await configAPI.get(projectName.value)
  } catch (err) {
    console.error('Failed to fetch project config:', err)
  }
}

// Project lifecycle actions
async function handlePauseProject() {
  if (!confirm('Pause this project? All agents will be stopped.')) return
  projectActionLoading.value = true
  try {
    await projectsAPI.pause(projectName.value)
    await fetchProject()
  } catch (err) {
    console.error('Failed to pause project:', err)
  } finally {
    projectActionLoading.value = false
  }
}

async function handleResumeProject() {
  projectActionLoading.value = true
  try {
    await projectsAPI.resume(projectName.value)
    await fetchProject()
  } catch (err) {
    console.error('Failed to resume project:', err)
  } finally {
    projectActionLoading.value = false
  }
}

async function handleFinishProject() {
  if (!confirm('Mark this project as finished? You can reopen it later if needed.')) return
  projectActionLoading.value = true
  try {
    await projectsAPI.finish(projectName.value)
    router.push('/projects/finished')
  } catch (err) {
    console.error('Failed to finish project:', err)
  } finally {
    projectActionLoading.value = false
  }
}

async function handleRestartProject() {
  if (!confirm('Restart this project? This will clear ALL progress and reset ALL features to pending.')) return
  projectActionLoading.value = true
  try {
    await projectsAPI.restart(projectName.value)
    await Promise.all([fetchProject(), fetchFeatures()])
  } catch (err) {
    console.error('Failed to restart project:', err)
  } finally {
    projectActionLoading.value = false
  }
}

async function handleResetProject() {
  if (!confirm('Reset progress? This will clear passes but keep features.')) return
  projectActionLoading.value = true
  try {
    await projectsAPI.reset(projectName.value)
    await Promise.all([fetchProject(), fetchFeatures()])
  } catch (err) {
    console.error('Failed to reset project:', err)
  } finally {
    projectActionLoading.value = false
  }
}

function handleFeatureAdded() {
  fetchFeatures()
  fetchProject()
}

function handleConfigSaved() {
  fetchProjectConfig()
}

function handleQuestionAnswered() {
  // Clear the pending question after answering
  clearPendingQuestion()
}

async function handleStartAgent() {
  agentActionLoading.value = true
  try {
    await agentAPI.start(projectName.value, { yolo_mode: yoloMode.value })
    await fetchAgentStatus()
  } catch (err) {
    console.error('Failed to start agent:', err)
  } finally {
    agentActionLoading.value = false
  }
}

async function handleStopAgent() {
  agentActionLoading.value = true
  try {
    await agentAPI.stop(projectName.value)
    await fetchAgentStatus()
  } catch (err) {
    console.error('Failed to stop agent:', err)
  } finally {
    agentActionLoading.value = false
  }
}

async function handlePauseAgent() {
  agentActionLoading.value = true
  try {
    await agentAPI.pause(projectName.value)
    await fetchAgentStatus()
  } catch (err) {
    console.error('Failed to pause agent:', err)
  } finally {
    agentActionLoading.value = false
  }
}

async function handleResumeAgent() {
  agentActionLoading.value = true
  try {
    await agentAPI.resume(projectName.value)
    await fetchAgentStatus()
  } catch (err) {
    console.error('Failed to resume agent:', err)
  } finally {
    agentActionLoading.value = false
  }
}

async function handleSkipFeature(featureId: number) {
  try {
    await featuresAPI.skip(projectName.value, featureId)
    selectedFeature.value = null
    await fetchFeatures()
  } catch (err) {
    console.error('Failed to skip feature:', err)
  }
}

async function handleClearInProgress(featureId: number) {
  try {
    await featuresAPI.clearInProgress(projectName.value, featureId)
    selectedFeature.value = null
    await fetchFeatures()
  } catch (err) {
    console.error('Failed to clear in-progress:', err)
  }
}

// Edit feature functions
function openEditFeature(feature: FeatureResponse) {
  editingFeature.value = feature
  editForm.value = {
    category: feature.category,
    name: feature.name,
    description: feature.description,
    steps: feature.steps && feature.steps.length > 0 ? [...feature.steps] : [''],
  }
  selectedFeature.value = null
}

async function handleSaveFeature() {
  if (!editingFeature.value) return
  isEditingSaving.value = true
  try {
    await featuresAPI.update(projectName.value, editingFeature.value.id, {
      category: editForm.value.category,
      name: editForm.value.name,
      description: editForm.value.description,
      steps: editForm.value.steps.filter(s => s.trim() !== ''),
    })
    editingFeature.value = null
    await fetchFeatures()
  } catch (err) {
    console.error('Failed to update feature:', err)
  } finally {
    isEditingSaving.value = false
  }
}

// Assistant chat functions
function connectAssistant() {
  if (assistantWs?.readyState === WebSocket.OPEN) return

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const wsUrl = `${protocol}//${host}/api/assistant/ws/${encodeURIComponent(projectName.value)}`

  assistantWs = new WebSocket(wsUrl)

  assistantWs.onopen = () => {
    console.log('Assistant WebSocket connected')
    // Send start message
    assistantWs?.send(JSON.stringify({ type: 'start' }))
  }

  assistantWs.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data)

      switch (message.type) {
        case 'started':
          console.log('Assistant session started')
          break

        case 'text':
          // Append or update assistant message
          if (assistantMessages.value.length > 0 &&
              assistantMessages.value[assistantMessages.value.length - 1].role === 'assistant') {
            assistantMessages.value[assistantMessages.value.length - 1].content += message.content
          } else {
            assistantMessages.value.push({ role: 'assistant', content: message.content })
          }
          break

        case 'tool_call':
          // Show tool usage
          const toolMsg = `[Using tool: ${message.tool}]`
          if (assistantMessages.value.length > 0 &&
              assistantMessages.value[assistantMessages.value.length - 1].role === 'assistant') {
            assistantMessages.value[assistantMessages.value.length - 1].content += '\n' + toolMsg
          } else {
            assistantMessages.value.push({ role: 'assistant', content: toolMsg })
          }
          break

        case 'done':
        case 'response_done':
          assistantLoading.value = false
          break

        case 'error':
          console.error('Assistant error:', message.message)
          assistantMessages.value.push({ role: 'assistant', content: `Error: ${message.message}` })
          assistantLoading.value = false
          break

        case 'pong':
          break
      }
    } catch (err) {
      console.error('Failed to parse assistant message:', err)
    }
  }

  assistantWs.onclose = () => {
    console.log('Assistant WebSocket disconnected')
    assistantLoading.value = false
  }

  assistantWs.onerror = (error) => {
    console.error('Assistant WebSocket error:', error)
    assistantLoading.value = false
  }
}

function disconnectAssistant() {
  if (assistantWs) {
    assistantWs.close()
    assistantWs = null
  }
}

function toggleAssistant() {
  showAssistant.value = !showAssistant.value
  if (showAssistant.value && !assistantWs) {
    connectAssistant()
  }
}

function sendAssistantMessage() {
  if (!assistantInput.value.trim() || assistantLoading.value) return

  const message = assistantInput.value.trim()
  assistantInput.value = ''

  // Add user message
  assistantMessages.value.push({ role: 'user', content: message })
  assistantLoading.value = true

  // Send to WebSocket
  if (assistantWs?.readyState === WebSocket.OPEN) {
    assistantWs.send(JSON.stringify({ type: 'message', content: message }))
  } else {
    // Reconnect and send
    connectAssistant()
    setTimeout(() => {
      assistantWs?.send(JSON.stringify({ type: 'message', content: message }))
    }, 500)
  }
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
}

.slide-enter-from > div:last-child,
.slide-leave-to > div:last-child {
  transform: translateX(100%);
}
</style>
