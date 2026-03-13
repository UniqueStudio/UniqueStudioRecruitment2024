import { writable, get } from "svelte/store";
import type { Writable } from "svelte/store";
import type { SingleTime } from "../../../types";
import type { Application } from "../../../types/application";
import { getInterviewTimes } from "../../../requests/application/getInterviewTimes";
import { allocateInterviewTime } from "../../../requests/application/allocateApplications";
import { setFallbackInterviewTimes } from "../../../requests/application/setInterviewTimes";
import {
	getWrittenTest,
	getWrittenTestUrl,
	getWrittenTestType
} from "../../../requests/recruitment/getWrittenTest";
import { uploadWrittenTest } from "../../../requests/application/uploadWrittenTest";
import { userInfo } from "../../../stores/userInfo";
import { globalLoading } from "../../../stores/globalLoading";
import { Message } from "../../../utils/Message";
import { translate } from "../../../utils/t";

export enum WrittenTestType {
	None = 0,
	File = 1,
	Url = 2
}

export const writtenTestLink = writable("");
export const writtenTestType = writable<WrittenTestType>(WrittenTestType.None);
export const isGettingWrittenTestFile = writable(false);
export const isUploading = writable(false);
export const file = writable<File | undefined>(undefined);
export const interviewTimesPromise = writable<ReturnType<typeof getInterviewTimes> | undefined>(
	undefined
);
export const groupInterviewTimesPromise = writable<
	ReturnType<typeof getInterviewTimes> | undefined
>(undefined);
export const teamInterviewTimesPromise = writable<ReturnType<typeof getInterviewTimes> | undefined>(
	undefined
);

export type InterviewTimesMode = "group" | "team";

type RequestState = {
	interviewTimes: {
		group?: {
			key: string;
			promise: ReturnType<typeof getInterviewTimes>;
		};
		team?: {
			key: string;
			promise: ReturnType<typeof getInterviewTimes>;
		};
	};
	writtenTest?: {
		key: string;
		promise: Promise<void>;
	};
};

const requestState = writable<RequestState>({
	interviewTimes: {}
});

const interviewTimesCacheKey = (applicationInfo: Application, mode: InterviewTimesMode) =>
	`${applicationInfo.recruitment_id}:${mode === "team" ? "unique" : applicationInfo.group}`;

const writtenTestCacheKey = (applicationInfo: Application) =>
	`${applicationInfo.recruitment_id}:${applicationInfo.group}`;

function fetchInterviewTimes(applicationInfo: Application, mode: InterviewTimesMode) {
	return getInterviewTimes(
		applicationInfo.recruitment_id,
		mode === "team" ? "unique" : applicationInfo.group
	);
}

export function getInterviewTimesPromise(applicationInfo: Application, mode: InterviewTimesMode) {
	const key = interviewTimesCacheKey(applicationInfo, mode);
	const cached = get(requestState).interviewTimes[mode];
	if (cached?.key === key) return cached.promise;

	const promise = fetchInterviewTimes(applicationInfo, mode);
	requestState.update((state) => ({
		...state,
		interviewTimes: {
			...state.interviewTimes,
			[mode]: { key, promise }
		}
	}));
	return promise;
}

export function refreshInterviewTimesPromise(
	applicationInfo: Application,
	mode: InterviewTimesMode
) {
	const key = interviewTimesCacheKey(applicationInfo, mode);
	const promise = fetchInterviewTimes(applicationInfo, mode);
	requestState.update((state) => ({
		...state,
		interviewTimes: {
			...state.interviewTimes,
			[mode]: { key, promise }
		}
	}));
	return promise;
}

export function createInterviewTimesPromiseController(params: {
	applicationInfo: Application;
	mode: InterviewTimesMode;
	promiseStore: Writable<ReturnType<typeof getInterviewTimes> | undefined>;
}) {
	const { applicationInfo, mode, promiseStore } = params;

	return {
		init() {
			promiseStore.set(getInterviewTimesPromise(applicationInfo, mode));
		},
		reload() {
			promiseStore.set(refreshInterviewTimesPromise(applicationInfo, mode));
		}
	};
}

export async function selectInterviewTimes(params: {
	uuid: string;
	isSelected: boolean;
	isSingleMode: boolean;
	selectedTimes: string[];
	aid: string;
	type: "team" | "group";
}) {
	const { uuid, isSelected, isSingleMode, selectedTimes, aid, type } = params;

	if (isSingleMode) {
		if (isSelected) return undefined;
		if (!window.confirm(translate("history.timeSelector.confirmSelection"))) return undefined;

		return allocateInterviewTime({ aid, type, iid: uuid })
			.then(() => {
				Message.success(translate("history.timeSelector.chooseSuccess"));
				return [uuid];
			})
			.catch(() => {
				Message.error(translate("history.timeSelector.chooseFailed"));
				return undefined;
			});
	}

	const nowSelectedTimes = isSelected
		? [...selectedTimes.filter((el) => el !== uuid)]
		: [...selectedTimes, uuid];

	return setFallbackInterviewTimes({ iids: nowSelectedTimes, aid, type })
		.then(() => {
			Message.success(translate("history.timeSelector.chooseSuccess"));
			return nowSelectedTimes;
		})
		.catch(() => {
			Message.error(translate("history.timeSelector.chooseFailed"));
			return undefined;
		});
}

