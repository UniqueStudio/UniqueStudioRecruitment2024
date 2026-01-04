<script lang="ts">
	import { fly, slide } from "svelte/transition";
	import { GROUP } from "../../config/const";
	import ApplicationState from "./ApplicationState.svelte";
	import ApplicationTitle from "./ApplicationTitle.svelte";
	import TimeLine from "./TimeLine.svelte";
	import out from "../../assets/out.svg";
	import DetailInfo from "./detailInfo/DetailInfo.svelte";
	import greet from "../../assets/greet.svg";
	import arrow from "../../assets/arrow.svg";
	import type { ProcessState as ProcessStateType, TimeLineNode, UserStep } from "../../types";
	import Button from "../public/Button.svelte";
	import type { Application } from "../../types/application";
	import clsx from "clsx";
	import { t } from "../../utils/t";
	import Modal from "../public/Modal.svelte";
	import MobileDetailInfo from "./detailInfo/MobileDetailInfo.svelte";
	// import { push } from "svelte-spa-router";
	import { recruitment } from "../../stores/recruitment";

	export let title: string;
	export let group: GROUP | null = null;
	export let step: UserStep;
	export let state: ProcessStateType;
	export let index: number;
	export let applicationInfo: Application = null;
	let showDetail = false;
	$: timeline = $t("history.timeLine") as unknown as TimeLineNode[];
	let showMobileModal = false;
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<div
	in:fly={{ y: 100 * (index + 1), duration: 500, delay: 500 }}
	out:fly={{ y: 50, duration: 500 }}
	class="mt-[1rem] rounded-[20px] bg-white p-[3rem_4rem] max-sm:rounded-[6px] max-sm:p-[20px_18px] sm:shadow-card"
>
	<div class="flex items-center gap-[0.5rem]">
		<ApplicationTitle {title} {group} />
		<ApplicationState {state} />
		<img
			src={arrow}
			on:click={() => (showDetail = !showDetail)}
			alt="查看详情"
			class={clsx([
				"ml-auto cursor-pointer sm:hidden",
				showDetail || "rotate-180",
				state !== $t("history.processState.PROCESSING") && "hidden"
			])}
		/>
	</div>

	{#if state === $t("history.processState.PROCESSING")}
		<p class="my-[8px] text-sm text-text-4 sm:hidden">
			{$t("history.currentProcess")}：{step}
		</p>
		{#if showDetail}
			<div transition:slide>
				<button
					on:click={() => (showMobileModal = true)}
					class="mb-[16px] mt-[8px] rounded-full bg-blue-100 p-[5px_12px] text-xs text-blue-400 sm:hidden"
					>{$t("history.viewDetails")}</button
				>
				<TimeLine items={timeline} className="mt-[24px] px-[12px] text-sm" currentItem={step} />
				<DetailInfo {step} {applicationInfo} />
			</div>
		{:else if group}
			<div class="flex max-sm:hidden">
				<Button
					highlight
					onClick={() => (showDetail = true)}
					className="p-[7px_20px] text-sm ml-auto rounded-full block clear-both"
					>{$t("history.viewDetails")}</Button
				>
			</div>
		{:else}
			<p class="mt-[8px] text-text-4 max-sm:text-sm">
				{$t("history.notApplyTips")}
			</p>
			<div class="flex">
				<Button
					highlight
					onClick={() => (showDetail = true)}
					className="p-[7px_20px] text-sm ml-auto rounded-full block clear-both"
					>{$t("history.step.SignUp")}</Button
				>
			</div>
		{/if}
	{:else if state === $t("history.processState.OUT")}
		<p class="mt-[1rem] text-text-4 max-sm:text-sm">
			{$t("history.outTips")}<img class="inline" src={out} alt="out" />
		</p>
	{:else if state === $t("history.processState.OVER")}
		<p class="mt-[1rem] text-text-4">{$t("history.overTips")}</p>
	{:else if state === $t("history.processState.PASS")}
		<div class="mt-[8px] flex items-center gap-[4px]">
			{#if $recruitment.name.endsWith("C")}
				<p class="text-lg max-sm:text-sm">{$t("history.passTipsSummerCamp")}</p>
			{:else}
				<p class="text-lg max-sm:text-sm">{$t("history.passTips")}</p>
			{/if}

			<img class="inline" src={greet} alt="欢迎" />
		</div>
	{/if}
</div>

<Modal visible={showMobileModal} onCancel={() => (showMobileModal = false)}>
	<MobileDetailInfo {step} onCancel={() => (showMobileModal = false)} {applicationInfo} />
</Modal>
