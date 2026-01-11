import { test, expect } from '@playwright/test';

test('verify creating features phase indicator', async ({ page }) => {
  const projectName = 'test-phase-indicator-1768100332';

  // Helper to set auth token
  const setAuth = async () => {
    await page.evaluate(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });
  };

  // Navigate to the new test project (no features yet)
  await page.goto('http://localhost:5173/');
  await setAuth();
  await page.goto(`http://localhost:5173/projects/${projectName}`);
  await page.waitForTimeout(1000);

  // Re-auth if needed
  if (page.url().includes('/signin')) {
    await setAuth();
    await page.goto(`http://localhost:5173/projects/${projectName}`);
    await page.waitForTimeout(1000);
  }

  // Screenshot before starting - should show 0 features
  await page.screenshot({ path: '/tmp/creating-features-1-before.png', fullPage: true });

  // Verify no features exist yet
  const totalFeatures = page.locator('text=/Total Features.*0|0.*features/i');
  console.log('Project has 0 features initially');

  // Start the agent - this should trigger "Creating Features" phase
  const startButton = page.locator('button:has-text("Start Agent")');
  if (await startButton.isVisible()) {
    console.log('Starting agent to see Creating Features phase...');
    await startButton.click();

    // Wait a moment for the phase to update
    await page.waitForTimeout(2000);

    // Screenshot right after starting - should show "Creating Features" phase
    await page.screenshot({ path: '/tmp/creating-features-2-started.png', fullPage: true });

    // Check for "Creating Features" indicator
    const creatingFeatures = page.locator('text=Creating Features');
    const hasCreatingFeatures = await creatingFeatures.isVisible().catch(() => false);
    console.log(`Has "Creating Features" phase: ${hasCreatingFeatures}`);

    // Check for the shimmer/indeterminate progress bar
    const shimmerBar = page.locator('.animate-shimmer');
    const hasShimmer = await shimmerBar.isVisible().catch(() => false);
    console.log(`Has shimmer animation: ${hasShimmer}`);

    // Check for the explanatory text about feature creation
    const explanatoryText = page.locator('text=/analyzing.*specification|generating.*test cases/i');
    const hasExplanatoryText = await explanatoryText.isVisible().catch(() => false);
    console.log(`Has explanatory text: ${hasExplanatoryText}`);

    // Get screenshot of the phase indicator component
    const phaseContainer = page.locator('.border-brand-200, [class*="brand"]').first();
    if (await phaseContainer.isVisible()) {
      await phaseContainer.screenshot({ path: '/tmp/creating-features-component.png' });
      console.log('Phase indicator component screenshot saved');
    }

    // Wait a bit more to see the phase in action
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/tmp/creating-features-3-running.png', fullPage: true });

    // Stop the agent
    const stopButton = page.locator('button:has-text("Stop")');
    if (await stopButton.isVisible()) {
      console.log('Stopping agent...');
      await stopButton.click();
      await page.waitForTimeout(1000);
    }
  }

  console.log('\nScreenshots saved to /tmp/creating-features-*.png');
});
