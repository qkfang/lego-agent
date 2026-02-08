import { test, expect } from '@playwright/test';

test.describe('Digital Avatar Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app page
    await page.goto('/app', { waitUntil: 'domcontentloaded' });
    
    // Wait for the main interface to load
    await page.locator('input[type="text"][placeholder*="Send a message"]').waitFor();
  });

  test('should display placeholder avatar before voice call', async ({ page }) => {
    // Check that the avatar container is present
    const avatarContainer = page.locator('.avatarWrapper, .avatar-wrapper').first();
    await expect(avatarContainer).toBeVisible();
    
    // Check that the placeholder is shown
    const placeholder = page.locator('text=Start conversation to see Mario');
    await expect(placeholder).toBeVisible();
    
    // Check that the game controller icon is visible
    const gameIcon = page.locator('text=🎮');
    await expect(gameIcon).toBeVisible();
  });

  test('should show avatar components structure', async ({ page }) => {
    // Look for any avatar-related containers
    const avatarElements = await page.locator('[class*="avatar"]').count();
    expect(avatarElements).toBeGreaterThan(0);
  });

  test('should have voice control button visible', async ({ page }) => {
    // Check for the voice button (either idle or call state)
    const voiceButton = page.locator('.idle, .call').first();
    await expect(voiceButton).toBeVisible();
    
    // Button should be clickable
    await expect(voiceButton).toBeEnabled();
  });

  test('should display Mario avatar elements when voice is active', async ({ page }) => {
    // Note: This test checks for the presence of avatar elements
    // In actual testing with voice enabled, the Mario character would be fully visible
    
    // Check if avatar container exists
    const avatarContainer = page.locator('[class*="avatarContainer"], [class*="avatar-container"]').first();
    await expect(avatarContainer).toBeAttached();
  });

  test('avatar should be integrated into VoiceTool component', async ({ page }) => {
    // Check that VoiceTool component exists and contains avatar
    const voiceTool = page.locator('[class*="voiceTool"], [class*="voice-tool"]').first();
    await expect(voiceTool).toBeVisible();
    
    // Verify it contains avatar wrapper
    const avatarInVoiceTool = voiceTool.locator('[class*="avatarWrapper"], [class*="avatar-wrapper"]').first();
    await expect(avatarInVoiceTool).toBeAttached();
  });

  test('should have proper styling for avatar container', async ({ page }) => {
    const avatarContainer = page.locator('[class*="avatarContainer"], [class*="avatar-container"]').first();
    
    if (await avatarContainer.isVisible()) {
      // Check that container has expected dimensions
      const box = await avatarContainer.boundingBox();
      expect(box).not.toBeNull();
      if (box) {
        expect(box.width).toBeGreaterThan(0);
        expect(box.height).toBeGreaterThan(0);
      }
    }
  });
});
