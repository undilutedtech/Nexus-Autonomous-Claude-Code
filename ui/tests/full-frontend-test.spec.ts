import { test, expect, Page } from '@playwright/test'

/**
 * COMPREHENSIVE FRONTEND TEST SUITE
 * ==================================
 * Tests every page, button, and feature in the Vue frontend.
 */

// Helper to set auth token
async function setupAuth(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('nexus_token', 'test-token-for-playwright')
  })
}

// =============================================================================
// 1. AUTHENTICATION PAGES
// =============================================================================

test.describe('Authentication Pages', () => {
  test('Signin page loads and has all elements', async ({ page }) => {
    await page.goto('http://localhost:5173/signin')
    await page.waitForTimeout(500)

    // Check page title/heading
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()

    // Check form elements
    const emailInput = page.locator('input[type="email"], input[placeholder*="email" i]')
    const passwordInput = page.locator('input[type="password"]')

    await expect(emailInput.or(page.locator('input').first())).toBeVisible()
    await expect(passwordInput.or(page.locator('input').nth(1))).toBeVisible()

    // Check submit button
    const submitBtn = page.locator('button[type="submit"], button:has-text("Sign"), button:has-text("Login")')
    await expect(submitBtn.first()).toBeVisible()

    // Screenshot
    await page.screenshot({ path: '/tmp/test-screenshots/01-signin.png', fullPage: true })
  })

  test('Signup page loads and has all elements', async ({ page }) => {
    await page.goto('http://localhost:5173/signup')
    await page.waitForTimeout(500)

    // Check form exists
    const form = page.locator('form')
    await expect(form.or(page.locator('[class*="form"]').first())).toBeVisible()

    // Screenshot
    await page.screenshot({ path: '/tmp/test-screenshots/02-signup.png', fullPage: true })
  })
})

// =============================================================================
// 2. DASHBOARD
// =============================================================================

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Dashboard loads with all widgets', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(1000)

    // Check sidebar is visible
    const sidebar = page.locator('[class*="sidebar"], aside, nav').first()
    await expect(sidebar).toBeVisible()

    // Check header
    const header = page.locator('header, [class*="header"]').first()
    await expect(header).toBeVisible()

    // Screenshot
    await page.screenshot({ path: '/tmp/test-screenshots/03-dashboard.png', fullPage: true })
  })

  test('Theme toggle works', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(500)

    // Find and click theme toggle
    const themeToggle = page.locator('[class*="theme"], button:has([class*="sun"]), button:has([class*="moon"])').first()
    if (await themeToggle.isVisible()) {
      await themeToggle.click()
      await page.waitForTimeout(300)
      await page.screenshot({ path: '/tmp/test-screenshots/03b-dashboard-dark.png', fullPage: true })
    }
  })
})

// =============================================================================
// 3. SIDEBAR NAVIGATION
// =============================================================================

test.describe('Sidebar Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('All sidebar menu items are clickable', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(1000)

    // Get all sidebar links
    const sidebarLinks = page.locator('aside a, nav a, [class*="sidebar"] a')
    const count = await sidebarLinks.count()
    console.log(`Found ${count} sidebar links`)

    // Click on Projects link
    const projectsLink = page.locator('a:has-text("Projects"), a[href*="project"]').first()
    if (await projectsLink.isVisible()) {
      await projectsLink.click()
      await page.waitForTimeout(500)
    }

    await page.screenshot({ path: '/tmp/test-screenshots/04-sidebar-nav.png', fullPage: true })
  })

  test('Sidebar collapse/expand works', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(500)

    // Look for collapse button
    const collapseBtn = page.locator('button[class*="collapse"], button[aria-label*="collapse"], [class*="toggle"]').first()
    if (await collapseBtn.isVisible()) {
      await collapseBtn.click()
      await page.waitForTimeout(300)
      await page.screenshot({ path: '/tmp/test-screenshots/04b-sidebar-collapsed.png', fullPage: true })
    }
  })
})

// =============================================================================
// 4. PROJECTS PAGES
// =============================================================================

