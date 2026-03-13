<script lang="ts">
	import { push } from "svelte-spa-router";
	import { Group } from "../../../config/const";
	import type { Application } from "../../../types/application";
	import Button from "../../public/Button.svelte";
	import Popover from "../../public/Popover.svelte";
	import type { UserStep } from "../../../types";
	import { recruitment } from "../../../stores/recruitment";
	import { userInfo } from "../../../stores/userInfo";
	import { parseTitle } from "../../../utils/parseTitle";
	import { formatDate, formatTime } from "../../../utils/formmatDate";
	import { t } from "../../../utils/t";
	import InterviewInfo from "./InterviewInfo.svelte";
	import BottomBar from "../../public/BottomBar.svelte";
	import TimeSelector from "./TimeSelector.svelte";
	import NightTestInfo from "./NightTestInfo.svelte";
	import greet from "../../../assets/greet.svg";
	import { onMount } from "svelte";
	import {
		WrittenTestType,
		writtenTestLink,
		writtenTestType,
		isGettingWrittenTestFile,
		file,
		groupInterviewTimesPromise,
		teamInterviewTimesPromise,
		createInterviewTimesPromiseController,
		fetchWrittenTest,
		doUpload,
		createApplicationInfoSelectTimeHandler,
		getApplicationInfoSelectedTimeIds
	} from "./detailInfoStore";

	$: myWrittenTestAnswer = $userInfo?.applications[0]?.answer.split("/").at(-1);
	let openGroupInterviewTimeSelector = false;
	let openTeamInterviewTimeSelector = false;
	const handleClick = (e) => {
		if (e.target.className.includes("go-user")) {
			push("/user");
		}
	};

	export let applicationInfo: Application;
	export let step: UserStep;

	let fileInput: HTMLInputElement;
	const uploadAnswer = () => {
		if (!$file) {
			fileInput.click();
		} else {
			doUpload(applicationInfo);
		}
	};

	const groupInterviewTimesController = createInterviewTimesPromiseController({
		applicationInfo,
		mode: "group",
		promiseStore: groupInterviewTimesPromise
	});
	const teamInterviewTimesController = createInterviewTimesPromiseController({
		applicationInfo,
		mode: "team",
		promiseStore: teamInterviewTimesPromise
	});

	if (step === $t("history.step.GroupTimeSelection")) {
		groupInterviewTimesController.init();
	}

	if (step === $t("history.step.TeamTimeSelection")) {
		teamInterviewTimesController.init();
	}

	export let onCancel: () => void;
	const onSaveAndCancel = async () => {
		// 注意这里必须要刷新 userInfo，不然下一次点进来显示不对
		// await userInfo.refresh();
		onCancel();
	};
	onMount(async () => {
		if (step === $t("history.step.WrittenTest")) {
			await fetchWrittenTest(applicationInfo);
		}
	});
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<div class="w-[270px] p-[20px_16px]">
	<p class="mb-[12px] text-center text-[17px] font-[500]">{step}</p>
	{#if step === $t("history.step.SignUp")}
		<p class="text-center text-sm" on:click={handleClick}>
			{$userInfo.applications[0]?.recruitment_id === $recruitment.uid
				? $t("history.mobile.signUpTips", {
						group: Group[$userInfo.applications[0]?.group],
						recruitment: $parseTitle($recruitment.name)
					})
				: $t("history.mobile.notSignUpTips", {
						recruitment: $parseTitle($recruitment.name)
					})}
		</p>
		<Button
			highlight
			className="mx-auto w-full rounded-full my-[8px] text-[15px] leading-[36px]"
			onClick={() => push("/user")}
			>{applicationInfo ? $t("history.mobile.change") : $t("history.mobile.input")}{$t(
				"header.info"
			)}</Button
		>
	{:else if step === $t("history.step.WrittenTest")}
		<p class="my-[8px] text-center text-sm text-text-4">
			{$t("history.writeTest.tips")}
		</p>
		<input
			on:change={(e) => {
				const el = e.currentTarget;
				if (el.files?.[0]) file.set(el.files[0]);
			}}
			bind:this={fileInput}
			type="file"
			class="hidden"
		/>
		{#if $isGettingWrittenTestFile}
			<p class="my-[8px] text-center text-sm">
				{$t("history.writeTest.loading")}
			</p>
		{/if}
		{#if $writtenTestLink}
			{#if $writtenTestType === WrittenTestType.File}
				{#if myWrittenTestAnswer}
					<div class="border-blue-200 shadow-sm mt-2 rounded-lg border bg-white p-3">
						<p class="text-gray-500 mb-1 text-sm">
							{$t("history.writeTest.myAnswer")}
						</p>
						<p class="break-all font-medium">{myWrittenTestAnswer}</p>
					</div>
				{/if}
				<Button
					highlight
					className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
					><a href={$writtenTestLink} download="${$t('history.step.WrittenTest')}"
						>{$t("history.mobile.viewLink")}</a
					></Button
				>
				<Button
					highlight
					className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
					onClick={uploadAnswer}
					>{$file
						? $t("history.mobile.uploadWrittenTest") +
							($file.name.length > 10
								? $file.name.slice(0, 5) + "..." + $file.name.slice(-5)
								: $file.name)
						: $t("history.mobile.selectWrittenTest")}
				</Button>
			{:else if $writtenTestType === WrittenTestType.Url}
				<Button
					highlight
					className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
					><a href={$writtenTestLink} target="_blank">{$t("history.mobile.viewLink")}</a></Button
				>
			{/if}
		{/if}
	{:else if step === $t("history.step.GroupTimeSelection")}
		<p class="my-[8px] text-center text-sm text-text-4">
			{$t("history.mobile.groupInterviewTips")}
		</p>
		<Button
			onClick={() => (openGroupInterviewTimeSelector = true)}
			highlight
			className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
			>{$t("history.mobile.selectTime")}</Button
		>
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
		<p class="my-[8px] text-center text-sm text-text-4">
			{$t("history.mobile.teamInterviewTips")}
		</p>
		<Button
			onClick={() => (openTeamInterviewTimeSelector = true)}
			highlight
			className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
			>{$t("history.mobile.selectTime")}</Button
		>
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
		<div class="flex items-center justify-center gap-[4px] text-sm">
			<p class="tetx-sm">{$t("history.passTips")}</p>
			<img class="inline" src={greet} alt="欢迎" />
		</div>
		<p class="mt-[8px] text-center text-sm text-gray-300">
			{$t("history.passSubTips")}
		</p>
	{/if}
	<Button
		onClick={onSaveAndCancel}
		className="mx-auto w-full text-[15px] bg-transparent leading-[36px] text-text-3"
		>{$t("history.mobile.known")}</Button
	>
</div>

<BottomBar
	className="min-h-[300px] px-[16px]"
	show={openGroupInterviewTimeSelector}
	on:close={() => (openGroupInterviewTimeSelector = false)}
>
	{#await $groupInterviewTimesPromise}
		<p>{$t("history.groupInterviewTimeSelector.loading")}</p>
	{:then res}
		<div class="space-y-2">
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
				on:reloadTimes={groupInterviewTimesController.reload}
				enableSlot={true}
			>
				<div slot="timeSlot" let:time class="flex items-center gap-1">
					<span class="bg-green-400 h-2 w-2 rounded-full"></span>
					<span class="text-xs">剩余 {time.slot_number - time.select_number} 个位置</span>
				</div>
			</TimeSelector>
			<div class="text-gray-500 flex items-center gap-1 text-sm">
				<span>选择候选时间</span>
				<Popover>
					<span slot="children" class="cursor-pointer">?</span>
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
</BottomBar>

<BottomBar
	className="min-h-[300px] px-[16px]"
	show={openTeamInterviewTimeSelector}
	on:close={() => (openTeamInterviewTimeSelector = false)}
>
	{#await $teamInterviewTimesPromise}
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
				on:reloadTimes={teamInterviewTimesController.reload}
				enableSlot={true}
			>
				<div slot="timeSlot" let:time class="flex items-center gap-1">
					<span class="bg-green-400 h-2 w-2 rounded-full"></span>
					<span class="text-xs">剩余 {time.slot_number - time.select_number} 个位置</span>
				</div>
			</TimeSelector>
			<div class="text-gray-500 flex items-center gap-1 text-sm">
				<span>选择候选时间</span>

				<Popover>
					<span slot="children" class="cursor-pointer">?</span>
					<span slot="content">请选择所有可以参与面试的时间，以供面试官调整</span>
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
</BottomBar>
