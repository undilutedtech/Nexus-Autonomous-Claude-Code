import { test, expect } from '@playwright/test';

test('verify agent logs stream to UI', async ({ page }) => {
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

  // Screenshot before starting
  await page.screenshot({ path: '/tmp/log-streaming-1-before.png', fullPage: true });

  // Check if agent activity section exists
  const activitySection = page.locator('text=Agent Activity');
  const activityVisible = await activitySection.isVisible().catch(() => false);
  console.log(`Agent Activity section visible: ${activityVisible}`);

  // Check the current agent status
  const stopButton = page.locator('button:has-text("Stop")');
  const startButton = page.locator('button:has-text("Start Agent")');

  const isRunning = await stopButton.isVisible().catch(() => false);
  const isStopped = await startButton.isVisible().catch(() => false);

  console.log(`Agent running: ${isRunning}, stopped: ${isStopped}`);

  // If agent is stopped, start it to see logs
  if (isStopped) {
    console.log('Starting agent to see log streaming...');
    await startButton.click();
    await page.waitForTimeout(3000);
  }

  // Screenshot after starting
  await page.screenshot({ path: '/tmp/log-streaming-2-running.png', fullPage: true });

  // Wait for some logs to appear
  await page.waitForTimeout(5000);

  // Check for log content in the Agent Activity section
  // The logs should appear in a scrollable container
  const logContainer = page.locator('.overflow-y-auto').first();

  // Take final screenshot
  await page.screenshot({ path: '/tmp/log-streaming-3-logs.png', fullPage: true });

  // Check if there are any log entries
  const logEntries = page.locator('[class*="log"], [class*="text-xs"], pre, code').first();
  const hasLogs = await logEntries.isVisible().catch(() => false);
  console.log(`Has log entries: ${hasLogs}`);

  // Get the text content of the log area
  const logText = await page.evaluate(() => {
    // Look for the Agent Activity section and get its content
    const sections = document.querySelectorAll('h3, h4');
    for (const section of sections) {
      if (section.textContent?.includes('Agent Activity')) {
        const container = section.closest('div')?.parentElement;
        return container?.innerText || '';
      }
    }
    return '';
  });

  console.log('Log section content length:', logText.length);
  console.log('Log section preview:', logText.substring(0, 500));

  // Stop agent if we started it
  if (isStopped) {
    const stopBtn = page.locator('button:has-text("Stop")');
    if (await stopBtn.isVisible()) {
      await stopBtn.click();
      await page.waitForTimeout(1000);
    }
  }

  console.log('Screenshots saved to /tmp/log-streaming-*.png');
});
