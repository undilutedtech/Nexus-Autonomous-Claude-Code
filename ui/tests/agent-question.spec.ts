import { test, expect } from '@playwright/test'

test.describe('Agent Questions', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token before loading
    await page.addInitScript(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright')
    })
  })

  test('shows question modal when pending question exists', async ({ page }) => {
    // First, create a test question via API
    const questionResponse = await page.request.post('http://localhost:8000/api/projects/ted/questions', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'Which database should we use for this feature?',
        context: 'The agent needs to implement data persistence.',
        options: ['PostgreSQL', 'MongoDB', 'SQLite']
      }
    })
    expect(questionResponse.ok()).toBeTruthy()
    const questionData = await questionResponse.json()
    const questionId = questionData.question.id

    // Navigate to the project detail page
    await page.goto('http://localhost:5173/projects/ted')
    await page.waitForTimeout(2000) // Wait for WebSocket to connect and poll

    // Check if the question modal is visible
    const modal = page.locator('text=Agent Question')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Check that the question text is displayed
    const questionText = page.locator('text=Which database should we use')
    await expect(questionText).toBeVisible()

    // Check that the context is displayed
    const contextText = page.locator('text=The agent needs to implement data persistence')
    await expect(contextText).toBeVisible()

    // Check that options are displayed
    await expect(page.locator('button:has-text("PostgreSQL")')).toBeVisible()
    await expect(page.locator('button:has-text("MongoDB")')).toBeVisible()
    await expect(page.locator('button:has-text("SQLite")')).toBeVisible()

    // Take a screenshot
    await page.screenshot({ path: '/tmp/agent-question-modal.png', fullPage: true })

    // Select an option
    await page.locator('button:has-text("PostgreSQL")').click()
    await page.waitForTimeout(300)

    // Submit the answer
    await page.locator('button:has-text("Submit Answer")').click()
    await page.waitForTimeout(1000)

    // Modal should be closed
    await expect(modal).not.toBeVisible()

    // Verify the question was answered via API
    const answeredResponse = await page.request.get(`http://localhost:8000/api/projects/ted/questions`)
    const answeredData = await answeredResponse.json()
    const answeredQuestion = answeredData.questions.find((q: any) => q.id === questionId)
    expect(answeredQuestion.answered).toBe(true)
    expect(answeredQuestion.answer).toBe('PostgreSQL')
  })

  test('allows custom text answer', async ({ page }) => {
    // Create a question
    const questionResponse = await page.request.post('http://localhost:8000/api/projects/ted/questions', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'What should be the primary color?',
        options: ['Blue', 'Green', 'Red']
      }
    })
    expect(questionResponse.ok()).toBeTruthy()
    const questionData = await questionResponse.json()
    const questionId = questionData.question.id

    // Navigate to project
    await page.goto('http://localhost:5173/projects/ted')
    await page.waitForTimeout(2000)

    // Wait for modal
    const modal = page.locator('text=Agent Question')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Type a custom answer
    const textarea = page.locator('textarea')
    await textarea.fill('I prefer a custom purple theme with #6B46C1')
    await page.waitForTimeout(300)

    // Submit
    await page.locator('button:has-text("Submit Answer")').click()
    await page.waitForTimeout(1000)

    // Verify
    const answeredResponse = await page.request.get(`http://localhost:8000/api/projects/ted/questions`)
    const answeredData = await answeredResponse.json()
    const answeredQuestion = answeredData.questions.find((q: any) => q.id === questionId)
    expect(answeredQuestion.answered).toBe(true)
    expect(answeredQuestion.answer).toBe('I prefer a custom purple theme with #6B46C1')
  })

  test('can skip question', async ({ page }) => {
    // Create a question
    const questionResponse = await page.request.post('http://localhost:8000/api/projects/ted/questions', {
      headers: { 'Content-Type': 'application/json' },
      data: {
        question: 'Skip test question?'
      }
    })
    expect(questionResponse.ok()).toBeTruthy()
    const questionData = await questionResponse.json()
    const questionId = questionData.question.id

    // Navigate to project
    await page.goto('http://localhost:5173/projects/ted')
    await page.waitForTimeout(2000)

    // Wait for modal
    const modal = page.locator('text=Agent Question')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Click Skip
    await page.locator('button:has-text("Skip")').click()
    await page.waitForTimeout(1000)

    // Modal should close
    await expect(modal).not.toBeVisible()

    // Verify question was marked as skipped
    const answeredResponse = await page.request.get(`http://localhost:8000/api/projects/ted/questions`)
    const answeredData = await answeredResponse.json()
    const answeredQuestion = answeredData.questions.find((q: any) => q.id === questionId)
    expect(answeredQuestion.answered).toBe(true)
    expect(answeredQuestion.answer).toBe('[SKIPPED]')
  })

  test.afterEach(async ({ page }) => {
    // Clean up questions
    await page.request.delete('http://localhost:8000/api/projects/ted/questions')
  })
})
