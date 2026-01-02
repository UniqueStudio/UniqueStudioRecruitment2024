<script lang="ts">
	import cx from "clsx";
	import { t } from "../../utils/t";
	import Popover from "../public/Popover.svelte";
	export let necessary: boolean = false;
	export let name: string;
	export let content: string;
	export let editMode: boolean = false;
	export let tips: string = "";
	export let errorMessage: string = "";
	export let isDisabled: boolean = false;
</script>

<div class="max-lg:my-[1.5rem] flex flex-col gap-[0.5rem]">
	<div class="flex items-center gap-[1rem]">
		<p class="  max-sm:text-sm shrink-0">
			{#if necessary}
				<span class="text-blue-300">*</span>
			{/if}{name}
		</p>
		{#if tips !== ""}
			<Popover
				direct="top"
				questionDirection="end"
				style="white"
				className="w-full"
				shouldShow={editMode}
			>
				<input
					on:blur
					on:input
					disabled={isDisabled || !editMode}
					placeholder={editMode ? $t("user.placeholder") : ""}
					class={cx([
						"max-sm:text-sm text-text-1 max-sm:h-[42px] h-[48px] w-full rounded-[8px] border-[1px] bg-[#FAFAFA] p-[4px_12px] transition-all outline-none  focus:border-[#165DFF]",
						errorMessage ? "border-red-500" : (editMode && !isDisabled ? "border-gray-200 bg-transparent" : "border-transparent")
					])}
					bind:value={content}
					slot="children"
				/>
				<p slot="content" class="w-[180px]">
					{tips}
				</p>
			</Popover>
		{:else}
			<input
				on:blur
				on:input
				disabled={isDisabled || !editMode}
				placeholder={editMode ? $t("user.placeholder") : ""}
				class={cx([
					"max-sm:text-sm text-text-1 max-sm:h-[42px] h-[48px] w-full rounded-[8px] border-[1px] bg-[#FAFAFA] p-[4px_12px] transition-all outline-none  focus:border-[#165DFF]",
					errorMessage ? "border-red-500" : (editMode && !isDisabled ? "border-gray-200 bg-transparent" : "border-transparent")
				])}
				bind:value={content}
			/>
		{/if}
	</div>
	{#if errorMessage}
		<p class="text-red-500 text-xs ml-[3rem]">{errorMessage}</p>
	{/if}
</div>
