import { test, expect } from '@playwright/test';

test('check agent status and activity', async ({ page }) => {
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
  await page.screenshot({ path: '/tmp/check-agent-1.png', fullPage: true });

  // Check status
  const runningIndicator = page.locator('text=Running').first();
  const isRunning = await runningIndicator.isVisible().catch(() => false);
  console.log(`Agent running: ${isRunning}`);

  // Check for any logs in the activity section
  const activitySection = page.locator('.bg-gray-900, [class*="activity"]').last();
  const activityText = await activitySection.textContent().catch(() => '');
  console.log(`Activity content: ${activityText?.substring(0, 200)}`);

  // Wait for more activity
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/tmp/check-agent-2.png', fullPage: true });

  // Check features
  const featuresSection = page.locator('text=Total Features').first();
  const featuresText = await featuresSection.textContent().catch(() => '');
  console.log(`Features: ${featuresText}`);

  console.log('Screenshots saved to /tmp/check-agent-*.png');
});
