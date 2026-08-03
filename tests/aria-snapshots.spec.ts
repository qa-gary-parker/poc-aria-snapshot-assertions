import { expect, type Page, test } from "@playwright/test";

// Strategy: actions use user-facing locators; assertions are ARIA snapshots —
// the test verifies the accessibility tree the user experiences, not
// individual elements. Templates are partial matches, written against v1.

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
	await expect(page.locator("body")).toMatchAriaSnapshot(`
		- textbox "Username"
		- textbox "Password"
		- button "Login"
		- alert: Invalid username or password
	`);
});

test("logs in and shows the dashboard", async ({ page }) => {
	await login(page);
	await expect(page.locator("body")).toMatchAriaSnapshot(`
		- heading "My Tasks" [level=2]
		- text: 2 active
		- textbox "New task"
		- button "Add"
	`);
});

test("adds a task to the list", async ({ page }) => {
	await login(page);
	await page.getByLabel("New task").fill("Book flights");
	await page.getByRole("button", { name: "Add", exact: true }).click();
	await expect(page.getByRole("list")).toMatchAriaSnapshot(`
		- list:
		  - listitem:
		    - text: Write report
		    - button "Done"
		  - listitem:
		    - text: Review PR
		    - button "Done"
		  - listitem:
		    - text: Ship release
		  - listitem:
		    - text: Book flights
		    - button "Done"
	`);
});

test("completes a task", async ({ page }) => {
	await login(page);
	await page
		.getByRole("listitem")
		.filter({ hasText: "Write report" })
		.getByRole("button", { name: "Done" })
		.click();
	await expect(page.locator("body")).toMatchAriaSnapshot(`
		- text: 1 active
		- list:
		  - listitem:
		    - text: Write report
		  - listitem:
		    - text: Review PR
		    - button "Done"
		  - listitem:
		    - text: Ship release
	`);
});

test("filters to active tasks", async ({ page }) => {
	await login(page);
	await page.getByRole("button", { name: "Active", exact: true }).click();
	await expect(page.getByRole("list")).toMatchAriaSnapshot(`
		- list:
		  - listitem:
		    - text: Write report
		    - button "Done"
		  - listitem:
		    - text: Review PR
		    - button "Done"
	`);
});

test("filters to completed tasks", async ({ page }) => {
	await login(page);
	await page.getByRole("button", { name: "Completed", exact: true }).click();
	await expect(page.getByRole("list")).toMatchAriaSnapshot(`
		- list:
		  - listitem:
		    - text: Ship release
	`);
});

test("shows the active task count", async ({ page }) => {
	await login(page);
	await expect(page.locator("body")).toMatchAriaSnapshot(`
		- heading "My Tasks" [level=2]
		- text: 2 active
	`);
});
