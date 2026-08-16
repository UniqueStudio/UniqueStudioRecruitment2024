import { get } from "svelte/store";
import { userInfo } from "./userInfo";
import { latestDraft } from "./latestDraft";
import { recruitment } from "./recruitment";
import { getLatestRecruitment } from "../requests/recruitment/getLatest";
import { departments, type Departments } from "./departments";
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

	if (!Object.keys($departments).length) {
		fetch(`${import.meta.env.BASE_URL}DEPARTMENTS.json`)
			.then((response) => {
				if (!response.ok) {
					throw new Error(`加载默认专业列表失败: ${response.status}`);
				}
				return response.json() as Promise<Departments>;
			})
			.then((data) => {
				if (!Object.values(data).every(Array.isArray)) {
					throw new Error("默认专业列表格式错误");
				}
				departments.setDepartments(data);
			})
			.catch((error: Error) => {
				console.error(error.message);
				Message.error(translate("header.getInfoFailed"));
			});
	}
}
