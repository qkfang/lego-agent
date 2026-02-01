import { test, expect } from '@playwright/test';

test.describe('lego-web end-to-end tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app page (not the landing page)
    // Use domcontentloaded instead of load to avoid waiting for external resources
    await page.goto('/app', { waitUntil: 'domcontentloaded' });
    
    // Wait a bit for React to render
    await page.waitForTimeout(1000);
  });

  test('should display the main page with input box', async ({ page }) => {
    // Check that the title is present
    await expect(page.getByText('Robotics Agents')).toBeVisible();
    
    // Check that the input box is present
    const inputBox = page.locator('input[type="text"][placeholder*="Send a message"]');
    await expect(inputBox).toBeVisible();
  });

  test('should be able to type in the input box', async ({ page }) => {
    const inputBox = page.locator('input[type="text"][placeholder*="Send a message"]');
    
    // Type a message
    await inputBox.fill('move robot forward');
    
    // Verify the text is in the input
    await expect(inputBox).toHaveValue('move robot forward');
  });

  test('should send message when pressing Enter', async ({ page }) => {
    const inputBox = page.locator('input[type="text"][placeholder*="Send a message"]');
    
    // Type a message
    await inputBox.fill('move robot forward');
    
    // Press Enter to send
    await inputBox.press('Enter');
    
    // Verify the input is cleared after sending
    await expect(inputBox).toHaveValue('');
    
    // Wait a bit to see if there's any response
    await page.waitForTimeout(1000);
  });

  test('should interact with the UI after sending command', async ({ page }) => {
    const inputBox = page.locator('input[type="text"][placeholder*="Send a message"]');
    
    // Send a robot command
    await inputBox.fill('move robot forward 10 cm');
    await inputBox.press('Enter');
    
    // Wait for potential updates
    await page.waitForTimeout(2000);
    
    // Take a screenshot for verification
    await page.screenshot({ path: 'tests/e2e/screenshots/after-command.png', fullPage: true });
  });

  test('should handle multiple commands', async ({ page }) => {
    const inputBox = page.locator('input[type="text"][placeholder*="Send a message"]');
    
    // Send first command
    await inputBox.fill('move robot forward');
    await inputBox.press('Enter');
    await page.waitForTimeout(500);
    
    // Send second command
    await inputBox.fill('turn robot left');
    await inputBox.press('Enter');
    await page.waitForTimeout(500);
    
    // Verify input is still functional
    await expect(inputBox).toBeVisible();
    await expect(inputBox).toHaveValue('');
  });
});
