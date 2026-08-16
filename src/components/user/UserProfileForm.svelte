<script lang="ts">
	import cx from "clsx";
	import { GENDERS, Group, GroupGroup } from "../../config/const";
	import type { User } from "../../types/user";
	import { t } from "../../utils/t";
	import Popover from "../public/Popover.svelte";
	import MultiSelectInfo from "./MultiSelectInfo.svelte";
	import SearchableSelectInfo from "./SearchableSelectInfo.svelte";
	import SingleInputInfo from "./SingleInputInfo.svelte";
	import SingleSelectInfo from "./SingleSelectInfo.svelte";

	interface Props {
		user: User;
		editMode: boolean;
		hasAppliedCurrentRecruitment: boolean;
		colleges: string[];
		majors: string[];
		genders: string[];
		grades: string[];
		ranks: string[];
		quicks: string[];
		groupGroupTitles: [string, string];
		grade?: string;
		institute?: string;
		major?: string;
		rank?: string;
		qqAccount?: string;
		referrer?: string;
		groups?: string[];
		isQuick?: string;
		intro?: string;
		onQuickChange?: (value: string) => void;
	}

	let {
		user,
		editMode,
		hasAppliedCurrentRecruitment,
		colleges,
		majors,
		genders,
		grades,
		ranks,
		quicks,
		groupGroupTitles,
		grade = $bindable(),
		institute = $bindable(),
		major = $bindable(),
		rank = $bindable(),
		qqAccount = $bindable(),
		referrer = $bindable(),
		groups = $bindable([]),
		isQuick = $bindable(),
		intro = $bindable(),
		onQuickChange = () => {}
	}: Props = $props();

	let groupGroupSelected = $derived(
		GroupGroup.map(
			(group) => group.find((g) => groups.some((selected) => Group[selected] === g)) || ""
		) as [string | null, string | null]
	);

	const updateGroups = (items: [string | null, string | null]) => {
		groups = items
			.map((item) => Object.entries(Group).find(([, value]) => value === item)?.[0])
			.filter((group): group is string => Boolean(group));
	};
</script>

<div class="mb-[2rem] w-full gap-[2rem] lg:grid lg:grid-cols-2">
	<SingleInputInfo
		necessary
		name={$t("user.name")}
		content={user.name}
		tips={$t("user.changeUserInfoTip")}
		{editMode}
		isDisabled={true}
	/>
	<SingleSelectInfo
		necessary
		name={$t("user.gender")}
		content={GENDERS[user.gender - 1]}
		selectItems={genders}
	/>
	<SingleSelectInfo
		necessary
		{editMode}
		name={$t("user.grade")}
		bind:content={grade}
		selectItems={grades}
	/>
	<SearchableSelectInfo
		selectItems={colleges}
		{editMode}
		onChange={() => (major = "")}
		necessary
		name={$t("user.college")}
		bind:content={institute}
	/>
	<SearchableSelectInfo
		placeholder={majors.length ? "" : "请选择学院"}
		selectItems={majors}
		{editMode}
		necessary
		name={$t("user.major")}
		bind:content={major}
	/>
	<SingleSelectInfo
		necessary
		{editMode}
		name={$t("user.rank")}
		bind:content={rank}
		selectItems={ranks}
	/>
	<SingleInputInfo
		necessary
		{editMode}
		name={$t("user.qq")}
		bind:content={qqAccount}
		tips={$t("user.changeUserInfoTip")}
		isDisabled={true}
	/>
	<SingleInputInfo
		necessary
		name={$t("user.phone")}
		content={user.phone}
		tips={$t("user.changeUserInfoTip")}
		{editMode}
		isDisabled={true}
	/>
	<SingleInputInfo
		necessary
		name={$t("user.email")}
		content={user.email}
		tips={$t("user.changeUserInfoTip")}
		{editMode}
		isDisabled={true}
	/>
	<SingleInputInfo {editMode} name={$t("user.recommender")} bind:content={referrer} />
	<div class="col-span-1 max-w-full gap-[1rem]">
		<Popover
			style="white"
			direct="left-top"
			questionDirection="end"
			className="w-full max-sm:mt-[-1.5rem]"
		>
			<MultiSelectInfo
				className="flex-shrink-0 max-sm:w-[calc(100%_-_24px)]"
				editMode={editMode && !hasAppliedCurrentRecruitment}
				necessary
				name={$t("user.group")}
				selectedItems={groupGroupSelected}
				onChange={updateGroups}
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
				{editMode}
				necessary
				name={$t("user.isQuick")}
				bind:content={isQuick}
				onChange={onQuickChange}
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
			disabled={!editMode}
			placeholder={$t("user.placeholder")}
			class={cx([
				"h-[10rem] w-full resize-none rounded-[8px] border-[1px] bg-[#FAFAFA] p-[0.75rem_1rem] outline-none transition-all focus:border-[#165DFF] max-sm:text-xs",
				editMode ? "border-gray-200 bg-transparent" : "border-transparent"
			])}
		></textarea>
	</div>
</div>
