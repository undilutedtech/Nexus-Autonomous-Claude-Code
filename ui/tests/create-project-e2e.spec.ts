import { test, expect } from './fixtures/auth'

test('create project through wizard end-to-end', async ({ authenticatedPage: page }) => {
  // Navigate to new project wizard
  await page.goto('/projects/new')
  await page.waitForLoadState('networkidle')

  console.log('=== STEP 1: Project Details ===')

  // Fill in project name with timestamp to make it unique
  const projectName = `test-project-${Date.now()}`
  await page.fill('input[placeholder="my-awesome-project"]', projectName)

  // Fill in project path
  const projectPath = `/home/iris/Documents/projects/${projectName}`
  await page.fill('input[placeholder*="projects"]', projectPath)

  console.log(`Project name: ${projectName}`)
  console.log(`Project path: ${projectPath}`)

  // Click Continue to Step 2
  await page.click('button:has-text("Continue")')
  await page.waitForTimeout(500)

  console.log('=== STEP 2: App Specification ===')

  // Select Web Application template if visible
  const webAppBtn = page.locator('button:has-text("Web Application")')
  if (await webAppBtn.isVisible()) {
    await webAppBtn.click()
    await page.waitForTimeout(300)
  }

  // Click Continue to Step 3
  await page.click('button:has-text("Continue")')
  await page.waitForTimeout(500)

  console.log('=== STEP 3: Agent Configuration ===')

  // Click Continue to Step 4
  await page.click('button:has-text("Continue")')
  await page.waitForTimeout(500)

  console.log('=== STEP 4: Review & Create ===')

  // Verify review shows correct info
  await expect(page.locator('text=Review').first()).toBeVisible()

  // Uncheck "Start agent immediately" if checked
  const startAgentCheckbox = page.locator('#startAgent')
  if (await startAgentCheckbox.isVisible() && await startAgentCheckbox.isChecked()) {
    await startAgentCheckbox.uncheck()
  }

  console.log('=== CREATING PROJECT ===')

  // Click Create Project
  await page.click('button:has-text("Create Project")')

  // Wait for navigation to project detail page
  await page.waitForURL(/\/projects\//, { timeout: 15000 })
  await page.waitForTimeout(1000)

  console.log('Project created successfully!')

  // Verify we're on a project page
  const currentUrl = page.url()
  console.log(`Navigated to: ${currentUrl}`)
  expect(currentUrl).toContain('/projects/')

  // Navigate to projects list to verify it appears
  await page.goto('/projects')
  await page.waitForLoadState('networkidle')

  // Look for our project in the list
  const projectCard = page.locator(`text=${projectName}`)
  await expect(projectCard.first()).toBeVisible({ timeout: 10000 })

  console.log('Project appears in projects list!')
  console.log(`Successfully created project: ${projectName}`)
})
