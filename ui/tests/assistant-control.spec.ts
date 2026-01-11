import { test, expect } from '@playwright/test';

test('assistant agent control via chat', async ({ page }) => {
  // Listen for console messages
  page.on('console', msg => {
    if (msg.type() === 'error' || msg.text().includes('WebSocket')) {
      console.log(`Console ${msg.type()}:`, msg.text());
    }
  });

  // Set auth token to bypass login
  await page.goto('http://localhost:5173/');
  await page.evaluate(() => {
    localStorage.setItem('auth_token', 'test-token-for-playwright');
  });

  // Navigate to a project
  await page.goto('http://localhost:5173/projects/ted');
  await page.waitForTimeout(2000);

  // Take screenshot of project page
  await page.screenshot({ path: '/tmp/assistant-control-1.png', fullPage: true });
  console.log('Screenshot 1: Project page loaded');

  // Look for the assistant toggle button (chat bubble icon in header)
  const assistantToggle = page.locator('button[aria-label="Toggle assistant"], button:has-text("Assistant"), header button').filter({ hasText: '' }).last();

  // Check if we can find any buttons in the header
  const headerButtons = page.locator('header button');
  const count = await headerButtons.count();
  console.log(`Found ${count} header buttons`);

  // Try to find the assistant panel or a way to open it
  // Look for a chat icon or assistant-related element
  const chatElements = page.locator('[class*="assistant"], [class*="chat"], [aria-label*="chat"], [aria-label*="assistant"]');
  const chatCount = await chatElements.count();
  console.log(`Found ${chatCount} assistant/chat elements`);

  // Take another screenshot
  await page.screenshot({ path: '/tmp/assistant-control-2.png', fullPage: true });
  console.log('Screenshot 2: After looking for assistant');

  // Try clicking the last header button (often the assistant toggle)
  if (count > 0) {
    await headerButtons.last().click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '/tmp/assistant-control-3.png', fullPage: true });
    console.log('Screenshot 3: After clicking last header button');
  }

  // Check for assistant panel visibility
  const assistantPanel = page.locator('[class*="assistant"], [class*="chat-panel"], aside:has-text("Assistant")');
  const panelVisible = await assistantPanel.isVisible().catch(() => false);
  console.log(`Assistant panel visible: ${panelVisible}`);

  console.log('Test complete - check screenshots in /tmp/');
});
