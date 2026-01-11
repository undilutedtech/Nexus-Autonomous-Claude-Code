/**
 * Project WebSocket Composable
 * ============================
 *
 * Real-time updates for project progress and agent output.
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import type { Ref } from 'vue'
import type { AgentStatusType, AgentQuestion } from '@/api/client'

export interface LogEntry {
  line: string
  timestamp: string
}

export interface ProgressUpdate {
  passing: number
  in_progress: number
  total: number
  percentage: number
}

export function useProjectWebSocket(projectName: Ref<string>) {
  const isConnected = ref(false)
  const agentStatus = ref<AgentStatusType>('stopped')
  const progress = ref<ProgressUpdate | null>(null)
  const logs = ref<LogEntry[]>([])
  const pendingQuestion = ref<AgentQuestion | null>(null)
  const maxLogs = 500

  let ws: WebSocket | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
  let pingInterval: ReturnType<typeof setInterval> | null = null

  function connect() {
    if (ws?.readyState === WebSocket.OPEN || ws?.readyState === WebSocket.CONNECTING) {
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/ws/projects/${encodeURIComponent(projectName.value)}`

    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      isConnected.value = true
      console.log('WebSocket connected for project:', projectName.value)

      // Start ping interval
      pingInterval = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }))
        }
      }, 30000)
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        switch (message.type) {
          case 'agent_status':
            agentStatus.value = message.status
            break

          case 'progress':
            progress.value = {
              passing: message.passing,
              in_progress: message.in_progress,
              total: message.total,
              percentage: message.percentage,
            }
            break

          case 'log':
            logs.value.push({
              line: message.line,
              timestamp: message.timestamp,
            })
            // Trim logs if too many
            if (logs.value.length > maxLogs) {
              logs.value = logs.value.slice(-maxLogs)
            }
            break

          case 'agent_question':
            pendingQuestion.value = message.question
            break

          case 'pong':
            // Keep-alive response, ignore
            break

          default:
            console.log('Unknown WebSocket message type:', message.type)
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }

    ws.onclose = () => {
      isConnected.value = false
      console.log('WebSocket disconnected')

      if (pingInterval) {
        clearInterval(pingInterval)
        pingInterval = null
      }

      // Attempt to reconnect after 3 seconds
      reconnectTimeout = setTimeout(() => {
        if (projectName.value) {
          connect()
        }
      }, 3000)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  function disconnect() {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }

    if (pingInterval) {
      clearInterval(pingInterval)
      pingInterval = null
    }

    if (ws) {
      ws.close()
      ws = null
    }

    isConnected.value = false
  }

  function clearLogs() {
    logs.value = []
  }

  function clearPendingQuestion() {
    pendingQuestion.value = null
  }

  // Watch for project name changes
  watch(projectName, (newName, oldName) => {
    if (newName !== oldName) {
      disconnect()
      logs.value = []
      if (newName) {
        connect()
      }
    }
  })

  onMounted(() => {
    if (projectName.value) {
      connect()
    }
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    agentStatus,
    progress,
    logs,
    pendingQuestion,
    clearLogs,
    clearPendingQuestion,
    reconnect: connect,
  }
}
