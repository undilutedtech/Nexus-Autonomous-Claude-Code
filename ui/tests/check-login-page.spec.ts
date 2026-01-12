import { test } from '@playwright/test';

test('screenshot login page', async ({ page }) => {
  await page.goto('/signin');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/tmp/current-login-page.png', fullPage: true });
  console.log('Screenshot saved to /tmp/current-login-page.png');
});
