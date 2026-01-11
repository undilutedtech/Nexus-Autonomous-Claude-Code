/**
 * Theme Composable
 * =================
 *
 * Vue composable for managing dark/light mode theme.
 */

import { ref, watch, onMounted } from 'vue'

const isDark = ref(false)

export function useTheme() {
  onMounted(() => {
    // Check for saved preference or system preference
    const savedTheme = localStorage.getItem('nexus_theme')
    if (savedTheme) {
      isDark.value = savedTheme === 'dark'
    } else {
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  })

  watch(isDark, () => {
    applyTheme()
    localStorage.setItem('nexus_theme', isDark.value ? 'dark' : 'light')
  })

  function applyTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function toggleTheme() {
    isDark.value = !isDark.value
  }

  function setTheme(dark: boolean) {
    isDark.value = dark
  }

  return {
    isDark,
    toggleTheme,
    setTheme,
  }
}
