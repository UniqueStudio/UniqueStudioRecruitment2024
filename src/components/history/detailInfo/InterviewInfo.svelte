<script lang="ts">
	// 目前找不到更好的方法解决
	/* eslint-disable svelte/no-at-html-tags */

	import { Group, InterviewPlace } from "../../../config/const";
	import type { InterviewType } from "../../../types";
	import { t } from "../../../utils/t";

	interface Props {
		time?: string;
		group?: string;
		type: InterviewType;
	}

	let { time = "", group = "", type }: Props = $props();
</script>

{#if time}
	<p class="max-sm:text-cente max-sm:text-smr">
		{#if type === "group"}
			{@html $t("history.groupInterview.tips", {
				group: Group[group],
				time: `<span class="text-blue-300">${time}</span>`,
				room: `<span class="text-blue-300"
      >${InterviewPlace[group]}</span>`
			})}
		{:else}
			{@html $t("history.teamInterview.tips", {
				time: `<span class="text-blue-300">${time}</span>`,
				room: `<span class="text-blue-300"
      >${InterviewPlace[group]}</span>`
			})}
		{/if}
	</p>
{:else}
	<p class="text-gray-300 max-sm:text-center">{$t("history.groupInterview.noTime")}</p>
{/if}
