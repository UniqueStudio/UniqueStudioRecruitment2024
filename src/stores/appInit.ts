import { get } from "svelte/store";
import { userInfo } from "./userInfo";
import { latestDraft } from "./latestDraft";
import { recruitment } from "./recruitment";
import { getLatestRecruitment } from "../requests/recruitment/getLatest";
import { departments } from "./departments";
import { getDepartments } from "../requests/config/getDepartments";
import { parseDepartments } from "../utils/parseDepartments";
import { Message } from "../utils/Message";
import { translate } from "../utils/t";

/**
 * 应用初始化：一次性拉取用户信息、最新招募和部门列表
 * 供 App.svelte 在挂载时调用
 */
export function initializeApp(): void {
	const $userInfo = get(userInfo);
	const $latestDraft = get(latestDraft);
	const $recruitment = get(recruitment);
	const $departments = get(departments);

	if ($userInfo && !$latestDraft) {
		latestDraft.hydrateFromUser($userInfo);
	}

	if (!$userInfo) {
		userInfo.refresh().catch((err: Error) => {
			if (err.message === "authentication failed could not get uid") {
				return;
			}
			Message.error(translate("header.getInfoFailed"));
		});
	}

	if (!$recruitment) {
		getLatestRecruitment()
			.then((res) => {
				recruitment.setRecruitments(res.data);
			})
			.catch((err: Error) => {
				if (
					err.message === "authentication failed could not get uid" ||
					err.message === `ERROR: invalid input syntax for type uuid: \\"\\" (SQLSTATE 22P02)`
				) {
					return;
				}
				Message.error(translate("header.getInfoFailed"));
			});
	}

	if (!$departments.length) {
		getDepartments()
			.then((resp) => parseDepartments(resp.data.nodes))
			.then((resp) => {
				const keys = Object.keys(resp);
				if (keys.length <= 10) {
					throw Error("专业个数过少");
				}
				const firstKey = keys[0];
				if (typeof firstKey !== "string") {
					throw Error("firstKey 应为 string");
				}
				if (!Array.isArray(resp[firstKey])) {
					throw Error("元素不为数组");
				}
				return resp;
			})
			.catch(async (e: Error) => {
				console.error("解析 飞书 专业列表报错：", e.message, "进入fallback");
				return (await import("../config/DEPARTMENTS")).default;
			})
			.then(departments.setDepartments);
	}
}