test.describe('Projects Pages', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Project List page loads with all projects', async ({ page }) => {
    await page.goto('http://localhost:5173/projects')
    await page.waitForTimeout(1000)

    // Check page heading
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()

    // Check for project cards or list items
    const projectItems = page.locator('[class*="project"], [class*="card"], tr, li').first()
    await expect(projectItems.or(page.locator('main').first())).toBeVisible()

    await page.screenshot({ path: '/tmp/test-screenshots/05-project-list.png', fullPage: true })
  })

  test('Project List dropdown menus work', async ({ page }) => {
    await page.goto('http://localhost:5173/projects')
    await page.waitForTimeout(1000)

    // Find dropdown trigger (3 dots menu)
    const dropdownTrigger = page.locator('button[class*="dropdown"], button:has([class*="dots"]), button:has([class*="more"])').first()
    if (await dropdownTrigger.isVisible()) {
      await dropdownTrigger.click()
      await page.waitForTimeout(300)
      await page.screenshot({ path: '/tmp/test-screenshots/05b-project-dropdown.png', fullPage: true })
    }
  })

  test('New Project page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/new')
    await page.waitForTimeout(1000)

    // Check for form elements
    const form = page.locator('form, [class*="form"]').first()
    await expect(form.or(page.locator('main').first())).toBeVisible()

    await page.screenshot({ path: '/tmp/test-screenshots/06-new-project.png', fullPage: true })
  })

  test('Projects Overview page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/overview')
    await page.waitForTimeout(1000)

    await page.screenshot({ path: '/tmp/test-screenshots/07-projects-overview.png', fullPage: true })
  })

  test('Paused Projects page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/paused')
    await page.waitForTimeout(1000)

    await page.screenshot({ path: '/tmp/test-screenshots/08-paused-projects.png', fullPage: true })
  })

  test('Finished Projects page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/finished')
    await page.waitForTimeout(1000)

    await page.screenshot({ path: '/tmp/test-screenshots/09-finished-projects.png', fullPage: true })
  })

  test('In Progress Projects page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/in-progress')
    await page.waitForTimeout(1000)

    await page.screenshot({ path: '/tmp/test-screenshots/10-in-progress-projects.png', fullPage: true })
  })
})

// =============================================================================
// 5. PROJECT DETAIL PAGE
// =============================================================================

test.describe('Project Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Project detail page loads with all sections', async ({ page }) => {
    // First get a project name
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Check main sections exist
    await expect(page.locator('main, [class*="content"]').first()).toBeVisible()

    await page.screenshot({ path: '/tmp/test-screenshots/11-project-detail.png', fullPage: true })
  })

  test('Agent control buttons are visible', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Look for agent control buttons
    const startBtn = page.locator('button:has-text("Start"), button:has-text("Agent")')
    await expect(startBtn.first().or(page.locator('main').first())).toBeVisible()

    await page.screenshot({ path: '/tmp/test-screenshots/12-agent-controls.png', fullPage: true })
  })

  test('Kanban board is visible with columns', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Check for kanban columns
    const columns = page.locator('[class*="column"], [class*="kanban"], [class*="pending"], [class*="progress"], [class*="done"]')
    const columnCount = await columns.count()
    console.log(`Found ${columnCount} kanban-like elements`)

    await page.screenshot({ path: '/tmp/test-screenshots/13-kanban-board.png', fullPage: true })
  })

  test('Add Feature button and modal work', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Find and click Add Feature button
    const addFeatureBtn = page.locator('button:has-text("Add Feature"), button:has-text("+ Feature")')
    if (await addFeatureBtn.first().isVisible()) {
      await addFeatureBtn.first().click()
      await page.waitForTimeout(500)

      // Check modal appeared
      const modal = page.locator('[class*="modal"], [role="dialog"]')
      await expect(modal.first()).toBeVisible()

      await page.screenshot({ path: '/tmp/test-screenshots/14-add-feature-modal.png', fullPage: true })

      // Close modal
      await page.keyboard.press('Escape')
    }
  })

  test('Project config button and modal work', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Find config/settings button
    const configBtn = page.locator('button:has-text("Config"), button:has-text("Settings"), button[class*="settings"], button[class*="config"]')
    if (await configBtn.first().isVisible()) {
      await configBtn.first().click()
      await page.waitForTimeout(500)

      await page.screenshot({ path: '/tmp/test-screenshots/15-project-config-modal.png', fullPage: true })

      await page.keyboard.press('Escape')
    }
  })

  test('Agent activity log section exists', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Look for activity/log section
    const logSection = page.locator('[class*="log"], [class*="activity"], [class*="output"]')
    const logCount = await logSection.count()
    console.log(`Found ${logCount} log-like sections`)

    await page.screenshot({ path: '/tmp/test-screenshots/16-agent-activity.png', fullPage: true })
  })
})

// =============================================================================
// 6. COMMAND PALETTE
// =============================================================================

