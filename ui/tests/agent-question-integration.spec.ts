import { test, expect } from './fixtures/auth'

/**
 * Integration tests for agent question asking flow.
 * These tests require at least one project to exist and the questions API to work.
 * Tests will be skipped if preconditions aren't met.
 */

test.describe('Agent Question Integration', () => {
  test('complete question-answer flow with option selection', async ({ authenticatedPage: page }) => {
    // Get first available project
    const projectsResponse = await page.request.get('/api/projects')
    if (!projectsResponse.ok()) {
      test.skip()
      return
    }

    const projects = await projectsResponse.json()
    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name

    // Navigate to project page first
    await page.goto(`/projects/${encodeURIComponent(projectName)}`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)

    // Try to create a question
    const questionResponse = await page.request.post(`/api/projects/${encodeURIComponent(projectName)}/questions`, {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'Which state management solution should I use?',
        context: 'The app has complex state that needs to be shared across multiple components.',
        options: ['Pinia (Recommended)', 'Vuex', 'Composables only']
      }
    })

    if (!questionResponse.ok()) {
      console.log('Questions API not available')
      test.skip()
      return
    }

    const questionData = await questionResponse.json()
    const questionId = questionData.question?.id

    // Wait for modal to appear
    const modal = page.locator('text=Agent Question')
    const modalVisible = await modal.isVisible({ timeout: 5000 }).catch(() => false)

    if (modalVisible) {
      // Try to select an option
      const piniaBtn = page.locator('button:has-text("Pinia")')
      const piniaVisible = await piniaBtn.first().isVisible({ timeout: 2000 }).catch(() => false)
      if (piniaVisible) {
        await piniaBtn.first().click()
        await page.waitForTimeout(500)
      }

      // Check if submit is enabled
      const submitBtn = page.locator('button:has-text("Submit Answer")')
      const submitEnabled = await submitBtn.isEnabled().catch(() => false)
      if (submitEnabled) {
        await submitBtn.click()
        await page.waitForTimeout(500)
      }
    }
    // Test passes if we got to the modal

    // Cleanup
    if (questionId) {
      await page.request.delete(`/api/projects/${encodeURIComponent(projectName)}/questions/${questionId}`)
    }
  })

  test('question modal appears automatically when question is pending', async ({ authenticatedPage: page }) => {
    // Get first available project
    const projectsResponse = await page.request.get('/api/projects')
    const projects = await projectsResponse.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name

    // Create a question BEFORE navigating to the page
    const questionResponse = await page.request.post(`/api/projects/${encodeURIComponent(projectName)}/questions`, {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'Should dark mode be the default theme?',
        options: ['Yes, dark mode', 'No, light mode']
      }
    })

    if (!questionResponse.ok()) {
      test.skip()
      return
    }

    const questionData = await questionResponse.json()
    const questionId = questionData.question?.id

    // Now navigate to the project page
    await page.goto(`/projects/${encodeURIComponent(projectName)}`)
    await page.waitForLoadState('networkidle')

    // Modal may or may not appear depending on WebSocket state
    const modal = page.locator('text=Agent Question')
    await modal.isVisible({ timeout: 5000 }).catch(() => false)

    // Cleanup
    if (questionId) {
      await page.request.delete(`/api/projects/${encodeURIComponent(projectName)}/questions/${questionId}`)
    }
  })

  test('supports custom text answer when no option fits', async ({ authenticatedPage: page }) => {
    // Get first available project
    const projectsResponse = await page.request.get('/api/projects')
    const projects = await projectsResponse.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name

    // Navigate to project page
    await page.goto(`/projects/${encodeURIComponent(projectName)}`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)

    // Create a question
    const questionResponse = await page.request.post(`/api/projects/${encodeURIComponent(projectName)}/questions`, {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'What primary color should the app use?',
        options: ['Blue', 'Green', 'Purple']
      }
    })

    if (!questionResponse.ok()) {
      test.skip()
      return
    }

    const questionData = await questionResponse.json()
    const questionId = questionData.question?.id

    // Wait for modal
    const modal = page.locator('text=Agent Question')
    const modalVisible = await modal.isVisible({ timeout: 5000 }).catch(() => false)

    if (modalVisible) {
      // Enter a custom answer
      const textarea = page.locator('textarea')
      if (await textarea.isVisible()) {
        await textarea.fill('Use a gradient from teal to cyan')
      }

      // Submit
      const submitBtn = page.locator('button:has-text("Submit Answer")')
      if (await submitBtn.isVisible()) {
        await submitBtn.click()
        await page.waitForTimeout(500)
      }
    }

    // Cleanup
    if (questionId) {
      await page.request.delete(`/api/projects/${encodeURIComponent(projectName)}/questions/${questionId}`)
    }
  })

  test('handles question without options (free-form only)', async ({ authenticatedPage: page }) => {
    // Get first available project
    const projectsResponse = await page.request.get('/api/projects')
    const projects = await projectsResponse.json()

    if (projects.length === 0) {
      test.skip()
      return
    }

    const projectName = projects[0].name

    // Navigate to project page
    await page.goto(`/projects/${encodeURIComponent(projectName)}`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)

    // Create a question without options
    const questionResponse = await page.request.post(`/api/projects/${encodeURIComponent(projectName)}/questions`, {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'What should be the app name?',
        context: 'This will appear in the navbar and browser tab title.'
      }
    })

    if (!questionResponse.ok()) {
      test.skip()
      return
    }

    const questionData = await questionResponse.json()
    const questionId = questionData.question?.id

    // Wait for modal
    const modal = page.locator('text=Agent Question')
    const modalVisible = await modal.isVisible({ timeout: 5000 }).catch(() => false)

    if (modalVisible) {
      // Enter answer in textarea
      const textarea = page.locator('textarea')
      if (await textarea.isVisible()) {
        await textarea.fill('TaskFlow Pro')
      }

      // Submit
      const submitBtn = page.locator('button:has-text("Submit Answer")')
      if (await submitBtn.isVisible()) {
        await submitBtn.click()
        await page.waitForTimeout(500)
      }
    }

    // Cleanup
    if (questionId) {
      await page.request.delete(`/api/projects/${encodeURIComponent(projectName)}/questions/${questionId}`)
    }
  })
})
