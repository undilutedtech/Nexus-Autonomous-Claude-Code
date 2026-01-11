import { test, expect } from '@playwright/test';

test('verify agent created features', async ({ page }) => {
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

  // Take screenshot showing features
  await page.screenshot({ path: '/tmp/agent-progress-1.png', fullPage: true });

  // Check total features count
  const totalFeatures = page.locator('text=Total Features').locator('..').locator('text=/\\d+/').first();
  const count = await totalFeatures.textContent().catch(() => '0');
  console.log(`Total Features: ${count}`);

  // Wait for page to update
  await page.waitForTimeout(2000);

  // Take another screenshot
  await page.screenshot({ path: '/tmp/agent-progress-2.png', fullPage: true });

  // Scroll down to see features section
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/agent-progress-3-features.png', fullPage: true });

  console.log('Screenshots saved to /tmp/agent-progress-*.png');
});
