<script lang="ts">
	import { fade, fly } from "svelte/transition";
	import { Group, Step } from "../config/const";
	import SingleApplicationItem from "../components/history/SingleApplicationItem.svelte";
	import type { Application } from "../types/application";
	import type { ProcessState as ProcessStateType } from "../types";
	import { userInfo } from "../stores/userInfo";
	import { recruitment } from "../stores/recruitment";
	import { parseTitle } from "../utils/parseTitle";
	import { t } from "../utils/t";
	import type { UserStep } from "../types";
	import {
		extendedApplications,
		extendedApplicationsLoading,
		loadExtendedApplications
	} from "../stores/extendedApplications";

	$: signUpStep = $t(`history.step.SignUp`) as UserStep;
	$: processing = $t("history.processState.PROCESSING") as ProcessStateType;

	const getState = (application: Application, date: string) =>
		$t(
			`history.processState.${
				application.rejected
					? "OUT"
					: application.abandoned
						? "ABANDONED"
						: new Date().getTime() >= new Date(date).getTime()
							? "OVER"
							: application.step === "Pass"
								? "PASS"
								: "PROCESSING"
			}`
		) as ProcessStateType;

	const getStep = (application: Application) => {
		if (Object.keys(Step).includes(application.step)) {
			return $t(`history.step.${application.step}`) as UserStep;
		} else {
			// 如果 step 不在 Step 枚举中，我们认为是在线组面和群面中的一个，转到对应的步骤
			if (application.step.includes("Team")) {
				return $t(`history.step.TeamInterview`) as UserStep;
			} else {
				return $t(`history.step.GroupInterview`) as UserStep;
			}
		}
	};

	$: if ($userInfo?.applications) {
		loadExtendedApplications($userInfo.applications);
	}

	$: applications = $extendedApplications;
	$: isLoading = $extendedApplicationsLoading;
</script>

<div
	class="relative mx-auto my-[1rem] flex h-full w-[60%] flex-col max-lg:w-[70%] max-md-lg:w-[80%] max-sm:w-[calc(100%_-_40px)]"
>
	<p in:fade out:fade class="text-[26px] text-white max-sm:text-[18px] max-sm:text-text-1">
		{$t("history.records")}
	</p>
	<div in:fly={{ y: 50, duration: 500, delay: 500 }} out:fly={{ y: 50, duration: 500 }}>
		{#if $userInfo && $recruitment}
			<!-- if user have not sign updateApplication, show this -->
			{#if $recruitment.uid !== $userInfo.applications[0]?.recruitment_id && new Date().getTime() >= new Date($recruitment.beginning).getTime() && new Date().getTime() <= new Date($recruitment.deadline).getTime()}
				<SingleApplicationItem
					index={0}
					title={$parseTitle($recruitment.name)}
					step={signUpStep}
					state={processing}
				/>
			{:else if applications.length === 0 && !isLoading}
				<div
					class="mt-[1rem] flex h-[290px] items-center justify-center rounded-[20px] bg-white p-[3rem_4rem] max-sm:rounded-[6px] max-sm:p-[20px_18px] sm:shadow-card"
				>
					<p class="text-2xl text-gray-250">{$t("history.noRecord")}</p>
				</div>
			{/if}

			{#each applications as application, i (application)}
				<SingleApplicationItem
					applicationInfo={application}
					index={i}
					title={application.title}
					group={Group[application.group]}
					step={getStep(application)}
					state={getState(application, application.end)}
				/>
			{/each}
		{:else}
			<div
				class="mt-[1rem] flex h-[290px] items-center justify-center rounded-[20px] bg-white p-[3rem_4rem] max-sm:rounded-[6px] max-sm:p-[20px_18px] sm:shadow-card"
			>
				<p class="text-2xl text-gray-250">{$t("history.noRecord")}</p>
			</div>
		{/if}
	</div>
</div>
