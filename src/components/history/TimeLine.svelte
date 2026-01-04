<script lang="ts">
	import cx from "clsx";
	import type { TimeLineNode } from "../../types";
	import Popover from "../public/Popover.svelte";

	export let items: readonly TimeLineNode[];
	export let currentItem: string;
	export let className: string = "";
</script>

<div class={cx(["flex w-full items-center gap-[4px] max-sm:hidden", className])}>
	{#each items as item, i (i)}
		{#if item.show}
			{#if item.info}
				<Popover direct="top" style="white">
					<div slot="children" class="relative cursor-pointer">
						<div
							class={cx([
								" h-[8px] w-[8px] rounded-full",
								item.name === currentItem ? "bg-blue-400" : "bg-gray-150"
							])}
						></div>
						<div class="absolute left-[-44px] top-[16px] w-[96px] text-center">
							{item.name}
						</div>
					</div>
					<p slot="content" class="w-fit min-w-[20ch] text-center">
						{item.info}
					</p>
				</Popover>
			{:else}
				<div class="relative">
					<div
						class={cx([
							" h-[10px] w-[10px] rounded-full",
							item.name === currentItem
								? "bg-blue-400"
								: i < items.findIndex((el) => el.name === currentItem)
									? "bg-blue-400/50"
									: "bg-gray-150"
						])}
					></div>
					<div class="absolute left-[-44px] top-[16px] w-[96px] text-center">
						{item.name}
					</div>
				</div>
			{/if}

			{#if i !== items.length - 1}
				<div
					class={cx([
						"h-0 w-full  border-[1px] border-dashed",
						i < items.findIndex((el) => el.name === currentItem)
							? "border-blue-300"
							: "border-blue-dash"
					])}
				></div>
			{/if}
		{/if}
	{/each}
</div>

<div class="sm:hidden">
	{#each items as item, i (i)}
		{#if item.show}
			<div class="flex items-center gap-[12px]">
				<div
					class={cx([
						" h-[8px] w-[8px] rounded-full",
						item.name === currentItem
							? "bg-blue-400"
							: i < items.findIndex((el) => el.name === currentItem)
								? "bg-blue-400/50"
								: "bg-gray-150"
					])}
				></div>
				<p class={cx([item.name === currentItem ? "text-blue-400" : "text-text-1"])}>
					{item.name}
				</p>
			</div>

			{#if i !== items.length - 1}
				<div class="flex">
					<div
						class={cx([
							" ml-[3.5px] h-[48px] w-[1px]",
							i < items.findIndex((el) => el.name === currentItem) ? "bg-blue-300" : "bg-gray-150"
						])}
					></div>
					{#if item.name === currentItem || (i > 0 && items[i - 1].name === currentItem && !items[i - 1].show)}
						<slot />
					{/if}
				</div>
			{/if}
		{/if}
	{/each}
</div>
