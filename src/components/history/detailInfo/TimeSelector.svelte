<script lang="ts">
	//ly: i have spent so much time on this shit component, WTF!!!
	import type { InterviewTime, SingleTime } from "../../../types";
	import { formatDate, formatTime } from "../../../utils/formmatDate";
	import cx from "clsx";
	import { slide } from "svelte/transition";
	import arrow from "../../../assets/arrow.svg";
	import { parseInterviewTime } from "../../../utils/parseInterviewTime";
	import CheckBox from "../../../icons/CheckBox.svelte";
	import { onMount } from "svelte";
	import { Message } from "../../../utils/Message";
	import { setInterviewTimes } from "../../../requests/application/setInterviewTimes";
	import { t } from "../../../utils/t";
	import { derived } from "svelte/store";
	import { localeLanguage } from "../../../stores/localeLanguage";
	import { isMobile } from "../../../stores/isMobile";
	import { selectedTimes as selectedTimeList } from "../../../stores/selectedTimes";

	//ly: type 'SingleTime' is the return-type of backend, type 'InterviewTime' is the useful type when rendering UI
	export let times: SingleTime[] = [];
	export let type: "team" | "group";
	export let aid: string;
	let timeTrees = parseInterviewTime(times);
	let showSelector = false;
	let curDate: string | undefined = undefined;
	let curPeriods: InterviewTime["detail"] | undefined = undefined;
	let curTimes: InterviewTime["detail"][number]["time"] | undefined = undefined;
	export let selectedTimes: string[] = [];
	const handleDateClick = (date: string, detail: InterviewTime["detail"]) => {
		if (curDate === date) {
			curDate = undefined;
			curPeriods = undefined;
			curTimes = undefined;
			return;
		}
		curDate = date;
		curPeriods = detail;
		curTimes = undefined;
	};
	const handlePeriodClick = (detail: InterviewTime["detail"][number]) => {
		curTimes = detail.time;
	};
	const selectTime = (uuid: string) => {
		if (selectedTimes.includes(uuid)) {
			selectedTimeList.setTimes([...selectedTimes.filter((el) => el !== uuid)]);
			selectedTimes = [...selectedTimes.filter((el) => el !== uuid)];
		} else {
			selectedTimeList.setTimes([...selectedTimes, uuid]);
			selectedTimes = [...selectedTimes, uuid];
		}
		setInterviewTimes({
			iids: selectedTimes,
			aid,
			type
		})
			.then(() => {
				Message.success($t("history.timeSelector.chooseSuccess"));
			})
			.catch(() => {
				Message.error($t("history.timeSelector.chooseFailed"));
			});
	};
	const transferTime = derived(localeLanguage, () => (uuid: string) => {
		const interviewTime = times.find((el) => el.uid === uuid);
		if (interviewTime) {
			const date = $formatDate(interviewTime.date);
			const startTime = $formatTime(interviewTime.start);
			const endTime = $formatTime(interviewTime.end);
			return { date, startTime, endTime };
		}
	});
	const handleOpen = (e: MouseEvent) => {
		e.stopPropagation();
		curDate = undefined;
		curPeriods = undefined;
		curTimes = undefined;

		showSelector = !showSelector;
	};
	onMount(() => {
		function hide() {
			showSelector = false;
		}
		document.addEventListener("click", hide);
		return () => {
			document.removeEventListener("click", hide);
		};
	});
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div on:click={(e) => e.stopPropagation()} class="relative w-full select-none">
	<div
		on:click={handleOpen}
		class="scrollbar-hidden flex h-[36px] w-full cursor-pointer items-center whitespace-nowrap rounded-[10px] border-[1px] border-blue-400 bg-white pl-[16px] pr-[24px] leading-[36px]"
	>
		<div class="scrollbar-hidden flex flex-nowrap gap-[8px] overflow-x-auto overflow-y-hidden">
			{#each selectedTimes as time (time)}
				{#if times.find((el) => el.uid === time)}
					<div
						class="h-[28px] flex-shrink-0 whitespace-nowrap rounded-[4px] bg-gray-150 px-[8px] leading-[28px]"
					>
						<span>{$transferTime(time)?.date}</span>
						<span>({$transferTime(time)?.startTime} - {$transferTime(time)?.endTime})</span>
					</div>
				{/if}
			{/each}
		</div>

		<img
			src={arrow}
			class={cx(["absolute right-[8px] transition-all", showSelector || "rotate-180"])}
			alt="arrow"
		/>
	</div>
	{#if showSelector}
		<div
			transition:slide
			class={cx(["absolute left-0 top-[40px] w-full rounded-[8px] p-[8px_16px] max-sm:text-sm"])}
		>
			<div class="sm:flex">
				<div
					class="w-1/3 rounded-l-md border-[1px] border-gray-150 bg-white py-[8px] max-sm:flex max-sm:w-full max-sm:overflow-x-auto"
				>
					{#if timeTrees.length === 0}
						<p class="p-[12px_14px]">{$t("history.timeSelector.noTime")}</p>
					{/if}
					{#each timeTrees as { date, detail } (date)}
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<div
							on:click={() => handleDateClick(date, detail)}
							class={cx([
								"flex h-[46px] cursor-pointer items-center p-[12px_14px] hover:bg-gray-100 max-sm:flex-shrink-0",
								curDate === date && "bg-gray-100"
							])}
						>
							<p class="ml-[8px]">{$formatDate(date)}</p>
							<img class="ml-auto rotate-90 max-sm:hidden" src={arrow} alt="arrow" />
						</div>
					{/each}
				</div>
				<!-- svelte-ignore a11y-no-static-element-interactions -->
				{#if curDate && curPeriods}
					<!-- svelte-ignore a11y-click-events-have-key-events -->
					<div
						transition:slide={{ axis: $isMobile ? "y" : "x" }}
						class="w-1/3 border-[1px] border-gray-150 bg-white py-[8px] max-sm:flex max-sm:w-full"
					>
						{#each curPeriods as period (period)}
							<div
								on:click={() => handlePeriodClick(period)}
								class={cx([
									"flex h-[46px] cursor-pointer items-center p-[12px_14px] hover:bg-gray-100 max-sm:min-w-[33%] max-sm:flex-shrink-0",
									curTimes === period.time && "bg-gray-100"
								])}
							>
								<p class="ml-[8px] w-full overflow-x-auto whitespace-nowrap">
									{$t(`history.period.${period.period}`)}
								</p>
								<img
									class="ml-auto flex-shrink-0 rotate-90 max-sm:hidden"
									src={arrow}
									alt="arrow"
								/>
							</div>
						{/each}
					</div>
				{/if}
				{#if curDate && curPeriods && curTimes}
					<div
						transition:slide={{ axis: $isMobile ? "y" : "x" }}
						class="w-1/3 rounded-r-md border-[1px] border-gray-150 bg-white py-[8px] max-sm:flex max-sm:w-full max-sm:overflow-x-auto"
					>
						{#each curTimes as time (time.uuid)}
							<!-- svelte-ignore a11y-click-events-have-key-events -->
							<!-- svelte-ignore a11y-no-static-element-interactions -->
							<div
								on:click={() => selectTime(time.uuid)}
								class="flex h-[46px] cursor-pointer items-center p-[12px_14px] hover:bg-gray-100 max-sm:min-w-[33%] max-sm:flex-shrink-0"
							>
								<CheckBox isSelected={selectedTimes.includes(time.uuid)} />
								<p class="ml-[8px] w-full overflow-x-auto whitespace-nowrap">
									{`${$formatTime(time.startTime)} - ${$formatTime(time.endTime)}`}
								</p>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
