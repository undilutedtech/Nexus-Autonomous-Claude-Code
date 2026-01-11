import { chromium } from 'playwright';

(async () => {
  console.log('Launching browser...');
  const browser = await chromium.launch({
    headless: false,  // Show the browser window
    slowMo: 500       // Slow down actions so user can see
  });

  const page = await browser.newPage();
  page.setViewportSize({ width: 1400, height: 900 });

  try {
    // Navigate to the project detail page
    console.log('1. Navigating to project page...');
    await page.goto('http://localhost:5173/projects/ted');
    await page.waitForTimeout(2000);

    // Wait for features to load
    console.log('2. Waiting for features to load...');
    await page.waitForSelector('.rounded-xl.bg-gray-50', { timeout: 10000 });
    await page.waitForTimeout(1000);

    // Click on the first feature card in the Pending column
    console.log('3. Clicking on a feature card...');
    const featureCard = page.locator('.rounded-xl.bg-gray-50').first().locator('.cursor-pointer').first();
    await featureCard.click();
    await page.waitForTimeout(1500);

    // Click the Edit Feature button
    console.log('4. Clicking Edit Feature button...');
    const editButton = page.getByRole('button', { name: 'Edit Feature' });
    await editButton.click();
    await page.waitForTimeout(1500);

    // Modify the feature name
    console.log('5. Modifying the feature name...');
    const nameInput = page.locator('input').nth(1); // Second input is the name field
    await nameInput.clear();
    await nameInput.fill('EDITED VIA PLAYWRIGHT: Test Feature');
    await page.waitForTimeout(1000);

    // Modify the description
    console.log('6. Modifying the description...');
    const descriptionField = page.locator('textarea');
    await descriptionField.clear();
    await descriptionField.fill('This description was edited using Playwright browser automation!');
    await page.waitForTimeout(1000);

    // Click Save Changes
    console.log('7. Saving changes...');
    const saveButton = page.getByRole('button', { name: 'Save Changes' });
    await saveButton.click();
    await page.waitForTimeout(2000);

    // Click the same feature again to verify
    console.log('8. Verifying the changes persisted...');
    await featureCard.click();
    await page.waitForTimeout(2000);

    console.log('Test complete! Check the browser to see the updated feature.');
    console.log('Press Ctrl+C to close the browser when done viewing.');

    // Keep browser open for viewing
    await page.waitForTimeout(30000);

  } catch (error) {
    console.error('Error during test:', error.message);
    await page.screenshot({ path: '/tmp/playwright-error.png' });
    console.log('Screenshot saved to /tmp/playwright-error.png');
  }

  await browser.close();
})();
