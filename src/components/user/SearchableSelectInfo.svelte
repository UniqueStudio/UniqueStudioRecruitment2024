<script lang="ts">
	import { run } from "svelte/legacy";

	import { slide } from "svelte/transition";
	import arrow from "/src/assets/arrow.svg";
	import search from "/src/assets/search.svg";
	import cx from "clsx";
	import { onMount } from "svelte";
	import BottomBar from "../public/BottomBar.svelte";
	import { isMobile } from "../../stores/isMobile";

	interface Props {
		necessary?: boolean;
		name: string;
		content: string;
		selectItems: readonly string[];
		editMode?: boolean;
		placeholder?: string;
		className?: string;
		//ly: when bind:content isn't useful, use content & onChange
		onChange?: (content?: string) => void;
	}

	let {
		necessary = false,
		name,
		content = $bindable(),
		selectItems,
		editMode = false,
		placeholder = "",
		className = "",
		onChange = () => {}
	}: Props = $props();

	let inputWrapper: HTMLDivElement = $state();
	let showItems = $state(false);
	let searchContent = $state(content ?? "");

	let normalizedSearch = $derived(searchContent.trim().toLowerCase());
	let filteredItems = $derived(
		normalizedSearch
			? selectItems.filter((item) => item.toLowerCase().includes(normalizedSearch))
			: [...selectItems]
	);

	run(() => {
		if (!showItems) {
			searchContent = content ?? "";
		}
	});

	const openItems = () => {
		if (!editMode) return;
		showItems = true;
		searchContent = "";
	};

	const closeItems = (withValidation: boolean) => {
		if (!showItems) return;
		showItems = false;
		if (withValidation) validateContent();
	};

	const validateContent = () => {
		if (content && !selectItems.includes(content)) {
			content = "";
			onChange("");
		}
	};

	onMount(() => {
		const close = (e: MouseEvent) => {
			if (inputWrapper && !inputWrapper.contains(e.target as Node)) {
				closeItems(true);
			}
		};
		document.addEventListener("click", close);
		return () => {
			document.removeEventListener("click", close);
		};
	});

	const handleSelect = (item: string) => {
		content = item;
		onChange(item);
		showItems = false;
	};
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	onclick={(e) => e.stopPropagation()}
	class={cx(["flex items-center gap-[1rem] max-lg:my-[1.5rem]", className])}
>
	<p class="shrink-0 max-sm:text-sm">
		{#if necessary}
			<span class="text-blue-300">*</span>
		{/if}{name}
	</p>
	<div class="relative w-full">
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			bind:this={inputWrapper}
			onclick={openItems}
			class={cx([
				"relative flex h-[48px] w-full items-center rounded-[8px] border-[1px] bg-gray-50 p-[4px_12px] text-text-1 outline-none transition-all focus:border-[#165DFF] max-sm:h-[42px] max-sm:text-sm",
				editMode ? "cursor-text border-[1px] border-gray-200 bg-transparent" : "border-transparent"
			])}
		>
			<img
				src={search}
				alt="search"
				class={cx("mr-[8px] h-[16px] w-[16px] flex-shrink-0", !showItems && "hidden")}
			/>
			<input
				disabled={!editMode}
				bind:value={searchContent}
				{placeholder}
				onfocus={openItems}
				oninput={() => editMode && (showItems = true)}
				class={cx("w-full bg-transparent outline-none", !editMode && "pointer-events-none")}
			/>
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
		{#if showItems && !$isMobile}
			<div
				class="shadow-lg absolute left-0 top-[110%] z-10 max-h-[300px] w-full overflow-y-auto rounded-[4px] border-[1px] border-gray-150 bg-white p-[0.75rem_1rem] shadow-card shadow-gray-150 max-sm:hidden"
				transition:slide
			>
				{#if filteredItems.length === 0}
					<p class="text-gray-400 p-[0.5rem_0.75rem] text-sm">无匹配选项</p>
				{:else}
					{#each filteredItems as item (item)}
						<!-- svelte-ignore a11y_click_events_have_key_events -->
						<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
						<p
							onclick={() => handleSelect(item)}
							class="cursor-pointer rounded-[0.5rem] p-[0.5rem_0.75rem] transition-all hover:bg-gray-150"
						>
							{item}
						</p>
					{/each}
				{/if}
			</div>
		{/if}
	</div>
</div>

<BottomBar
	onClose={() => closeItems(true)}
	show={$isMobile && showItems}
	className="h-[200px] overflow-y-auto "
>
	{#if filteredItems.length === 0}
		<p class="text-gray-400 p-[1rem_0.75rem] text-center">无匹配选项</p>
	{:else}
		{#each filteredItems as item (item)}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
			<p
				onclick={() => handleSelect(item)}
				class="mx-[3rem] cursor-pointer rounded-[0.5rem] border-b-[1px] border-b-gray-150 p-[1rem_0.75rem] text-center transition-all hover:bg-gray-150"
			>
				{item}
			</p>
		{/each}
	{/if}
</BottomBar>
