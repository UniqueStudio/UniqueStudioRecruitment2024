<script lang="ts">
	//ly: maybe it would be better to encapsulate more UI but to make style flexible i just encapsulate minium UI:)
	import cx from "clsx";
	import { fade, fly } from "svelte/transition";
	interface Props {
		className?: string;
		onCancel: () => void;
		visible: boolean;
		children?: import("svelte").Snippet;
	}

	let { className = "", onCancel, visible, children }: Props = $props();
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
{#if visible}
	<div
		transition:fade
		onclick={onCancel}
		class={cx([
			"fixed left-0 top-0 z-[100] flex h-screen w-screen items-center justify-center bg-black/60 transition-all max-sm:text-sm"
		])}
	>
		<div
			onclick={(e) => e.stopPropagation()}
			transition:fly={{ y: 50, duration: 500 }}
			class={cx(["rounded-[8px] bg-white", className])}
		>
			{@render children?.()}
		</div>
	</div>
{/if}
