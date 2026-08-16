<script lang="ts">
	import cx from "clsx";
	interface Props {
		className?: string;
		highlight?: boolean;
		onClick?: () => void;
		isLoading?: boolean;
		disabled?: boolean;
		children?: import("svelte").Snippet;
	}

	let {
		className = "",
		highlight = false,
		onClick = () => {},
		isLoading = false,
		disabled = false,
		children
	}: Props = $props();
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	onclick={() => disabled || isLoading || onClick()}
	class={cx([
		"w-fit cursor-pointer rounded-[8px] text-center transition-all hover:opacity-80",
		highlight ? " bg-blue-400 text-white" : "bg-[#F3F3F5]",
		isLoading && "cursor-wait opacity-50",
		disabled && "cursor-not-allowed opacity-50",
		className
	])}
>
	{@render children?.()}
</div>
