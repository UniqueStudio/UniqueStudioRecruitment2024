<script lang="ts">
	import clsx from "clsx";
	import type { GROUP } from "../../config/const";
	import { t } from "../../utils/t";
	interface Props {
		title: string;
		group: GROUP | null;
	}

	let { title, group }: Props = $props();
</script>

<div class="select-none text-text-1 sm:text-[24px]">
	{title} |
	<span class={clsx(group || "text-text-3")}>{group ? `${group}` : $t("history.notSelected")}</span>
</div>
