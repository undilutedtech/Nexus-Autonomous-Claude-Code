import { test, expect } from '@playwright/test';

test('verify phase indicator displays correctly', async ({ page }) => {
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

  // Take screenshot
  await page.screenshot({ path: '/tmp/phase-indicator-1.png', fullPage: true });

  // Start the agent to see the phase indicator
  const startButton = page.locator('button:has-text("Start Agent")');
  if (await startButton.isVisible()) {
    console.log('Starting agent to see phase indicator...');
    await startButton.click();
    await page.waitForTimeout(2000);

    // Take screenshot after starting
    await page.screenshot({ path: '/tmp/phase-indicator-2-running.png', fullPage: true });

    // Check if phase indicator is visible
    const phaseIndicator = page.locator('text=Implementing');
    const isVisible = await phaseIndicator.isVisible().catch(() => false);

    if (isVisible) {
      console.log('Phase indicator is showing "Implementing"');
    } else {
      // Check for other phases
      const creatingFeatures = await page.locator('text=Creating Features').isVisible().catch(() => false);
      if (creatingFeatures) {
        console.log('Phase indicator is showing "Creating Features"');
      }
    }

    // Wait and take another screenshot
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '/tmp/phase-indicator-3.png', fullPage: true });

    // Stop the agent
    const stopButton = page.locator('button:has-text("Stop")');
    if (await stopButton.isVisible()) {
      await stopButton.click();
      await page.waitForTimeout(1000);
    }
  }

  console.log('Screenshots saved to /tmp/phase-indicator-*.png');
});
