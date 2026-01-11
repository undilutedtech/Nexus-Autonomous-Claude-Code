<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="'Create New Project'" />

    <div class="mx-auto max-w-3xl">
      <!-- Stepper Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <template v-for="(step, index) in steps" :key="index">
            <!-- Step Circle -->
            <div class="flex flex-col items-center">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold transition-all"
                :class="getStepClass(index)"
              >
                <svg v-if="index < currentStep" class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <span
                class="mt-2 text-xs font-medium"
                :class="index <= currentStep ? 'text-brand-600 dark:text-brand-400' : 'text-gray-400'"
              >
                {{ step.title }}
              </span>
            </div>
            <!-- Connector Line -->
            <div
              v-if="index < steps.length - 1"
              class="h-0.5 flex-1 mx-2"
              :class="index < currentStep ? 'bg-brand-500' : 'bg-gray-200 dark:bg-gray-700'"
            ></div>
          </template>
        </div>
      </div>

      <!-- Step Content -->
      <div class="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <!-- Step 1: Basic Info -->
        <div v-if="currentStep === 0" class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              Project Details
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Give your project a name and choose where to store it.
            </p>
          </div>

          <!-- Project Name -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Project Name <span class="text-error-500">*</span>
            </label>
            <input
              v-model="form.name"
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
              Project Location <span class="text-error-500">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="form.path"
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
          <FolderBrowser
            v-if="showFolderBrowser"
            :initial-path="form.path"
            @select="handleFolderSelect"
            @close="showFolderBrowser = false"
          />
        </div>

        <!-- Step 2: App Specification -->
        <div v-if="currentStep === 1" class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              App Specification
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Describe what you want to build. This will guide the AI agent.
            </p>
          </div>

          <!-- Template Selection -->
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Start from a template (optional)
            </label>
            <div class="grid grid-cols-2 gap-3">
              <button
                v-for="template in templates"
                :key="template.id"
                type="button"
                @click="selectTemplate(template)"
                class="flex flex-col items-start rounded-lg border p-3 text-left transition"
                :class="selectedTemplate?.id === template.id
                  ? 'border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-900/20'
                  : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'"
              >
                <span class="text-sm font-medium text-gray-800 dark:text-white/90">{{ template.name }}</span>
                <span class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ template.description }}</span>
              </button>
            </div>
          </div>

          <!-- App Spec Editor -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Application Specification
            </label>
            <textarea
              v-model="form.appSpec"
              rows="12"
              placeholder="<project_specification>
<name>My Application</name>
<description>A brief description of what your app does...</description>
<tech_stack>
  <frontend>React, TypeScript, TailwindCSS</frontend>
  <backend>Node.js, Express</backend>
</tech_stack>
<features>
  <feature>User authentication</feature>
  <feature>Dashboard with analytics</feature>
