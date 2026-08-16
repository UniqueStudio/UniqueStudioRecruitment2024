import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";
import { chromium } from "playwright";

const mockUrl = "http://127.0.0.1:8788";
const appUrl = "http://127.0.0.1:5174";

const start = (command, args, options = {}) => {
	const child = spawn(command, args, { stdio: "inherit", ...options });
	child.on("error", (error) => console.error(error));
	return child;
};

const waitFor = async (url) => {
	for (let attempt = 0; attempt < 60; attempt += 1) {
		try {
			if ((await fetch(url)).ok) return;
		} catch {
			// The process is still starting.
		}
		await delay(250);
	}
	throw new Error(`Timed out waiting for ${url}`);
};

const reset = async (scenario) => {
	const response = await fetch(`${mockUrl}/__mock__/reset?scenario=${scenario}`, {
		method: "POST"
	});
	assert.equal(response.ok, true);
};

const state = async () => (await fetch(`${mockUrl}/__mock__/state`)).json();

let mock;
let app;
let browser;

try {
	mock = start("node", ["scripts/mock-api.mjs"]);
	await waitFor(`${mockUrl}/__mock__/state`);
	app = start("pnpm", ["vite", "--mode", "e2e", "--host", "127.0.0.1", "--port", "5174"]);
	await waitFor(appUrl);

	browser = await chromium.launch({ headless: true });
	const context = await browser.newContext({
		acceptDownloads: true,
		viewport: { width: 1440, height: 1100 }
	});
	const page = await context.newPage();
	page.on("dialog", (dialog) => dialog.accept());
	const backendDepartmentRequests = [];
	page.on("request", (request) => {
		if (new URL(request.url()).pathname === "/config/whiteboard") {
			backendDepartmentRequests.push(request.url());
		}
	});

	await reset("registered");
	console.log("Testing registered candidate history flow");
	await page.goto(appUrl, { waitUntil: "domcontentloaded" });
	await page.getByText("申请记录", { exact: true }).waitFor();
	await page.getByText("查看详情", { exact: true }).click();
	await page.getByText("选择候选时间", { exact: false }).first().waitFor();
	await page.locator("div.border-blue-400").nth(1).click();
	await page.locator("p").filter({ hasText: "10月10日" }).first().dispatchEvent("click");
	await page.getByText("上午", { exact: true }).click();
	await page.getByText("09:00 - 10:00", { exact: true }).click();
	await page.getByText("修改成功", { exact: true }).waitFor();
	assert.deepEqual(backendDepartmentRequests, []);

	console.log("Testing registered candidate profile save flow");
	await page.goto(`${appUrl}/user`, { waitUntil: "domcontentloaded" });
	await page.locator("p").filter({ hasText: /^个人信息$/ }).first().waitFor();
	await page.getByText("编辑", { exact: true }).click();
	await page.getByText("保存", { exact: true }).click();
	await page.getByText("保存成功", { exact: true }).waitFor();

	const firstSaveState = await state();
	assert.ok(firstSaveState.data.mutations.some((entry) => entry.path === "/applications/app-1"));
	assert.ok(
		firstSaveState.data.mutations.some((entry) => entry.path.includes("/interview/group/self"))
	);

	await reset("unregistered");
	console.log("Testing unregistered candidate sign-up flow");
	await page.reload({ waitUntil: "domcontentloaded" });
	await page.getByText("报名", { exact: true }).waitFor();
	await page.getByText("个人信息", { exact: true }).click();
	await page.getByText("编辑", { exact: true }).click();
	await page.getByText("报名", { exact: true }).first().click();
	await page.getByText("确认报名", { exact: true }).click();
	await page.getByText("报名成功", { exact: true }).waitFor();

	const signUpState = await state();
	assert.ok(
		signUpState.data.mutations.some(
			(entry) => entry.method === "POST" && entry.path === "/applications/"
		)
	);

	await page.screenshot({ path: "test-results/e2e-final.png", fullPage: true });
	console.log("E2E workflow completed successfully");
} catch (error) {
	console.error("E2E workflow failed", error);
	process.exitCode = 1;
} finally {
	await browser?.close();
	app?.kill("SIGTERM");
	mock?.kill("SIGTERM");
}
