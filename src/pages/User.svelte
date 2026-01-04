<script lang="ts">
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
	import { getRecruitmentById } from "../requests/recruitment/getById";
	import { getResume } from "../requests/user/getResume";
	import { recruitment } from "../stores/recruitment";
	import Popover from "../components/public/Popover.svelte";
	import { Message } from "../utils/Message";
	import { latestInfo } from "../stores/latestApplication";
	import Modal from "../components/public/Modal.svelte";
	import { checkNecessaryInfo } from "../utils/checkNecessaryInfo";
	import { signUpRecruitment } from "../requests/application/signUpRecruitment";
	import { updateApplication } from "../requests/application/updateApplication";
	import { parseTitle } from "../utils/parseTitle";
	import { t } from "../utils/t";
	import { getInfo } from "../requests/user/getInfo";
	import { localeLanguage } from "../stores/localeLanguage";
	import uploadSvg from "../assets/upload.svg";
	import { departments } from "../stores/departments";
	import MultiSelectInfo from "../components/user/MultiSelectInfo.svelte";
	import { globalLoading } from "../stores/globalLoading";
	import { editMode } from "../stores/editMode";

	$: colleges = Object.keys($departments).sort();
	let isUploading = false;
	let showSignUpModal = false;
	let resume: File;
	let fileInput: HTMLInputElement;
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
		uid = "",
		is_quick = false,
		is_project_c = false
	} = $latestInfo || {};
	//ly:this asset would be wrong but I just don't want to see TypeError :)
	$: majors = $departments[institute as College] || [];
	$: ranks = $t("user.selector.rank") as unknown as string[];
	$: genders = $t("user.selector.gender") as unknown as string[];
	$: grades = $t("user.selector.grade") as unknown as string[];
	let isQuick = is_quick ? $t("user.quick") : $t("user.notQuick");
	let isProjectC = is_project_c ? $t("user.selector.projectC")[0] : $t("user.selector.projectC")[1];
	$: if ($userInfo?.qq_account || $latestInfo?.qq_account) {
		qq_account = $userInfo?.qq_account || $latestInfo?.qq_account || "";
	}
	let qqError = "";
	const validateQQ = () => {
		if (qq_account && !/^[1-9][0-9]{4,10}$/.test(qq_account)) {
			qqError = $t("user.checkQQ");
		} else {
			qqError = "";
		}
	};

	localeLanguage.subscribe(() => {
		Promise.resolve().then(() => {
			isQuick = is_quick ? $t("user.quick") : $t("user.notQuick");
		});
	});
	$: quicks = $t("user.selector.isQuick") as unknown as string[];
	// $: projectC = $t("user.selector.projectC") as unknown as string[];

	$: groupGroupSelected = GroupGroup.map(
		(group) => group.find((g) => groups.some((gg) => Group[gg] === g)) || ""
	) as [string | null, string | null];

	$: groupGroupTitles = $t("user.selector.groupGroup") as unknown as [string, string];

	const downloadResume = () => {
		getResume(uid, $userInfo?.applications[0]?.resume?.split("/").pop() || "个人简历");
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
			uid = "",
			is_quick = false,
			is_project_c = false
		} = $latestInfo || {});
		resume = undefined;
		editMode.out();
	};
	const signUp = () => {
		if (
			!$checkNecessaryInfo({
				rank,
				major,
				institute,
				groups,
				grade,
				intro,
				qq_account,
				is_quick: isQuick === $t("user.quick") ? true : false,
				is_project_c: isProjectC === $t("user.selector.projectC")[0] ? true : false
			})
		)
			return;
		globalLoading.set(true);
		try {
			groups.forEach((group) => {
				const formData = new FormData();
				formData.append("recruitment_id", $recruitment.uid);
				if (resume) formData.append("resume", resume);
				for (const [key, value] of Object.entries({
					rank,
					major,
					qq_account,
					institute,
					group,
					grade,
					intro,
					referrer,
					is_quick: isQuick === $t("user.quick") ? "true" : "false"
				})) {
					formData.append(key, value);
				}
				signUpRecruitment(formData)
					.then(() => {
						Message.success($t("user.signUpSuccess"));
						showSignUpModal = false;
						editMode.out();
						return getInfo();
					})
					.then((res) => {
						userInfo.setInfo(res.data);
						latestInfo.setApplication(res.data);
					});
			});
		} catch {
			Message.error($t("user.signUpFail"));
		} finally {
			globalLoading.set(false);
		}
	};
	const saveApplicationInfo = async () => {
		if (isUploading) return;
		isUploading = true;
		if (resume) {
			globalLoading.set(true);
		}
		if (
			!$checkNecessaryInfo({
				rank,
				major,
				institute,
				qq_account,
				groups,
				grade,
				intro,
				is_quick: isQuick === $t("user.quick") ? true : false
			})
		) {
			isUploading = false;
			globalLoading.set(false);
			return;
		}

		if (
			$recruitment &&
			$recruitment.uid === $userInfo.applications[0]?.recruitment_id &&
			!$userInfo.applications[0]?.rejected &&
			!$userInfo.applications[0]?.abandoned
		) {
			// 如果还在流程中，修改后端 application
			const formData = new FormData();
			formData.append("recruitment_id", $recruitment.uid);
			if (resume) formData.append("resume", resume);
			for (const [key, value] of Object.entries({
				rank,
				major,
				institute,
				qq_account,
				grade,
				intro,
				referrer,
				is_quick: isQuick === $t("user.quick") ? "true" : "false"
			})) {
				formData.append(key, value);
			}
			try {
				$userInfo.applications.forEach(async (app) => {
					// lyx: 可能有多个申请
					if (app.recruitment_id !== $recruitment.uid) return;
					console.log("send application of group", app.group);
					await updateApplication(app.uid, formData);
				});
				const res = await getInfo();
				userInfo.setInfo(res.data);
				latestInfo.updateInfo({
					rank,
					referrer,
					major,
					qq_account,
					institute,
					groups,
					grade,
					intro,
					is_quick: isQuick === $t("user.quick") ? true : false
				});
				Message.success($t("user.saveSuccess"));
			} catch {
				Message.error($t("user.saveFailed"));
			}
		} else {
			latestInfo.updateInfo({
				rank,
				referrer,
				major,
				qq_account,
				institute,
				groups,
				grade,
				intro,
				is_quick: isQuick === $t("user.quick") ? true : false
			});
			Message.success($t("user.saveSuccess"));
		}
		isUploading = false;
		globalLoading.set(false);
		editMode.out();
	};
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
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
								slot="children"
								className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
								highlight>{$t("user.save")}</Button
							>
							<p slot="content" class="w-[180px]">
								{$userInfo.applications[0]?.recruitment_id === $recruitment.uid &&
								!$userInfo.applications[0]?.rejected
									? $t("user.saveTips")
									: $t("user.saveTips1")}
							</p>
						</Popover>
					</div>
				{:else}
					<div
						on:click={() => {
							editMode.in();
						}}
						class={cx([
							"ml-auto flex h-[28px] cursor-pointer items-center gap-[0.25rem] rounded-full bg-blue-100 p-[7px_20px] text-sm text-blue-400 max-sm:w-[88px] max-sm:justify-center max-sm:p-[3px_12px]",
							$editMode && "hidden"
						])}
					>
						<img src={edit} class="max-sm:hidden" alt="edit" />
						<p class="text-blue-300 max-sm:text-xs">{$t("user.edit")}</p>
					</div>
				{/if}
			</div>
			<div class="mb-[1rem] flex w-full -translate-y-2 flex-row-reverse">
				{#if !$editMode && $recruitment && $recruitment.uid !== $userInfo.applications[0]?.recruitment_id && new Date().getTime() >= new Date($recruitment.beginning).getTime() && new Date().getTime() <= new Date($recruitment.deadline).getTime()}
					<Popover style="white" direct="top" questionDirection="end">
						<Button
							onClick={() => (showSignUpModal = true)}
							slot="children"
							className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
							highlight>{$t("user.signUp")}</Button
						>
						<p class="w-[142px]" slot="content">
							{$t("user.signUpConfirm", {
								recruitment: $parseTitle($recruitment.name)
							})}
						</p>
					</Popover>
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
					bind:content={GENDERS[$userInfo.gender - 1]}
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
					on:blur={validateQQ}
					errorMessage={qqError}
					name={$t("user.qq")}
					bind:content={qq_account}
					isDisabled={true}
				/>
				<SingleInputInfo
					necessary
					name={$t("user.phone")}
					bind:content={$userInfo.phone}
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
					<Popover style="white" direct="left-top" className="w-full max-sm:mt-[-1.5rem]">
						<MultiSelectInfo
							className="flex-shrink-0 max-sm:w-[calc(100%_-_24px)]"
							slot="children"
							editMode={$editMode &&
								(!$recruitment || $userInfo?.applications[0]?.recruitment_id !== $recruitment.uid)}
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
						<p slot="content" class="w-[300px]">{$t("user.groupTips")}</p>
					</Popover>
				</div>
				<div class="col-span-1 max-w-full gap-[1rem]">
					<Popover style="white" direct="left-top" className="w-full max-sm:mt-[-1.5rem]">
						<SingleSelectInfo
							className="flex-shrink-0 max-sm:w-[calc(100%_-_24px)]"
							slot="children"
							editMode={$editMode}
							necessary
							name={$t("user.isQuick")}
							bind:content={isQuick}
							selectItems={quicks}
						/>
						<p slot="content" class="w-[300px]">{$t("user.isQuickTips")}</p>
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
					/>
				</div>
			</div>
			<div class="mb-[2rem] h-[1px] w-full bg-[#E5E6EB]" />
			<UserInfoTitle title={$t("user.attachment")} />
			<div
				class="flex-col items-center gap-[1rem] rounded-[1rem] bg-[#FAFAFA] py-[2rem] max-sm:rounded-[4px] max-sm:p-[18px] sm:flex sm:justify-center"
			>
				{#if $editMode}
					<div on:click={() => fileInput.click()} class="flex gap-[1rem] sm:hidden">
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
					{:else if $recruitment && $userInfo.applications[0]?.recruitment_id === $recruitment.uid && $userInfo.applications[0].resume}
						<div
							on:click={downloadResume}
							class="flex cursor-pointer items-center justify-center gap-[8px] sm:flex-col"
						>
							<img src={word} alt="简历" />
							{#await getRecruitmentById($userInfo.applications[0].recruitment_id) then res}
								<p class="max-sm:text-sm">
									{$parseTitle(res.data.name)}-{$userInfo.name}-{$t("user.resume")}
								</p>
							{/await}
						</div>
					{/if}
					<div
						class="cursor-pointer rounded-[0.5rem] border-[1px] border-[#0A84FF] p-[0.5rem_2rem] text-[#0A84FF] transition-all hover:bg-[#0A84FF] hover:text-white max-sm:hidden"
						on:click={() => fileInput.click()}
					>
						{resume ? $t("user.reselect") : $t("user.select")}
					</div>
					<input
						on:change={() => {
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
				{:else if $recruitment && $userInfo.applications[0]?.recruitment_id === $recruitment.uid && $userInfo.applications[0]?.resume}
					<div
						on:click={downloadResume}
						class="flex cursor-pointer items-center justify-center gap-[8px] sm:flex-col"
					>
						<img src={word} alt="简历" />
						{#await getRecruitmentById($userInfo.applications[0]?.recruitment_id) then res}
							<p class="max-sm:text-sm">
								{$parseTitle(res.data.name)}-{$userInfo.name}-{$t("user.resume")}
							</p>
						{/await}
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