export function syncApplicationInfoSelectedTimes(params: {
	applicationInfo: Application;
	times: SingleTime[];
	selectedIds: string[];
	type: "team" | "group";
	isSingleMode: boolean;
}) {
	const { applicationInfo, times, selectedIds, type, isSingleMode } = params;

	if (isSingleMode) {
		const selectedTime = times.find((time) => selectedIds.includes(time.uid));
		if (!selectedTime) return;

		if (type === "group") {
			applicationInfo.interview_allocations_group = selectedTime;
			return;
		}

		applicationInfo.interview_allocations_team = selectedTime;
		return;
	}

	applicationInfo.interview_selections = times.filter((time) => selectedIds.includes(time.uid));
}

export function createApplicationInfoSelectTimeHandler(params: {
	applicationInfo: Application;
	times: SingleTime[];
	onUpdated?: () => void;
}) {
	const { applicationInfo, times, onUpdated } = params;

	return (selectParams: {
		uuid: string;
		isSelected: boolean;
		isSingleMode: boolean;
		selectedTimes: string[];
		aid: string;
		type: "team" | "group";
	}) =>
		selectInterviewTimes(selectParams).then((selectedIds) => {
			if (!selectedIds) return selectedIds;

			syncApplicationInfoSelectedTimes({
				applicationInfo,
				times,
				selectedIds,
				type: selectParams.type,
				isSingleMode: selectParams.isSingleMode
			});
			onUpdated?.();

			return selectedIds;
		});
}

export function getApplicationInfoSelectedTimeIds(params: {
	applicationInfo: Application;
	type: "team" | "group";
	isSingleMode: boolean;
}) {
	const { applicationInfo, type, isSingleMode } = params;

	if (isSingleMode) {
		const selectedId =
			type === "group"
				? applicationInfo.interview_allocations_group?.uid
				: applicationInfo.interview_allocations_team?.uid;

		return selectedId ? [selectedId] : [];
	}

	return applicationInfo.interview_selections?.map((selection) => selection.uid) ?? [];
}

export async function fetchWrittenTest(applicationInfo: Application) {
	const key = writtenTestCacheKey(applicationInfo);
	const cached = get(requestState).writtenTest;
	if (cached?.key === key) {
		return cached.promise;
	}

	isGettingWrittenTestFile.set(true);
	const promise = (async () => {
		const typeResp = await getWrittenTestType(
			applicationInfo.recruitment_id,
			applicationInfo.group
		);
		if (!typeResp.ok) {
			Message.warning(translate("history.writeTest.downloadError"));
			return;
		}
		const typeData = await typeResp.json();
		if (typeData.data === 2) {
			// 在线问卷链接
			const res = await getWrittenTestUrl(applicationInfo.recruitment_id, applicationInfo.group);
			if (!res.ok) {
				Message.warning(translate("history.writeTest.downloadError"));
				return;
			}
			const data = await res.json();
			writtenTestLink.set(data.data);
			writtenTestType.set(WrittenTestType.Url);
			return;
		}

		if (typeData.data === 1) {
			// 文件下载
			const res = await getWrittenTest(applicationInfo.recruitment_id, applicationInfo.group);
			if (!res.ok) {
				Message.warning(translate("history.writeTest.downloadError"));
				return;
			}
			const blob = await res.blob();
			const url = URL.createObjectURL(blob);
			writtenTestLink.set(url);
			writtenTestType.set(WrittenTestType.File);
			return;
		}

		writtenTestType.set(WrittenTestType.None);
	})().finally(() => {
		isGettingWrittenTestFile.set(false);
	});

	requestState.update((state) => ({
		...state,
		writtenTest: {
			key,
			promise
		}
	}));

	return promise;
}

export function doUpload(applicationInfo: Application) {
	const currentFile = get(file);
	if (!currentFile || get(isUploading)) return;
	isUploading.set(true);
	globalLoading.set(true);
	const formData = new FormData();
	formData.append("file", currentFile);
	uploadWrittenTest(applicationInfo.uid, formData)
		.then(() => {
			Message.success(translate("history.writeTest.uploadSuccess"));
			file.set(undefined);
			return userInfo.refresh();
		})
		.catch(() => Message.error(translate("history.writeTest.uploadError")))
		.finally(() => {
			isUploading.set(false);
			globalLoading.set(false);
		});
}
