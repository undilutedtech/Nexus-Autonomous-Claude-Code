import { test, expect } from '@playwright/test';

test('start agent on test project', async ({ page }) => {
  // Helper to set auth token
  const setAuth = async () => {
    await page.evaluate(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });
  };

  // Set auth token and go to projects
  await page.goto('http://localhost:5173/');
  await setAuth();
  await page.goto('http://localhost:5173/projects');
  await page.waitForTimeout(1000);

  // Take screenshot of projects
  await page.screenshot({ path: '/tmp/start-agent-1-projects.png', fullPage: true });

  // Find a test project card - get its href and navigate directly
  const testProjectLink = page.locator('a[href*="test-project-"]').first();
  const href = await testProjectLink.getAttribute('href');
  console.log(`Found project link: ${href}`);

  // Navigate directly with auth
  await setAuth();
  await page.goto(`http://localhost:5173${href}`);
  await page.waitForTimeout(1000);

  // Check if redirected to signin, re-auth if needed
  if (page.url().includes('/signin')) {
    console.log('Re-authenticating...');
    await setAuth();
    await page.goto(`http://localhost:5173${href}`);
    await page.waitForTimeout(1000);
  }

  // Take screenshot of project detail
  await page.screenshot({ path: '/tmp/start-agent-2-detail.png', fullPage: true });

  // Click Start Agent button
  console.log('Clicking Start Agent button...');
  const startButton = page.locator('button:has-text("Start Agent")');
  await expect(startButton).toBeVisible();
  await startButton.click();

  // Wait for agent to start
  await page.waitForTimeout(2000);

  // Take screenshot after starting
  await page.screenshot({ path: '/tmp/start-agent-3-started.png', fullPage: true });

  // Check agent status changed
  const statusIndicator = page.locator('text=Running').first();
  const isRunning = await statusIndicator.isVisible().catch(() => false);

  if (isRunning) {
    console.log('Agent is now RUNNING!');
  } else {
    // Check for initializing or other status
    const pageContent = await page.content();
    if (pageContent.includes('Initializing') || pageContent.includes('Starting')) {
      console.log('Agent is initializing...');
    } else if (pageContent.includes('Stopped')) {
      console.log('Agent is still stopped - check logs for errors');
    }
  }

  // Wait a bit and check agent activity
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/start-agent-4-activity.png', fullPage: true });

  // Check for activity in the Agent Activity section
  const activitySection = page.locator('text=Agent Activity').first();
  await expect(activitySection).toBeVisible();

  console.log('Check screenshots in /tmp/start-agent-*.png');
  console.log('Test complete!');
});