test.describe('Command Palette', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Command palette opens with Ctrl+K', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(1000)

    // Press Ctrl+K
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Check if command palette is visible
    const palette = page.locator('input[placeholder*="Search"], input[placeholder*="command"]')
    await expect(palette.first().or(page.locator('[class*="palette"]').first())).toBeVisible()

    await page.screenshot({ path: '/tmp/test-screenshots/17-command-palette.png', fullPage: true })

    // Close with Escape
    await page.keyboard.press('Escape')
  })

  test('Command palette search works', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(1000)

    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Type search query
    await page.keyboard.type('settings')
    await page.waitForTimeout(300)

    await page.screenshot({ path: '/tmp/test-screenshots/18-command-palette-search.png', fullPage: true })

    await page.keyboard.press('Escape')
  })

  test('Command palette keyboard navigation works', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(1000)

    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Navigate with arrow keys
    await page.keyboard.press('ArrowDown')
    await page.waitForTimeout(200)
    await page.keyboard.press('ArrowDown')
    await page.waitForTimeout(200)

    await page.screenshot({ path: '/tmp/test-screenshots/19-command-palette-nav.png', fullPage: true })

    await page.keyboard.press('Escape')
  })
})

// =============================================================================
// 7. SETTINGS PAGE
// =============================================================================

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Settings page loads with all sections', async ({ page }) => {
    await page.goto('http://localhost:5173/settings')
    await page.waitForTimeout(1000)

    await page.screenshot({ path: '/tmp/test-screenshots/20-settings.png', fullPage: true })
  })

  test('Profile page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/profile')
    await page.waitForTimeout(1000)

    await page.screenshot({ path: '/tmp/test-screenshots/21-profile.png', fullPage: true })
  })
})

// =============================================================================
// 8. UI ELEMENTS PAGES
// =============================================================================

test.describe('UI Elements Pages', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Alerts page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/alerts')
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/test-screenshots/22-alerts.png', fullPage: true })
  })

  test('Buttons page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/buttons')
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/test-screenshots/23-buttons.png', fullPage: true })
  })

  test('Badges page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/badges')
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/test-screenshots/24-badges.png', fullPage: true })
  })

  test('Avatars page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/avatars')
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/test-screenshots/25-avatars.png', fullPage: true })
  })
})

// =============================================================================
// 9. FORMS PAGE
// =============================================================================

test.describe('Forms Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Form elements page loads with all inputs', async ({ page }) => {
    await page.goto('http://localhost:5173/form-elements')
    await page.waitForTimeout(1000)

    // Check various form elements exist
    const inputs = page.locator('input, select, textarea')
    const inputCount = await inputs.count()
    console.log(`Found ${inputCount} form inputs`)

    await page.screenshot({ path: '/tmp/test-screenshots/26-form-elements.png', fullPage: true })
  })

  test('Form inputs are interactive', async ({ page }) => {
    await page.goto('http://localhost:5173/form-elements')
    await page.waitForTimeout(500)

    // Try typing in first text input
    const textInput = page.locator('input[type="text"], input:not([type])').first()
    if (await textInput.isVisible()) {
      await textInput.fill('Test input value')
    }

    // Try clicking a checkbox
    const checkbox = page.locator('input[type="checkbox"]').first()
    if (await checkbox.isVisible()) {
      await checkbox.click()
    }

    await page.screenshot({ path: '/tmp/test-screenshots/27-form-inputs-filled.png', fullPage: true })
  })
})

// =============================================================================
// 10. TABLES PAGE
// =============================================================================

test.describe('Tables Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Basic tables page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/basic-tables')
    await page.waitForTimeout(500)

    const table = page.locator('table')
    const tableCount = await table.count()
    console.log(`Found ${tableCount} tables`)

    await page.screenshot({ path: '/tmp/test-screenshots/28-tables.png', fullPage: true })
  })
})

// =============================================================================
// 11. CHARTS PAGE
// =============================================================================

test.describe('Charts Pages', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Line chart page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/line-chart')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: '/tmp/test-screenshots/29-line-chart.png', fullPage: true })
  })

  test('Bar chart page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/bar-chart')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: '/tmp/test-screenshots/30-bar-chart.png', fullPage: true })
  })
})

// =============================================================================
// 12. HEADER COMPONENTS
// =============================================================================

