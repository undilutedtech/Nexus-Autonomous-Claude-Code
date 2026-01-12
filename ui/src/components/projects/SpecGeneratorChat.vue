<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
      <div class="flex items-center gap-2">
        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-900/30">
          <svg class="w-4 h-4 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-800 dark:text-white/90">AI Spec Generator</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400">Describe your app idea</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span
          class="flex items-center gap-1.5 text-xs px-2 py-1 rounded-full"
          :class="isConnected ? 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="isConnected ? 'bg-success-500' : 'bg-gray-400'"></span>
          {{ isConnected ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
    </div>

    <!-- Chat Messages -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 dark:bg-gray-800/50">
      <!-- Initial state -->
      <div v-if="messages.length === 0 && !isLoading" class="text-center text-gray-500 dark:text-gray-400 py-8">
        <svg class="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <p class="font-medium">Let's create your app specification</p>
        <p class="text-sm mt-1">Describe what you want to build in a few sentences</p>
        <div class="mt-4 text-left max-w-md mx-auto">
          <p class="text-xs font-medium text-gray-600 dark:text-gray-300 mb-2">Example prompts:</p>
          <div class="space-y-2">
            <button
              v-for="example in examplePrompts"
              :key="example"
              @click="setInput(example)"
              class="w-full text-left text-xs p-2 rounded border border-gray-200 dark:border-gray-600 hover:bg-white dark:hover:bg-gray-700 transition"
            >
              "{{ example }}"
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div
        v-for="(msg, index) in messages"
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

      <!-- Loading indicator -->
      <div v-if="isLoading" class="mr-auto bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600 rounded-lg p-3 max-w-[85%]">
        <div class="flex items-center gap-2">
          <div class="flex space-x-1">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
          <span class="text-xs text-gray-500">Claude is thinking...</span>
        </div>
      </div>
    </div>

    <!-- Spec Complete Banner -->
    <div v-if="isComplete" class="px-4 py-3 bg-success-50 dark:bg-success-900/20 border-t border-success-200 dark:border-success-800">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-success-600 dark:text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-sm font-medium text-success-800 dark:text-success-300">Specification complete!</span>
      </div>
      <p class="text-xs text-success-600 dark:text-success-400 mt-1">Your app spec has been generated and saved.</p>
    </div>

    <!-- Input Area -->
    <div class="p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
      <div class="flex gap-2">
        <input
          v-model="input"
          @keydown.enter="sendMessage"
          :disabled="isLoading || isComplete"
          type="text"
          :placeholder="isComplete ? 'Specification complete' : 'Describe your app idea...'"
          class="flex-1 h-10 rounded-lg border border-gray-300 bg-transparent px-3 text-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-500/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white/90 dark:placeholder:text-white/30 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          @click="sendMessage"
          :disabled="!input.trim() || isLoading || isComplete"
          class="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500 text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const props = defineProps<{
  projectName: string
}>()

const emit = defineEmits<{
  (e: 'complete', specPath: string): void
  (e: 'update:spec', spec: string): void
}>()

// State
const messages = ref<Message[]>([])
const input = ref('')
const isLoading = ref(false)
const isConnected = ref(false)
const isComplete = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

// WebSocket
let ws: WebSocket | null = null
let reconnectAttempts = 0
const maxReconnectAttempts = 3

// Example prompts
const examplePrompts = [
  'A habit tracking app where users can create daily habits and see streak statistics',
  'A recipe manager with ingredients, instructions, and meal planning',
  'A project task board like Trello with drag-and-drop columns'
]

function setInput(text: string) {
  input.value = text
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function connect() {
  if (ws?.readyState === WebSocket.OPEN) return

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const wsUrl = `${protocol}//${host}/api/spec/ws/${encodeURIComponent(props.projectName)}`

  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('Spec generator WebSocket connected')
    isConnected.value = true
    reconnectAttempts = 0

    // Start the session
    ws?.send(JSON.stringify({ type: 'start' }))
  }

  ws.onclose = () => {
    console.log('Spec generator WebSocket disconnected')
    isConnected.value = false

    // Attempt reconnect if not complete
    if (!isComplete.value && reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++
      setTimeout(connect, 1000 * reconnectAttempts)
    }
  }

  ws.onerror = (error) => {
    console.error('Spec generator WebSocket error:', error)
  }

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data)
      handleMessage(message)
    } catch (err) {
      console.error('Failed to parse spec generator message:', err)
    }
  }
}

function handleMessage(message: any) {
  switch (message.type) {
    case 'text':
      // Append or update assistant message
      if (messages.value.length > 0 && messages.value[messages.value.length - 1].role === 'assistant') {
        messages.value[messages.value.length - 1].content += message.content
      } else {
        messages.value.push({ role: 'assistant', content: message.content })
      }
      scrollToBottom()
      break

    case 'question':
      // Handle structured questions (simplified - just show as text)
      if (message.questions?.length > 0) {
        const questionText = message.questions.map((q: any) => q.question).join('\n')
        messages.value.push({ role: 'assistant', content: questionText })
        scrollToBottom()
      }
      isLoading.value = false
      break

    case 'spec_complete':
      emit('complete', message.path || '')
      break

    case 'file_written':
      // A file was written - could track this
      console.log('File written:', message.path)
      break

    case 'complete':
      isComplete.value = true
      isLoading.value = false
      emit('complete', message.path || '')
      break

    case 'response_done':
      isLoading.value = false
      break

    case 'error':
      messages.value.push({ role: 'assistant', content: `Error: ${message.content}` })
      isLoading.value = false
      scrollToBottom()
      break

    case 'pong':
      // Keep-alive response
      break
  }
}

function sendMessage() {
  if (!input.value.trim() || isLoading.value || isComplete.value) return

  const content = input.value.trim()
  input.value = ''

  // Add user message
  messages.value.push({ role: 'user', content })
  isLoading.value = true
  scrollToBottom()

  // Send to WebSocket
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'message', content }))
  } else {
    // Try to reconnect
    connect()
    setTimeout(() => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'message', content }))
      } else {
        messages.value.push({ role: 'assistant', content: 'Failed to connect. Please try again.' })
        isLoading.value = false
      }
    }, 1000)
  }
}

// Keep-alive ping
let pingInterval: ReturnType<typeof setInterval> | null = null

function startPing() {
  pingInterval = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }, 30000)
}

function stopPing() {
  if (pingInterval) {
    clearInterval(pingInterval)
    pingInterval = null
  }
}

onMounted(() => {
  connect()
  startPing()
})

onUnmounted(() => {
  stopPing()
  if (ws) {
    ws.close()
    ws = null
  }
})

// Reconnect if project name changes
watch(() => props.projectName, () => {
  if (ws) {
    ws.close()
  }
  messages.value = []
  isComplete.value = false
  isLoading.value = false
  connect()
})
</script>
