<template>
  <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
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
        @keyup.esc="cancelNewFolder"
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
        @click="cancelNewFolder"
        class="rounded px-2 py-1 text-sm text-gray-600 transition hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-700"
      >
        Cancel
      </button>
    </div>

    <!-- Folder List -->
    <div class="max-h-60 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center py-8">
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
          :class="{ 'bg-brand-50 dark:bg-brand-900/20': selectedPath === entry.path }"
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

    <!-- Error Message -->
    <div v-if="error" class="border-t border-gray-200 bg-error-50 px-3 py-2 text-sm text-error-600 dark:border-gray-700 dark:bg-error-900/20 dark:text-error-400">
      {{ error }}
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
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { filesystemAPI, type DirectoryListResponse } from '@/api/client'

const props = defineProps<{
  initialPath?: string
}>()

const emit = defineEmits<{
  select: [path: string]
  close: []
}>()

const loading = ref(false)
const error = ref('')
const browserData = ref<DirectoryListResponse | null>(null)
const showNewFolderInput = ref(false)
const newFolderName = ref('')
const newFolderInput = ref<HTMLInputElement | null>(null)
const selectedPath = ref('')

onMounted(async () => {
  await loadDirectory(props.initialPath || undefined)
})

watch(showNewFolderInput, async (show) => {
  if (show) {
    await nextTick()
    newFolderInput.value?.focus()
  }
})

async function loadDirectory(path?: string) {
  loading.value = true
  error.value = ''
  try {
    browserData.value = await filesystemAPI.list(path)
  } catch (err: any) {
    error.value = err.message || 'Failed to load directory'
  } finally {
    loading.value = false
  }
}

async function navigateToFolder(path: string) {
  await loadDirectory(path)
}

async function navigateToParent() {
  if (browserData.value?.parent_path) {
    await loadDirectory(browserData.value.parent_path)
  }
}

async function navigateToHome() {
  try {
    const home = await filesystemAPI.getHome()
    await loadDirectory(home.path)
  } catch (err) {
    console.error('Failed to navigate to home:', err)
  }
}

function selectFolder(path: string) {
  emit('select', path)
}

function selectCurrentFolder() {
  if (browserData.value?.current_path) {
    emit('select', browserData.value.current_path)
  }
}

function cancelNewFolder() {
  showNewFolderInput.value = false
  newFolderName.value = ''
}

async function createNewFolder() {
  if (!newFolderName.value.trim() || !browserData.value?.current_path) return

  try {
    const result = await filesystemAPI.createDirectory(
      browserData.value.current_path,
      newFolderName.value.trim()
    )

    // Navigate to the new folder
    await loadDirectory(result.path)
    selectedPath.value = result.path

    // Reset input
    cancelNewFolder()
  } catch (err: any) {
    error.value = err.message || 'Failed to create folder'
  }
}
</script>
