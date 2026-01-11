<template>
  <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
        Assets
      </h3>
      <span class="text-sm text-gray-500 dark:text-gray-400">
        {{ formatBytes(totalSize) }} used
      </span>
    </div>

    <!-- Drop Zone -->
    <div
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      class="relative mb-4 rounded-xl border-2 border-dashed p-6 text-center transition-colors"
      :class="isDragging ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20' : 'border-gray-300 dark:border-gray-700'"
    >
      <input
        type="file"
        multiple
        @change="handleFileSelect"
        class="absolute inset-0 cursor-pointer opacity-0"
        accept=".png,.jpg,.jpeg,.gif,.webp,.svg,.ico,.pdf,.txt,.md,.json,.xml,.yaml,.yml,.py,.js,.ts,.html,.css,.sql"
      />

      <div class="flex flex-col items-center">
        <svg class="mb-2 h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          <span class="font-medium text-brand-500">Click to upload</span> or drag and drop
        </p>
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-500">
          Images, PDFs, text files (max 10MB each)
        </p>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploading" class="absolute inset-0 flex items-center justify-center rounded-xl bg-white/90 dark:bg-gray-900/90">
        <div class="text-center">
          <svg class="mx-auto h-8 w-8 animate-spin text-brand-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Uploading...</p>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mb-4 rounded-lg bg-error-50 p-3 text-sm text-error-600 dark:bg-error-900/20 dark:text-error-400">
      {{ error }}
    </div>

    <!-- Assets List -->
    <div v-if="assets.length > 0" class="space-y-2">
      <div
        v-for="asset in assets"
        :key="asset.filename"
        class="flex items-center justify-between rounded-lg border border-gray-200 p-3 dark:border-gray-700"
      >
        <div class="flex items-center gap-3">
          <!-- File Icon -->
          <div
            class="flex h-10 w-10 items-center justify-center rounded-lg"
            :class="getAssetIconClass(asset.mime_type)"
          >
            <component :is="getAssetIcon(asset.mime_type)" class="w-5 h-5" />
          </div>

          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-gray-800 dark:text-white/90">
              {{ asset.filename }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatBytes(asset.size) }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Copy Reference -->
          <button
            @click="copyReference(asset.filename)"
            class="rounded-lg border border-gray-300 px-2 py-1.5 text-xs text-gray-600 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
            title="Copy reference for app spec"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>

          <!-- Delete -->
          <button
            @click="deleteAsset(asset.filename)"
            :disabled="deleting === asset.filename"
            class="rounded-lg border border-error-300 px-2 py-1.5 text-xs text-error-600 transition hover:bg-error-50 dark:border-error-700 dark:text-error-400 dark:hover:bg-error-900/20 disabled:opacity-50"
            title="Delete asset"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!isLoading" class="py-6 text-center">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        No assets uploaded yet
      </p>
    </div>

    <!-- Copy Toast -->
    <div
      v-if="showCopyToast"
      class="fixed bottom-4 right-4 rounded-lg bg-gray-800 px-4 py-2 text-sm text-white shadow-lg"
    >
      Copied to clipboard!
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { assetsAPI, type AssetInfo } from '@/api/client'

const props = defineProps<{
  projectName: string
}>()

const assets = ref<AssetInfo[]>([])
const totalSize = ref(0)
const isLoading = ref(false)
const uploading = ref(false)
const deleting = ref<string | null>(null)
const isDragging = ref(false)
const error = ref('')
const showCopyToast = ref(false)

onMounted(async () => {
  await fetchAssets()
})

async function fetchAssets() {
  isLoading.value = true
  try {
    const response = await assetsAPI.list(props.projectName)
    assets.value = response.assets
    totalSize.value = response.total_size
  } catch (err) {
    console.error('Failed to fetch assets:', err)
  } finally {
    isLoading.value = false
  }
}

async function handleDrop(e: DragEvent) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  await uploadFiles(files)
}

async function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  await uploadFiles(files)
  target.value = '' // Reset input
}

async function uploadFiles(files: File[]) {
  if (files.length === 0) return

  uploading.value = true
  error.value = ''

  try {
    for (const file of files) {
      await assetsAPI.upload(props.projectName, file)
    }
    await fetchAssets()
  } catch (err: any) {
    error.value = err.message || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

async function deleteAsset(filename: string) {
  if (!confirm(`Delete ${filename}?`)) return

  deleting.value = filename
  try {
    await assetsAPI.delete(props.projectName, filename)
    await fetchAssets()
  } catch (err: any) {
    error.value = err.message || 'Delete failed'
  } finally {
    deleting.value = null
  }
}

function copyReference(filename: string) {
  const reference = `[See: assets/${filename}]`
  navigator.clipboard.writeText(reference)
  showCopyToast.value = true
  setTimeout(() => {
    showCopyToast.value = false
  }, 2000)
}

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function getAssetIconClass(mimeType: string | null) {
  if (!mimeType) return 'bg-gray-100 text-gray-500 dark:bg-gray-800'
  if (mimeType.startsWith('image/')) return 'bg-brand-100 text-brand-500 dark:bg-brand-900/20'
  if (mimeType.includes('pdf')) return 'bg-error-100 text-error-500 dark:bg-error-900/20'
  if (mimeType.includes('json') || mimeType.includes('xml')) return 'bg-warning-100 text-warning-500 dark:bg-warning-900/20'
  return 'bg-gray-100 text-gray-500 dark:bg-gray-800'
}

function getAssetIcon(mimeType: string | null) {
  // Return SVG path data based on mime type
  const iconPath = mimeType?.startsWith('image/')
    ? 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z'
    : 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'

  return h('svg', {
    fill: 'none',
    stroke: 'currentColor',
    viewBox: '0 0 24 24',
  }, [
    h('path', {
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      'stroke-width': '2',
      d: iconPath,
    })
  ])
}
</script>
