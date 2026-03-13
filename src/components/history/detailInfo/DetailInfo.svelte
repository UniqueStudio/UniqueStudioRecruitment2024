<script lang="ts">
	/* eslint-disable svelte/no-at-html-tags */
	import { push } from "svelte-spa-router";
	import { Group } from "../../../config/const";
	import Button from "../../public/Button.svelte";
	import Popover from "../../public/Popover.svelte";
	import type { UserStep } from "../../../types";
	import TimeSelector from "./TimeSelector.svelte";
	import InterviewInfo from "./InterviewInfo.svelte";
	import greet from "../../../assets/greet.svg";
	import NightTestInfo from "./NightTestInfo.svelte";
	import { userInfo } from "../../../stores/userInfo";
	import { recruitment } from "../../../stores/recruitment";
	import type { Application } from "../../../types/application";
	import { formatDate, formatTime } from "../../../utils/formmatDate";
	import { parseTitle } from "../../../utils/parseTitle";
	import { t } from "../../../utils/t";
	import { onMount } from "svelte";
	import {
		WrittenTestType,
		writtenTestLink,
		writtenTestType,
		isGettingWrittenTestFile,
		isUploading,
		file,
		interviewTimesPromise,
		createInterviewTimesPromiseController,
		fetchWrittenTest,
		doUpload,
		createApplicationInfoSelectTimeHandler,
		getApplicationInfoSelectedTimeIds
	} from "./detailInfoStore";

	export let step: UserStep;
	export let applicationInfo: Application;
	$: myWrittenTestAnswer = applicationInfo?.answer?.split("/").at(-1);
	const handleClick = (e) => {
		if (e.target.className.includes("go-user")) {
			push("/user");
		}
	};
	let fileInput: HTMLInputElement;
	const uploadAnswer = () => {
		if (!$file) {
			fileInput.click();
		} else {
			doUpload(applicationInfo);
		}
	};

	onMount(async () => {
		if (step === $t("history.step.WrittenTest")) {
			await fetchWrittenTest(applicationInfo);
		}
	});

	const interviewTimesMode = step === $t("history.step.TeamTimeSelection") ? "team" : "group";
	const interviewTimesController = createInterviewTimesPromiseController({
		applicationInfo,
		mode: interviewTimesMode,
		promiseStore: interviewTimesPromise
	});
	if (
		step === $t("history.step.GroupTimeSelection") ||
		step === $t("history.step.TeamTimeSelection")
	) {
		interviewTimesController.init();
	}
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="mt-[3rem] w-full rounded-lg bg-blue-100 p-[20px_28px] max-sm:hidden">
	{#if step !== $t("history.step.Pass")}
		<p class="mb-[1rem] text-lg font-bold">
			{$t("history.currentProcess")}：{step}
		</p>
	{/if}
	{#if step === $t("history.step.SignUp")}
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<p on:click={handleClick}>
			{@html $userInfo.applications[0]?.recruitment_id === $recruitment.uid
				? $t("history.signUpTips.SignInTips", {
						changeInfo: `<span
         class="text-blue-300 underline cursor-pointer go-user">${$t("history.signUpTips.changeInfo")}</span
      >`,
						group: Group[$userInfo.applications[0]?.group],
						recruitment: $parseTitle($recruitment.name)
					})
				: $t("history.signUpTips.notSignInTips", {
						changeInfo: `<span
        
        class="text-blue-300 underline cursor-pointer go-user">${$t("history.signUpTips.changeInfo")}</span
      >`
					})}
		</p>
	{:else if step === $t("history.step.WrittenTest")}
		<p>{$t("history.writeTest.tips")}</p>
		<input
			on:change={(e) => {
				const el = e.currentTarget;
				if (el.files?.[0]) file.set(el.files[0]);
			}}
			bind:this={fileInput}
			type="file"
			class="hidden"
		/>
		{#if $isGettingWrittenTestFile && !$writtenTestLink}
			<p class="mt-[0.5rem]">{$t("history.writeTest.loading")}</p>
			<Button
				highlight
				className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px] opacity-50"
				>{$t("history.writeTest.loading")}
			</Button>
		{/if}
		{#if $writtenTestLink}
			<p class="mt-[0.5rem]">
				{@html $t("history.writeTest.viewLink", {
					writtenTest: `<a
        class=" text-blue-300 underline"
        href=${$writtenTestLink}
        download=${$t("history.step.WrittenTest")}>${$t("history.writeTest.writtenTest")}</a
      >`
				})}
			</p>
			{#if $writtenTestType === WrittenTestType.Url}
				<p class="text-gray-500 mt-[0.5rem]">{$t("history.writeTest.urlTips")}</p>
			{:else if $writtenTestType === WrittenTestType.File}
				{#if myWrittenTestAnswer}
					<div class="border-blue-200 shadow-sm mb-5 mt-5 rounded-[10px] border bg-white p-3">
						<p class="text-gray-500 mb-1 text-[1.1rem] font-bold">
							{$t("history.writeTest.myAnswer")}
						</p>
						<p class="break-all font-medium">{myWrittenTestAnswer}</p>
					</div>
				{/if}
				<Button
					highlight
					className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
					isLoading={$isUploading}
					onClick={uploadAnswer}
				>
					{$file
						? $t("history.mobile.uploadWrittenTest") +
							($file.name.length > 16
								? $file.name.slice(0, 8) + "..." + $file.name.slice(-8)
								: $file.name)
						: $t("history.mobile.selectWrittenTest")}
				</Button>
			{/if}
		{/if}
	{:else if step === $t("history.step.GroupTimeSelection")}
		{#await $interviewTimesPromise}
			<p>{$t("history.groupInterviewTimeSelector.loading")}</p>
		{:then res}
			<div class="space-y-2">
				<!-- todo/: res.data.filter过期时间and已满时间 -->
				<TimeSelector
					type="group"
					aid={applicationInfo.uid}
					times={res.data}
					maxSelected={1}
					selectedTimes={getApplicationInfoSelectedTimeIds({
						applicationInfo,
						type: "group",
						isSingleMode: true
					})}
					onSelectTime={createApplicationInfoSelectTimeHandler({
						applicationInfo,
						times: res.data,
						onUpdated: () => (applicationInfo = applicationInfo)
					})}
					on:reloadTimes={interviewTimesController.reload}
					enableSlot={true}
				>
					<div slot="timeSlot" let:time class="flex items-center gap-1">
						<span class="bg-green-400 h-2 w-2 rounded-full"></span>
						<span class="text-xs">剩余 {time.slot_number - time.select_number} 个位置</span>
					</div>
				</TimeSelector>
				<div class="text-gray-500 flex items-center gap-1 text-sm">
					<Popover>
						<span slot="children"
							>选择候选时间<span
								class="ml-1 inline h-5 w-5 cursor-pointer items-center justify-center text-blue-400"
								>?</span
							></span
						>
						<span slot="content"
							>请勾选所有您方便参加面试的时段，作为您的备选时段。若原定排期需调整，面试官将优先从您的候选名单中进行匹配并及时通知您。</span
						>
					</Popover>
				</div>
				<TimeSelector
					type="group"
					aid={applicationInfo.uid}
					times={res.data}
					maxSelected={0}
					selectedTimes={getApplicationInfoSelectedTimeIds({
						applicationInfo,
						type: "group",
						isSingleMode: false
					})}
					onSelectTime={createApplicationInfoSelectTimeHandler({
						applicationInfo,
						times: res.data,
						onUpdated: () => (applicationInfo = applicationInfo)
					})}
				/>
			</div>
		{/await}
	{:else if step === $t("history.step.GroupInterview")}
		<InterviewInfo
			group={applicationInfo.group}
			time={applicationInfo.interview_allocations_group.uid
				? `${$formatDate(
						applicationInfo.interview_allocations_group.date
					)} ${$formatTime(applicationInfo.interview_allocations_group.start)}`
				: ""}
			type="group"
		/>
	{:else if step === $t("history.step.StressTest")}
		<NightTestInfo
			group={applicationInfo.group}
			time={$formatDate($recruitment.stress_test_start) +
				$formatTime($recruitment.stress_test_start)}
		/>
	{:else if step === $t("history.step.TeamTimeSelection")}
		{#await $interviewTimesPromise}
			<p>{$t("history.teamInterviewTimeSelector.loading")}</p>
		{:then res}
			<div class="space-y-2">
				<TimeSelector
					type="team"
					aid={applicationInfo.uid}
					times={res.data}
					maxSelected={1}
					selectedTimes={getApplicationInfoSelectedTimeIds({
						applicationInfo,
						type: "team",
						isSingleMode: true
					})}
					onSelectTime={createApplicationInfoSelectTimeHandler({
						applicationInfo,
						times: res.data,
						onUpdated: () => (applicationInfo = applicationInfo)
					})}
					on:reloadTimes={interviewTimesController.reload}
					enableSlot={true}
				>
					<div slot="timeSlot" let:time class="flex items-center gap-1">
						<span class="bg-green-400 h-2 w-2 rounded-full"></span>
						<span class="text-xs">剩余 {time.slot_number - time.select_number} 个位置</span>
					</div>
				</TimeSelector>
				<div class="text-gray-500 flex items-center gap-1 text-sm">
					<Popover>
						<span slot="children">选择候选时间</span>
						<span slot="content"> 请选择所有可以参与面试的时间，以供面试官调整 </span>
					</Popover>
				</div>
				<TimeSelector
					type="team"
					aid={applicationInfo.uid}
					times={res.data}
					maxSelected={0}
					selectedTimes={getApplicationInfoSelectedTimeIds({
						applicationInfo,
						type: "team",
						isSingleMode: false
					})}
					onSelectTime={createApplicationInfoSelectTimeHandler({
						applicationInfo,
						times: res.data,
						onUpdated: () => (applicationInfo = applicationInfo)
					})}
				/>
			</div>
		{/await}
	{:else if step === $t("history.step.TeamInterview")}
		<InterviewInfo
			time={applicationInfo.interview_allocations_team.uid
				? `${$formatDate(
						applicationInfo.interview_allocations_team.date
					)} ${$formatTime(applicationInfo.interview_allocations_team.start)}`
				: ""}
			type="team"
			group={applicationInfo.group}
		/>
	{:else if step === $t("history.step.Pass")}
		<div class="flex items-center gap-[4px]">
			<p class="text-lg">{$t("history.passTips")}</p>
			<img class="inline" src={greet} alt="欢迎" />
		</div>
		<p class="mt-[8px] text-gray-300">{$t("history.passSubTips")}</p>
	{/if}
</div>
