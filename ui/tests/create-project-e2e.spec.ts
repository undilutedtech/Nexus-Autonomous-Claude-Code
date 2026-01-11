import { test, expect } from '@playwright/test';

test('create project through wizard end-to-end', async ({ page }) => {
  // Set auth token to bypass login
  await page.goto('http://localhost:5173/');
  await page.evaluate(() => {
    localStorage.setItem('nexus_token', 'test-token-for-playwright');
  });

  // Navigate to new project wizard
  await page.goto('http://localhost:5173/projects/new');
  await page.waitForTimeout(1000);

  console.log('=== STEP 1: Project Details ===');

  // Take initial screenshot
  await page.screenshot({ path: '/tmp/create-e2e-1-start.png', fullPage: true });

  // Fill in project name with timestamp to make it unique
  const projectName = `test-project-${Date.now()}`;
  await page.fill('input[placeholder="my-awesome-project"]', projectName);

  // Fill in project path - use home directory to avoid security restrictions
  const projectPath = `/home/iris/projects/${projectName}`;
  await page.fill('input[placeholder="/home/user/projects/my-project"]', projectPath);

  console.log(`Project name: ${projectName}`);
  console.log(`Project path: ${projectPath}`);

  await page.screenshot({ path: '/tmp/create-e2e-2-details-filled.png', fullPage: true });

  // Click Continue to Step 2
  await page.click('button:has-text("Continue")');
  await page.waitForTimeout(500);

  console.log('=== STEP 2: App Specification ===');
  await page.screenshot({ path: '/tmp/create-e2e-3-spec.png', fullPage: true });

  // Select Web Application template
  await page.click('button:has-text("Web Application")');
  await page.waitForTimeout(300);

  // Verify textarea has content
  const textarea = page.locator('textarea');
  const specContent = await textarea.inputValue();
  expect(specContent).toContain('project_specification');
  console.log('Template selected, spec populated');

  await page.screenshot({ path: '/tmp/create-e2e-4-spec-filled.png', fullPage: true });

  // Click Continue to Step 3
  await page.click('button:has-text("Continue")');
  await page.waitForTimeout(500);

  console.log('=== STEP 3: Agent Configuration ===');
  await page.screenshot({ path: '/tmp/create-e2e-5-config.png', fullPage: true });

  // Verify YOLO mode is checked by default
  const yoloCheckbox = page.locator('#yoloMode');
  await expect(yoloCheckbox).toBeChecked();
  console.log('YOLO mode is enabled by default');

  // Click Continue to Step 4
  await page.click('button:has-text("Continue")');
  await page.waitForTimeout(500);

  console.log('=== STEP 4: Review & Create ===');
  await page.screenshot({ path: '/tmp/create-e2e-6-review.png', fullPage: true });

  // Verify review shows correct info
  await expect(page.locator('text=Review & Create')).toBeVisible();

  // Check summary shows our project name
  const summaryText = await page.locator('.space-y-4.rounded-lg.bg-gray-50').textContent();
  expect(summaryText).toContain(projectName);
  console.log('Review page shows correct project name');

  // Do NOT check "Start agent immediately" - we just want to create the project
  const startAgentCheckbox = page.locator('#startAgent');
  if (await startAgentCheckbox.isChecked()) {
    await startAgentCheckbox.uncheck();
  }

  console.log('=== CREATING PROJECT ===');

  // Click Create Project
  await page.click('button:has-text("Create Project")');

  // Wait for navigation to project detail page
  await page.waitForURL(/\/projects\//, { timeout: 10000 });
  await page.waitForTimeout(1000);

  console.log('Project created successfully!');
  await page.screenshot({ path: '/tmp/create-e2e-7-created.png', fullPage: true });

  // Verify we're on the project detail page (or redirect happened)
  const currentUrl = page.url();
  console.log(`Navigated to: ${currentUrl}`);

  // The URL may include signin redirect - check that it contains the project name
  expect(currentUrl).toContain(projectName);

  // Re-authenticate if redirected to signin
  if (currentUrl.includes('/signin')) {
    console.log('Re-authenticating after redirect...');
    await page.evaluate(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });
    await page.goto(`http://localhost:5173/projects/${projectName}`);
    await page.waitForTimeout(1000);
  }

  await page.screenshot({ path: '/tmp/create-e2e-7b-project-detail.png', fullPage: true });

  // Verify project detail page loaded
  await expect(page.locator('h2').first()).toBeVisible();

  console.log('=== VERIFYING PROJECT EXISTS ===');

  // Re-set auth token (it may have been cleared during navigation)
  await page.evaluate(() => {
    localStorage.setItem('nexus_token', 'test-token-for-playwright');
  });

  // Navigate to projects list to verify it appears
  await page.goto('http://localhost:5173/projects');
  await page.waitForTimeout(1000);

  await page.screenshot({ path: '/tmp/create-e2e-8-list.png', fullPage: true });

  // Look for our project in the list
  const projectCard = page.locator(`text=${projectName}`);
  await expect(projectCard.first()).toBeVisible();

  console.log('Project appears in projects list!');

  console.log('=== TEST PASSED ===');
  console.log(`Successfully created project: ${projectName}`);
  console.log(`Check screenshots in /tmp/create-e2e-*.png`);
});
