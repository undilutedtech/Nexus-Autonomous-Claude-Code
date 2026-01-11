<template>
  <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
        Agents
      </h3>
      <div class="flex items-center gap-2">
        <button
          v-if="agents.length > 1"
          @click="stopAllAgents"
          :disabled="isLoading"
          class="rounded-lg border border-error-300 px-3 py-1.5 text-sm font-medium text-error-600 transition hover:bg-error-50 dark:border-error-700 dark:text-error-400 dark:hover:bg-error-900/20"
        >
          Stop All
        </button>
        <button
          @click="spawnAgent"
          :disabled="isLoading || agents.length >= maxAgents"
          class="inline-flex items-center gap-1 rounded-lg bg-brand-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Agent
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && agents.length === 0" class="flex items-center justify-center py-8">
      <svg class="animate-spin h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Agents List -->
    <div v-else-if="agents.length > 0" class="space-y-3">
      <div
        v-for="agent in agents"
        :key="agent.agent_id"
        class="flex items-center justify-between rounded-xl border p-4"
        :class="getAgentBorderClass(agent.status)"
      >
        <div class="flex items-center gap-3">
          <!-- Status Indicator -->
          <div
            class="h-3 w-3 rounded-full"
            :class="getAgentStatusClass(agent.status)"
          ></div>

          <div>
            <p class="font-medium text-gray-800 dark:text-white/90">
              {{ agent.agent_id }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Mode: {{ agent.mode }}
              <span v-if="agent.current_feature_id">
                | Working on feature #{{ agent.current_feature_id }}
              </span>
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Action Buttons based on status -->
          <template v-if="agent.status === 'stopped'">
            <button
              @click="startAgent(agent.agent_id)"
              :disabled="actionLoading === agent.agent_id"
              class="rounded-lg bg-success-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-success-600 disabled:opacity-50"
            >
              Start
            </button>
          </template>
          <template v-else-if="agent.status === 'running'">
            <button
              @click="pauseAgent(agent.agent_id)"
              :disabled="actionLoading === agent.agent_id"
              class="rounded-lg bg-warning-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-warning-600 disabled:opacity-50"
            >
              Pause
            </button>
            <button
              @click="stopAgent(agent.agent_id)"
              :disabled="actionLoading === agent.agent_id"
              class="rounded-lg bg-error-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-error-600 disabled:opacity-50"
            >
              Stop
            </button>
          </template>
          <template v-else-if="agent.status === 'paused'">
            <button
              @click="resumeAgent(agent.agent_id)"
              :disabled="actionLoading === agent.agent_id"
              class="rounded-lg bg-brand-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
            >
              Resume
            </button>
            <button
              @click="stopAgent(agent.agent_id)"
              :disabled="actionLoading === agent.agent_id"
              class="rounded-lg bg-error-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-error-600 disabled:opacity-50"
            >
              Stop
            </button>
          </template>
          <template v-else-if="agent.status === 'crashed'">
            <button
              @click="startAgent(agent.agent_id)"
              :disabled="actionLoading === agent.agent_id"
              class="rounded-lg bg-success-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-success-600 disabled:opacity-50"
            >
              Restart
            </button>
          </template>

          <!-- Remove Button -->
          <button
            @click="removeAgent(agent.agent_id)"
            :disabled="actionLoading === agent.agent_id || agent.status === 'running'"
            class="rounded-lg border border-gray-300 px-2 py-1.5 text-xs text-gray-600 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800 disabled:opacity-50"
            title="Remove agent"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="py-8 text-center">
      <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
        <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        No agents spawned yet
      </p>
      <p class="text-xs text-gray-400 dark:text-gray-500">
        Add an agent to start working on features
      </p>
    </div>

    <!-- Info Bar -->
    <div v-if="agents.length > 0" class="mt-4 flex items-center justify-between border-t border-gray-200 pt-4 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-400">
      <span>{{ agents.length }}/{{ maxAgents }} agents</span>
      <span v-if="runningCount > 0" class="text-success-600 dark:text-success-400">
        {{ runningCount }} running
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { multiAgentAPI, type MultiAgentInfo } from '@/api/client'

const props = defineProps<{
  projectName: string
  maxAgents?: number
}>()

const emit = defineEmits<{
  (e: 'agent-started', agentId: string): void
  (e: 'agent-stopped', agentId: string): void
}>()

const agents = ref<MultiAgentInfo[]>([])
const isLoading = ref(false)
const actionLoading = ref<string | null>(null)

const maxAgents = computed(() => props.maxAgents || 5)
const runningCount = computed(() => agents.value.filter(a => a.status === 'running').length)

let refreshInterval: number | null = null

onMounted(async () => {
  await fetchAgents()
  // Refresh every 5 seconds
  refreshInterval = window.setInterval(fetchAgents, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

async function fetchAgents() {
  try {
    const response = await multiAgentAPI.list(props.projectName)
    agents.value = response.agents
  } catch (err) {
    console.error('Failed to fetch agents:', err)
  }
}

async function spawnAgent() {
  isLoading.value = true
  try {
    await multiAgentAPI.spawn(props.projectName)
    await fetchAgents()
  } catch (err) {
    console.error('Failed to spawn agent:', err)
  } finally {
    isLoading.value = false
  }
}

async function startAgent(agentId: string) {
  actionLoading.value = agentId
  try {
    await multiAgentAPI.start(props.projectName, agentId)
    await fetchAgents()
    emit('agent-started', agentId)
  } catch (err) {
    console.error('Failed to start agent:', err)
  } finally {
    actionLoading.value = null
  }
}

async function stopAgent(agentId: string) {
  actionLoading.value = agentId
  try {
    await multiAgentAPI.stop(props.projectName, agentId)
    await fetchAgents()
    emit('agent-stopped', agentId)
  } catch (err) {
    console.error('Failed to stop agent:', err)
  } finally {
    actionLoading.value = null
  }
}

async function pauseAgent(agentId: string) {
  actionLoading.value = agentId
  try {
    await multiAgentAPI.pause(props.projectName, agentId)
    await fetchAgents()
  } catch (err) {
    console.error('Failed to pause agent:', err)
  } finally {
    actionLoading.value = null
  }
}

async function resumeAgent(agentId: string) {
  actionLoading.value = agentId
  try {
    await multiAgentAPI.resume(props.projectName, agentId)
    await fetchAgents()
    emit('agent-started', agentId)
  } catch (err) {
    console.error('Failed to resume agent:', err)
  } finally {
    actionLoading.value = null
  }
}

async function removeAgent(agentId: string) {
  if (!confirm(`Remove agent ${agentId}?`)) return

  actionLoading.value = agentId
  try {
    await multiAgentAPI.remove(props.projectName, agentId)
    await fetchAgents()
  } catch (err) {
    console.error('Failed to remove agent:', err)
  } finally {
    actionLoading.value = null
  }
}

async function stopAllAgents() {
  if (!confirm('Stop all agents?')) return

  isLoading.value = true
  try {
    await multiAgentAPI.stopAll(props.projectName)
    await fetchAgents()
  } catch (err) {
    console.error('Failed to stop all agents:', err)
  } finally {
    isLoading.value = false
  }
}

function getAgentStatusClass(status: string) {
  switch (status) {
    case 'running':
      return 'bg-success-500 animate-pulse'
    case 'paused':
      return 'bg-warning-500'
    case 'crashed':
      return 'bg-error-500'
    default:
      return 'bg-gray-400'
  }
}

function getAgentBorderClass(status: string) {
  switch (status) {
    case 'running':
      return 'border-success-200 bg-success-50 dark:border-success-800 dark:bg-success-900/10'
    case 'paused':
      return 'border-warning-200 bg-warning-50 dark:border-warning-800 dark:bg-warning-900/10'
    case 'crashed':
      return 'border-error-200 bg-error-50 dark:border-error-800 dark:bg-error-900/10'
    default:
      return 'border-gray-200 dark:border-gray-700'
  }
}
</script>