</features>
</project_specification>"
              class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-3 font-mono text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              XML format recommended. You can also edit this later in the project settings.
            </p>
          </div>
        </div>

        <!-- Step 3: Configuration -->
        <div v-if="currentStep === 2" class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              Agent Configuration
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Configure how the AI agent will work on your project.
            </p>
          </div>

          <!-- Model Selection -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              AI Model
            </label>
            <select
              v-model="form.model"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
            >
              <option value="claude-opus-4-5-20251101">Claude Opus 4.5 (Most capable)</option>
              <option value="claude-sonnet-4-5-20250929">Claude Sonnet 4.5 (Balanced)</option>
            </select>
          </div>

          <!-- YOLO Mode -->
          <div class="flex items-start gap-3">
            <input
              v-model="form.yoloMode"
              type="checkbox"
              id="yoloMode"
              class="mt-1 h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
            />
            <div>
              <label for="yoloMode" class="text-sm font-medium text-gray-700 dark:text-gray-300">
                YOLO Mode
              </label>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Skip testing for faster prototyping. Recommended for initial development.
              </p>
            </div>
          </div>

          <!-- Max Parallel Agents -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Max Parallel Agents
            </label>
            <select
              v-model="form.maxAgents"
              class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
            >
              <option :value="1">1 Agent (Sequential)</option>
              <option :value="2">2 Agents (Parallel)</option>
              <option :value="3">3 Agents (Parallel)</option>
              <option :value="4">4 Agents (Parallel)</option>
            </select>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Multiple agents can work on different features simultaneously.
            </p>
          </div>

          <!-- Auto-stop on Completion -->
          <div class="flex items-start gap-3">
            <input
              v-model="form.autoStop"
              type="checkbox"
              id="autoStop"
              class="mt-1 h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
            />
            <div>
              <label for="autoStop" class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Auto-stop on Completion
              </label>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Automatically stop agents when all features are complete.
              </p>
            </div>
          </div>
        </div>

        <!-- Step 4: Review -->
        <div v-if="currentStep === 3" class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
              Review & Create
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Review your project configuration before creating.
            </p>
          </div>

          <!-- Summary -->
          <div class="space-y-4 rounded-lg bg-gray-50 p-4 dark:bg-gray-800/50">
            <div class="flex justify-between border-b border-gray-200 pb-3 dark:border-gray-700">
              <span class="text-sm text-gray-500 dark:text-gray-400">Project Name</span>
              <span class="text-sm font-medium text-gray-800 dark:text-white/90">{{ form.name }}</span>
            </div>
            <div class="flex justify-between border-b border-gray-200 pb-3 dark:border-gray-700">
              <span class="text-sm text-gray-500 dark:text-gray-400">Location</span>
              <span class="text-sm font-medium text-gray-800 dark:text-white/90 truncate max-w-xs">{{ form.path }}</span>
            </div>
            <div class="flex justify-between border-b border-gray-200 pb-3 dark:border-gray-700">
              <span class="text-sm text-gray-500 dark:text-gray-400">Has App Spec</span>
              <span class="text-sm font-medium" :class="form.appSpec ? 'text-success-600' : 'text-gray-400'">
                {{ form.appSpec ? 'Yes' : 'No (can be added later)' }}
              </span>
            </div>
            <div class="flex justify-between border-b border-gray-200 pb-3 dark:border-gray-700">
              <span class="text-sm text-gray-500 dark:text-gray-400">AI Model</span>
              <span class="text-sm font-medium text-gray-800 dark:text-white/90">
                {{ form.model === 'claude-opus-4-5-20251101' ? 'Claude Opus 4.5' : 'Claude Sonnet 4.5' }}
              </span>
            </div>
            <div class="flex justify-between border-b border-gray-200 pb-3 dark:border-gray-700">
              <span class="text-sm text-gray-500 dark:text-gray-400">YOLO Mode</span>
              <span class="text-sm font-medium" :class="form.yoloMode ? 'text-warning-600' : 'text-gray-400'">
                {{ form.yoloMode ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-500 dark:text-gray-400">Max Agents</span>
              <span class="text-sm font-medium text-gray-800 dark:text-white/90">{{ form.maxAgents }}</span>
            </div>
          </div>

          <!-- Start Agent Option -->
          <div class="flex items-start gap-3 rounded-lg border border-brand-200 bg-brand-50 p-4 dark:border-brand-800 dark:bg-brand-900/20">
            <input
              v-model="form.startAgent"
              type="checkbox"
              id="startAgent"
              class="mt-1 h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
            />
            <div>
              <label for="startAgent" class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Start agent immediately after creation
              </label>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                The AI agent will begin working on your project right away.
              </p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="createError" class="rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
            {{ createError }}
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="mt-8 flex justify-between gap-3 border-t border-gray-200 pt-6 dark:border-gray-700">
          <button
            v-if="currentStep > 0"
            type="button"
            @click="prevStep"
            class="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Back
          </button>
          <router-link
            v-else
            to="/projects"
            class="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Cancel
          </router-link>

          <button
            v-if="currentStep < steps.length - 1"
            type="button"
            @click="nextStep"
            :disabled="!canProceed"
            class="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue
          </button>
          <button
            v-else
            type="button"
            @click="createProject"
            :disabled="isCreating || !canProceed"
            class="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
          >
            {{ isCreating ? 'Creating...' : 'Create Project' }}
          </button>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import FolderBrowser from '@/components/projects/FolderBrowser.vue'
import { projectsAPI, configAPI, agentAPI } from '@/api/client'

const router = useRouter()

// Steps configuration
const steps = [
  { title: 'Details', description: 'Name and location' },
  { title: 'Specification', description: 'App description' },
  { title: 'Configuration', description: 'Agent settings' },
  { title: 'Review', description: 'Create project' },
]

const currentStep = ref(0)

// Form state
const form = ref({
  name: '',
  path: '',
  appSpec: '',
  model: 'claude-opus-4-5-20251101',
  yoloMode: true,
  maxAgents: 1,
  autoStop: true,
  startAgent: false,
})

// UI state
const showFolderBrowser = ref(false)
const isCreating = ref(false)
const createError = ref('')
const selectedTemplate = ref<typeof templates[0] | null>(null)

// Templates
const templates = [
  {
    id: 'blank',
    name: 'Blank Project',
    description: 'Start from scratch',
    spec: '',
  },
  {
    id: 'webapp',
    name: 'Web Application',
    description: 'Full-stack web app',
    spec: `<project_specification>
<name>Web Application</name>
<description>A modern full-stack web application with user authentication, dashboard, and core features.</description>
<tech_stack>
  <frontend>React, TypeScript, TailwindCSS</frontend>
  <backend>Node.js, Express, PostgreSQL</backend>
</tech_stack>
<features>
  <feature priority="1">User registration and login</feature>
  <feature priority="2">User dashboard</feature>
  <feature priority="3">Profile management</feature>
  <feature priority="4">Settings page</feature>
</features>
</project_specification>`,
  },
  {
    id: 'api',
    name: 'REST API',
    description: 'Backend API service',
    spec: `<project_specification>
<name>REST API Service</name>
<description>A robust REST API with authentication, CRUD operations, and data validation.</description>
<tech_stack>
  <backend>Python, FastAPI</backend>
  <database>PostgreSQL</database>
</tech_stack>
<features>
  <feature priority="1">JWT authentication</feature>
  <feature priority="2">User CRUD endpoints</feature>
  <feature priority="3">Data validation middleware</feature>
  <feature priority="4">API documentation with OpenAPI</feature>
</features>
</project_specification>`,
  },
  {
    id: 'cli',
    name: 'CLI Tool',
    description: 'Command-line application',
    spec: `<project_specification>
<name>CLI Tool</name>
<description>A command-line tool with subcommands, configuration, and helpful output.</description>
<tech_stack>
  <language>Python</language>
  <framework>Click</framework>
</tech_stack>
<features>
  <feature priority="1">Main command with help</feature>
  <feature priority="2">Subcommand structure</feature>
  <feature priority="3">Configuration file support</feature>
  <feature priority="4">Colored output and progress bars</feature>
</features>
</project_specification>`,
  },
]

// Computed
const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return form.value.name.trim() && form.value.path.trim()
  }
  return true
})

