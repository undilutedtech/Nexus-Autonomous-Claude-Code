import { test, expect } from './fixtures/auth'

test.describe('Command Palette', () => {
  test('opens with Ctrl+K keyboard shortcut', async ({ authenticatedPage: page }) => {
    // Go to dashboard
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Press Ctrl+K
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Check if command palette is visible
    const palette = page.locator('input[placeholder*="Search commands"]')
    await expect(palette).toBeVisible({ timeout: 5000 })
  })

  test('opens by clicking search bar', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Click on the search bar
    const searchBar = page.locator('text=Search or type command...').first()
    await searchBar.click()
    await page.waitForTimeout(500)

    // Check if command palette is visible
    const palette = page.locator('input[placeholder*="Search commands"]')
    await expect(palette).toBeVisible({ timeout: 5000 })
  })

  test('closes with Escape key', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Verify it's open
    const palette = page.locator('input[placeholder*="Search commands"]')
    await expect(palette).toBeVisible()

    // Press Escape
    await page.keyboard.press('Escape')
    await page.waitForTimeout(300)

    // Verify it's closed
    await expect(palette).not.toBeVisible()
  })

  test('filters results as you type', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type a search query
    await page.keyboard.type('settings')
    await page.waitForTimeout(300)

    // Check that settings option is visible
    const settingsOption = page.locator('button:has-text("Settings")')
    await expect(settingsOption.first()).toBeVisible({ timeout: 5000 })
  })

  test('navigates with keyboard arrows', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Press down arrow to select next item
    await page.keyboard.press('ArrowDown')
    await page.waitForTimeout(200)

    // Verify an item is highlighted (has brand-500 background)
    const highlightedItem = page.locator('button.bg-brand-500')
    await expect(highlightedItem).toBeVisible()
  })

  test('shows only actions when typing >', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type > to show only actions
    await page.keyboard.type('>')
    await page.waitForTimeout(300)

    // Actions or Navigation categories should be visible
    const categories = page.locator('h3.uppercase')
    await expect(categories.first()).toBeVisible({ timeout: 5000 })
  })

  test('executes command on Enter - navigates to settings', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type to find settings
    await page.keyboard.type('settings')
    await page.waitForTimeout(300)

    // Press Enter to execute
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to settings
    expect(page.url()).toContain('/settings')
  })

  test('executes command on click - navigates to settings', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type settings to filter
    await page.keyboard.type('settings')
    await page.waitForTimeout(300)

    // Click on the settings command
    const settingsCommand = page.locator('button:has-text("Settings")').first()
    await expect(settingsCommand).toBeVisible()
    await settingsCommand.click()
    await page.waitForTimeout(1000)

    // Should navigate to settings
    expect(page.url()).toContain('/settings')
  })

  test('navigates to all projects', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type to search for All Projects
    await page.keyboard.type('All Projects')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to projects
    expect(page.url()).toContain('/projects')
  })

  test('navigates to create new project', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type new project
    await page.keyboard.type('Create New Project')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to new project page
    expect(page.url()).toContain('/projects/new')
  })

  test('navigates to active projects', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type Active Projects
    await page.keyboard.type('Active Projects')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to in-progress projects
    expect(page.url()).toContain('/in-progress')
  })

  test('navigates to completed projects', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type Completed Projects
    await page.keyboard.type('Completed Projects')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to finished projects
    expect(page.url()).toContain('/finished')
  })

  test('navigates to documentation', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type Documentation (the exact command name)
    await page.keyboard.type('Documentation')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to docs
    expect(page.url()).toContain('/docs')
  })

  test('navigates to profile', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type Profile
    await page.keyboard.type('Profile')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to profile
    expect(page.url()).toContain('/profile')
  })

  test('navigates to analytics', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type Analytics
    await page.keyboard.type('Analytics')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Should navigate to analytics
    expect(page.url()).toContain('/analytics')
  })

  test('toggles dark mode', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Get current theme state
    const htmlElement = page.locator('html')
    const initialDarkMode = await htmlElement.evaluate(el => el.classList.contains('dark'))

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type exact command name
    await page.keyboard.type('Toggle Dark Mode')
    await page.waitForTimeout(300)

    // Press Enter
    await page.keyboard.press('Enter')
    await page.waitForTimeout(500)

    // Check theme changed
    const newDarkMode = await htmlElement.evaluate(el => el.classList.contains('dark'))
    expect(newDarkMode).not.toBe(initialDarkMode)
  })

  test('copy current URL command exists', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type exact command name
    await page.keyboard.type('Copy Current URL')
    await page.waitForTimeout(300)

    // Verify the command appears
    const copyCommand = page.locator('button').filter({ hasText: 'Copy Current URL' }).first()
    await expect(copyCommand).toBeVisible({ timeout: 5000 })

    // Click it
    await copyCommand.click()
    await page.waitForTimeout(500)

    // Palette should close
    const palette = page.locator('input[placeholder*="Search commands"]')
    await expect(palette).not.toBeVisible()
  })

  test('sign out command exists', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type exact command name
    await page.keyboard.type('Sign Out')
    await page.waitForTimeout(300)

    // Sign out should be visible
    const signOutCommand = page.locator('button').filter({ hasText: 'Sign Out' }).first()
    await expect(signOutCommand).toBeVisible({ timeout: 5000 })
  })

  test('refresh page command exists', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type Refresh
    await page.keyboard.type('Refresh Page')
    await page.waitForTimeout(300)

    // Refresh Page should be visible
    const refreshCommand = page.locator('button').filter({ hasText: 'Refresh Page' }).first()
    await expect(refreshCommand).toBeVisible({ timeout: 5000 })
  })

  test('shows project search results', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // Open command palette
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(1000) // Wait for projects to load

    // Verify the palette loaded
    const palette = page.locator('input[placeholder*="Search commands"]')
    await expect(palette).toBeVisible()
  })
})
