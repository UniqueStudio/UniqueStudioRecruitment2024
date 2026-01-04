<script lang="ts">
	import cx from "clsx";
	import { createEventDispatcher } from "svelte";
	import { fade, slide } from "svelte/transition";
	import title from "../../assets/titleBlack.svg";
	import closeSvg from "../../assets/close.svg";
	import arrow from "../../assets/arrow.svg";
	import { t } from "../../utils/t";
	import { location, push } from "svelte-spa-router";
	import { localeLanguage } from "../../stores/localeLanguage";
	import { LANGUAGES } from "../../config/const";
	import { i18nConstants } from "../../config/i18n";
	import { editMode } from "../../stores/editMode";
	import { Message } from "../../utils/Message";
	export let hide = true;
	const dispatch = createEventDispatcher<{ hide: void }>();
	let openLanguage = false;
	const i18nKeys = Object.keys(i18nConstants) as (keyof typeof i18nConstants)[];
	const router = [
		{
			location: "/",
			name: "header.applications"
		},
		{
			location: "/user",
			name: "header.info"
		}
	];
	const close = () => {
		dispatch("hide");
	};
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
	class={cx([
		"fixed left-0 top-0 z-20 h-full w-[70%] bg-white transition-all duration-700",
		hide ? "translate-x-[-100%]" : "translate-x-0"
	])}
>
	<div class="flex w-full items-center p-[1rem]">
		<img on:click={close} src={closeSvg} alt="X" />
		<img src={title} alt="联创招新" class="ml-[1rem] h-[22px] flex-shrink-0 self-center" />
	</div>
	{#each router as item (item.location)}
		<div
			on:click={() => {
				if ($editMode) {
					Message.warning("请先退出编辑模式，以防数据丢失");
					return;
				}
				push(item.location);
			}}
			class={cx([
				"h-[62px] p-[20px_16px]",
				$location === item.location && "bg-gray-100 text-blue-400"
			])}
		>
			{$t(item.name)}
		</div>
	{/each}
	<div
		on:click={() => (openLanguage = !openLanguage)}
		class={cx([
			"flex h-[62px] items-center p-[20px_16px]",
			openLanguage === true && "bg-gray-100 text-blue-400"
		])}
	>
		<p>{$t("header.language")}</p>
		<!-- svelte-ignore a11y-missing-attribute -->
		<img
			src={arrow}
			class={cx(["ml-[16px] mt-[2px] w-[16px]", openLanguage ? "rotate-0" : "rotate-180"])}
		/>
	</div>
	{#if openLanguage}
		<div class="px-[1rem]" transition:slide>
			{#each i18nKeys as key (key)}
				<div
					transition:slide
					on:click={() => {
						openLanguage = false;
						localeLanguage.updateLanguage(key);
					}}
					class="h-[62px] w-full p-[20px_16px] text-text-4 hover:bg-gray-150"
				>
					{LANGUAGES[key]}
				</div>
			{/each}
		</div>
	{/if}
	<div
		on:click={() => (window.location.href = "https://sso2024.hustunique.com/")}
		class={cx(["h-[62px] p-[20px_16px]"])}
	>
		{$t("header.accountManagement")}
	</div>
	<div
		on:click={() =>
			(window.location.href =
				"https://sso2024.hustunique.com/login?logout=true&from=join2024.hustunique.com")}
		class={cx(["h-[62px] p-[20px_16px] text-red-warning"])}
	>
		{$t("header.logout")}
	</div>
</div>
<!-- svelte-ignore a11y-no-static-element-interactions -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
{#if !hide}
	<div
		on:click={close}
		transition:fade
		class={cx(["fixed left-0 top-0 z-10 h-full w-full bg-black/60"])}
	></div>
{/if}
