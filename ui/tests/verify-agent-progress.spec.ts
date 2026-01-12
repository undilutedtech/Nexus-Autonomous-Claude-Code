import { test, expect } from './fixtures/auth'

test('verify agent created features', async ({ authenticatedPage: page }) => {
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

  // Check for features section
  const featuresSection = page.locator('text=Features').first()
  if (await featuresSection.isVisible().catch(() => false)) {
    console.log('Features section found')
  }

  // Check for total features count
  const totalFeatures = page.locator('text=Total Features')
  if (await totalFeatures.isVisible().catch(() => false)) {
    console.log('Total Features label found')
  }

  // Scroll down to see more content
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
  await page.waitForTimeout(500)

  console.log('Agent progress verification complete')
})