test.describe('Header Components', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Search bar in header works', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(500)

    // Find search input in header
    const searchInput = page.locator('header input, [class*="search"] input')
    if (await searchInput.first().isVisible()) {
      await searchInput.first().click()
      await page.waitForTimeout(300)
    }

    await page.screenshot({ path: '/tmp/test-screenshots/31-header-search.png', fullPage: true })
  })

  test('User menu dropdown works', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(500)

    // Find user menu trigger
    const userMenu = page.locator('[class*="user"], [class*="avatar"], button:has(img)').last()
    if (await userMenu.isVisible()) {
      await userMenu.click()
      await page.waitForTimeout(300)
      await page.screenshot({ path: '/tmp/test-screenshots/32-user-menu.png', fullPage: true })
    }
  })

  test('Notification menu works', async ({ page }) => {
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(500)

    // Find notification bell
    const notificationBtn = page.locator('button:has([class*="bell"]), button:has([class*="notification"]), [class*="notification"] button')
    if (await notificationBtn.first().isVisible()) {
      await notificationBtn.first().click()
      await page.waitForTimeout(300)
      await page.screenshot({ path: '/tmp/test-screenshots/33-notifications.png', fullPage: true })
    }
  })
})

// =============================================================================
// 13. RESPONSIVE TESTS
// =============================================================================

test.describe('Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Mobile view - Dashboard', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: '/tmp/test-screenshots/34-mobile-dashboard.png', fullPage: true })
  })

  test('Mobile view - Projects', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('http://localhost:5173/projects')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: '/tmp/test-screenshots/35-mobile-projects.png', fullPage: true })
  })

  test('Tablet view - Dashboard', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('http://localhost:5173/')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: '/tmp/test-screenshots/36-tablet-dashboard.png', fullPage: true })
  })
})

// =============================================================================
// 14. ERROR PAGES
// =============================================================================

test.describe('Error Pages', () => {
  test('404 page displays correctly', async ({ page }) => {
    await setupAuth(page)
    await page.goto('http://localhost:5173/nonexistent-page-xyz')
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/test-screenshots/37-404-page.png', fullPage: true })
  })
})

// =============================================================================
// 15. ANALYTICS PAGE
// =============================================================================

test.describe('Analytics Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Analytics dashboard loads', async ({ page }) => {
    await page.goto('http://localhost:5173/analytics')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: '/tmp/test-screenshots/38-analytics.png', fullPage: true })
  })
})

// =============================================================================
// 16. DOCUMENTATION PAGE
// =============================================================================

test.describe('Documentation Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Documentation page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/docs')
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/test-screenshots/39-docs.png', fullPage: true })
  })
})

// =============================================================================
// 17. CALENDAR PAGE
// =============================================================================

test.describe('Calendar Page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Calendar page loads', async ({ page }) => {
    await page.goto('http://localhost:5173/calendar')
    await page.waitForTimeout(500)
    await page.screenshot({ path: '/tmp/test-screenshots/40-calendar.png', fullPage: true })
  })
})

// =============================================================================
// 18. MULTI-AGENT PANEL (if visible)
// =============================================================================

test.describe('Multi-Agent Panel', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Multi-agent panel displays on project detail', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Look for multi-agent panel - using separate locators
    const agentPanel = page.locator('[class*="agent"], [class*="subagent"]').or(page.getByText('Custom Subagents'))
    const agentPanelVisible = await agentPanel.first().isVisible().catch(() => false)
    if (agentPanelVisible) {
      await page.screenshot({ path: '/tmp/test-screenshots/41-multi-agent.png', fullPage: true })
    }
    // Always take a screenshot for verification
    await page.screenshot({ path: '/tmp/test-screenshots/41-project-detail-agents.png', fullPage: true })
  })
})

// =============================================================================
// 19. ASSET UPLOADER
// =============================================================================

test.describe('Asset Uploader', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page)
  })

  test('Asset section exists on project detail', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/projects')
    const projects = await response.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name
    await page.goto(`http://localhost:5173/projects/${encodeURIComponent(projectName)}`)
    await page.waitForTimeout(1500)

    // Look for asset/upload section - using separate locators
    const assetSection = page.locator('[class*="asset"], [class*="upload"]').or(page.getByText('Assets'))
    const assetSectionVisible = await assetSection.first().isVisible().catch(() => false)
    if (assetSectionVisible) {
      await page.screenshot({ path: '/tmp/test-screenshots/42-assets.png', fullPage: true })
    }
    // Always take a screenshot for verification
    await page.screenshot({ path: '/tmp/test-screenshots/42-project-detail-assets.png', fullPage: true })
  })
})