// Methods
function getStepClass(index: number) {
  if (index < currentStep.value) {
    return 'bg-brand-500 text-white'
  }
  if (index === currentStep.value) {
    return 'bg-brand-500 text-white ring-4 ring-brand-100 dark:ring-brand-900/50'
  }
  return 'bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
}

function nextStep() {
  if (currentStep.value < steps.length - 1 && canProceed.value) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function handleFolderSelect(path: string) {
  form.value.path = path
  showFolderBrowser.value = false
}

function selectTemplate(template: typeof templates[0]) {
  if (selectedTemplate.value?.id === template.id) {
    selectedTemplate.value = null
    form.value.appSpec = ''
  } else {
    selectedTemplate.value = template
    form.value.appSpec = template.spec
  }
}

async function createProject() {
  if (!form.value.name || !form.value.path) return

  isCreating.value = true
  createError.value = ''

  try {
    // Create the project
    const project = await projectsAPI.create({
      name: form.value.name,
      path: form.value.path,
    })

    // Update prompts if app spec provided
    if (form.value.appSpec.trim()) {
      try {
        await fetch(`/api/projects/${encodeURIComponent(form.value.name)}/prompts`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ app_spec: form.value.appSpec }),
        })
      } catch (err) {
        console.warn('Failed to save app spec:', err)
      }
    }

    // Update config
    try {
      await configAPI.update(form.value.name, {
        max_parallel_agents: form.value.maxAgents,
        auto_stop_on_completion: form.value.autoStop,
      })
    } catch (err) {
      console.warn('Failed to update config:', err)
    }

    // Start agent if requested
    if (form.value.startAgent) {
      try {
        await agentAPI.start(form.value.name, {
          yolo_mode: form.value.yoloMode,
          model: form.value.model,
        })
      } catch (err) {
        console.warn('Failed to start agent:', err)
      }
    }

    // Navigate to the new project
    router.push(`/projects/${encodeURIComponent(project.name)}`)
  } catch (err: any) {
    createError.value = err.message || 'Failed to create project'
  } finally {
    isCreating.value = false
  }
}
</script>
