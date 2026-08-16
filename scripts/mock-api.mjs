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
	applications: state.scenario === "registered" ? [state.application] : []
});

const reset = (scenario = "registered") => {
	state.scenario = scenario;
	state.application = makeApplication();
	state.mutations = [];
};
reset();

const respond = (res, data, status = 200) => {
	const body = JSON.stringify({ code: status, data, msg: "ok" });
	res.writeHead(status, {
		"content-type": "application/json",
		"content-length": Buffer.byteLength(body),
		connection: "close",
		"access-control-allow-origin": appOrigin,
		"access-control-allow-credentials": "true"
	});
	res.end(body);
};

createServer(async (req, res) => {
	if (req.method === "OPTIONS") {
		res.writeHead(204, {
			"access-control-allow-origin": appOrigin,
			"access-control-allow-credentials": "true",
			"access-control-allow-methods": "GET,POST,PUT,OPTIONS",
			"access-control-allow-headers": "content-type, accept"
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
		state.scenario = "registered";
		state.application = makeApplication(String(form.get("group") ?? "web"));
		state.mutations.push({
			method: "POST",
			path: url.pathname,
			fields: Object.fromEntries(form.entries())
		});
		return respond(res, state.application);
	}

	if (req.method === "PUT" && url.pathname.startsWith("/applications/")) {
		return new Promise((resolve) => {
			req.on("data", () => {});
			req.on("end", () => {
				state.mutations.push({ method: "PUT", path: url.pathname });
				if (url.pathname.includes("/interview/group/self"))
					state.application.interview_allocations_group = interviewTimes[0];
				if (url.pathname.includes("/slots/group"))
					state.application.interview_selections = [interviewTimes[1]];
				respond(res, state.application);
				resolve();
			});
		});
	}

	respond(res, { error: `Unhandled ${req.method} ${url.pathname}` }, 404);
}).listen(port, "127.0.0.1", () => console.log(`Mock API listening on ${port}`));
