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
    const settingsOption = page.locator('text=Go to Settings')
    await expect(settingsOption).toBeVisible({ timeout: 5000 })
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

    // Actions category should be visible (use exact match to avoid "Quick Actions")
    const actionsCategory = page.getByRole('heading', { name: 'Actions', exact: true })
    await expect(actionsCategory).toBeVisible({ timeout: 5000 })
  })

  test('executes command on Enter', async ({ authenticatedPage: page }) => {
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

  test('executes command on click', async ({ authenticatedPage: page }) => {
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
})
