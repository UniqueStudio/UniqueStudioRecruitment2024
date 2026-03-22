<script lang="ts">
	import cx from "clsx";
	import { scale } from "svelte/transition";
	import question from "../../assets/question.svg";
	import Modal from "./Modal.svelte";
	// import { isMobile } from "../../stores/isMobile";

	interface Props {
		//ly: now i just finished top & bottom props cuz i'm lazy :)
		direct?: "left" | "right" | "top" | "bottom" | "left-top";
		style?: "white" | "black";
		questionDirection?: "front" | "end";
		className?: string;
		isShowImg?: boolean;
		shouldShow?: boolean;
		children?: import("svelte").Snippet;
		content?: import("svelte").Snippet;
	}

	let {
		direct = "bottom",
		style = "black",
		questionDirection = "front",
		className = "",
		isShowImg = true,
		shouldShow = true,
		children,
		content
	}: Props = $props();
	let box: HTMLDivElement = $state();
	let showContent = $state(false);
	let showModal = $state(false);
	let timerIn: ReturnType<typeof setTimeout>;
	let timerOut: ReturnType<typeof setTimeout>;

	const handleMouseMoveIn = () => {
		if (!shouldShow) return;
		clearTimeout(timerOut);
		timerIn = setTimeout(() => {
			showContent = true;
		}, 300);
	};
	const handleMouseMoveOut = () => {
		clearTimeout(timerIn);
		timerOut = setTimeout(() => {
			showContent = false;
		}, 500);
	};
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
	role="tooltip"
	onpointerover={handleMouseMoveIn}
	onpointerout={handleMouseMoveOut}
	bind:this={box}
	class={cx([
		"relative w-fit max-sm:flex max-sm:gap-[8px]",
		questionDirection === "end" && "max-sm:flex-row-reverse",
		className
	])}
>
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	{#if isShowImg}
		<img class="inline sm:hidden" onclick={() => (showModal = true)} src={question} alt="?" />
	{/if}
	{@render children?.()}
	{#if showContent}
		<div
			transition:scale
			class={cx([
				"absolute z-[90] rounded-[6px]",
				style === "black" ? "shadow-drop" : "shadow-card",
				direct === "bottom" &&
					"left-[50%]  top-[calc(100%_+_12px)] origin-[top_center] translate-x-[-50%] ",
				direct === "top" &&
					"bottom-[calc(100%_+_12px)] left-[50%] origin-[bottom_center] translate-x-[-50%]",
				direct === "left-top" && "bottom-[calc(100%_+_12px)] left-[0] origin-[bottom_left] "
			])}
		>
			<div
				class={cx([
					"w-fit min-w-[180px] max-w-[320px] whitespace-normal rounded-[6px] border-gray-150 p-[8px_12px] text-center text-sm",
					style === "black" ? "bg-black text-white" : "bg-white text-black"
				])}
			>
				{@render content?.()}
			</div>
			<div
				class={cx([
					"absolute h-0 w-0 border-[8px] border-transparent ",
					direct === "bottom" && "left-[calc(50%_-_8px)] top-[-14px]",
					direct === "top" && "bottom-[-14px] left-[calc(50%_-_8px)] rotate-180",
					direct === "left-top" && "bottom-[-14px] left-[8px] rotate-180",
					style === "black" ? "border-b-black" : "border-b-white"
				])}
			></div>
		</div>
	{/if}
</div>

<Modal
	className="p-[1rem] text-sm text-center"
	onCancel={() => (showModal = false)}
	visible={showModal}
>
	{@render content?.()}
</Modal>
