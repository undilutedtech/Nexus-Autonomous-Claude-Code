import { test, expect } from './fixtures/auth'

test('start agent on test project', async ({ authenticatedPage: page }) => {
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

  // Navigate to project detail
  await page.goto(`/projects/${encodeURIComponent(projectName)}`)
  await page.waitForLoadState('networkidle')

  // Page should load
  await expect(page.locator('#app')).toBeVisible()

  // Look for Start Agent button
  const startButton = page.locator('button:has-text("Start Agent")')
  const startButtonVisible = await startButton.isVisible().catch(() => false)

  if (startButtonVisible) {
    console.log('Start Agent button found')
    // We won't actually start the agent as it would trigger real work
    // Just verify the button exists and is clickable
    await expect(startButton).toBeEnabled()
    console.log('Start Agent button is enabled')
  } else {
    // Agent might already be running
    const stopButton = page.locator('button:has-text("Stop")')
    const resumeButton = page.locator('button:has-text("Resume")')
    const isRunning = await stopButton.isVisible().catch(() => false)
    const isPaused = await resumeButton.isVisible().catch(() => false)
    console.log(`Agent state - Running: ${isRunning}, Paused: ${isPaused}`)
  }

  console.log('Test complete!')
})
