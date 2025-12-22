<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { Group, ProcessState, Step } from '../config/const';
  import SingleApplicationItem from '../components/history/SingleApplicationItem.svelte';
  import type { Application } from '../types/application';
  import type { ProcessState as ProcessStateType } from '../types';
  import { userInfo } from '../stores/userInfo';
  import { getRecruitmentById } from '../requests/recruitment/getById';
  import { recruitment } from '../stores/recruitment';
  import { parseTitle } from '../utils/parseTitle';
  import { t } from '../utils/t';
  import type { UserStep } from '../types';
  import { selectedTimes } from '../stores/selectedTimes';
  $: signUpStep = $t(`history.step.SignUp`) as UserStep;
  $: processing = $t('history.processState.PROCESSING') as ProcessStateType;
  $: getState = (application: Application, date: string) =>
    $t(
      `history.processState.${
        application.rejected
          ? 'OUT'
          : application.abandoned
            ? 'ABANDONED'
            : new Date().getTime() >= new Date(date).getTime()
              ? 'OVER'
              : application.step === 'Pass'
                ? 'PASS'
                : 'PROCESSING'
      }`
    ) as ProcessStateType;

  $: getStep = (application: Application) =>
    $t(`history.step.${application.step}`) as UserStep;

  let applications: any[] = [];
  let isLoading = false;
  
  $: $userInfo &&
    Promise.all(
      $userInfo.applications.map(async (application) => {
        isLoading = true;
        const res = await getRecruitmentById(application.recruitment_id);
        const processedApplication = {
          ...application,
          title: $parseTitle(res.data.name),
          end: res.data.end,
          deadline: res.data.deadline,
          beginning: res.data.beginning,
        };
        return processedApplication;
      })
    ).then((res) => {
      applications = res;
    }).finally(() => {
      isLoading = false;
    });
  $: $userInfo && selectedTimes.setTimes($userInfo.applications[0]?.interview_selections?.map(el => el.uid) || []);
</script>

<div
  class="h-full relative my-[1rem] w-[60%] max-lg:w-[70%] max-md-lg:w-[80%] max-sm:w-[calc(100%_-_40px)] mx-auto flex flex-col"
>
  <p
    in:fade
    out:fade
    class="text-[26px] max-sm:text-text-1 max-sm:text-[18px] text-white"
  >
    {$t('history.records')}
  </p>
  <div
    in:fly={{ y: 50, duration: 500, delay: 500 }}
    out:fly={{ y: 50, duration: 500 }}
  >
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
          class="rounded-[20px] mt-[1rem] h-[290px] bg-white max-sm:rounded-[6px] flex justify-center items-center p-[3rem_4rem] max-sm:p-[20px_18px] sm:shadow-card"
        >
          <p class="text-gray-250 text-2xl">{$t('history.noRecord')}</p>
        </div>
      {/if}

      {#each applications as application, i}
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
        class="rounded-[20px] mt-[1rem] h-[290px] bg-white max-sm:rounded-[6px] flex justify-center items-center p-[3rem_4rem] max-sm:p-[20px_18px] sm:shadow-card"
      >
        <p class="text-gray-250 text-2xl">{$t('history.noRecord')}</p>
      </div>
    {/if}
  </div>
</div>
