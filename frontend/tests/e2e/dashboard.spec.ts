import { test, expect } from '@playwright/test';

test.describe('Inventory Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3000/login');
    
    // Mock login - fill in form and submit
    // Note: This assumes the backend is running and accepts test credentials
    await page.fill('input[id="tenant_id"]', 'test-tenant-id');
    await page.fill('input[id="username"]', 'testuser');
    await page.fill('input[id="password"]', 'testpass');
    await page.click('button[type="submit"]');
    
    // Wait for navigation to dashboard
    await page.waitForURL('**/inventory', { timeout: 10000 });
  });

  test('should display inventory dashboard', async ({ page }) => {
    // Check that dashboard title is visible
    await expect(page.locator('h1:has-text("Inventory Dashboard")')).toBeVisible();
  });

  test('should display statistics cards', async ({ page }) => {
    // Check for stat cards
    await expect(page.locator('text=Total Items')).toBeVisible();
    await expect(page.locator('text=Low Stock Items')).toBeVisible();
    await expect(page.locator('text=Warehouses')).toBeVisible();
  });

  test('should display inventory table', async ({ page }) => {
    // Wait for inventory table to load
    await page.waitForSelector('.inventory-table, .inventory-list-empty', { timeout: 10000 });
    
    // Check if table exists or empty state
    const tableExists = await page.locator('.inventory-table').count();
    const emptyStateExists = await page.locator('.inventory-list-empty').count();
    
    expect(tableExists > 0 || emptyStateExists > 0).toBeTruthy();
  });

  test('should filter by warehouse', async ({ page }) => {
    // Wait for warehouse filter to be visible
    await page.waitForSelector('#warehouse-filter', { timeout: 10000 });
    
    // Check that filter exists
    const filter = page.locator('#warehouse-filter');
    await expect(filter).toBeVisible();
    
    // Select a warehouse if available
    const options = await filter.locator('option').count();
    if (options > 1) {
      await filter.selectOption({ index: 1 });
      // Wait for inventory to update
      await page.waitForTimeout(1000);
    }
  });

  test('should toggle low stock filter', async ({ page }) => {
    // Find and click the low stock checkbox
    const checkbox = page.locator('input[type="checkbox"]');
    await expect(checkbox).toBeVisible();
    
    // Toggle the checkbox
    await checkbox.click();
    await page.waitForTimeout(500);
    
    // Toggle back
    await checkbox.click();
    await page.waitForTimeout(500);
  });
});
