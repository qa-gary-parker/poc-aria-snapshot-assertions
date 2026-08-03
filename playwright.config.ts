import { defineConfig } from "@playwright/test";

// APP_VERSION selects the app build to serve (v1 | v2 | v3 | v1-regressed | r1..r5).
// SUITE_DIR selects the suite copy (tests | tests-updated).
const version = process.env.APP_VERSION || "v1";

export default defineConfig({
	testDir: process.env.SUITE_DIR || "./tests",
	fullyParallel: true,
	reporter: [["list"]],
	use: {
		baseURL: "http://localhost:4174",
	},
	webServer: {
		command: `npx http-server app/${version} -p 4174 -s -c-1`,
		url: "http://localhost:4174",
		reuseExistingServer: false,
	},
});
