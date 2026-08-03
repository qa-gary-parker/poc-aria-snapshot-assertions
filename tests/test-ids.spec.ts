import { expect, type Page, test } from "@playwright/test";

// Strategy: dedicated data-testid attributes — a contract between
// the app and the suite, immune to styling and copy changes
// for exactly as long as developers honour the contract.

async function login(page: Page) {
	await page.goto("/");
	await page.getByTestId("username-input").fill("demo");
	await page.getByTestId("password-input").fill("demo123");
	await page.getByTestId("login-submit").click();
}

test("shows an error for invalid credentials", async ({ page }) => {
	await page.goto("/");
	await page.getByTestId("username-input").fill("demo");
	await page.getByTestId("password-input").fill("wrong");
	await page.getByTestId("login-submit").click();
	await expect(page.getByTestId("login-error")).toBeVisible();
});

test("logs in and shows the dashboard", async ({ page }) => {
	await login(page);
	await expect(page.getByTestId("dashboard-title")).toHaveText("My Tasks");
});

test("adds a task to the list", async ({ page }) => {
	await login(page);
	await page.getByTestId("task-input").fill("Book flights");
	await page.getByTestId("task-add").click();
	await expect(page.getByTestId("task-item")).toHaveCount(4);
	await expect(page.getByTestId("task-item").last()).toContainText("Book flights");
});

test("completes a task", async ({ page }) => {
	await login(page);
	await page
		.getByTestId("task-item")
		.filter({ hasText: "Write report" })
		.getByTestId("task-complete")
		.click();
	await expect(
		page.getByTestId("task-item").filter({ hasText: "Write report" }).getByTestId("task-complete"),
	).toHaveCount(0);
});

test("filters to active tasks", async ({ page }) => {
	await login(page);
	await page.getByTestId("filter-active").click();
	await expect(page.getByTestId("task-item")).toHaveCount(2);
	await expect(page.getByTestId("task-list")).not.toContainText("Ship release");
});

test("filters to completed tasks", async ({ page }) => {
	await login(page);
	await page.getByTestId("filter-completed").click();
	await expect(page.getByTestId("task-item")).toHaveCount(1);
	await expect(page.getByTestId("task-list")).toContainText("Ship release");
});

test("shows the active task count", async ({ page }) => {
	await login(page);
	await expect(page.getByTestId("active-count")).toHaveText("2 active");
});
