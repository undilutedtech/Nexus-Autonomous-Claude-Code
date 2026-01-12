import { test as base, expect, Page, BrowserContext } from '@playwright/test'

// Test user credentials - create fresh user per test run
let testUserCount = 0

interface AuthFixtures {
  authenticatedPage: Page
  authContext: BrowserContext
}

async function signup(page: Page): Promise<string> {
  const timestamp = Date.now()
  const suffix = testUserCount++
  const email = `testuser${timestamp}${suffix}@test.com`
  const username = `testuser${timestamp}${suffix}`
  const password = 'Test1234!'

  await page.goto('/signup')
  await page.waitForLoadState('networkidle')

  await page.locator('#email').fill(email)
  await page.locator('#username').fill(username)
  await page.locator('#password').fill(password)
  await page.locator('#confirmPassword').fill(password)
  await page.click('button[type="submit"]')

  // Wait for redirect after successful signup
  await page.waitForTimeout(2000)

  // Navigate to dashboard to ensure we're on an authenticated page
  await page.goto('/dashboard')
  await page.waitForLoadState('networkidle')

  // Get the token from localStorage
  const token = await page.evaluate(() => localStorage.getItem('nexus_token'))
  return token || ''
}

// Extended test with authenticated page fixture
export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext()
    const page = await context.newPage()

    // Sign up to get authenticated
    await signup(page)

    // Use the authenticated page
    await use(page)

    // Cleanup
    await context.close()
  },

  authContext: async ({ browser }, use) => {
    const context = await browser.newContext()
    const page = await context.newPage()

    // Sign up to get authenticated
    await signup(page)

    // Use the context (which now has auth cookies/storage)
    await use(context)

    // Cleanup
    await context.close()
  },
})

export { expect }

// Helper to check if we're authenticated
export async function isAuthenticated(page: Page): Promise<boolean> {
  const token = await page.evaluate(() => localStorage.getItem('nexus_token'))
  return !!token
}

// Helper to get auth token
export async function getAuthToken(page: Page): Promise<string | null> {
  return page.evaluate(() => localStorage.getItem('nexus_token'))
}
