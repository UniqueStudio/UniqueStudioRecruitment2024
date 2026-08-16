<script lang="ts">
	import { fade, slide } from "svelte/transition";
	import cx from "clsx";
	import { t } from "../../utils/t";
	interface Props {
		show?: boolean;
		className?: string;
		confirm?: boolean;
		onClose?: () => void;
		onConfirm?: () => void;
		children?: import("svelte").Snippet;
	}

	let {
		show = false,
		className = "",
		confirm = false,
		onClose = () => {},
		onConfirm = () => {},
		children
	}: Props = $props();
	const close = () => {
		onClose();
	};
	const ensure = () => {
		onConfirm();
	};
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
{#if show}
	<div
		transition:slide
		class={cx(["fixed bottom-0 left-0 z-30 w-full rounded-t-md bg-white text-sm transition-all"])}
	>
		<div class="flex h-[53px] items-center p-[1rem]">
			<p class="text-gray-300" onclick={close}>
				{$t("history.mobile.cancel")}
			</p>
			{#if confirm}
				<p class="ml-auto text-blue-400" onclick={ensure}>
					{$t("history.mobile.confirm")}
				</p>
			{/if}
		</div>
		<div class={className}>
			{@render children?.()}
		</div>
	</div>
{/if}

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
{#if show}
	<div
		onclick={close}
		transition:fade
		class={cx(["fixed left-0 top-0 z-10 h-full w-full bg-black/60"])}
	></div>
{/if}
