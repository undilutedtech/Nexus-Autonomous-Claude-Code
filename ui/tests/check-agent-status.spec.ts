import { test, expect } from './fixtures/auth'

test('check agent status and activity', async ({ authenticatedPage: page }) => {
  // Get first available project
  const projectsResponse = await page.request.get('/api/projects')
  const projects = await projectsResponse.json()

  if (projects.length === 0) {
    console.log('No projects available, skipping test')
    test.skip()
    return
  }

  const projectName = projects[0].name
  console.log(`Testing with project: ${projectName}`)

  // Navigate to the project
  await page.goto(`/projects/${encodeURIComponent(projectName)}`)
  await page.waitForLoadState('networkidle')

  // Page should load
  await expect(page.locator('#app')).toBeVisible()

  // Check for status indicators
  const runningIndicator = page.locator('text=Running').first()
  const stoppedIndicator = page.locator('text=Stopped').first()
  const isRunning = await runningIndicator.isVisible().catch(() => false)
  const isStopped = await stoppedIndicator.isVisible().catch(() => false)
  console.log(`Agent running: ${isRunning}, stopped: ${isStopped}`)

  // Check for features section
  const featuresSection = page.locator('text=Features').first()
  if (await featuresSection.isVisible().catch(() => false)) {
    console.log('Features section found')
  }

  console.log('Agent status check completed')
})
