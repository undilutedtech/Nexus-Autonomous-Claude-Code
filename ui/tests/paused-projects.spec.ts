import { test, expect } from '@playwright/test';

test('verify paused projects page', async ({ page }) => {
  // Set auth token before loading
  await page.addInitScript(() => {
    localStorage.setItem('nexus_token', 'test-token-for-playwright');
  });

  // Listen to API calls
  page.on('response', response => {
    if (response.url().includes('/api/')) {
      console.log(`API ${response.status()}: ${response.url()}`);
    }
  });

  // Go to paused projects page
  await page.goto('/projects/paused');
  await page.waitForTimeout(2000);

  await page.screenshot({ path: '/tmp/paused-projects.png', fullPage: true });

  // Check page content
  const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 500));
  console.log('Page content:', bodyText.substring(0, 300));

  // Check if there are any project cards
  const projectCards = page.locator('.rounded-2xl.border-warning-200');
  const count = await projectCards.count();
  console.log(`Found ${count} paused project cards`);

  // Check for loading state
  const isLoading = await page.locator('.animate-spin').isVisible();
  console.log(`Loading spinner visible: ${isLoading}`);

  // Check for empty state
  const emptyState = await page.locator('text=No paused projects').isVisible();
  console.log(`Empty state visible: ${emptyState}`);
});
