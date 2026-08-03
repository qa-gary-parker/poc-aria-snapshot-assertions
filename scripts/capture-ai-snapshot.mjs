// Captures the AI-optimized ARIA snapshot (refs + bounding boxes) of the
// logged-in dashboard — the view an agent gets of the page.
import { chromium } from "@playwright/test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(`file://${join(root, "app/v1/index.html")}`);
await page.locator("#username").fill("demo");
await page.locator("#password").fill("demo123");
await page.locator("#login-btn").click();
await page.locator("#task-list li").first().waitFor();
console.log(await page.locator("body").ariaSnapshot({ mode: "ai", boxes: true }));
await browser.close();
