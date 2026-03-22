<script lang="ts">
	import { InterviewPlace } from "../../../config/const";
	import { t } from "../../../utils/t";

	interface Props {
		time: string;
		group: string;
	}

	let { time, group }: Props = $props();

	let tipText = $derived($t("history.stressTest.tips", { group }));

	let parts = $derived(tipText.split(/(\{time\}|\{room\})/));
</script>

<p class="max-sm:text-center max-sm:text-sm">
	{#each parts as part, i (i)}
		{#if part === "{time}"}
			<span class="text-blue-300">{time}</span>
		{:else if part === "{room}"}
			<span class="text-blue-300">{InterviewPlace[group]}</span>
		{:else}
			{part}
		{/if}
	{/each}
</p>
