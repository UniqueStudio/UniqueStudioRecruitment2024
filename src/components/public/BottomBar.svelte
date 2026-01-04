<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { fade, slide } from "svelte/transition";
	import cx from "clsx";
	import { t } from "../../utils/t";
	export let show = false;
	export let className = "";
	export let confirm = false;
	const dispatch = createEventDispatcher<{ close: void; confirm: void }>();
	const close = () => {
		dispatch("close");
	};
	const ensure = () => {
		dispatch("confirm");
	};
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
{#if show}
	<div
		transition:slide
		class={cx(["fixed bottom-0 left-0 z-30 w-full rounded-t-md bg-white text-sm transition-all"])}
	>
		<div class="flex h-[53px] items-center p-[1rem]">
			<p class="text-gray-300" on:click={close}>
				{$t("history.mobile.cancel")}
			</p>
			{#if confirm}
				<p class="ml-auto text-blue-400" on:click={ensure}>
					{$t("history.mobile.confirm")}
				</p>
			{/if}
		</div>
		<div class={className}>
			<slot />
		</div>
	</div>
{/if}

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
{#if show}
	<div
		on:click={close}
		transition:fade
		class={cx(["fixed left-0 top-0 z-10 h-full w-full bg-black/60"])}
	></div>
{/if}
