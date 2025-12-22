<script lang="ts">
  import { push } from "svelte-spa-router";
  import {
    Group,
    InterviewPlace,
    Period,
    type TIMELINE,
  } from "../../../config/const";
  import Button from "../../public/Button.svelte";
  import type { UserStep } from "../../../types";
  import TimeSelector from "./TimeSelector.svelte";
  import InterviewInfo from "./InterviewInfo.svelte";
  import greet from "../../../assets/greet.svg";
  import NightTestInfo from "./NightTestInfo.svelte";
  import { userInfo } from "../../../stores/userInfo";
  import { recruitment } from "../../../stores/recruitment";
  import type { Application } from "../../../types/application";
  import { getInterviewTimes } from "../../../requests/application/getInterviewTimes";
  import { formatDate, formatTime } from "../../../utils/formmatDate";
  import { parseTitle } from "../../../utils/parseTitle";
  import { t } from "../../../utils/t";
  import { uploadWrittenTest } from "../../../requests/application/uploadWrittenTest";
  import { Message } from "../../../utils/Message";
  import { onMount } from "svelte";
  import { getWrittenTest } from "../../../requests/recruitment/getWrittenTest";
  import { globalLoading } from "../../../stores/globalLoading";
  import { getInfo } from "../../../requests/user/getInfo";

  let myWrittenTestAnswer = $userInfo?.applications[0]?.answer
    .split("/")
    .at(-1);

  export let step: UserStep;
  export let applicationInfo: Application;
  let selectedTimes = applicationInfo?.interview_selections?.map(
    (el) => el.uid,
  );
  const handleClick = (e) => {
    if (e.target.className.includes("go-user")) {
      push("/user");
    }
  };
  let file: File;
  let fileInput: HTMLInputElement;
  let writtenTestLink = "";
  let isGettingWrittenTestFile = true;
  let isUploading = false;
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
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
  class="w-full max-sm:hidden rounded-lg p-[20px_28px] mt-[3rem] bg-blue-100"
>
  {#if step !== $t("history.step.Pass")}
    <p class="font-bold text-lg mb-[1rem]">
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
            recruitment: $parseTitle($recruitment.name),
          })
        : $t("history.signUpTips.notSignInTips", {
            changeInfo: `<span
        
        class="text-blue-300 underline cursor-pointer go-user">${$t("history.signUpTips.changeInfo")}</span
      >`,
          })}
    </p>
  {:else if step === $t("history.step.WrittenTest")}
    <p>{$t("history.writeTest.tips")}</p>
    <input
      on:change={() => {
        file = fileInput.files[0];
      }}
      bind:this={fileInput}
      type="file"
      class="hidden"
    />
    {#if isGettingWrittenTestFile && !writtenTestLink}
      <p class="mt-[0.5rem]">{$t("history.writeTest.loading")}</p>
      <Button
        highlight
        className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px] opacity-50"
        >{$t("history.writeTest.loading")}
      </Button>
    {/if}
    {#if writtenTestLink}
      <p class="mt-[0.5rem]">
        {@html $t("history.writeTest.viewLink", {
          writtenTest: `<a
        class=" text-blue-300 underline"
        href=${writtenTestLink}
        download=${$t("history.step.WrittenTest")}>${$t("history.writeTest.writtenTest")}</a
      >`,
        })}
      </p>
      {#if myWrittenTestAnswer}
        <div
          class="bg-white p-3 rounded-[10px] mt-5 mb-5 border border-blue-200 shadow-sm"
        >
          <p class="text-[1.1rem] text-gray-500 mb-1 font-bold">
            {$t("history.writeTest.myAnswer")}
          </p>
          <p class="font-medium break-all">{myWrittenTestAnswer}</p>
        </div>
      {/if}
      <Button
        highlight
        className="mx-auto rounded-full my-[8px] w-full text-[15px] leading-[36px]"
        isLoading={isUploading}
        onClick={uploadAnswer}
      >
        {file
          ? $t("history.mobile.uploadWrittenTest") +
            (file.name.length > 16
              ? file.name.slice(0, 8) + "..." + file.name.slice(-8)
              : file.name)
          : $t("history.mobile.selectWrittenTest")}
      </Button>
    {/if}
  {:else if step === $t("history.step.GroupTimeSelection")}
    {#await getInterviewTimes(applicationInfo.recruitment_id, applicationInfo.group)}
      <p>{$t("history.groupInterviewTimeSelector.loading")}</p>
    {:then res}
      <TimeSelector
        type="group"
        aid={applicationInfo.uid}
        times={res.data}
        bind:selectedTimes
      />
    {/await}
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
    {#await getInterviewTimes(applicationInfo.recruitment_id)}
      <p>{$t("history.teamInterviewTimeSelector.loading")}</p>
    {:then res}
      <TimeSelector
        type="team"
        aid={applicationInfo.uid}
        times={res.data}
        bind:selectedTimes
      />
    {/await}
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
    <div class="flex items-center gap-[4px]">
      <p class="text-lg">{$t("history.passTips")}</p>
      <img class="inline" src={greet} alt="欢迎" />
    </div>
    <p class="text-gray-300 mt-[8px]">{$t("history.passSubTips")}</p>
  {/if}
</div>
