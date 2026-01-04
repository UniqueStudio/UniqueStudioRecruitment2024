<script lang="ts">
	// import { ProcessState } from "../../config/const";
	import cx from "clsx";
	import { t } from "../../utils/t";
	export let state: string;
</script>

<div
	class={cx([
		state === $t("history.processState.OUT") && "border-red-warning bg-gray-red text-red-warning",
		state === $t("history.processState.PROCESSING") && "border-blue-400 bg-gray-blue text-blue-400",
		state === $t("history.processState.PASS") && "border-green-300 bg-gray-green text-green-300",
		state === $t("history.processState.OVER") && "border-orange bg-gray-orange text-orange",
		"w-fit flex-shrink-0 select-none rounded-full border-[1px] px-[1rem] max-sm:p-[3px_8px] max-sm:text-[10px]"
	])}
>
	{state}
</div>
