<script lang="ts">
	//ly: maybe it would be better to encapsulate more UI but to make style flexible i just encapsulate minium UI:)
	import cx from "clsx";
	import { fade, fly } from "svelte/transition";
	export let className = "";
	export let onCancel: () => void;
	export let visible: boolean;
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
{#if visible}
	<div
		transition:fade
		on:click={onCancel}
		class={cx([
			"fixed left-0 top-0 z-[100] flex h-screen w-screen items-center justify-center bg-black/60 transition-all max-sm:text-sm"
		])}
	>
		<div
			on:click={(e) => e.stopPropagation()}
			transition:fly={{ y: 50, duration: 500 }}
			class={cx(["rounded-[8px] bg-white", className])}
		>
			<slot />
		</div>
	</div>
{/if}
