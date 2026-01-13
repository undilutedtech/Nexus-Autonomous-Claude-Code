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

const MoonIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z' })
])

const SunIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z' })
])

const LogoutIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1' })
])

const TrashIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16' })
])

const ClipboardIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' })
])

const CheckCircleIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' })
])

const ExternalLinkIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14' })
])

const TerminalIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' })
])

const SparklesIcon: FunctionalComponent = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' })
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

// Theme state
const isDarkMode = ref(document.documentElement.classList.contains('dark'))

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

function handleSignOut() {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user')
  router.push('/signin')
}

function copyCurrentUrl() {
  navigator.clipboard.writeText(window.location.href)
}

// Base commands
const baseCommands: CommandItem[] = [
  // Navigation
  {
    id: 'nav-dashboard',
    name: 'Dashboard',
    description: 'View overview and recent activity',
    category: 'Navigation',
    icon: HomeIcon,
    action: () => router.push('/dashboard'),
    shortcut: '⌘D',
    keywords: ['home', 'main', 'overview'],
  },
  {
    id: 'nav-projects',
    name: 'All Projects',
    description: 'Browse and manage all projects',
    category: 'Navigation',
    icon: FolderIcon,
    action: () => router.push('/projects'),
    shortcut: '⌘P',
    keywords: ['list', 'browse'],
  },
  {
    id: 'nav-in-progress',
    name: 'Active Projects',
    description: 'Projects currently being built by agents',
    category: 'Navigation',
    icon: LightningIcon,
    action: () => router.push('/projects/in-progress'),
    keywords: ['running', 'active', 'building', 'working'],
  },
  {
    id: 'nav-paused',
    name: 'Paused Projects',
    description: 'Projects on hold',
    category: 'Navigation',
    icon: PauseIcon,
    action: () => router.push('/projects/paused'),
    keywords: ['stopped', 'halted', 'waiting'],
  },
  {
    id: 'nav-finished',
    name: 'Completed Projects',
    description: 'Successfully finished projects',
    category: 'Navigation',
    icon: CheckCircleIcon,
    action: () => router.push('/projects/finished'),
    keywords: ['done', 'complete', 'success'],
  },
  {
    id: 'nav-overview',
    name: 'Projects Overview',
    description: 'Aggregate stats and metrics',
    category: 'Navigation',
    icon: ChartIcon,
    action: () => router.push('/projects/overview'),
    keywords: ['stats', 'summary', 'metrics'],
  },
  {
    id: 'nav-analytics',
    name: 'Analytics',
    description: 'Usage statistics and insights',
    category: 'Navigation',
    icon: ChartIcon,
    action: () => router.push('/analytics'),
    keywords: ['stats', 'metrics', 'usage', 'reports'],
  },
  {
    id: 'nav-docs',
    name: 'Documentation',
    description: 'Guides and API reference',
    category: 'Navigation',
    icon: DocumentIcon,
    action: () => router.push('/docs'),
    shortcut: '⌘/',
    keywords: ['help', 'guide', 'docs', 'api'],
  },
  {
    id: 'nav-settings',
    name: 'Settings',
    description: 'Configure app preferences',
    category: 'Navigation',
    icon: CogIcon,
    action: () => router.push('/settings'),
    shortcut: '⌘,',
    keywords: ['config', 'preferences', 'options'],
  },
  {
    id: 'nav-profile',
    name: 'Profile',
    description: 'View and edit your profile',
    category: 'Navigation',
    icon: UserIcon,
    action: () => router.push('/profile'),
    keywords: ['account', 'user', 'me'],
  },

  // Actions - Project
  {
    id: 'action-new-project',
    name: 'Create New Project',
    description: 'Start building a new application',
    category: 'Actions',
    icon: PlusIcon,
    action: () => router.push('/projects/new'),
    shortcut: '⌘N',
    keywords: ['add', 'create', 'new', 'start'],
  },

  // Actions - Theme
  {
    id: 'action-toggle-theme',
    name: 'Toggle Dark Mode',
    description: 'Switch between light and dark theme',
    category: 'Actions',
    icon: MoonIcon,
    action: toggleDarkMode,
    shortcut: '⌘⇧D',
    keywords: ['dark', 'light', 'theme', 'mode', 'night'],
  },

  // Actions - Utility
  {
    id: 'action-refresh',
    name: 'Refresh Page',
    description: 'Reload current page',
    category: 'Actions',
    icon: RefreshIcon,
    action: () => window.location.reload(),
    shortcut: '⌘R',
    keywords: ['reload', 'update'],
  },
  {
    id: 'action-copy-url',
    name: 'Copy Current URL',
    description: 'Copy page link to clipboard',
    category: 'Actions',
    icon: ClipboardIcon,
    action: copyCurrentUrl,
    keywords: ['copy', 'link', 'share', 'url'],
  },
  {
    id: 'action-clear-cache',
    name: 'Clear Local Cache',
    description: 'Clear cached data (keeps login)',
    category: 'Actions',
    icon: TrashIcon,
    action: () => {
      const token = localStorage.getItem('auth_token')
      const user = localStorage.getItem('user')
      localStorage.clear()
      if (token) localStorage.setItem('auth_token', token)
      if (user) localStorage.setItem('user', user)
      window.location.reload()
    },
    keywords: ['clear', 'cache', 'reset', 'storage'],
  },

  // Actions - External
  {
    id: 'action-github',
    name: 'Open GitHub Repo',
    description: 'View source code on GitHub',
    category: 'Actions',
    icon: ExternalLinkIcon,
    action: () => window.open('https://github.com/anthropics/claude-code', '_blank'),
    keywords: ['github', 'source', 'code', 'repo'],
  },
  {
    id: 'action-claude-docs',
    name: 'Claude Code Docs',
    description: 'Official Claude Code documentation',
    category: 'Actions',
    icon: ExternalLinkIcon,
    action: () => window.open('https://docs.anthropic.com/claude-code', '_blank'),
    keywords: ['claude', 'docs', 'anthropic', 'documentation'],
  },

  // Actions - Account
  {
    id: 'action-signout',
    name: 'Sign Out',
    description: 'Log out of your account',
    category: 'Account',
    icon: LogoutIcon,
    action: handleSignOut,
    keywords: ['logout', 'signout', 'exit', 'leave'],
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
      .filter(item => item.category === 'Actions' || item.category === 'Navigation' || item.category === 'Account')
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

  // Order: Projects, Navigation, Actions, Account
  const order = ['Projects', 'Navigation', 'Actions', 'Account']
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
