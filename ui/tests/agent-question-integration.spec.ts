import { test, expect } from '@playwright/test'

/**
 * Integration tests for agent question asking flow.
 *
 * This tests the complete flow:
 * 1. Question is created (simulating MCP tool call)
 * 2. WebSocket broadcasts question to UI
 * 3. Modal appears for user to answer
 * 4. User submits answer
 * 5. Answer is available for polling
 */

test.describe('Agent Question Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token before loading
    await page.addInitScript(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright')
    })

    // Clear any existing questions
    await page.request.delete('http://localhost:8000/api/projects/ted/questions')
  })

  test.afterEach(async ({ page }) => {
    // Clean up questions
    await page.request.delete('http://localhost:8000/api/projects/ted/questions')
  })

  test('complete question-answer flow with option selection', async ({ page }) => {
    // Navigate to project page first
    await page.goto('http://localhost:5173/projects/ted')
    await page.waitForTimeout(1500) // Wait for WebSocket to connect

    // Simulate MCP tool creating a question (as if agent called ask_user_question)
    const questionResponse = await page.request.post('http://localhost:8000/api/projects/ted/questions', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'Which state management solution should I use?',
        context: 'The app has complex state that needs to be shared across multiple components.',
        options: ['Pinia (Recommended)', 'Vuex', 'Composables only']
      }
    })
    expect(questionResponse.ok()).toBeTruthy()
    const questionData = await questionResponse.json()
    const questionId = questionData.question.id

    // Wait for modal to appear (WebSocket should broadcast it)
    const modal = page.locator('text=Agent Question')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Verify question content is displayed
    await expect(page.locator('text=Which state management solution')).toBeVisible()
    await expect(page.locator('text=complex state')).toBeVisible()

    // Verify options are displayed
    await expect(page.locator('button:has-text("Pinia (Recommended)")')).toBeVisible()
    await expect(page.locator('button:has-text("Vuex")')).toBeVisible()
    await expect(page.locator('button:has-text("Composables only")')).toBeVisible()

    // Select an option
    await page.locator('button:has-text("Pinia (Recommended)")').click()

    // Submit the answer
    await page.locator('button:has-text("Submit Answer")').click()
    await page.waitForTimeout(500)

    // Modal should close
    await expect(modal).not.toBeVisible()

    // Verify the answer is stored correctly (as MCP tool would poll for it)
    const answerResponse = await page.request.get(`http://localhost:8000/api/projects/ted/questions`)
    const answerData = await answerResponse.json()
    const answeredQuestion = answerData.questions.find((q: any) => q.id === questionId)

    expect(answeredQuestion.answered).toBe(true)
    expect(answeredQuestion.answer).toBe('Pinia (Recommended)')
  })

  test('question modal appears automatically when question is pending', async ({ page }) => {
    // Create a question BEFORE navigating to the page
    const questionResponse = await page.request.post('http://localhost:8000/api/projects/ted/questions', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'Should dark mode be the default theme?',
        options: ['Yes, dark mode', 'No, light mode']
      }
    })
    expect(questionResponse.ok()).toBeTruthy()

    // Now navigate to the project page
    await page.goto('http://localhost:5173/projects/ted')

    // Modal should appear automatically
    const modal = page.locator('text=Agent Question')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Verify the question is shown
    await expect(page.locator('text=dark mode be the default')).toBeVisible()
  })

  test('supports custom text answer when no option fits', async ({ page }) => {
    // Navigate to project page
    await page.goto('http://localhost:5173/projects/ted')
    await page.waitForTimeout(1500)

    // Create a question
    const questionResponse = await page.request.post('http://localhost:8000/api/projects/ted/questions', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'What primary color should the app use?',
        options: ['Blue', 'Green', 'Purple']
      }
    })
    expect(questionResponse.ok()).toBeTruthy()
    const questionData = await questionResponse.json()
    const questionId = questionData.question.id

    // Wait for modal
    const modal = page.locator('text=Agent Question')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Enter a custom answer instead of selecting an option
    const textarea = page.locator('textarea')
    await textarea.fill('Use a gradient from teal (#14b8a6) to cyan (#06b6d4)')

    // Submit
    await page.locator('button:has-text("Submit Answer")').click()
    await page.waitForTimeout(500)

    // Verify custom answer was saved
    const answerResponse = await page.request.get(`http://localhost:8000/api/projects/ted/questions`)
    const answerData = await answerResponse.json()
    const answeredQuestion = answerData.questions.find((q: any) => q.id === questionId)

    expect(answeredQuestion.answer).toContain('gradient from teal')
  })

  test('handles question without options (free-form only)', async ({ page }) => {
    // Navigate to project page
    await page.goto('http://localhost:5173/projects/ted')
    await page.waitForTimeout(1500)

    // Create a question without options
    const questionResponse = await page.request.post('http://localhost:8000/api/projects/ted/questions', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'What should be the app name displayed in the header?',
        context: 'This will appear in the navbar and browser tab title.'
      }
    })
    expect(questionResponse.ok()).toBeTruthy()
    const questionData = await questionResponse.json()
    const questionId = questionData.question.id

    // Wait for modal
    const modal = page.locator('text=Agent Question')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Enter answer in textarea (should be the only input option)
    const textarea = page.locator('textarea')
    await textarea.fill('TaskFlow Pro')

    // Submit
    await page.locator('button:has-text("Submit Answer")').click()
    await page.waitForTimeout(500)

    // Verify answer
    const answerResponse = await page.request.get(`http://localhost:8000/api/projects/ted/questions`)
    const answerData = await answerResponse.json()
    const answeredQuestion = answerData.questions.find((q: any) => q.id === questionId)

    expect(answeredQuestion.answer).toBe('TaskFlow Pro')
  })
})
