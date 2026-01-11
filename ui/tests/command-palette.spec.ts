import { test, expect } from '@playwright/test';

test.describe('Command Palette', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token before loading
    await page.addInitScript(() => {
      localStorage.setItem('nexus_token', 'test-token-for-playwright');
    });

    // Go to dashboard
    await page.goto('http://localhost:5174/');
    await page.waitForTimeout(1000);
  });

  test('opens with Cmd+K keyboard shortcut', async ({ page }) => {
    // Press Cmd+K (or Ctrl+K on non-Mac)
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(500);

    // Check if command palette is visible
    const palette = page.locator('input[placeholder*="Search commands"]');
    await expect(palette).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: '/tmp/command-palette-open.png', fullPage: true });
  });

  test('opens by clicking search bar', async ({ page }) => {
    // Click on the search bar
    const searchBar = page.locator('text=Search or type command...').first();
    await searchBar.click();
    await page.waitForTimeout(500);

    // Check if command palette is visible
    const palette = page.locator('input[placeholder*="Search commands"]');
    await expect(palette).toBeVisible();
  });

  test('closes with Escape key', async ({ page }) => {
    // Open command palette
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(500);

    // Verify it's open
    const palette = page.locator('input[placeholder*="Search commands"]');
    await expect(palette).toBeVisible();

    // Press Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // Verify it's closed
    await expect(palette).not.toBeVisible();
  });

  test('filters results as you type', async ({ page }) => {
    // Open command palette
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(500);

    // Type a search query
    await page.keyboard.type('settings');
    await page.waitForTimeout(300);

    // Check that settings option is visible
    const settingsOption = page.locator('text=Go to Settings');
    await expect(settingsOption).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: '/tmp/command-palette-filtered.png', fullPage: true });
  });

  test('shows projects when searching', async ({ page }) => {
    // Open command palette
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(1000); // Wait for projects to load

    // Check that projects category is visible
    const projectsCategory = page.locator('text=Projects').first();
    await expect(projectsCategory).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: '/tmp/command-palette-projects.png', fullPage: true });
  });

  test('shows only actions when typing >', async ({ page }) => {
    // Open command palette
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(500);

    // Type > to show only commands
    await page.keyboard.type('>');
    await page.waitForTimeout(300);

    // Check that Actions category is visible
    const actionsCategory = page.locator('h3:has-text("Actions"), h3:has-text("Navigation")').first();
    await expect(actionsCategory).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: '/tmp/command-palette-actions.png', fullPage: true });
  });

  test('navigates with keyboard arrows', async ({ page }) => {
    // Open command palette
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(500);

    // Press down arrow to select next item
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(200);

    // Press down arrow again
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(200);

    // Take screenshot showing selection
    await page.screenshot({ path: '/tmp/command-palette-navigation.png', fullPage: true });
  });

  test('executes command on Enter', async ({ page }) => {
    // Open command palette
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(500);

    // Type to find settings
    await page.keyboard.type('settings');
    await page.waitForTimeout(300);

    // Press Enter to execute
    await page.keyboard.press('Enter');
    await page.waitForTimeout(1000);

    // Check that we navigated to settings
    expect(page.url()).toContain('/settings');
  });

  test('executes command on click', async ({ page }) => {
    // Open command palette
    await page.keyboard.press('Control+k');
    await page.waitForTimeout(500);

    // Click on Dashboard option
    const dashboardOption = page.locator('button:has-text("Go to Dashboard")');
    await dashboardOption.click();
    await page.waitForTimeout(500);

    // Check that we navigated to dashboard
    expect(page.url()).toBe('http://localhost:5174/');
  });
});
