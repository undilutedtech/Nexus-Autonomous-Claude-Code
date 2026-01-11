<template>
  <ThemeProvider>
    <SidebarProvider>
      <RouterView />
    </SidebarProvider>
  </ThemeProvider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import ThemeProvider from './components/layout/ThemeProvider.vue'
import SidebarProvider from './components/layout/SidebarProvider.vue'
import { useAuth } from './composables/useAuth'
import { useTheme } from './composables/useTheme'

const { initialize } = useAuth()

// Initialize auth and theme on app start
onMounted(async () => {
  await initialize()
})

// Also initialize theme
useTheme()
</script>
