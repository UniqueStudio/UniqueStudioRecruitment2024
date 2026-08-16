import { get, writable } from "svelte/store";
import type { ApplicationMutipleGroups, EditableInfo } from "../types/application";
import type { User } from "../types/user";
import { produce } from "immer";
import { userInfo } from "./userInfo";

const isString = (value: unknown): value is string => typeof value === "string";
const isBoolean = (value: unknown): value is boolean => typeof value === "boolean";
const isOptionalString = (value: unknown): value is string | undefined =>
	typeof value === "undefined" || typeof value === "string";
const isOptionalBoolean = (value: unknown): value is boolean | undefined =>
	typeof value === "undefined" || typeof value === "boolean";

const isApplicationMutipleGroups = (value: unknown): value is ApplicationMutipleGroups => {
	if (!value || typeof value !== "object") return false;

	const data = value as Record<string, unknown>;
	return (
		Array.isArray(data.groups) &&
		data.groups.every(isString) &&
		isString(data.uid) &&
		isString(data.created_at) &&
		isString(data.updated_at) &&
		isString(data.grade) &&
		isString(data.institute) &&
		isString(data.major) &&
		isString(data.rank) &&
		isString(data.intro) &&
		isBoolean(data.is_quick) &&
		isOptionalBoolean(data.is_project_c) &&
		isString(data.referrer) &&
		isOptionalString(data.qq_account) &&
		isString(data.resume) &&
		isString(data.candidate_id) &&
		isString(data.recruitment_id) &&
		isOptionalString(data.answer) &&
		isOptionalString(data.title)
	);
};

const getValidatedValue = (key: string): ApplicationMutipleGroups | undefined => {
	const raw = localStorage.getItem(key);
	if (!raw) return undefined;

	try {
		const parsed = JSON.parse(raw) as unknown;
		if (isApplicationMutipleGroups(parsed)) return parsed;
	} catch {
		// Ignore malformed JSON and clear stale cache below.
	}

	localStorage.removeItem(key);
	return undefined;
};

const createEmptyDraft = (user: User | undefined): ApplicationMutipleGroups => ({
	created_at: "",
	updated_at: "",
	grade: "",
	institute: "",
	major: "",
	rank: "",
	intro: "",
	is_quick: false,
	is_project_c: false,
	referrer: "",
	qq_account: user?.qq_account || "",
	resume: "",
	candidate_id: user?.uid || "",
	recruitment_id: "",
	user_detail: null,
	answer: "",
	title: "",
	groups: [] as string[]
});

const createDraftFromUser = (user: User | undefined): ApplicationMutipleGroups | undefined => {
	const activeApplication = user?.applications[0];
	if (!activeApplication) return undefined;

	const groups = user.applications
		.filter(
			(app) =>
				app.recruitment_id === activeApplication.recruitment_id && !app.rejected && !app.abandoned
		)
		.map((app) => app.group)
		.filter((group) => group);

	return {
		...activeApplication,
		groups,
		qq_account: user.qq_account
	};
};

// 该 store 只保存“用户资料页编辑草稿”，不是后端真值。
// 后端真值统一放在 userInfo store。
const createLatestDraftStore = () => {
	const { set, subscribe, update } = writable<ApplicationMutipleGroups | undefined>(undefined);
	const storageKey = (uid: string) => `latest:${uid}`;

	const persist = (uid: string, data: ApplicationMutipleGroups) => {
		localStorage.setItem(storageKey(uid), JSON.stringify(data));
	};

	const hydrateFromUser = (user: User) => {
		const applicationDraft = createDraftFromUser(user);
		if (applicationDraft) {
			set(applicationDraft);
			persist(user.uid, applicationDraft);
			return;
		}

		set(getValidatedValue(storageKey(user.uid)) ?? createEmptyDraft(user));
	};

	const patchDraft = (info: EditableInfo) => {
		update((oldInfo) => {
			const currentUser = get(userInfo);
			if (!currentUser) return oldInfo;
			const baseDraft =
				oldInfo ?? createDraftFromUser(currentUser) ?? createEmptyDraft(currentUser);

			const newInfo = produce(baseDraft, (draft) => {
				Object.keys(info).forEach((key) => {
					if (key === "groups") {
						draft[key] = info[key].map((item: string) => item.toLowerCase());
					} else {
						draft[key] = info[key];
					}
				});
			});

			persist(currentUser.uid, newInfo);
			return newInfo;
		});
	};

	return { subscribe, hydrateFromUser, patchDraft };
};

export const latestDraft = createLatestDraftStore();
