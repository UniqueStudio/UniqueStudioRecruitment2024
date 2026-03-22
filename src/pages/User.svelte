<script lang="ts">
	import { run } from "svelte/legacy";

	/* eslint-disable svelte/no-at-html-tags */

	import { fade, fly } from "svelte/transition";
	import UserInfoTitle from "../components/user/UserInfoTitle.svelte";
	import SingleInputInfo from "../components/user/SingleInputInfo.svelte";
	import SingleSelectInfo from "../components/user/SingleSelectInfo.svelte";
	import SearchableSelectInfo from "../components/user/SearchableSelectInfo.svelte";
	import edit from "/src/assets/edit.svg";
	import cx from "clsx";
	import Button from "../components/public/Button.svelte";
	import word from "../assets/word.svg";
	import { GENDERS, Group, GroupGroup } from "../config/const";
	import type { College } from "../types";
	import { userInfo } from "../stores/userInfo";
	import { getResume } from "../requests/user/getResume";
	import { recruitment } from "../stores/recruitment";
	import Popover from "../components/public/Popover.svelte";
	import { latestDraft } from "../stores/latestDraft";
	import Modal from "../components/public/Modal.svelte";
	import { Message } from "../utils/Message";
	import { parseTitle } from "../utils/parseTitle";
	import { t } from "../utils/t";
	import { localeLanguage } from "../stores/localeLanguage";
	import uploadSvg from "../assets/upload.svg";
	import { departments } from "../stores/departments";
	import MultiSelectInfo from "../components/user/MultiSelectInfo.svelte";
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
	let fileInput: HTMLInputElement = $state();
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
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
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
	let isProjectC =
		($latestDraft?.is_project_c ?? false)
			? $t("user.selector.projectC")[0]
			: $t("user.selector.projectC")[1];
	run(() => {
		if ($userInfo?.qq_account || $latestDraft?.qq_account) {
			qq_account = $userInfo?.qq_account || $latestDraft?.qq_account || "";
		}
	});

	localeLanguage.subscribe(() => {
		Promise.resolve().then(() => {
			isQuick = is_quick ? $t("user.quick") : $t("user.notQuick");
		});
	});
	let quicks = $derived($t("user.selector.isQuick") as unknown as string[]);
	// $: projectC = $t("user.selector.projectC") as unknown as string[];

	let groupGroupSelected = $derived(
		GroupGroup.map((group) => group.find((g) => groups.some((gg) => Group[gg] === g)) || "") as [
			string | null,
			string | null
		]
	);

	let groupGroupTitles = $derived($t("user.selector.groupGroup") as unknown as [string, string]);
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
		} = $latestDraft || {});
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
			<div class=" mb-[2rem] w-full gap-[2rem] lg:grid lg:grid-cols-2">
				<SingleInputInfo
					necessary
					name={$t("user.name")}
					bind:content={$userInfo.name}
					tips={$t("user.changeUserInfoTip")}
					editMode={$editMode}
					isDisabled={true}
				/>
				<SingleSelectInfo
					necessary
					name={$t("user.gender")}
					content={GENDERS[$userInfo.gender - 1]}
					selectItems={genders}
				/>
				<SingleSelectInfo
					necessary
					editMode={$editMode}
					name={$t("user.grade")}
					bind:content={grade}
					selectItems={grades}
				/>
				<SearchableSelectInfo
					selectItems={colleges}
					editMode={$editMode}
					onChange={() => (major = "")}
					necessary
					name={$t("user.college")}
					bind:content={institute}
				/>
				<SearchableSelectInfo
					placeholder={majors.length ? "" : "请选择学院"}
					selectItems={majors}
					editMode={$editMode}
					necessary
					name={$t("user.major")}
					bind:content={major}
				/>
				<SingleSelectInfo
					editMode={$editMode}
					necessary
					name={$t("user.rank")}
					bind:content={rank}
					selectItems={ranks}
				/>
				<SingleInputInfo
					editMode={$editMode}
					necessary
					name={$t("user.qq")}
					bind:content={qq_account}
					tips={$t("user.changeUserInfoTip")}
					isDisabled={true}
				/>
				<SingleInputInfo
					necessary
					name={$t("user.phone")}
					bind:content={$userInfo.phone}
					tips={$t("user.changeUserInfoTip")}
					editMode={$editMode}
					isDisabled={true}
				/>
				<SingleInputInfo
					necessary
					name={$t("user.email")}
					bind:content={$userInfo.email}
					tips={$t("user.changeUserInfoTip")}
					editMode={$editMode}
					isDisabled={true}
				/>
				<SingleInputInfo
					editMode={$editMode}
					name={$t("user.recommender")}
					bind:content={referrer}
				/>
				<div class="col-span-1 max-w-full gap-[1rem]">
					<Popover
						style="white"
						direct="left-top"
						questionDirection="end"
						className="w-full max-sm:mt-[-1.5rem]"
					>
						<MultiSelectInfo
							className="flex-shrink-0 max-sm:w-[calc(100%_-_24px)]"
							editMode={$editMode && !hasAppliedCurrentRecruitment}
							necessary
							name={$t("user.group")}
							selectedItems={groupGroupSelected}
							onChange={(items) => {
								groups = items
									.map((item) => Object.entries(Group).find(([, v]) => v === item)?.[0])
									.filter((g) => g);
							}}
							selectItems={GroupGroup}
							columnTitles={groupGroupTitles}
						/>
						{#snippet content()}
							<p class="w-[300px]">{$t("user.groupTips")}</p>
						{/snippet}
					</Popover>
				</div>
				<div class="col-span-1 max-w-full gap-[1rem]">
					<Popover
						style="white"
						direct="left-top"
						questionDirection="end"
						className="w-full max-sm:mt-[-1.5rem]"
					>
						<SingleSelectInfo
							className="flex-shrink-0 max-sm:w-[calc(100%_-_24px)]"
							editMode={$editMode}
							necessary
							name={$t("user.isQuick")}
							bind:content={isQuick}
							selectItems={quicks}
						/>
						{#snippet content()}
							<p class="w-[300px]">{$t("user.isQuickTips")}</p>
						{/snippet}
					</Popover>
				</div>
				<div class="col-span-2 flex gap-[1rem]">
					<p class="mt-[0.75rem] shrink-0 max-sm:text-xs">
						<span class="text-blue-300">*</span>{$t("user.selfIntro")}
					</p>
					<textarea
						bind:value={intro}
						disabled={!$editMode}
						placeholder={$t("user.placeholder")}
						class={cx([
							"h-[10rem] w-full resize-none rounded-[8px] border-[1px] bg-[#FAFAFA] p-[0.75rem_1rem] outline-none transition-all focus:border-[#165DFF] max-sm:text-xs",
							$editMode ? "border-gray-200 bg-transparent" : "border-transparent"
						])}
					></textarea>
				</div>
			</div>
			<div class="mb-[2rem] h-[1px] w-full bg-[#E5E6EB]"></div>
			<UserInfoTitle title={$t("user.attachment")} />
			<div
				class="flex-col items-center gap-[1rem] rounded-[1rem] bg-[#FAFAFA] py-[2rem] max-sm:rounded-[4px] max-sm:p-[18px] sm:flex sm:justify-center"
			>
				{#if $editMode}
					<div onclick={() => fileInput.click()} class="flex gap-[1rem] sm:hidden">
						<img src={uploadSvg} alt="upload" />
						<div>
							<p class="my-[4px] text-sm font-bold">{$t("user.upload")}</p>
							<p class=" text-xs text-text-3">
								{$t("user.resumePopover")}
							</p>
							{#if resume}
								<p class="mt-[4px] text-xs">{resume.name}</p>
							{/if}
						</div>
					</div>
					<p class="text-lg font-bold max-sm:hidden">{$t("user.upload")}</p>
					<p class="px-[3rem] text-center text-xs text-text-3 max-sm:hidden">
						{$t("user.resumePopover")}
					</p>
					{#if resume}
						<p class="max-sm:hidden">{resume.name}</p>
					{:else if hasAppliedCurrentRecruitment && $userInfo.applications[0].resume}
						<div
							onclick={downloadResume}
							class="flex cursor-pointer items-center justify-center gap-[8px] text-center sm:flex-col"
						>
							<img src={word} alt="简历" />
							<p class="max-sm:text-sm">
								{$parseTitle($recruitment.name)}-{$userInfo.name}-{$t("user.resume")}<br />
								<span class="text-gray-300"> {downloadResumeName}</span>
							</p>
						</div>
					{/if}
					<button
						class="cursor-pointer rounded-[0.5rem] border-[1px] border-[#0A84FF] p-[0.5rem_2rem] text-[#0A84FF] transition-all hover:bg-[#0A84FF] hover:text-white max-sm:hidden"
						onclick={() => fileInput.click()}
					>
						{resume ? $t("user.reselect") : $t("user.select")}
					</button>
					<input
						onchange={() => {
							const file = fileInput.files[0];
							if (file && file.size > 20 * 1024 * 1024) {
								fileInput.value = "";
								Message.error($t("user.resumeTooLarge"));
							} else {
								resume = fileInput.files[0];
							}
						}}
						bind:this={fileInput}
						type="file"
						class="hidden"
					/>
				{:else if hasAppliedCurrentRecruitment && $userInfo.applications[0]?.resume}
					<div
						onclick={downloadResume}
						class="flex cursor-pointer items-center justify-center gap-[8px] sm:flex-col"
					>
						<img src={word} alt="简历" />
						<p class="text-center max-sm:text-sm">
							{$parseTitle($recruitment.name)}-{$userInfo.name}-{$t("user.resume")}<br />
							<span class="text-gray-300"> {downloadResumeName}</span>
						</p>
					</div>
				{:else}
					<p class="text-gray-400 select-none text-lg font-bold max-sm:text-sm">
						{$t("user.noResume")}
					</p>
				{/if}
			</div>
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
