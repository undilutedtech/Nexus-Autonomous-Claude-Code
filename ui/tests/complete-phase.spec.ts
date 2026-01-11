import { test, expect } from '@playwright/test';

test('verify complete phase indicator', async ({ page }) => {
  const BASE_URL = 'http://localhost:5176';

  // First, go to login page and set up storage
  await page.goto(`${BASE_URL}/login`);

  // Set the auth token
  await page.evaluate(() => {
    localStorage.setItem('nexus_token', 'test-token-for-playwright');
  });

  // Navigate directly to the Axionore project page (100% complete)
  await page.goto(`${BASE_URL}/projects/Axionore`);
  await page.waitForTimeout(2000);

  // If redirected to signin, set token again and retry
  if (page.url().includes('signin') || page.url().includes('login')) {
    console.log('Redirected to signin, setting token again...');
    await page.evaluate(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });
    await page.goto(`${BASE_URL}/projects/Axionore`);
    await page.waitForTimeout(2000);
  }

  await page.screenshot({ path: '/tmp/complete-phase-1.png', fullPage: true });
  console.log(`Current URL: ${page.url()}`);

  console.log('\n=== Checking Complete Phase Indicator ===\n');

  // Check for "Complete" indicator
  const completeH4 = page.locator('h4:has-text("Complete")');
  const hasCompleteH4 = await completeH4.isVisible().catch(() => false);
  console.log(`Has "Complete" h4 label: ${hasCompleteH4}`);

  // Check for success styling (green)
  const successContainer = page.locator('.border-success-200').first();
  const hasSuccessStyling = await successContainer.isVisible().catch(() => false);
  console.log(`Has success (green) container: ${hasSuccessStyling}`);

  // Check for 100% in stats
  const has100 = await page.locator('text=100%').isVisible().catch(() => false);
  console.log(`Has 100% displayed: ${has100}`);

  // Check for Axionore project name
  const hasAxionore = await page.locator('text=Axionore').first().isVisible().catch(() => false);
  console.log(`Has Axionore project name: ${hasAxionore}`);

  // Check for 261 total features
  const has261 = await page.locator('text=261').first().isVisible().catch(() => false);
  console.log(`Has 261 features: ${has261}`);

  // Get the phase indicator if visible
  const phaseIndicator = page.locator('[class*="border-success-200"]').first();
  if (await phaseIndicator.isVisible().catch(() => false)) {
    await phaseIndicator.screenshot({ path: '/tmp/complete-phase-component.png' });
    console.log('Complete phase indicator screenshot saved');
  }

  // Check page content
  const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 600));
  console.log(`Page preview: ${bodyText.substring(0, 400)}...`);

  await page.screenshot({ path: '/tmp/complete-phase-2.png', fullPage: true });
  console.log('\nScreenshots saved to /tmp/complete-phase-*.png');
});
