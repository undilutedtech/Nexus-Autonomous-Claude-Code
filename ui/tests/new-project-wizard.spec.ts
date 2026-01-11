import { test, expect } from '@playwright/test';

test.describe('New Project Wizard', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token to bypass login
    await page.goto('http://localhost:5173/');
    await page.evaluate(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });
  });

  test('wizard page loads with stepper', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/new');
    await page.waitForTimeout(1000);

    // Take screenshot
    await page.screenshot({ path: '/tmp/wizard-1-loaded.png', fullPage: true });

    // Check stepper is visible
    const stepperSteps = page.locator('text=Details');
    await expect(stepperSteps.first()).toBeVisible();

    // Check step titles are present
    await expect(page.locator('text=Specification')).toBeVisible();
    await expect(page.locator('text=Configuration')).toBeVisible();
    await expect(page.locator('text=Review')).toBeVisible();

    // Check first step content
    await expect(page.locator('text=Project Details')).toBeVisible();
    await expect(page.locator('text=Project Name')).toBeVisible();
    await expect(page.locator('text=Project Location')).toBeVisible();

    console.log('Step 1: Wizard loaded successfully');
  });

  test('can navigate through wizard steps', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/new');
    await page.waitForTimeout(1000);

    // Step 1: Fill in project details
    await page.fill('input[placeholder="my-awesome-project"]', 'test-wizard-project');
    await page.fill('input[placeholder="/home/user/projects/my-project"]', '/tmp/test-wizard-project');

    await page.screenshot({ path: '/tmp/wizard-2-step1-filled.png', fullPage: true });

    // Click Continue
    await page.click('button:has-text("Continue")');
    await page.waitForTimeout(500);

    await page.screenshot({ path: '/tmp/wizard-3-step2.png', fullPage: true });

    // Step 2: App Specification should be visible
    await expect(page.locator('text=App Specification')).toBeVisible();
    await expect(page.locator('text=Start from a template')).toBeVisible();

    // Check templates are visible
    await expect(page.locator('text=Blank Project')).toBeVisible();
    await expect(page.locator('text=Web Application')).toBeVisible();
    await expect(page.locator('text=REST API')).toBeVisible();
    await expect(page.locator('text=CLI Tool')).toBeVisible();

    console.log('Step 2: App Specification page loaded');

    // Select a template
    await page.click('button:has-text("Web Application")');
    await page.waitForTimeout(300);

    await page.screenshot({ path: '/tmp/wizard-4-template-selected.png', fullPage: true });

    // Check textarea has content
    const textarea = page.locator('textarea');
    const textareaValue = await textarea.inputValue();
    expect(textareaValue).toContain('project_specification');

    // Click Continue
    await page.click('button:has-text("Continue")');
    await page.waitForTimeout(500);

    await page.screenshot({ path: '/tmp/wizard-5-step3.png', fullPage: true });

    // Step 3: Configuration should be visible
    await expect(page.locator('text=Agent Configuration')).toBeVisible();
    await expect(page.locator('text=AI Model')).toBeVisible();
    await expect(page.locator('text=YOLO Mode')).toBeVisible();
    await expect(page.locator('text=Max Parallel Agents')).toBeVisible();

    console.log('Step 3: Configuration page loaded');

    // Click Continue
    await page.click('button:has-text("Continue")');
    await page.waitForTimeout(500);

    await page.screenshot({ path: '/tmp/wizard-6-step4-review.png', fullPage: true });

    // Step 4: Review should be visible
    await expect(page.locator('text=Review & Create')).toBeVisible();
    await expect(page.locator('text=test-wizard-project')).toBeVisible();

    console.log('Step 4: Review page loaded');

    // Check all summary items
    await expect(page.locator('text=Has App Spec')).toBeVisible();
    await expect(page.locator('text=Claude Opus 4.5')).toBeVisible();

    console.log('All wizard steps work correctly!');
  });

  test('back button navigates to previous step', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/new');
    await page.waitForTimeout(1000);

    // Fill step 1 and go to step 2
    await page.fill('input[placeholder="my-awesome-project"]', 'back-test-project');
    await page.fill('input[placeholder="/home/user/projects/my-project"]', '/tmp/back-test');
    await page.click('button:has-text("Continue")');
    await page.waitForTimeout(500);

    // Should be on step 2
    await expect(page.locator('text=App Specification')).toBeVisible();

    // Click Back
    await page.click('button:has-text("Back")');
    await page.waitForTimeout(500);

    // Should be back on step 1
    await expect(page.locator('text=Project Details')).toBeVisible();

    // Values should be preserved
    const nameInput = page.locator('input[placeholder="my-awesome-project"]');
    await expect(nameInput).toHaveValue('back-test-project');

    console.log('Back navigation works correctly');
  });

  test('continue button disabled without required fields', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/new');
    await page.waitForTimeout(1000);

    // Continue button should be disabled initially
    const continueBtn = page.locator('button:has-text("Continue")');
    await expect(continueBtn).toBeDisabled();

    // Fill only name
    await page.fill('input[placeholder="my-awesome-project"]', 'test-project');
    await expect(continueBtn).toBeDisabled();

    // Fill path too
    await page.fill('input[placeholder="/home/user/projects/my-project"]', '/tmp/test');
    await expect(continueBtn).toBeEnabled();

    console.log('Form validation works correctly');
  });

  test('folder browser opens and closes', async ({ page }) => {
    await page.goto('http://localhost:5173/projects/new');
    await page.waitForTimeout(1000);

    // Click folder browser button
    const folderBtn = page.locator('button:has(svg path[d*="M3 7v10a2 2 0 002"])').first();
    await folderBtn.click();
    await page.waitForTimeout(500);

    await page.screenshot({ path: '/tmp/wizard-7-folder-browser.png', fullPage: true });

    // Folder browser should be visible
    await expect(page.locator('text=Select This Folder')).toBeVisible();

    // Should show navigation buttons
    await expect(page.locator('text=New Folder')).toBeVisible();

    console.log('Folder browser opens correctly');
  });

  test('header new project button links to wizard', async ({ page }) => {
    await page.goto('http://localhost:5173/projects');
    await page.waitForTimeout(1000);

    // Find the New Project button in header
    const newProjectLink = page.locator('a[href="/projects/new"]').first();
    await expect(newProjectLink).toBeVisible();

    // Click it
    await newProjectLink.click();
    await page.waitForTimeout(500);

    // Should be on wizard page
    await expect(page).toHaveURL(/\/projects\/new/);
    await expect(page.locator('text=Project Details')).toBeVisible();

    console.log('Header button links to wizard correctly');
  });

  test('sidebar new project link works', async ({ page }) => {
    await page.goto('http://localhost:5173/');
    await page.waitForTimeout(1000);

    // Open Projects submenu
    const projectsMenu = page.locator('button:has-text("Projects")');
    await projectsMenu.click();
    await page.waitForTimeout(300);

    await page.screenshot({ path: '/tmp/wizard-8-sidebar.png', fullPage: true });

    // Click New Project
    const newProjectLink = page.locator('a[href="/projects/new"]:has-text("New Project")');
    await expect(newProjectLink).toBeVisible();
    await newProjectLink.click();
    await page.waitForTimeout(500);

    // Should be on wizard page
    await expect(page).toHaveURL(/\/projects\/new/);

    console.log('Sidebar link works correctly');
  });
});
