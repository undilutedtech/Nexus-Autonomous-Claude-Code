import { test, expect } from '@playwright/test';

test('verify phase indicator shows all elements correctly', async ({ page }) => {
  // Helper to set auth token
  const setAuth = async () => {
    await page.evaluate(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });
  };

  // Navigate to the test project
  await page.goto('http://localhost:5173/');
  await setAuth();
  await page.goto('http://localhost:5173/projects/test-project-1768098283820');
  await page.waitForTimeout(1000);

  // Re-auth if needed
  if (page.url().includes('/signin')) {
    await setAuth();
    await page.goto('http://localhost:5173/projects/test-project-1768098283820');
    await page.waitForTimeout(1000);
  }

  // Start the agent
  const startButton = page.locator('button:has-text("Start Agent")');
  if (await startButton.isVisible()) {
    console.log('Starting agent...');
    await startButton.click();
    await page.waitForTimeout(3000);
  }

  // Check for phase indicator elements
  console.log('\n=== Checking Phase Indicator Elements ===\n');

  // Check for "Implementing" text
  const implementing = page.locator('text=Implementing');
  const hasImplementing = await implementing.isVisible().catch(() => false);
  console.log(`Has "Implementing" label: ${hasImplementing}`);

  // Check for progress text (X/Y features)
  const progressText = page.locator('text=/\\d+\\/\\d+ features/');
  const hasProgress = await progressText.isVisible().catch(() => false);
  console.log(`Has progress text (X/Y features): ${hasProgress}`);
  if (hasProgress) {
    const text = await progressText.textContent();
    console.log(`Progress text: ${text}`);
  }

  // Check for time estimate badge
  const timeEstimate = page.locator('text=/\\d+-\\d+ min|~\\d+ min/');
  const hasTimeEstimate = await timeEstimate.isVisible().catch(() => false);
  console.log(`Has time estimate badge: ${hasTimeEstimate}`);
  if (hasTimeEstimate) {
    const text = await timeEstimate.textContent();
    console.log(`Time estimate: ${text}`);
  }

  // Check for progress bar
  const progressBar = page.locator('.bg-cyan-500, .bg-success-500').first();
  const hasProgressBar = await progressBar.isVisible().catch(() => false);
  console.log(`Has progress bar: ${hasProgressBar}`);

  // Check for phase description
  const description = page.locator('text=/Working through features|implementing/i');
  const hasDescription = await description.isVisible().catch(() => false);
  console.log(`Has phase description: ${hasDescription}`);

  // Take a focused screenshot of the phase indicator area
  await page.screenshot({ path: '/tmp/phase-indicator-detailed.png', fullPage: true });

  // Get the phase indicator container and screenshot just that area
  const phaseContainer = page.locator('.border-cyan-200, .border-brand-200').first();
  if (await phaseContainer.isVisible()) {
    await phaseContainer.screenshot({ path: '/tmp/phase-indicator-component.png' });
    console.log('\nPhase indicator component screenshot saved');
  }

  // Wait a bit longer to see progress
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/tmp/phase-indicator-after-wait.png', fullPage: true });

  // Stop the agent
  const stopButton = page.locator('button:has-text("Stop")');
  if (await stopButton.isVisible()) {
    await stopButton.click();
    await page.waitForTimeout(1000);
  }

  console.log('\n=== Screenshots saved to /tmp/phase-indicator-*.png ===');
});
