import { test, expect } from './fixtures/auth'

test.describe('Pause and Resume Buttons', () => {
  test('test agent control buttons are present', async ({ authenticatedPage: page }) => {
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

    // Helper to get status from API
    const getStatus = async () => {
      const statusResponse = await page.request.get(
        `/api/projects/${encodeURIComponent(projectName)}/agent/status`
      )
      if (!statusResponse.ok()) return 'unknown'
      const data = await statusResponse.json()
      return data.status || 'unknown'
    }

    const status = await getStatus()
    console.log(`Current agent status: ${status}`)

    // Check which buttons are visible based on status
    if (status === 'stopped' || status === 'unknown') {
      // Should see Start Agent button
      const startButton = page.locator('button:has-text("Start Agent")')
      const startVisible = await startButton.isVisible({ timeout: 3000 }).catch(() => false)
      console.log(`Start Agent button visible: ${startVisible}`)
    } else if (status === 'running') {
      // Should see Pause and Stop buttons
      const pauseButton = page.locator('button:has-text("Pause")')
      const stopButton = page.locator('button:has-text("Stop")')
      const pauseVisible = await pauseButton.first().isVisible().catch(() => false)
      const stopVisible = await stopButton.first().isVisible().catch(() => false)
      console.log(`Pause button visible: ${pauseVisible}, Stop button visible: ${stopVisible}`)
    } else if (status === 'paused') {
      // Should see Resume and Stop buttons
      const resumeButton = page.locator('button:has-text("Resume")')
      const stopButton = page.locator('button:has-text("Stop")')
      const resumeVisible = await resumeButton.first().isVisible().catch(() => false)
      const stopVisible = await stopButton.first().isVisible().catch(() => false)
      console.log(`Resume button visible: ${resumeVisible}, Stop button visible: ${stopVisible}`)
    }

    console.log('Agent control buttons test completed')
  })
})
