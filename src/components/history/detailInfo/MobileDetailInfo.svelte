<script lang="ts">
  import { push } from "svelte-spa-router";
  import { Group, InterviewPlace, Period, Step } from "../../../config/const";
  import type { Application } from "../../../types/application";
  import Button from "../../public/Button.svelte";
  import type { UserStep } from "../../../types";
  import { recruitment } from "../../../stores/recruitment";
  import { userInfo } from "../../../stores/userInfo";
  import { parseTitle } from "../../../utils/parseTitle";
  import { formatDate, formatTime } from "../../../utils/formmatDate";
  import { t } from "../../../utils/t";
  import InterviewInfo from "./InterviewInfo.svelte";
  import BottomBar from "../../public/BottomBar.svelte";
  import TimeSelector from "./TimeSelector.svelte";
  import { getInterviewTimes } from "../../../requests/application/getInterviewTimes";
  import NightTestInfo from "./NightTestInfo.svelte";
  import greet from "../../../assets/greet.svg";
  import { onMount } from "svelte";
  import { getWrittenTest } from "../../../requests/recruitment/getWrittenTest";
  import { Message } from "../../../utils/Message";
  import { uploadWrittenTest } from "../../../requests/application/uploadWrittenTest";
  import { selectedTimes } from "../../../stores/selectedTimes";
  import { globalLoading } from "../../../stores/globalLoading";
  import { getInfo } from "../../../requests/user/getInfo";

  $: myWrittenTestAnswer = $userInfo?.applications[0]?.answer.split("/").at(-1);
  let openGroupInterviewTimeSelector = false;
  let openTeamInterviewTimeSelector = false;
  let writtenTestLink = "";
  let file: File;
  let fileInput: HTMLInputElement;
  let isGettingWrittenTestFile = false;
  let isUploading = false;
  const handleClick = (e) => {
    if (e.target.className.includes("go-user")) {
      push("/user");
    }
  };
  export let applicationInfo: Application;
  let selectedTimeList = $selectedTimes;
  const uploadAnswer = () => {
    if (!file) {
      fileInput.click();
    } else {
      if (isUploading) return;
      isUploading = true;
      globalLoading.set(true);
      const formData = new FormData();
      formData.append("file", file);
      uploadWrittenTest(applicationInfo.uid, formData)
        .then(() => {
          Message.success($t("history.writeTest.uploadSuccess"));
          file = undefined;
          return getInfo();
        })
        .then((res) => {
          userInfo.setInfo(res.data);
        })
        .catch(() => {
          Message.error($t("history.writeTest.uploadError"));
        })
        .finally(() => {
          isUploading = false;
          globalLoading.set(false);
        });
    }
  };
  export let onCancel: () => void;
  export let step: UserStep;
  onMount(() => {
    if (step === $t("history.step.WrittenTest")) {
      isGettingWrittenTestFile = true;
      getWrittenTest(applicationInfo.recruitment_id, applicationInfo.group)
        .then((res) => {
          if (!res.ok) {
            Message.warning($t("history.writeTest.downloadError"));
            return;
          }
          return res.blob();
        })
        .then((blob) => {
          const url = URL.createObjectURL(blob);
          writtenTestLink = url;
        })
        .finally(() => {
          isGettingWrittenTestFile = false;
        });
    }
  });
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<div class="w-[270px] p-[20px_16px]">
  <p class="text-center text-[17px] mb-[12px] font-[500]">{step}</p>
  {#if step === $t("history.step.SignUp")}
    <p class="text-sm text-center" on:click={handleClick}>
      {@html $userInfo.applications[0]?.recruitment_id === $recruitment.uid
        ? $t('history.mobile.signUpTips', {
            group: Group[$userInfo.applications[0]?.group],
            recruitment: $parseTitle($recruitment.name),
          })
        : $t("history.mobile.notSignUpTips")}
    </p>
    <Button
      highlight
      className="mx-auto w-full rounded-full my-[8px] text-[15px] leading-[36px]"
      onClick={() => push("/user")}
      >{applicationInfo
        ? $t("history.mobile.change")
        : $t("history.mobile.input")}{$t("header.info")}</Button
    >
  {:else if step === $t("history.step.WrittenTest")}
    <p class="text-sm text-text-4 my-[8px] text-center">
      {$t("history.writeTest.tips")}
    </p>
    <input
      on:change={() => {
        file = fileInput.files[0];
      }}
      bind:this={fileInput}
      type="file"
      class="hidden"
    />
    {#if isGettingWrittenTestFile}
      <p class="text-sm my-[8px] text-center">
        {$t("history.writeTest.loading")}
      </p>
    {/if}
    {#if writtenTestLink}
      {#if myWrittenTestAnswer}
        <div
          class="bg-white p-3 rounded-lg mt-2 border border-blue-200 shadow-sm"
        >
          <p class="text-sm text-gray-500 mb-1">
            {$t("history.writeTest.myAnswer")}
          </p>
          <p class="font-medium break-all">{myWrittenTestAnswer}</p>
        </div>
      {/if}
      <Button
        highlight
        className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
        ><a href={writtenTestLink} download="${$t('history.step.WrittenTest')}"
          >{$t("history.mobile.viewLink")}</a
        ></Button
      >
      <Button
        highlight
        className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
        onClick={uploadAnswer}
        >{file
          ? $t("history.mobile.uploadWrittenTest") +
            (file.name.length > 10
              ? file.name.slice(0, 5) + "..." + file.name.slice(-5)
              : file.name)
          : $t("history.mobile.selectWrittenTest")}
      </Button>
    {/if}
  {:else if step === $t("history.step.GroupTimeSelection")}
    <p class="text-sm my-[8px] text-text-4 text-center">
      {$t("history.mobile.groupInterviewTips")}
    </p>
    <Button
      onClick={() => (openGroupInterviewTimeSelector = true)}
      highlight
      className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
      >{$t("history.mobile.selectTime")}</Button
    >
    <!-- svelte-ignore missing-declaration -->
  {:else if step === $t("history.step.GroupInterview")}
    <InterviewInfo
      group={applicationInfo.group}
      time={applicationInfo.interview_allocations_group.uid
        ? `${$formatDate(
            applicationInfo.interview_allocations_group.date,
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
    <p class="text-sm my-[8px] text-text-4 text-center">
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
            applicationInfo.interview_allocations_team.date,
          )} ${$formatTime(applicationInfo.interview_allocations_team.start)}`
        : ""}
      type="team"
      group={applicationInfo.group}
    />
  {:else if step === $t("history.step.Pass")}
    <div class="flex text-sm justify-center items-center gap-[4px]">
      <p class="tetx-sm">{$t("history.passTips")}</p>
      <img class="inline" src={greet} alt="欢迎" />
    </div>
    <p class="text-gray-300 text-sm text-center mt-[8px]">
      {$t("history.passSubTips")}
    </p>
  {/if}
  <Button
    onClick={onCancel}
    className="mx-auto w-full text-[15px] bg-transparent leading-[36px] text-text-3"
    >{$t("history.mobile.known")}</Button
  >
</div>

<BottomBar
  className="min-h-[300px] px-[16px]"
  show={openGroupInterviewTimeSelector}
  on:close={() => (openGroupInterviewTimeSelector = false)}
>
  {#await getInterviewTimes(applicationInfo.recruitment_id, applicationInfo.group)}
    <p>{$t("history.groupInterviewTimeSelector.loading")}</p>
  {:then res}
    <TimeSelector
      type="group"
      aid={applicationInfo.uid}
      times={res.data}
      bind:selectedTimes={selectedTimeList}
    />
  {/await}
</BottomBar>

<BottomBar
  className="min-h-[300px] px-[16px]"
  show={openTeamInterviewTimeSelector}
  on:close={() => (openTeamInterviewTimeSelector = false)}
>
  {#await getInterviewTimes(applicationInfo.recruitment_id)}
    <p>{$t("history.teamInterviewTimeSelector.loading")}</p>
  {:then res}
    <TimeSelector
      type="team"
      aid={applicationInfo.uid}
      times={res.data}
      bind:selectedTimes={selectedTimeList}
    />
  {/await}
</BottomBar>
