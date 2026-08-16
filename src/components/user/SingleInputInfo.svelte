<script lang="ts">
	import { createBubbler } from "svelte/legacy";

	const bubble = createBubbler();
	import cx from "clsx";
	import { t } from "../../utils/t";
	import Popover from "../public/Popover.svelte";
	interface Props {
		necessary?: boolean;
		name: string;
		content: string;
		editMode?: boolean;
		tips?: string;
		errorMessage?: string;
		isDisabled?: boolean;
	}

	let {
		necessary = false,
		name,
		content: inputValue = $bindable(),
		editMode = false,
		tips = "",
		errorMessage = "",
		isDisabled = false
	}: Props = $props();
</script>

<div class="flex flex-col gap-[0.5rem] max-lg:my-[1.5rem]">
	<div class="flex items-center gap-[1rem]">
		<p class="  shrink-0 max-sm:text-sm">
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
					onblur={bubble("blur")}
					oninput={bubble("input")}
					disabled={isDisabled || !editMode}
					placeholder={editMode ? $t("user.placeholder") : ""}
					class={cx([
						"h-[48px] w-full rounded-[8px] border-[1px] bg-[#FAFAFA] p-[4px_12px] text-text-1 outline-none transition-all focus:border-[#165DFF] max-sm:h-[42px]  max-sm:text-sm",
						errorMessage
							? "border-red-500"
							: editMode && !isDisabled
								? "border-gray-200 bg-transparent"
								: "border-transparent"
					])}
					bind:value={inputValue}
				/>
				{#snippet content()}
					<p class="w-[180px]">
						{tips}
					</p>
				{/snippet}
			</Popover>
		{:else}
			<input
				onblur={bubble("blur")}
				oninput={bubble("input")}
				disabled={isDisabled || !editMode}
				placeholder={editMode ? $t("user.placeholder") : ""}
				class={cx([
					"h-[48px] w-full rounded-[8px] border-[1px] bg-[#FAFAFA] p-[4px_12px] text-text-1 outline-none transition-all focus:border-[#165DFF] max-sm:h-[42px]  max-sm:text-sm",
					errorMessage
						? "border-red-500"
						: editMode && !isDisabled
							? "border-gray-200 bg-transparent"
							: "border-transparent"
				])}
				bind:value={inputValue}
			/>
		{/if}
	</div>
	{#if errorMessage}
		<p class="text-red-500 ml-[3rem] text-xs">{errorMessage}</p>
	{/if}
</div>
