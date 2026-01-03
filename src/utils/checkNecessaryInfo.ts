import { derived } from "svelte/store";
import type { NecessaryInfo } from "../types/application";
import { Message } from "./Message";
import { t } from "./t";
import { DeprecatedGroups } from "../config/const";

export const checkNecessaryInfo = derived(t, ($t) => (info: NecessaryInfo) => {
	let ok = true;
	Object.keys(info).forEach((key) => {
		if (key === "is_quick") return;
		if (key === "groups" && info[key].some((g) => DeprecatedGroups.includes(g))) {
			ok = false;
			Message.error($t("user.checkDeprecatedGroups"));
		}
		if (info[key].length === 0) {
			ok = false;
			Message.error(
				$t("user.checkInfo", {
					key: $t(`user.necessary.${key}`)
				})
			);
		}
		if (key === "qq_account" && !/^[1-9][0-9]{4,10}$/.test(info[key] as string)) {
			ok = false;
			Message.error($t("user.checkQQ"));
		}
	});
	return ok;
});
