<script lang="ts">
	import cx from "clsx";
	import { fade, slide } from "svelte/transition";
	import title from "../../assets/titleBlack.svg";
	import closeSvg from "../../assets/close.svg";
	import arrow from "../../assets/arrow.svg";
	import { t } from "../../utils/t";
	import { goto } from "$app/navigation";
	import { resolve } from "$app/paths";
	import { page } from "$app/stores";
	import { localeLanguage } from "../../stores/localeLanguage";
	import { LANGUAGES } from "../../config/const";
	import { i18nConstants } from "../../config/i18n";
	import { editMode } from "../../stores/editMode";
	import { Message } from "../../utils/Message";
	interface Props {
		hide?: boolean;
		onHide?: () => void;
	}

	let { hide = true, onHide = () => {} }: Props = $props();
	let openLanguage = $state(false);
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
		onHide();
	};
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class={cx([
		"fixed left-0 top-0 z-20 h-full w-[70%] bg-white transition-all duration-700",
		hide ? "translate-x-[-100%]" : "translate-x-0"
	])}
>
	<div class="flex w-full items-center p-[1rem]">
		<img onclick={close} src={closeSvg} alt="X" />
		<img src={title} alt="联创招新" class="ml-[1rem] h-[22px] flex-shrink-0 self-center" />
	</div>
	{#each router as item (item.location)}
		<div
			onclick={() => {
				if ($editMode) {
					Message.warning("请先退出编辑模式，以防数据丢失");
					return;
				}
				goto(resolve(item.location, {}));
			}}
			class={cx([
				"h-[62px] p-[20px_16px]",
				$page.url.pathname === item.location && "bg-gray-100 text-blue-400"
			])}
		>
			{$t(item.name)}
		</div>
	{/each}
	<div
		onclick={() => (openLanguage = !openLanguage)}
		class={cx([
			"flex h-[62px] items-center p-[20px_16px]",
			openLanguage === true && "bg-gray-100 text-blue-400"
		])}
	>
		<p>{$t("header.language")}</p>
		<!-- svelte-ignore a11y_missing_attribute -->
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
					onclick={() => {
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
		onclick={() => (window.location.href = "https://sso2024.hustunique.com/")}
		class={cx(["h-[62px] p-[20px_16px]"])}
	>
		{$t("header.accountManagement")}
	</div>
	<div
		onclick={() =>
			(window.location.href =
				"https://sso2024.hustunique.com/login?logout=true&from=join2024.hustunique.com")}
		class={cx(["h-[62px] p-[20px_16px] text-red-warning"])}
	>
		{$t("header.logout")}
	</div>
</div>
<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
{#if !hide}
	<div
		onclick={close}
		transition:fade
		class={cx(["fixed left-0 top-0 z-10 h-full w-full bg-black/60"])}
	></div>
{/if}
