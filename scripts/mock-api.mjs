import { createServer } from "node:http";

const port = Number(process.env.MOCK_API_PORT ?? 8788);
const appOrigin = "http://127.0.0.1:5174";
const now = "2026-08-16T00:00:00.000Z";
const recruitment = {
	uid: "rec-1",
	created_at: now,
	updated_at: now,
	name: "2026 秋季招新 A",
	beginning: "2026-01-01T00:00:00.000Z",
	deadline: "2099-12-31T23:59:59.000Z",
	end: "2099-12-31T23:59:59.000Z",
	stress_test_start: "2099-10-01T18:00:00.000Z",
	stress_test_end: "2099-10-01T22:00:00.000Z"
};

const emptyTime = {
	uid: "",
	date: "",
	period: "morning",
	start: "",
	end: "",
	name: "web",
	applications: [],
	select_number: 0,
	slot_number: 0
};

const makeApplication = (group = "web") => ({
	uid: "app-1",
	created_at: now,
	updated_at: now,
	grade: "大二",
	institute: "计算机学院",
	major: "计算机科学与技术",
	rank: "10%",
	group,
	intro: "Mock candidate introduction",
	is_quick: false,
	is_project_c: false,
	referrer: "",
	qq_account: "123456",
	resume: "mock-resume.pdf",
	abandoned: false,
	rejected: false,
	step: "GroupTimeSelection",
	candidate_id: "user-1",
	recruitment_id: recruitment.uid,
	interview_allocations_group: { ...emptyTime },
	interview_allocations_team: { ...emptyTime },
	interview_selections: [],
	comments: null,
	user_detail: null,
	answer: ""
});

const interviewTimes = [
	{
		uid: "slot-1",
		date: "2099-10-10T00:00:00.000Z",
		period: "morning",
		start: "2099-10-10T09:00:00+08:00",
		end: "2099-10-10T10:00:00+08:00",
		name: "web",
		applications: [],
		select_number: 0,
		slot_number: 5
	},
	{
		uid: "slot-2",
		date: "2099-10-10T00:00:00.000Z",
		period: "afternoon",
		start: "2099-10-10T14:00:00+08:00",
		end: "2099-10-10T15:00:00+08:00",
		name: "web",
		applications: [],
		select_number: 0,
		slot_number: 5
	}
];

const state = { scenario: "registered", mutations: [] };

// ---- SSO fixtures + session (used by the skill CLI; scenario "authed" gates routes) ----
const ssoInfo = {
	uid: "sso-user-1",
	phone: "13800138000",
	email: "mock@example.com",
	roles: [],
	name: "Mock User",
	avatar_url: "",
	gender: 1,
	join_time: now,
	groups: [],
	lark_union_id: "mock-union",
	qq_account: "123456"
};
const ssoPassword = "123456";
const ssoSmsCode = "123456";
let ssoSession = null;

const user = () => ({
	uid: "user-1",
	phone: "13800138000",
	email: "mock@example.com",
	qq_account: "123456",
	name: "Mock User",
	avatar_url: "",
	gender: 1,
	join_time: now,
	groups: null,
	lark_union_id: "mock-union",
	applications:
		state.scenario === "registered" || state.scenario === "authed" ? [state.application] : []
});

const reset = (scenario = "registered") => {
	state.scenario = scenario;
	state.application = makeApplication();
	state.mutations = [];
	Object.assign(ssoInfo, {
		uid: "sso-user-1",
		phone: "13800138000",
		email: "mock@example.com",
		roles: [],
		name: "Mock User",
		avatar_url: "",
		gender: 1,
		join_time: now,
		groups: [],
		lark_union_id: "mock-union",
		qq_account: "123456"
	});
};
reset();

const respond = (res, data, status = 200, msg = "ok") => {
	const body = JSON.stringify({ code: status, data, msg });
	res.writeHead(status, {
		"content-type": "application/json",
		"content-length": Buffer.byteLength(body),
		connection: "close",
		"access-control-allow-origin": appOrigin,
		"access-control-allow-credentials": "true"
	});
	res.end(body);
};

const departmentsFixture = {
	计算机学院: ["计算机科学与技术"],
	软件学院: ["软件工程"]
};

const readJson = (req) =>
	new Promise((resolve, reject) => {
		const chunks = [];
		req.on("data", (chunk) => chunks.push(chunk));
		req.on("end", () => {
			try {
				resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}"));
			} catch (error) {
				reject(error);
			}
		});
		req.on("error", reject);
	});

