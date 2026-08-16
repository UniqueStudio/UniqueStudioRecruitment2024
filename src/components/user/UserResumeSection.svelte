<script lang="ts">
	import word from "../../assets/word.svg";
	import uploadSvg from "../../assets/upload.svg";
	import { parseTitle } from "../../utils/parseTitle";
	import { t } from "../../utils/t";
	import { Message } from "../../utils/Message";
	import UserInfoTitle from "./UserInfoTitle.svelte";

	interface Props {
		editMode: boolean;
		hasAppliedCurrentRecruitment: boolean;
		hasResume: boolean;
		userName: string;
		recruitmentName?: string;
		downloadResumeName: string;
		onDownload: () => void;
		resume?: File;
	}

	let {
		editMode,
		hasAppliedCurrentRecruitment,
		hasResume,
		userName,
		recruitmentName,
		downloadResumeName,
		onDownload,
		resume = $bindable()
	}: Props = $props();
	let fileInput: HTMLInputElement = $state();

	const selectResume = () => fileInput.click();
	const updateResume = () => {
		const file = fileInput.files?.[0];
		if (file && file.size > 20 * 1024 * 1024) {
			fileInput.value = "";
			Message.error($t("user.resumeTooLarge"));
			return;
		}
		resume = file;
	};
</script>

<UserInfoTitle title={$t("user.attachment")} />
<div
	class="flex-col items-center gap-[1rem] rounded-[1rem] bg-[#FAFAFA] py-[2rem] max-sm:rounded-[4px] max-sm:p-[18px] sm:flex sm:justify-center"
>
	{#if editMode}
		<button
			type="button"
			onclick={selectResume}
			class="flex border-0 bg-transparent p-0 text-left sm:hidden"
		>
			<img src={uploadSvg} alt="upload" />
			<div>
				<p class="my-[4px] text-sm font-bold">{$t("user.upload")}</p>
				<p class="text-xs text-text-3">{$t("user.resumePopover")}</p>
				{#if resume}
					<p class="mt-[4px] text-xs">{resume.name}</p>
				{/if}
			</div>
		</button>
		<p class="text-lg font-bold max-sm:hidden">{$t("user.upload")}</p>
		<p class="px-[3rem] text-center text-xs text-text-3 max-sm:hidden">
			{$t("user.resumePopover")}
		</p>
		{#if resume}
			<p class="max-sm:hidden">{resume.name}</p>
		{:else if hasAppliedCurrentRecruitment && hasResume}
			<button
				type="button"
				onclick={onDownload}
				class="flex cursor-pointer items-center justify-center gap-[8px] border-0 bg-transparent p-0 text-center sm:flex-col"
			>
				<img src={word} alt="resume" />
				<p class="max-sm:text-sm">
					{recruitmentName ? $parseTitle(recruitmentName) : ""}-{userName}-{$t("user.resume")}<br />
					<span class="text-gray-300">{downloadResumeName}</span>
				</p>
			</button>
		{/if}
		<button
			class="cursor-pointer rounded-[0.5rem] border-[1px] border-[#0A84FF] p-[0.5rem_2rem] text-[#0A84FF] transition-all hover:bg-[#0A84FF] hover:text-white max-sm:hidden"
			onclick={selectResume}
		>
			{resume ? $t("user.reselect") : $t("user.select")}
		</button>
		<input onchange={updateResume} bind:this={fileInput} type="file" class="hidden" />
	{:else if hasAppliedCurrentRecruitment && hasResume}
		<button
			type="button"
			onclick={onDownload}
			class="flex cursor-pointer items-center justify-center gap-[8px] border-0 bg-transparent p-0 sm:flex-col"
		>
			<img src={word} alt="resume" />
			<p class="text-center max-sm:text-sm">
				{recruitmentName ? $parseTitle(recruitmentName) : ""}-{userName}-{$t("user.resume")}<br />
				<span class="text-gray-300">{downloadResumeName}</span>
			</p>
		</button>
	{:else}
		<p class="text-gray-400 select-none text-lg font-bold max-sm:text-sm">{$t("user.noResume")}</p>
	{/if}
</div>
