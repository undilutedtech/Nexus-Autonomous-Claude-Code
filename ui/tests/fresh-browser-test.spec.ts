import { test, expect } from '@playwright/test'

test('fresh browser - create project button', async ({ browser }) => {
  // Create a fresh context (no cookies, no cache)
  const context = await browser.newContext()
  const page = await context.newPage()

  // Signup first
  await page.goto('/signup')
  await page.waitForLoadState('networkidle')

  const timestamp = Date.now()
  await page.locator('#email').fill(`fresh${timestamp}@test.com`)
  await page.locator('#username').fill(`freshuser${timestamp}`)
  await page.locator('#password').fill('Test1234!')
  await page.locator('#confirmPassword').fill('Test1234!')
  await page.click('button[type="submit"]')
  await page.waitForTimeout(3000)

  // Now go to projects
  await page.goto('/projects')
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(1000)

  // Look for New Project link in main content area (use .first() since there are multiple)
  const newProjectLink = page.locator('a[href="/projects/new"]').first()
  await expect(newProjectLink).toBeVisible({ timeout: 5000 })

  // Click and verify navigation
  await newProjectLink.click()
  await page.waitForURL('**/projects/new')
  expect(page.url()).toContain('/projects/new')

  await context.close()
})

test('projects page shows new project options', async ({ browser }) => {
  const context = await browser.newContext()
  const page = await context.newPage()

  // Signup
  await page.goto('/signup')
  await page.waitForLoadState('networkidle')

  const timestamp = Date.now()
  await page.locator('#email').fill(`test${timestamp}@test.com`)
  await page.locator('#username').fill(`testuser${timestamp}`)
  await page.locator('#password').fill('Test1234!')
  await page.locator('#confirmPassword').fill('Test1234!')
  await page.click('button[type="submit"]')
  await page.waitForTimeout(3000)

  // Go to projects page
  await page.goto('/projects')
  await page.waitForLoadState('networkidle')

  // Verify multiple New Project entry points exist
  // 1. Header button
  const headerButton = page.locator('header button:has-text("New Project"), header a:has-text("New Project")')
  await expect(headerButton.first()).toBeVisible()

  // 2. Sidebar link
  const sidebarLink = page.locator('aside a:has-text("New Project"), nav a:has-text("New Project")')
  await expect(sidebarLink.first()).toBeVisible()

  // 3. Main content area link
  const mainLink = page.locator('main a[href="/projects/new"], .space-y-6 a[href="/projects/new"]')
  await expect(mainLink.first()).toBeVisible()

  await context.close()
})