const parseCookies = (header) => {
	const result = {};
	if (!header) return result;
	for (const part of header.split(";")) {
		const eq = part.indexOf("=");
		if (eq === -1) continue;
		result[part.slice(0, eq).trim()] = part.slice(eq + 1).trim();
	}
	return result;
};

const isAuthed = (req) => {
	if (state.scenario !== "authed" && state.scenario !== "authed-clean") return true;
	const cookies = parseCookies(req.headers.cookie);
	return !!cookies.SSO_SESSION && cookies.SSO_SESSION === ssoSession;
};

const ssoRespond = (res, message, data, status = 200) => {
	const body = JSON.stringify({ message, data });
	res.writeHead(status, {
		"content-type": "application/json",
		"content-length": Buffer.byteLength(body),
		connection: "close",
		"access-control-allow-origin": appOrigin,
		"access-control-allow-credentials": "true"
	});
	res.end(body);
};

/** 把 FormData 中的可编辑字段回填到 application(模拟真实后端持久化)。 */
const applyFormToApplication = (form) => {
	for (const [key, value] of form.entries()) {
		if (key === "resume" || key === "file" || key === "group") continue;
		state.application[key] = key === "is_quick" ? value === "true" : value;
	}
};

createServer(async (req, res) => {
	if (req.method === "OPTIONS") {
		res.writeHead(204, {
			"access-control-allow-origin": appOrigin,
			"access-control-allow-credentials": "true",
			"access-control-allow-methods": "GET,POST,PUT,OPTIONS",
			"access-control-allow-headers": "content-type, accept, cookie"
		});
		res.end();
		return;
	}

	const url = new URL(req.url, `http://${req.headers.host}`);
	if (url.pathname === "/__mock__/reset" && req.method === "POST") {
		reset(url.searchParams.get("scenario") ?? "registered");
		respond(res, { scenario: state.scenario });
		return;
	}
	if (url.pathname === "/__mock__/state") {
		respond(res, state);
		return;
	}
	if (url.pathname === "/__mock__/mutate" && req.method === "POST") {
		const body = await readJson(req);
		if (body && typeof body.field === "string") state.application[body.field] = body.value;
		respond(res, state.application);
		return;
	}
	if (url.pathname === "/DEPARTMENTS.json") {
		const body = JSON.stringify(departmentsFixture);
		res.writeHead(200, {
			"content-type": "application/json",
			"content-length": Buffer.byteLength(body)
		});
		res.end(body);
		return;
	}

	// ---- SSO (/api/v1/*) ----
	if (url.pathname.startsWith("/api/v1/")) {
		if (url.pathname === "/api/v1/ping" && req.method === "GET") {
			return ssoRespond(res, "pong", "pong");
		}
		if (url.pathname === "/api/v1/code/sms" && req.method === "POST") {
			return ssoRespond(res, "ok", "ok");
		}
		if (url.pathname === "/api/v1/register" && req.method === "POST") {
			return ssoRespond(res, "ok", "ok");
		}
		if (url.pathname === "/api/v1/logout" && req.method === "POST") {
			ssoSession = null;
			return ssoRespond(res, "ok", "ok");
		}
		if (url.pathname === "/api/v1/login" && req.method === "POST") {
			const body = await readJson(req);
			const ok = body.validate_code
				? body.phone === ssoInfo.phone &&
					body.email === ssoInfo.email &&
					body.validate_code === ssoSmsCode
				: (body.phone === ssoInfo.phone || body.email === ssoInfo.email) &&
					body.password === ssoPassword;
			if (!ok) return ssoRespond(res, "wrong password", "", 401);
			ssoSession = `mock-session-${Date.now()}`;
			const bodyOut = JSON.stringify({ message: "ok", data: "ok" });
			res.writeHead(200, {
				"content-type": "application/json",
				"content-length": Buffer.byteLength(bodyOut),
				connection: "close",
				"set-cookie": `SSO_SESSION=${ssoSession}; Path=/; HttpOnly`,
				"access-control-allow-origin": appOrigin,
				"access-control-allow-credentials": "true"
			});
			res.end(bodyOut);
			return;
		}
		if (url.pathname === "/api/v1/user/my") {
			if (!isAuthed(req)) return ssoRespond(res, "unauthorized", "", 401);
			if (req.method === "GET") return ssoRespond(res, "ok", ssoInfo);
			if (req.method === "PUT") {
				const body = await readJson(req);
				Object.assign(ssoInfo, body);
				return ssoRespond(res, "ok", ssoInfo);
			}
		}
		return ssoRespond(res, "not found", "", 404);
	}

	// ---- HR routes: scenario "authed" 需要有效 SSO_SESSION cookie ----
	const protectedHr =
		url.pathname === "/user/me" ||
		url.pathname.startsWith("/recruitments/") ||
		url.pathname.startsWith("/applications/");
	if (protectedHr && !isAuthed(req)) {
		return respond(res, null, 401, "authentication failed could not get uid");
	}

	if (url.pathname === "/user/me") return respond(res, user());
	if (
		url.pathname === "/recruitments/pending" ||
		url.pathname === `/recruitments/${recruitment.uid}`
	)
		return respond(res, recruitment);
	if (url.pathname.startsWith(`/recruitments/${recruitment.uid}/interviews/`))
		return respond(res, interviewTimes);
	if (url.pathname.includes("/written-test-type/")) return respond(res, 2);
	if (url.pathname.includes("/written-test-url/"))
		return respond(res, "https://example.test/written-test");
	if (url.pathname.endsWith("/resume")) {
		res.writeHead(200, {
			"content-type": "application/pdf",
			"access-control-allow-origin": appOrigin,
			"access-control-allow-credentials": "true"
		});
		res.end("mock resume");
		return;
	}

	if (req.method === "POST" && url.pathname === "/applications/") {
		const form = await new Request(`http://mock${url.pathname}`, {
			method: "POST",
			headers: req.headers,
			body: req,
			duplex: "half"
		}).formData();
		if (state.scenario === "registered" || state.scenario === "unregistered") {
			state.scenario = "registered";
		} else if (state.scenario === "authed-clean") {
			// 报名后进入带认证且有申请的 authed 状态
			state.scenario = "authed";
		}
		state.application = makeApplication(String(form.get("group") ?? "web"));
		applyFormToApplication(form);
		state.mutations.push({
			method: "POST",
			path: url.pathname,
			fields: Object.fromEntries(form.entries())
		});
		return respond(res, state.application);
	}

	if (req.method === "PUT" && url.pathname.startsWith("/applications/")) {
		return new Promise((resolve) => {
			const consume = async () => {
				state.mutations.push({ method: "PUT", path: url.pathname });
				if (url.pathname.endsWith("/file/WrittenTest")) {
					const form = await new Request(`http://mock${url.pathname}`, {
						method: "PUT",
						headers: req.headers,
						body: req,
						duplex: "half"
					}).formData();
					state.application.answer = "mock-wt-answer.pdf";
					state.mutations[state.mutations.length - 1].fields = Object.fromEntries(
						form.entries()
					);
				} else if (url.pathname.endsWith("/abandoned")) {
					req.on("data", () => {});
					await new Promise((done) => req.on("end", done));
					state.application.abandoned = true;
				} else if (url.pathname.includes("/interview/group/self")) {
					req.on("data", () => {});
					await new Promise((done) => req.on("end", done));
					state.application.interview_allocations_group = interviewTimes[0];
				} else if (url.pathname.includes("/interview/team/self")) {
					req.on("data", () => {});
					await new Promise((done) => req.on("end", done));
					state.application.interview_allocations_team = interviewTimes[0];
				} else if (url.pathname.includes("/slots/group")) {
					req.on("data", () => {});
					await new Promise((done) => req.on("end", done));
					state.application.interview_selections = [interviewTimes[1]];
				} else if (url.pathname.includes("/slots/team")) {
					req.on("data", () => {});
					await new Promise((done) => req.on("end", done));
					state.application.interview_selections = [interviewTimes[1]];
				} else {
					// 普通资料更新 (FormData)
					const form = await new Request(`http://mock${url.pathname}`, {
						method: "PUT",
						headers: req.headers,
						body: req,
						duplex: "half"
					}).formData();
					applyFormToApplication(form);
					state.mutations[state.mutations.length - 1].fields = Object.fromEntries(
						form.entries()
					);
				}
				respond(res, state.application);
				resolve();
			};
			consume();
		});
	}

	respond(res, { error: `Unhandled ${req.method} ${url.pathname}` }, 404);
}).listen(port, "127.0.0.1", () => console.log(`Mock API listening on ${port}`));