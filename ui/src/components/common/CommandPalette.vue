<template>
  <Teleport to="body">
    <Transition
      enter-active-class="duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-99999 overflow-y-auto"
        @click.self="close"
      >
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm" @click="close"></div>

        <!-- Modal -->
        <div class="relative flex min-h-full items-start justify-center p-4 pt-[15vh]">
          <Transition
            enter-active-class="duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="isOpen"
              class="relative w-full max-w-xl transform overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-black/5 dark:bg-gray-900 dark:ring-white/10"
              @click.stop
            >
              <!-- Search Input -->
              <div class="relative border-b border-gray-200 dark:border-gray-800">
                <svg
                  class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <input
                  ref="searchInput"
                  v-model="query"
                  type="text"
                  placeholder="Search commands, projects, or type '>' for actions..."
                  class="h-14 w-full border-0 bg-transparent pl-12 pr-4 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-0 dark:text-white sm:text-sm"
                  @keydown="handleKeyDown"
                />
                <div class="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  <kbd class="rounded bg-gray-100 px-2 py-1 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                    ESC
                  </kbd>
                </div>
              </div>

              <!-- Results -->
              <div class="max-h-[60vh] overflow-y-auto p-2">
                <!-- Loading State -->
                <div v-if="loading" class="flex items-center justify-center py-8">
                  <svg class="animate-spin h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                </div>

                <!-- No Results -->
                <div v-else-if="filteredItems.length === 0" class="py-8 text-center">
                  <svg class="mx-auto h-12 w-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">No results found</p>
                  <p class="text-xs text-gray-400 dark:text-gray-500">Try a different search term</p>
                </div>

                <!-- Results List -->
                <template v-else>
                  <div v-for="(group, groupIndex) in groupedItems" :key="group.category" class="mb-2">
                    <h3 class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      {{ group.category }}
                    </h3>
                    <ul>
                      <li v-for="(item, itemIndex) in group.items" :key="item.id">
                        <button
                          :ref="el => setItemRef(el, groupIndex, itemIndex)"
                          @click="executeCommand(item)"
                          @mouseenter="setActiveIndex(groupIndex, itemIndex)"
                          :class="[
                            'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition',
                            isActive(groupIndex, itemIndex)
                              ? 'bg-brand-500 text-white'
                              : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                          ]"
                        >
                          <span
                            :class="[
                              'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg',
                              isActive(groupIndex, itemIndex)
                                ? 'bg-brand-600 text-white'
                                : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                            ]"
                          >
                            <component :is="item.icon" class="h-5 w-5" />
                          </span>
                          <div class="flex-1 min-w-0">
                            <p :class="['text-sm font-medium truncate', isActive(groupIndex, itemIndex) ? 'text-white' : '']">
                              {{ item.name }}
                            </p>
                            <p :class="['text-xs truncate', isActive(groupIndex, itemIndex) ? 'text-brand-100' : 'text-gray-500 dark:text-gray-400']">
                              {{ item.description }}
                            </p>
                          </div>
                          <kbd
                            v-if="item.shortcut"
                            :class="[
                              'hidden sm:flex items-center gap-1 rounded px-2 py-1 text-xs',
                              isActive(groupIndex, itemIndex)
                                ? 'bg-brand-600 text-brand-100'
                                : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                            ]"
                          >
                            {{ item.shortcut }}
                          </kbd>
                        </button>
                      </li>
                    </ul>
                  </div>
                </template>
              </div>

              <!-- Footer -->
              <div class="border-t border-gray-200 bg-gray-50 px-4 py-2.5 dark:border-gray-800 dark:bg-gray-900/50">
                <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <div class="flex items-center gap-4">
                    <span class="flex items-center gap-1">
                      <kbd class="rounded bg-gray-200 px-1.5 py-0.5 dark:bg-gray-700">↑↓</kbd>
                      Navigate
                    </span>
                    <span class="flex items-center gap-1">
                      <kbd class="rounded bg-gray-200 px-1.5 py-0.5 dark:bg-gray-700">↵</kbd>
                      Select
                    </span>
                    <span class="flex items-center gap-1">
                      <kbd class="rounded bg-gray-200 px-1.5 py-0.5 dark:bg-gray-700">ESC</kbd>
                      Close
                    </span>
                  </div>
                  <span>Type <code class="text-brand-500">></code> for commands</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick, h, type FunctionalComponent, type ComponentPublicInstance } from 'vue'
import { useRouter } from 'vue-router'
import { projectsAPI } from '@/api/client'

// Icons as functional components
const FolderIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z' })
])

const PlusIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 6v6m0 0v6m0-6h6m-6 0H6' })
])

const PlayIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z' }),
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
])

const PauseIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z' })
])

const ChartIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
])

const CogIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }),
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' })
])

const UserIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' })
])

const HomeIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
])

const DocumentIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
])

const RefreshIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' })
])

const LightningIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' })
])

interface CommandItem {
  id: string
  name: string
  description: string
  category: string
  icon: FunctionalComponent
  action: () => void
  shortcut?: string
  keywords?: string[]
}

const router = useRouter()
const isOpen = ref(false)
const query = ref('')
const loading = ref(false)
const searchInput = ref<HTMLInputElement | null>(null)
const activeGroupIndex = ref(0)
const activeItemIndex = ref(0)
const itemRefs = ref<Map<string, HTMLElement>>(new Map())
const projects = ref<Array<{ name: string; path: string }>>([])

// Base commands
const baseCommands: CommandItem[] = [
  // Navigation
  {
    id: 'nav-dashboard',
    name: 'Go to Dashboard',
    description: 'View the main dashboard',
    category: 'Navigation',
    icon: HomeIcon,
    action: () => router.push('/'),
    shortcut: '⌘D',
    keywords: ['home', 'main'],
  },
  {
    id: 'nav-projects',
    name: 'Go to Projects',
    description: 'View all projects',
    category: 'Navigation',
    icon: FolderIcon,
    action: () => router.push('/projects'),
    shortcut: '⌘P',
    keywords: ['list', 'all'],
  },
  {
    id: 'nav-analytics',
    name: 'Go to Analytics',
    description: 'View analytics dashboard',
    category: 'Navigation',
    icon: ChartIcon,
    action: () => router.push('/analytics'),
    keywords: ['stats', 'metrics'],
  },
  {
    id: 'nav-settings',
    name: 'Go to Settings',
    description: 'Manage your settings',
    category: 'Navigation',
    icon: CogIcon,
    action: () => router.push('/settings'),
    keywords: ['config', 'preferences'],
  },
  {
    id: 'nav-profile',
    name: 'Go to Profile',
    description: 'View your profile',
    category: 'Navigation',
    icon: UserIcon,
    action: () => router.push('/profile'),
    keywords: ['account', 'user'],
  },
  {
    id: 'nav-docs',
    name: 'Go to Documentation',
    description: 'View documentation',
    category: 'Navigation',
    icon: DocumentIcon,
    action: () => router.push('/docs'),
    keywords: ['help', 'guide'],
  },
  // Actions
  {
    id: 'action-new-project',
    name: 'Create New Project',
    description: 'Start a new coding project',
    category: 'Actions',
    icon: PlusIcon,
    action: () => router.push('/projects/new'),
    shortcut: '⌘N',
    keywords: ['add', 'create'],
  },
  {
    id: 'action-overview',
    name: 'Projects Overview',
    description: 'View aggregate project stats',
    category: 'Actions',
    icon: ChartIcon,
    action: () => router.push('/projects/overview'),
    keywords: ['stats', 'summary'],
  },
  {
    id: 'action-in-progress',
    name: 'In Progress Projects',
    description: 'View projects being worked on',
    category: 'Actions',
    icon: LightningIcon,
    action: () => router.push('/projects/in-progress'),
    keywords: ['active', 'working'],
  },
  {
    id: 'action-paused',
    name: 'Paused Projects',
    description: 'View paused projects',
    category: 'Actions',
    icon: PauseIcon,
    action: () => router.push('/projects/paused'),
    keywords: ['stopped', 'halted'],
  },
  {
    id: 'action-finished',
    name: 'Finished Projects',
    description: 'View completed projects',
    category: 'Actions',
    icon: PlayIcon,
    action: () => router.push('/projects/finished'),
    keywords: ['completed', 'done'],
  },
  {
    id: 'action-refresh',
    name: 'Refresh Page',
    description: 'Reload the current page',
    category: 'Actions',
    icon: RefreshIcon,
    action: () => window.location.reload(),
    shortcut: '⌘R',
    keywords: ['reload'],
  },
]

// Computed commands including projects
const allCommands = computed<CommandItem[]>(() => {
  const projectCommands = projects.value.map(project => ({
    id: `project-${project.name}`,
    name: project.name,
    description: project.path,
    category: 'Projects',
    icon: FolderIcon,
    action: () => router.push(`/projects/${encodeURIComponent(project.name)}`),
    keywords: [project.name.toLowerCase()],
  }))

  return [...baseCommands, ...projectCommands]
})

