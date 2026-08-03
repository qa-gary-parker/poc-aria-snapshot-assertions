import { expect, type Page, test } from "@playwright/test";

// Strategy: user-facing locators — roles, labels, accessible names.
// The locators Playwright's own docs recommend.

async function login(page: Page) {
	await page.goto("/");
	await page.getByLabel("Username").fill("demo");
	await page.getByLabel("Password").fill("demo123");
	await page.getByRole("button", { name: "Login" }).click();
}

test("shows an error for invalid credentials", async ({ page }) => {
	await page.goto("/");
	await page.getByLabel("Username").fill("demo");
	await page.getByLabel("Password").fill("wrong");
	await page.getByRole("button", { name: "Login" }).click();
	await expect(page.getByRole("alert")).toContainText("Invalid username or password");
});

test("logs in and shows the dashboard", async ({ page }) => {
	await login(page);
	await expect(page.getByRole("heading", { name: "My Tasks" })).toBeVisible();
});

test("adds a task to the list", async ({ page }) => {
	await login(page);
	await page.getByLabel("New task").fill("Book flights");
	await page.getByRole("button", { name: "Add", exact: true }).click();
	await expect(page.getByRole("listitem").filter({ hasText: "Book flights" })).toBeVisible();
});

test("completes a task", async ({ page }) => {
	await login(page);
	await page
		.getByRole("listitem")
		.filter({ hasText: "Write report" })
		.getByRole("button", { name: "Done" })
		.click();
	await expect(page.getByText("1 active")).toBeVisible();
});

test("filters to active tasks", async ({ page }) => {
	await login(page);
	await page.getByRole("button", { name: "Active", exact: true }).click();
	await expect(page.getByRole("listitem")).toHaveCount(2);
	await expect(page.getByText("Ship release")).toBeHidden();
});

test("filters to completed tasks", async ({ page }) => {
	await login(page);
	await page.getByRole("button", { name: "Completed", exact: true }).click();
	await expect(page.getByRole("listitem")).toHaveCount(1);
	await expect(page.getByText("Ship release")).toBeVisible();
});

test("shows the active task count", async ({ page }) => {
	await login(page);
	await expect(page.getByText("2 active")).toBeVisible();
});
