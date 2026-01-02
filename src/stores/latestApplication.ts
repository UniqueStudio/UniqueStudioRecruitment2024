import { writable } from "svelte/store";
import type { ApplicationMutipleGroups, EditableInfo } from "../types/application";
import type { User } from "../types/user";
import { produce } from "immer";

//ly: if we just use UserInfoStore, if we change data in  User Page, data in History Page will also change, so this store is just for User Page
const createLatestApplicationStore = () => {
	const initValue = localStorage.getItem("latest")
		? (JSON.parse(localStorage.getItem("latest")!) as ApplicationMutipleGroups)
		: undefined;
	const { set, subscribe, update } = writable<ApplicationMutipleGroups>(initValue);
	const setApplication = (userInfo: User) => {
		const groups = userInfo.applications
			.filter(
				(app) =>
					app.recruitment_id === userInfo.applications[0]?.recruitment_id &&
					!app.rejected &&
					!app.abandoned
			)
			.map((app) => app.group)
			.filter((g) => g);
		const info: ApplicationMutipleGroups = {
			...userInfo.applications[0],
			groups,
			qq_account: userInfo.qq_account
		};
		set(info);
		localStorage.setItem("latest", JSON.stringify(info));
	};
	const updateInfo = (info: EditableInfo) =>
		update((oldInfo) => {
			oldInfo = oldInfo ?? ({} as ApplicationMutipleGroups);
			const newInfo = produce(oldInfo, (draft) => {
				Object.keys(info).forEach((key) => {
					if (key === "groups") {
						draft[key] = info[key].map((item: string) => item.toLowerCase());
					} else {
						draft[key] = info[key];
					}
				});
			});
			localStorage.setItem("latest", JSON.stringify(newInfo));
			return newInfo;
		});
	return { subscribe, setApplication, updateInfo };
};

export const latestInfo = createLatestApplicationStore();
