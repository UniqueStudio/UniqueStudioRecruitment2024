/* eslint-disable @typescript-eslint/no-explicit-any */
import { get } from "svelte/store";
import { userInfo } from "../stores/userInfo";
import { latestDraft } from "../stores/latestDraft";
import { recruitment } from "../stores/recruitment";
import { editMode } from "../stores/editMode";
import { checkNecessaryInfo } from "../utils/checkNecessaryInfo";
import { signUpRecruitment } from "../requests/application/signUpRecruitment";
import { updateApplication } from "../requests/application/updateApplication";
import { Message } from "../utils/Message";
import { translate } from "../utils/t";

const t = (key: string, vars?: Record<string, string>) => translate(key, undefined, vars);

export interface ApplicationFormState {
	rank: string;
	referrer: string;
	major: string;
	qq_account: string;
	institute: string;
	groups: string[];
	grade: string;
	intro: string;
	/** 当前语言下"快速通道"的字符串值，用于 is_quick 的转换 */
	isQuick: string;
	/** 当前语言下"有意向参与 Project C"的字符串值 */
	isProjectC: string;
	resume?: File;
}

/**
 * 报名最新招募
 * @returns true 表示成功，调用方可关闭报名弹窗
 */
export async function signUp(form: ApplicationFormState): Promise<boolean> {
	const {
		rank,
		referrer,
		major,
		qq_account,
		institute,
		groups,
		grade,
		intro,
		resume,
		isQuick,
		isProjectC
	} = form;

	const $checkNecessaryInfo = get(checkNecessaryInfo);
	const projectCOptions = t("user.selector.projectC") as any as string[];
	if (
		!$checkNecessaryInfo({
			rank,
			major,
			institute,
			groups,
			grade,
			intro,
			qq_account,
			is_quick: isQuick === t("user.quick"),
			is_project_c: isProjectC === projectCOptions[0]
		})
	)
		return false;

	const $recruitment = get(recruitment);
	try {
		for (const group of groups) {
			const formData = new FormData();
			formData.append("recruitment_id", $recruitment.uid);
			if (resume) formData.append("resume", resume);
			for (const [key, value] of Object.entries({
				rank,
				major,
				qq_account,
				institute,
				group,
				grade,
				intro,
				referrer,
				is_quick: isQuick === t("user.quick") ? "true" : "false"
			})) {
				formData.append(key, String(value));
			}
			await signUpRecruitment(formData);
		}
		Message.success(t("user.signUpSuccess"));
		editMode.out();
		await userInfo.refresh();
		return true;
	} catch {
		Message.error(t("user.signUpFail"));
		return false;
	}
}

/**
 * 保存申请表单信息
 * 若当前还在招募流程中则同步到后端，否则仅保存到本地
 * @returns true 表示保存成功
 */
export async function saveApplicationInfo(form: ApplicationFormState): Promise<boolean> {
	const { rank, referrer, major, qq_account, institute, groups, grade, intro, resume, isQuick } =
		form;

	const $checkNecessaryInfo = get(checkNecessaryInfo);
	if (
		!$checkNecessaryInfo({
			rank,
			major,
			institute,
			qq_account,
			groups,
			grade,
			intro,
			is_quick: isQuick === t("user.quick")
		})
	)
		return false;

	const $recruitment = get(recruitment);
	const $userInfo = get(userInfo);
	const hasAppliedCurrentRecruitment =
		!!$recruitment && $recruitment.uid === $userInfo.applications[0]?.recruitment_id;

	if (
		$recruitment &&
		$recruitment.uid === $userInfo.applications[0]?.recruitment_id &&
		!$userInfo.applications[0]?.rejected &&
		!$userInfo.applications[0]?.abandoned
	) {
		// 还在招募流程中 → 同步到后端
		const formData = new FormData();
		formData.append("recruitment_id", $recruitment.uid);
		if (resume) formData.append("resume", resume);
		for (const [key, value] of Object.entries({
			rank,
			major,
			institute,
			qq_account,
			grade,
			intro,
			referrer,
			is_quick: isQuick === t("user.quick") ? "true" : "false"
		})) {
			formData.append(key, value);
		}
		try {
			// lyx: 可能有多个申请
			for (const app of $userInfo.applications) {
				if (app.recruitment_id !== $recruitment.uid) continue;
				await updateApplication(app.uid, formData);
			}
			await userInfo.refresh();
			Message.success(t("user.saveSuccess"));
		} catch {
			Message.error(t("user.saveFailed"));
			return false;
		}
	} else {
		// 未报名当前批次或流程已结束：仅保存本地草稿，文件不会保存
		latestDraft.patchDraft({
			rank,
			referrer,
			major,
			qq_account,
			institute,
			groups,
			grade,
			intro,
			is_quick: isQuick === t("user.quick")
		});

		if (!hasAppliedCurrentRecruitment && resume) {
			Message.warning(t("user.resumeNotSavedNotSignedUp"));
		} else {
			Message.success(t("user.localSaveSuccess"));
		}
	}

	editMode.out();
	return true;
}
