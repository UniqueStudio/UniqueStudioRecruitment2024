<script lang="ts">
	/* eslint-disable svelte/no-at-html-tags */

	import { fade, fly } from "svelte/transition";
	import UserInfoTitle from "../components/user/UserInfoTitle.svelte";
	import UserProfileForm from "../components/user/UserProfileForm.svelte";
	import UserResumeSection from "../components/user/UserResumeSection.svelte";
	import edit from "/src/assets/edit.svg";
	import Button from "../components/public/Button.svelte";
	import type { College } from "../types";
	import { userInfo } from "../stores/userInfo";
	import { getResume } from "../requests/user/getResume";
	import { recruitment } from "../stores/recruitment";
	import Popover from "../components/public/Popover.svelte";
	import { latestDraft } from "../stores/latestDraft";
	import Modal from "../components/public/Modal.svelte";
	import { parseTitle } from "../utils/parseTitle";
	import { t } from "../utils/t";
	import { departments } from "../stores/departments";
	import { globalLoading } from "../stores/globalLoading";
	import { editMode } from "../stores/editMode";
	import {
		signUp as doSignUp,
		saveApplicationInfo as doSaveApplicationInfo
	} from "../actions/applicationActions";

	let colleges = $derived(Object.keys($departments).sort());
	let isUploading = $state(false);
	let showSignUpModal = $state(false);
	let resume: File = $state();
	let formInitialized = $state(false);
	interface DraftFormState {
		rank: string;
		referrer: string;
		major: string;
		qq_account: string;
		institute: string;
		groups: string[];
		grade: string;
		intro: string;
		is_quick: boolean;
		is_project_c: boolean;
	}
	// groups 应该能申请任意多个组
	let {
		rank = "",
		referrer = "",
		major = "",
		qq_account = "",
		institute = "",
		groups = [],
		grade = "",
		intro = "",
		is_quick = false,
		is_project_c = false
	}: DraftFormState = $state({
		rank: $latestDraft?.rank ?? "",
		referrer: $latestDraft?.referrer ?? "",
		major: $latestDraft?.major ?? "",
		qq_account: $latestDraft?.qq_account ?? "",
		institute: $latestDraft?.institute ?? "",
		groups: $latestDraft?.groups ?? [],
		grade: $latestDraft?.grade ?? "",
		intro: $latestDraft?.intro ?? "",
		is_quick: $latestDraft?.is_quick ?? false,
		is_project_c: $latestDraft?.is_project_c ?? false
	});
	//ly:this asset would be wrong but I just don't want to see TypeError :)
	let majors = $derived($departments[institute as College] || []);
	let ranks = $derived($t("user.selector.rank") as unknown as string[]);
	let genders = $derived($t("user.selector.gender") as unknown as string[]);
	let grades = $derived($t("user.selector.grade") as unknown as string[]);
	let isQuick = $state(($latestDraft?.is_quick ?? false) ? $t("user.quick") : $t("user.notQuick"));
	let isProjectC = $state(
		($latestDraft?.is_project_c ?? false)
			? $t("user.selector.projectC")[0]
			: $t("user.selector.projectC")[1]
	);

	const applyDraft = (draft: Partial<DraftFormState> = {}) => {
		({
			rank = "",
			referrer = "",
			major = "",
			qq_account = "",
			institute = "",
			groups = [],
			grade = "",
			intro = "",
			is_quick = false,
			is_project_c = false
		} = draft);
	};

	$effect(() => {
		isQuick = is_quick ? $t("user.quick") : $t("user.notQuick");
		isProjectC = is_project_c ? $t("user.selector.projectC")[0] : $t("user.selector.projectC")[1];
	});

	$effect(() => {
		const draft = $latestDraft;
		if (!draft || formInitialized) return;

		applyDraft(draft);
		formInitialized = true;
	});

	let quicks = $derived($t("user.selector.isQuick") as unknown as string[]);
	let hasAppliedCurrentRecruitment = $derived(
		!!$recruitment && $userInfo?.applications[0]?.recruitment_id === $recruitment.uid
	);
	let canShowSaveTips = $derived(
		hasAppliedCurrentRecruitment && !$userInfo.applications[0]?.rejected
	);

	let downloadResumeName = $derived(
		$userInfo?.applications[0]?.resume?.split("/").pop() || "个人简历"
	);

	const downloadResume = () => {
		getResume($userInfo.applications[0].uid, downloadResumeName);
	};
	const closeEditMode = () => {
		applyDraft($latestDraft);
		resume = undefined;
		editMode.out();
	};
	const signUp = async () => {
		globalLoading.set(true);
		const ok = await doSignUp({
			rank,
			referrer,
			major,
			qq_account,
			institute,
			groups,
			grade,
			intro,
			isQuick,
			isProjectC,
			resume
		});
		globalLoading.set(false);
		if (ok) {
			showSignUpModal = false;
			resume = undefined;
		}
	};
	const saveApplicationInfo = async () => {
		if (isUploading) return;
		isUploading = true;
		if (resume) globalLoading.set(true);
		const ok = await doSaveApplicationInfo({
			rank,
			referrer,
			major,
			qq_account,
			institute,
			groups,
			grade,
			intro,
			isQuick,
			isProjectC,
			resume
		});
		isUploading = false;
		globalLoading.set(false);
		// doSaveApplicationInfo 不成功时 editMode 不退出，保持表单可继续编辑
		if (!ok) return;
	};
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="mx-auto flex h-full w-[60%] flex-col max-xl:w-[80%] max-sm:w-full">
	<p transition:fade class="text-[26px] text-white max-sm:hidden">
		{$t("user.selfInfo")}
	</p>
	<div
		in:fly={{ y: 50, duration: 500, delay: 500 }}
		out:fly={{ y: 50, duration: 500 }}
		class="my-[1rem] w-[full] rounded-[20px] bg-white px-[55px] py-[30px] max-lg:px-[80px] max-sm:my-0 max-sm:rounded-none max-sm:p-[20px]"
	>
		{#if $userInfo}
			<p transition:fade class="text-text mb-[1rem] font-bold sm:hidden">
				{$t("user.selfInfo")}
			</p>
			<div class="mb-[1rem] flex items-center">
				<UserInfoTitle title={$t("user.basicInfo")} />
				{#if $editMode}
					<div class="ml-auto flex items-center gap-[1rem]">
						<Button
							onClick={closeEditMode}
							className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
							>{$t("user.cancel")}</Button
						>
						<!-- ly: if user applied latest recruitment, "save" button will save info to backend, or will save to localStorage and will not save resume file -->
						<Popover direct="top" questionDirection="end" style="white">
							<Button
								isLoading={isUploading}
								onClick={saveApplicationInfo}
								className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
								highlight>{$t("user.save")}</Button
							>
							{#snippet content()}
								<p class="w-[180px]">
									{canShowSaveTips ? $t("user.saveTips") : $t("user.saveTips1")}
								</p>
							{/snippet}
						</Popover>
					</div>
				{:else}
					<div class="ml-auto flex flex-row-reverse items-center gap-[1rem] max-sm:gap-[0.5rem]">
						{#if $recruitment && $recruitment.uid !== $userInfo.applications[0]?.recruitment_id && new Date().getTime() >= new Date($recruitment.beginning).getTime() && new Date().getTime() <= new Date($recruitment.deadline).getTime()}
							<Popover style="white" direct="top" questionDirection="end">
								<Button
									onClick={() => (showSignUpModal = true)}
									className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
									highlight>{$t("user.signUp")}</Button
								>
								{#snippet content()}
									<p class="w-[142px]">
										{$t("user.signUpConfirm", {
											recruitment: $parseTitle($recruitment.name)
										})}
									</p>
								{/snippet}
							</Popover>
						{/if}
						<div
							onclick={() => {
								editMode.in();
							}}
							class="flex h-[28px] cursor-pointer items-center gap-[0.25rem] rounded-full bg-blue-100 p-[7px_20px] text-sm text-blue-400 max-sm:w-[88px] max-sm:justify-center max-sm:p-[3px_12px]"
						>
							<img src={edit} class="max-sm:hidden" alt="edit" />
							<p class="text-blue-300 max-sm:text-xs">{$t("user.edit")}</p>
						</div>
					</div>
				{/if}
			</div>
			{#if $editMode}
				<p class="mb-[1rem] mt-[-1rem] text-text-4">
					{@html $t("user.modifyBasicInfoTip", {
						link: `<a class="text-blue-400" href="https://sso2024.hustunique.com/">${$t("header.accountManagement")}</a>`
					})}
				</p>
			{/if}
			<UserProfileForm
				user={$userInfo}
				editMode={$editMode}
				{hasAppliedCurrentRecruitment}
				{colleges}
				{majors}
				{genders}
				{grades}
				{ranks}
				{quicks}
				bind:grade
				bind:institute
				bind:major
				bind:rank
				bind:qqAccount={qq_account}
				bind:referrer
				bind:groups
				bind:isQuick
				bind:intro
				onQuickChange={(value) => (is_quick = value === $t("user.quick"))}
			/>
			<div class="mb-[2rem] h-[1px] w-full bg-[#E5E6EB]"></div>
			<UserResumeSection
				editMode={$editMode}
				{hasAppliedCurrentRecruitment}
				hasResume={Boolean($userInfo.applications[0]?.resume)}
				userName={$userInfo.name}
				recruitmentName={$recruitment?.name}
				{downloadResumeName}
				onDownload={downloadResume}
				bind:resume
			/>
		{:else}
			<p class="my-[2rem] text-center text-2xl text-gray-250">暂无个人信息</p>
		{/if}
		<Modal
			className="w-[524px] max-sm:w-[280px] flex flex-col gap-[1rem] text-center p-[20px_20px]"
			visible={showSignUpModal}
			onCancel={() => (showSignUpModal = false)}
		>
			<p>{$t("user.signUpTips")}{$parseTitle($recruitment.name)}</p>
			<p>{$t("user.signUpTips1")}</p>
			<div class="flex justify-center gap-[1rem]">
				<Button onClick={signUp} highlight className="p-[7px_30px] text-sm rounded-full"
					>{$t("user.signUp")}</Button
				>
				<Button
					onClick={() => (showSignUpModal = false)}
					className="p-[7px_30px] text-sm rounded-full">{$t("user.cancel")}</Button
				>
			</div>
		</Modal>
	</div>
</div>
