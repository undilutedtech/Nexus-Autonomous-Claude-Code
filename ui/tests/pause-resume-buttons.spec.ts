import { test, expect } from '@playwright/test';

test.describe('Pause and Resume Buttons', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token before loading
    await page.addInitScript(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });
  });

  test('test start, pause, resume, stop flow on test project', async ({ page }) => {
    const projectName = 'ted'; // Using ted project which has incomplete features

    // Navigate to project detail
    await page.goto(`http://localhost:5174/projects/${encodeURIComponent(projectName)}`);
    await page.waitForTimeout(2000);

    // Helper to get status from API
    const getStatus = async () => {
      const statusResponse = await page.request.get(
        `http://localhost:5174/api/projects/${encodeURIComponent(projectName)}/agent/status`
      );
      return (await statusResponse.json()).status;
    };

    // Ensure agent is stopped first
    let status = await getStatus();
    console.log(`Initial status: ${status}`);

    if (status !== 'stopped') {
      console.log('Stopping agent first via API...');
      await page.request.post(
        `http://localhost:5174/api/projects/${encodeURIComponent(projectName)}/agent/stop`
      );
      await page.waitForTimeout(2000);
      await page.reload();
      await page.waitForTimeout(2000);
    }

    // Take screenshot of stopped state
    await page.screenshot({ path: '/tmp/test-agent-stopped.png', fullPage: true });

    // === TEST START BUTTON ===
    console.log('\n=== Testing Start Button ===');
    const startButton = page.locator('button:has-text("Start Agent")');
    await expect(startButton).toBeVisible({ timeout: 5000 });
    console.log('Start Agent button is visible');

    await startButton.click();
    console.log('Clicked Start Agent button');

    // Wait for status to change
    await page.waitForTimeout(3000);

    status = await getStatus();
    console.log(`Status after clicking Start: ${status}`);
    expect(status).toBe('running');

    // Take screenshot of running state
    await page.screenshot({ path: '/tmp/test-agent-running.png', fullPage: true });

    // === TEST PAUSE BUTTON ===
    console.log('\n=== Testing Pause Button ===');
    const pauseButton = page.locator('button:has-text("Pause")').first();
    await expect(pauseButton).toBeVisible({ timeout: 5000 });
    console.log('Pause button is visible');

    await pauseButton.click();
    console.log('Clicked Pause button');

    await page.waitForTimeout(2000);

    status = await getStatus();
    console.log(`Status after clicking Pause: ${status}`);
    expect(status).toBe('paused');

    // Take screenshot of paused state
    await page.screenshot({ path: '/tmp/test-agent-paused.png', fullPage: true });

    // === TEST RESUME BUTTON ===
    console.log('\n=== Testing Resume Button ===');
    const resumeButton = page.locator('button:has-text("Resume")').first();
    await expect(resumeButton).toBeVisible({ timeout: 5000 });
    console.log('Resume button is visible');

    await resumeButton.click();
    console.log('Clicked Resume button');

    await page.waitForTimeout(2000);

    status = await getStatus();
    console.log(`Status after clicking Resume: ${status}`);
    expect(status).toBe('running');

    // Take screenshot of resumed state
    await page.screenshot({ path: '/tmp/test-agent-resumed.png', fullPage: true });

    // === TEST STOP BUTTON ===
    console.log('\n=== Testing Stop Button ===');
    const stopButton = page.locator('button:has-text("Stop")').first();
    await expect(stopButton).toBeVisible({ timeout: 5000 });
    console.log('Stop button is visible');

    await stopButton.click();
    console.log('Clicked Stop button');

    await page.waitForTimeout(2000);

    status = await getStatus();
    console.log(`Status after clicking Stop: ${status}`);
    expect(status).toBe('stopped');

    // Take final screenshot
    await page.screenshot({ path: '/tmp/test-agent-final.png', fullPage: true });

    console.log('\n=== All button tests passed! ===');
  });
});