// Filter items based on query
const filteredItems = computed<CommandItem[]>(() => {
  const q = query.value.toLowerCase().trim()

  // If query starts with >, only show actions/commands
  if (q.startsWith('>')) {
    const actionQuery = q.slice(1).trim()
    return allCommands.value
      .filter(item => item.category === 'Actions' || item.category === 'Navigation')
      .filter(item => {
        if (!actionQuery) return true
        return (
          item.name.toLowerCase().includes(actionQuery) ||
          item.description.toLowerCase().includes(actionQuery) ||
          item.keywords?.some(k => k.includes(actionQuery))
        )
      })
  }

  if (!q) return allCommands.value

  return allCommands.value.filter(item => {
    return (
      item.name.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q) ||
      item.keywords?.some(k => k.includes(q))
    )
  })
})

// Group items by category
const groupedItems = computed(() => {
  const groups: { category: string; items: CommandItem[] }[] = []
  const categoryMap = new Map<string, CommandItem[]>()

  for (const item of filteredItems.value) {
    if (!categoryMap.has(item.category)) {
      categoryMap.set(item.category, [])
    }
    categoryMap.get(item.category)!.push(item)
  }

  // Order: Projects, Actions, Navigation
  const order = ['Projects', 'Actions', 'Navigation']
  for (const cat of order) {
    if (categoryMap.has(cat)) {
      groups.push({ category: cat, items: categoryMap.get(cat)! })
    }
  }

  return groups
})

// Check if item is active
function isActive(groupIndex: number, itemIndex: number): boolean {
  return activeGroupIndex.value === groupIndex && activeItemIndex.value === itemIndex
}

// Set active index
function setActiveIndex(groupIndex: number, itemIndex: number) {
  activeGroupIndex.value = groupIndex
  activeItemIndex.value = itemIndex
}

// Set item ref for scrolling
function setItemRef(el: Element | ComponentPublicInstance | null, groupIndex: number, itemIndex: number) {
  if (el && el instanceof HTMLElement) {
    itemRefs.value.set(`${groupIndex}-${itemIndex}`, el)
  }
}

// Keyboard navigation
function handleKeyDown(event: KeyboardEvent) {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      moveSelection(1)
      break
    case 'ArrowUp':
      event.preventDefault()
      moveSelection(-1)
      break
    case 'Enter':
      event.preventDefault()
      executeSelectedCommand()
      break
    case 'Escape':
      event.preventDefault()
      close()
      break
  }
}

function moveSelection(direction: number) {
  const groups = groupedItems.value
  if (groups.length === 0) return

  let newGroupIndex = activeGroupIndex.value
  let newItemIndex = activeItemIndex.value + direction

  // Handle wrapping within and between groups
  if (newItemIndex < 0) {
    // Move to previous group
    newGroupIndex--
    if (newGroupIndex < 0) {
      newGroupIndex = groups.length - 1
    }
    newItemIndex = groups[newGroupIndex].items.length - 1
  } else if (newItemIndex >= groups[newGroupIndex]?.items.length) {
    // Move to next group
    newGroupIndex++
    if (newGroupIndex >= groups.length) {
      newGroupIndex = 0
    }
    newItemIndex = 0
  }

  activeGroupIndex.value = newGroupIndex
  activeItemIndex.value = newItemIndex

  // Scroll into view
  nextTick(() => {
    const ref = itemRefs.value.get(`${newGroupIndex}-${newItemIndex}`)
    ref?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  })
}

function executeSelectedCommand() {
  const groups = groupedItems.value
  if (groups.length === 0) return

  const group = groups[activeGroupIndex.value]
  if (!group) return

  const item = group.items[activeItemIndex.value]
  if (item) {
    executeCommand(item)
  }
}

function executeCommand(item: CommandItem) {
  close()
  item.action()
}

// Open/Close
function open() {
  isOpen.value = true
  nextTick(() => {
    searchInput.value?.focus()
    fetchProjects()
  })
}

function close() {
  isOpen.value = false
  query.value = ''
  activeGroupIndex.value = 0
  activeItemIndex.value = 0
}

function toggle() {
  if (isOpen.value) {
    close()
  } else {
    open()
  }
}

// Fetch projects for search
async function fetchProjects() {
  try {
    loading.value = true
    const data = await projectsAPI.list()
    projects.value = data.map(p => ({ name: p.name, path: p.path }))
  } catch (err) {
    console.error('Failed to fetch projects:', err)
  } finally {
    loading.value = false
  }
}

// Reset selection when query changes
watch(query, () => {
  activeGroupIndex.value = 0
  activeItemIndex.value = 0
})

// Global keyboard shortcut
function handleGlobalKeyDown(event: KeyboardEvent) {
  // Cmd/Ctrl + K
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault()
    toggle()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown)
})

// Expose for parent components
defineExpose({ open, close, toggle })
</script>
