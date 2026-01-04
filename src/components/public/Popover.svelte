<script lang="ts">
	import cx from "clsx";
	import { scale } from "svelte/transition";
	import question from "../../assets/question.svg";
	import Modal from "./Modal.svelte";
	// import { isMobile } from "../../stores/isMobile";
	//ly: now i just finished top & bottom props cuz i'm lazy :)
	export let direct: "left" | "right" | "top" | "bottom" | "left-top" = "bottom";
	export let style: "white" | "black" = "black";
	export let questionDirection: "front" | "end" = "front";
	export let className: string = "";
	export let isShowImg = true;
	export let shouldShow: boolean = true;
	let box: HTMLDivElement;
	let showContent = false;
	let showModal = false;
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

<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<div
	role="tooltip"
	on:pointerover={handleMouseMoveIn}
	on:pointerout={handleMouseMoveOut}
	bind:this={box}
	class={cx([
		"relative w-fit max-sm:flex max-sm:gap-[8px]",
		questionDirection === "end" && "max-sm:flex-row-reverse",
		className
	])}
>
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	{#if isShowImg}
		<img class="inline sm:hidden" on:click={() => (showModal = true)} src={question} alt="?" />
	{/if}
	<slot name="children" />
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
					"w-fit  rounded-[6px] border-gray-150 p-[8px_12px] text-center text-sm",
					style === "black" ? "bg-black text-white" : "bg-white text-black"
				])}
			>
				<slot name="content" />
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
	<slot name="content" />
</Modal>
