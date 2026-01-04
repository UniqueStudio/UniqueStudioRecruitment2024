<script lang="ts">
	import { slide } from "svelte/transition";
	import arrow from "/src/assets/arrow.svg";
	import cx from "clsx";
	import { onMount } from "svelte";
	import BottomBar from "../public/BottomBar.svelte";
	import { isMobile } from "../../stores/isMobile";
	export let necessary: boolean = false;
	export let name: string;
	export let content: string;
	export let selectItems: readonly string[];
	export let editMode: boolean = false;
	export let placeholder: string = "";
	export let className: string = "";
	let input: HTMLDivElement;
	//ly: when bind:content isn't useful, use content & onChange
	export let onChange: (content?: string) => void = () => {};

	let showItems = false;
	onMount(() => {
		const close = () => {
			showItems = false;
		};
		document.addEventListener("click", close);
		return () => {
			document.removeEventListener("click", close);
		};
	});
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
	on:click={(e) => e.stopPropagation()}
	class={cx(["flex items-center gap-[1rem] max-lg:my-[1.5rem]", className])}
>
	<p class="shrink-0 max-sm:text-sm">
		{#if necessary}
			<span class="text-blue-300">*</span>
		{/if}{name}
	</p>
	<div class="relative w-full">
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div
			bind:this={input}
			on:click={() => {
				if (!editMode) return;
				showItems = !showItems;
			}}
			class={cx([
				"relative flex h-[48px] w-full items-center rounded-[8px] border-[1px] bg-gray-50 p-[4px_12px] text-text-1 outline-none transition-all focus:border-[#165DFF] max-sm:h-[42px] max-sm:text-sm",
				editMode
					? "cursor-pointer border-[1px] border-gray-200 bg-transparent"
					: "border-transparent"
			])}
		>
			<input disabled value={content} class="pointer-events-none w-full bg-transparent" />
			<img
				src={arrow}
				alt="arrow"
				class={cx([
					" h-[16px] flex-shrink-0 transition-all max-sm:hidden",
					showItems || "rotate-180",
					editMode || "hidden"
				])}
			/>
		</div>
		{#if showItems}
			<div
				class="shadow-lg absolute left-0 top-[110%] z-10 max-h-[300px] w-full overflow-y-auto rounded-[4px] border-[1px] border-gray-150 bg-white p-[0.75rem_1rem] shadow-card shadow-gray-150 max-sm:hidden"
				transition:slide
			>
				{#if placeholder}
					<p class="cursor-pointer rounded-[0.5rem] p-[0.5rem_0.75rem] opacity-50 transition-all">
						{placeholder}
					</p>
				{/if}
				{#each selectItems as item (item)}
					<!-- svelte-ignore a11y-click-events-have-key-events -->
					<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
					<p
						on:click={() => {
							content = item;
							onChange(item);
							showItems = false;
						}}
						class="cursor-pointer rounded-[0.5rem] p-[0.5rem_0.75rem] transition-all hover:bg-gray-150"
					>
						{item}
					</p>
				{/each}
			</div>
		{/if}
	</div>
</div>

<BottomBar
	on:close={() => (showItems = false)}
	show={$isMobile && showItems}
	className="h-[200px] overflow-y-auto "
>
	{#if placeholder}
		<p class="cursor-pointer rounded-[0.5rem] p-[1rem_0.75rem] text-sm opacity-50 transition-all">
			{placeholder}
		</p>
	{/if}
	{#each selectItems as item (item)}
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<p
			on:click={() => {
				content = item;
				onChange(item);
				showItems = false;
			}}
			class="mx-[3rem] cursor-pointer rounded-[0.5rem] border-b-[1px] border-b-gray-150 p-[1rem_0.75rem] text-center transition-all hover:bg-gray-150"
		>
			{item}
		</p>
	{/each}
</BottomBar>
