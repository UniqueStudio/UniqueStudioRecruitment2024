import { writable, get } from "svelte/store";
import type { Application } from "../types/application";
import type { Recruitment } from "../types/recruitment";
import { getRecruitmentById } from "../requests/recruitment/getById";
import { parseTitle } from "../utils/parseTitle";

export interface ExtendedApplication extends Application {
	title: string;
	end: string;
	deadline: string;
	beginning: string;
}

const applicationsStore = writable<ExtendedApplication[]>([]);
export const extendedApplicationsLoading = writable(false);

let _lastRaw: Application[] | undefined;
let requestVersion = 0;
const recruitmentCache = new Map<string, Recruitment>();

/**
 * 触发异步加载：为每个 application 拉取其对应的招募信息并合并
 * 供 History.svelte 在 rawApplications 变化时调用
 */
export function loadExtendedApplications(rawApplications: Application[]): void {
	// 引用不变且已有数据，直接跳过
	if (_lastRaw === rawApplications && get(applicationsStore).length > 0) {
		return;
	}
	_lastRaw = rawApplications;
	const currentRequest = ++requestVersion;

	if (!rawApplications?.length) {
		applicationsStore.set([]);
		extendedApplicationsLoading.set(false);
		return;
	}

	applicationsStore.set([]);
	extendedApplicationsLoading.set(true);
	Promise.all(
		rawApplications.map(async (application) => {
			const rid = application.recruitment_id;
			if (!recruitmentCache.has(rid)) {
				const res = await getRecruitmentById(rid);
				recruitmentCache.set(rid, res.data);
			}
			const rec = recruitmentCache.get(rid)!;
			const $parseTitle = get(parseTitle);
			return {
				...application,
				title: $parseTitle(rec.name),
				end: rec.end,
				deadline: rec.deadline,
				beginning: rec.beginning
			} as ExtendedApplication;
		})
	)
		.then((res) => {
			// 防止竞态问题：只接受最新一次请求的结果
			if (currentRequest === requestVersion) {
				applicationsStore.set(res);
			}
		})
		.catch(() => {
			if (currentRequest === requestVersion) applicationsStore.set([]);
		})
		.finally(() => {
			if (currentRequest === requestVersion) extendedApplicationsLoading.set(false);
		});
}

export const extendedApplications = { subscribe: applicationsStore.subscribe };
