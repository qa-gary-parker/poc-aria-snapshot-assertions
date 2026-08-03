import { expect, type Page, test } from "@playwright/test";

// Strategy: id/class CSS selectors, the way legacy suites are written.
// Written against app v1 and never updated — like most real suites.

async function login(page: Page) {
	await page.goto("/");
	await page.locator("#username").fill("demo");
	await page.locator("#password").fill("demo123");
	await page.locator("#login-btn").click();
}

test("shows an error for invalid credentials", async ({ page }) => {
	await page.goto("/");
	await page.locator("#username").fill("demo");
	await page.locator("#password").fill("wrong");
	await page.locator("#login-btn").click();
	await expect(page.locator(".alert-error")).toBeVisible();
});

test("logs in and shows the dashboard", async ({ page }) => {
	await login(page);
	await expect(page.locator("#dashboard-title")).toHaveText("My Tasks");
});

test("adds a task to the list", async ({ page }) => {
	await login(page);
	await page.locator("#new-task").fill("Book flights");
	await page.locator("#add-btn").click();
	await expect(page.locator("#task-list li.task-item")).toHaveCount(4);
	await expect(page.locator("#task-list li.task-item").last()).toContainText("Book flights");
});

test("completes a task", async ({ page }) => {
	await login(page);
	await page
		.locator("li.task-item", { hasText: "Write report" })
		.locator(".complete-btn")
		.click();
	await expect(page.locator("#task-list li.completed")).toHaveCount(2);
	await expect(page.locator("#count-badge")).toHaveText("1 active");
});

test("filters to active tasks", async ({ page }) => {
	await login(page);
	await page.locator("#filters .filter-btn").nth(1).click();
	await expect(page.locator("#task-list li.task-item")).toHaveCount(2);
	await expect(page.locator("#task-list")).not.toContainText("Ship release");
});

test("filters to completed tasks", async ({ page }) => {
	await login(page);
	await page.locator("#filters .filter-btn").nth(2).click();
	await expect(page.locator("#task-list li.task-item")).toHaveCount(1);
	await expect(page.locator("#task-list")).toContainText("Ship release");
});

test("shows the active task count", async ({ page }) => {
	await login(page);
	await expect(page.locator("#count-badge")).toHaveText("2 active");
});
