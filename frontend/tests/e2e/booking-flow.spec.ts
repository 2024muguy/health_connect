/**
 * HealthConnect AI - Booking Flow E2E Tests (Playwright)
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';

async function login(page: Page) {
  await page.goto(`${BASE_URL}/login`);
  await page.fill('[data-testid="input-email"]', 'test@example.com');
  await page.fill('[data-testid="input-password"]', 'TestPass123!');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
}

test.describe('Appointment Booking Flow', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('complete appointment booking flow', async ({ page }) => {
    // Navigate to new appointment page
    await page.click('[data-testid="link-book-appointment"]');
    await page.waitForURL('**/appointments/new');

    // Step 1: Select service
    await page.selectOption('[data-testid="select-service"]', {
      label: 'General Consultation · 30 min',
    });

    // Step 2: Select date and time
    const tomorrow = new Date(Date.now() + 86400000);
    const dateString = tomorrow.toISOString().slice(0, 10);
    await page.fill('[data-testid="input-date"]', dateString);

    // Wait for time slots to load
    await page.waitForTimeout(1000);

    // Click first available time slot
    const firstTimeSlot = page.locator('[data-testid^="button-time-"]').first();
    if (await firstTimeSlot.isVisible()) {
      await firstTimeSlot.click();
    }

    // Step 3: Add notes
    await page.fill('[data-testid="textarea-notes"]', 'E2E test appointment');

    // Submit
    await page.click('button[type="submit"]');

    // Verify navigation to detail page
    await page.waitForURL('**/appointments/*');
  });

  test('validation prevents submission without required fields', async ({ page }) => {
    await page.goto(`${BASE_URL}/appointments/new`);

    // Try to submit without selecting service
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeDisabled();

    // Select service
    await page.selectOption('[data-testid="select-service"]', {
      label: 'General Consultation · 30 min',
    });

    // Still disabled without time
    await expect(submitButton).toBeDisabled();
  });
});

test.describe('Chat Flow', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('send message to AI assistant', async ({ page }) => {
    await page.goto(`${BASE_URL}/chat`);

    // Type message
    await page.fill(
      '[data-testid="textarea-new-chat"]',
      'What are your opening hours?',
    );

    // Send
    await page.click('[data-testid="button-send-new-chat"]');

    // Wait for navigation to conversation
    await page.waitForURL('**/chat/*');
  });

  test('quick reply suggestion populates input', async ({ page }) => {
    await page.goto(`${BASE_URL}/chat`);

    // Click suggestion
    await page.click('[data-testid="button-suggestion-0"]');

    // Verify textarea has content
    const textarea = page.locator('[data-testid="textarea-new-chat"]');
    const value = await textarea.inputValue();
    expect(value.length).toBeGreaterThan(0);
  });
});

test.describe('Navigation', () => {
  test('sidebar navigation works', async ({ page }) => {
    await login(page);

    // Navigate to appointments
    await page.click('[data-testid="link-appointments"]');
    await page.waitForURL('**/appointments');

    // Navigate to clinic
    await page.click('[data-testid="link-clinic-services"]');
    await page.waitForURL('**/clinic');

    // Navigate to profile
    await page.click('[data-testid="link-my-profile"]');
    await page.waitForURL('**/profile');
  });

  test('mobile menu opens and closes', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await login(page);

    // Open menu
    await page.click('[data-testid="button-open-menu"]');
    await expect(page.locator('[data-testid="button-close-menu"]')).toBeVisible();

    // Close menu
    await page.click('[data-testid="button-close-menu"]');
  });
});