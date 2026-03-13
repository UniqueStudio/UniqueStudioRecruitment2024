import { writable } from "svelte/store";
import { getInfo } from "../requests/user/getInfo";
import type { User } from "../types/user";

const isObjectLike = (value: unknown): value is Record<string, unknown> =>
	typeof value === "object" && value !== null;

const deepEqual = (a: unknown, b: unknown): boolean => {
	if (Object.is(a, b)) return true;

	if (Array.isArray(a) && Array.isArray(b)) {
		if (a.length !== b.length) return false;
		for (let i = 0; i < a.length; i += 1) {
			if (!deepEqual(a[i], b[i])) return false;
		}
		return true;
	}

	if (isObjectLike(a) && isObjectLike(b)) {
		const keysA = Object.keys(a);
		const keysB = Object.keys(b);
		if (keysA.length !== keysB.length) return false;

		for (const key of keysA) {
			if (!(key in b)) return false;
			if (!deepEqual(a[key], b[key])) return false;
		}

		return true;
	}

	return false;
};

const createUserStore = () => {
	const { set, subscribe } = writable<User>();
	let current: User | undefined;

	const applyInfo = (next: User) => {
		const shouldUpdateStore = !current || !deepEqual(current, next);
		if (shouldUpdateStore) {
			current = next;
			set(next);
		}

		void import("./latestDraft").then(({ latestDraft }) => {
			latestDraft.hydrateFromUser(next);
		});

		return current ?? next;
	};

	const setInfo = (info: User) => {
		return applyInfo(info);
	};

	const refresh = async () => {
		const res = await getInfo();
		return applyInfo(res.data);
	};

	return {
		subscribe,
		setInfo,
		refresh
	};
};

export const userInfo = createUserStore();
