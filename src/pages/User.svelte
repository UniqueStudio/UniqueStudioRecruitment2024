<script lang="ts">
  import { fade, fly, slide } from 'svelte/transition';
  import UserInfoTitle from '../components/user/UserInfoTitle.svelte';
  import SingleInputInfo from '../components/user/SingleInputInfo.svelte';
  import SingleSelectInfo from '../components/user/SingleSelectInfo.svelte';
  import edit from '/src/assets/edit.svg';
  import cx from 'clsx';
  import Button from '../components/public/Button.svelte';
  import word from '../assets/word.svg';
  import {
    DEPARTMENTS,
    DEPARTMENTS_EN,
    GENDERS,
    GRADE,
    Group,
    RANK,
  } from '../config/const';
  import type { College } from '../types';
  import { userInfo } from '../stores/userInfo';
  import { getRecruitmentById } from '../requests/recruitment/getById';
  import { getResume } from '../requests/user/getResume';
  import { recruitment } from '../stores/recruitment';
  import Popover from '../components/public/Popover.svelte';
  import { Message } from '../utils/Message';
  import { latestInfo } from '../stores/latestApplication';
  import Modal from '../components/public/Modal.svelte';
  import { checkNecessaryInfo } from '../utils/checkNecessaryInfo';
  import { signUpRecruitment } from '../requests/application/signUpRecruitment';
  import { updateApplication } from '../requests/application/updateApplication';
  import { parseTitle } from '../utils/parseTitle';
  import { t } from '../utils/t';
  import { getInfo } from '../requests/user/getInfo';
  import { localeLanguage } from '../stores/localeLanguage';
  import uploadSvg from '../assets/upload.svg';
  import { isMobile } from '../stores/isMobile';
  import { editMode } from '../stores/editMode';
  
  let colleges = Object.keys(DEPARTMENTS);
  let isUploading = false;
  let showSignUpModal = false;
  let resume: File;
  let fileInput: HTMLInputElement;
  let {
    rank = '',
    referrer = '',
    major = '',
    institute = '',
    group = '',
    grade = '',
    intro = '',
    uid = '',
    is_quick = false,
  } = $latestInfo || {};
  //ly:this asset would be wrong but I just don't want to see TypeError :)
  $: majors = DEPARTMENTS[institute as College] || [];
  $: ranks = $t('user.selector.rank') as unknown as string[];
  $: genders = $t('user.selector.gender') as unknown as string[];
  $: grades = $t('user.selector.grade') as unknown as string[];
  let isQuick = is_quick ? $t('user.quick') : $t('user.notQuick');
  localeLanguage.subscribe(() => {
    Promise.resolve().then(() => {
      isQuick = is_quick ? $t('user.quick') : $t('user.notQuick');
    });
  });
  $: quicks = $t('user.selector.isQuick') as unknown as string[];
  const downloadResume = () => {
    getResume(
      uid,
      $userInfo?.applications[0]?.resume?.split('/').pop() || '个人简历'
    );
  };
  const closeEditMode = () => {
    ({
      rank = '',
      referrer = '',
      major = '',
      institute = '',
      group = '',
      grade = '',
      intro = '',
      uid = '',
      is_quick = false,
    } = $latestInfo || {});
    editMode.out();
  };
  const signUp = () => {
    if (
      !$checkNecessaryInfo({
        rank,
        major,
        institute,
        group,
        grade,
        intro,
        is_quick: isQuick === $t('user.quick') ? true : false,
      })
    )
      return;
    const formData = new FormData();
    formData.append('recruitment_id', $recruitment.uid);
    resume && formData.append('resume', resume);
    for (const [key, value] of Object.entries({
      rank,
      major,
      institute,
      group,
      grade,
      intro,
      referrer,
    })) {
      formData.append(key, value);
    }
    signUpRecruitment(formData)
      .then(() => {
        Message.success($t('user.signUpSuccess'));
        showSignUpModal = false;
        editMode.out();
        return getInfo();
      })
      .then((res) => {
        userInfo.setInfo(res.data);
        latestInfo.setApplication(res.data.applications[0]);
      })
      .catch((_err) => {
        Message.error($t('user.signUpFail'));
      });
  };
  const saveApplicationInfo = async () => {
    if(isUploading) return;
    isUploading = true;
    if (
      !$checkNecessaryInfo({
        rank,
        major,
        institute,
        group,
        grade,
        intro,
        is_quick: isQuick === $t('user.quick') ? true : false,
      })
    ) {
      isUploading = false;
      return;
    }
      
    if (
      $recruitment &&
      $recruitment.uid === $userInfo.applications[0].recruitment_id &&
      !$userInfo.applications[0].rejected &&
      !$userInfo.applications[0].abandoned
    ) {
      const formData = new FormData();
      formData.append('recruitment_id', $recruitment.uid);
      resume && formData.append('resume', resume);
      for (const [key, value] of Object.entries({
        rank,
        major,
        institute,
        group,
        grade,
        intro,
        referrer,
        is_quick: isQuick === $t('user.quick') ? 'true' : 'false',
      })) {
        formData.append(key, value);
      }
      try {
        await updateApplication($userInfo.applications[0].uid, formData);
        const res = await getInfo();
        userInfo.setInfo(res.data);
        latestInfo.updateInfo({
          rank,
          referrer,
          major,
          institute,
          group,
          grade,
          intro,
          is_quick: isQuick === $t('user.quick') ? true : false,
        });
        Message.success($t('user.saveSuccess'));
      } catch (_err) {
        Message.error($t('user.saveFailed'));
      }
    } else {
      latestInfo.updateInfo({
        rank,
        referrer,
        major,
        institute,
        group,
        grade,
        intro,
        is_quick: isQuick === $t('user.quick') ? true : false,
      });
      Message.success($t('user.saveSuccess'));
    }
    isUploading = false;
    editMode.out();
  };
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="h-full w-[60%] max-xl:w-[80%] max-sm:w-full mx-auto flex flex-col">
  <p transition:fade class="text-[26px] max-sm:hidden text-white">
    {$t('user.selfInfo')}
  </p>
  <div
    in:fly={{ y: 50, duration: 500, delay: 500 }}
    out:fly={{ y: 50, duration: 500 }}
    class="w-[full] my-[1rem] max-sm:my-0 bg-white max-sm:rounded-none max-sm:p-[20px] rounded-[20px] py-[30px] px-[55px] max-lg:px-[80px]"
  >
    {#if $userInfo}
      <p transition:fade class="sm:hidden mb-[1rem] text-text font-bold">
        {$t('user.selfInfo')}
      </p>
      <div class="flex items-center mb-[1rem]">
        <UserInfoTitle title={$t('user.basicInfo')} />
        {#if $editMode}
          <div class="ml-auto flex items-center gap-[1rem]">
            <Button
              onClick={closeEditMode}
              className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
              >{$t('user.cancel')}</Button
            >
            <!-- ly: if user applied latest recruitment, "save" button will save info to backend, or will save to localStorage and will not save resume file -->
            <Popover direct="top" questionDirection="end" style="white">
              <Button
                isLoading={isUploading}
                onClick={saveApplicationInfo}
                slot="children"
                className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
                highlight>{$t('user.save')}</Button
              >
              <p slot="content" class="w-[180px]">
                {$userInfo.applications[0]?.recruitment_id ===
                  $recruitment.uid && !$userInfo.applications[0]?.rejected
                  ? $t('user.saveTips')
                  : $t('user.saveTips1')}
              </p>
            </Popover>
          </div>
        {:else}
          <div
            on:click={() => {
              editMode.in();
            }}
            class={cx([
              'ml-auto cursor-pointer text-blue-400 text-sm bg-blue-100 rounded-full p-[7px_20px] max-sm:p-[3px_12px] max-sm:w-[88px] h-[28px] max-sm:justify-center flex gap-[0.25rem] items-center',
              $editMode && 'hidden',
            ])}
          >
            <img src={edit} class="max-sm:hidden" alt="edit" />
            <p class="text-blue-300 max-sm:text-xs">{$t('user.edit')}</p>
          </div>
        {/if}
      </div>
      <div class="flex mb-[1rem] -translate-y-2 w-full flex-row-reverse">
        {#if !$editMode && $recruitment && $recruitment.uid !== $userInfo.applications[0]?.recruitment_id && new Date().getTime() >= new Date($recruitment.beginning).getTime() && new Date().getTime() <= new Date($recruitment.deadline).getTime()}
          <Popover style="white" direct="top" questionDirection="end">
            <Button
              onClick={() => (showSignUpModal = true)}
              slot="children"
              className="sm:p-[7px_30px] max-sm:text-xs max-sm:w-[88px] max-sm:h-[28px] max-sm:leading-[28px] text-sm rounded-full"
              highlight>{$t('user.signUp')}</Button
            >
            <p class="w-[142px]" slot="content">
              {$t('user.signUpConfirm', {
                recruitment: $parseTitle($recruitment.name),
              })}
            </p>
          </Popover>
        {/if}
      </div>
      <div class=" lg:grid lg:grid-cols-2 mb-[2rem] w-full gap-[2rem]">
        <SingleInputInfo
          necessary
          name={$t('user.name')}
          bind:content={$userInfo.name}
          tips={$t("user.changeUserInfoTip")}
          editMode={$editMode}
          isDisabled={true}
        />
        <SingleSelectInfo
          necessary
          name={$t('user.gender')}
          bind:content={GENDERS[$userInfo.gender - 1]}
          selectItems={genders}
        />
        <SingleSelectInfo
          necessary
          editMode={$editMode}
          name={$t('user.grade')}
          bind:content={grade}
          selectItems={grades}
        />
        <SingleSelectInfo
          selectItems={colleges}
          editMode={$editMode}
          onChange={() => (major = '')}
          necessary
          name={$t('user.college')}
          bind:content={institute}
        />
        <SingleSelectInfo
          placeholder={majors.length ? '' : '请选择学院'}
          selectItems={majors}
          editMode={$editMode}
          necessary
          name={$t('user.major')}
          bind:content={major}
        />
        <SingleSelectInfo
          editMode={$editMode}
          necessary
          name={$t('user.rank')}
          bind:content={rank}
          selectItems={ranks}
        />
        <SingleInputInfo
          necessary
          name={$t('user.phone')}
          bind:content={$userInfo.phone}
          isDisabled={true}
        />
        <SingleInputInfo
          necessary
          name={$t('user.email')}
          bind:content={$userInfo.email}
          tips={$t("user.changeUserInfoTip")}
          editMode={$editMode}
          isDisabled={true}
        />
        <SingleInputInfo
          editMode={$editMode}
          name={$t('user.recommender')}
          bind:content={referrer}
        />
        <SingleSelectInfo
          editMode={$editMode &&
            (!$recruitment ||
              $userInfo?.applications[0]?.recruitment_id !== $recruitment.uid)}
          necessary
          name={$t('user.group')}
          content={Group[group] || ''}
          onChange={(item) => (group = item.toLowerCase())}
          selectItems={['AI', 'Design', 'Game', 'Lab', 'Mobile', 'PM', 'Web']}
        />
        <div class="col-span-2 max-w-full gap-[1rem]">
          <Popover
            style="white"
            direct="left-top"
            className="w-full max-sm:mt-[-1.5rem]"
          >
            <SingleSelectInfo
              className="flex-shrink-0 max-sm:w-[calc(100%_-_24px)]"
              slot="children"
              editMode={$editMode}
              necessary
              name={$t('user.isQuick')}
              bind:content={isQuick}
              selectItems={quicks}
            />
            <p slot="content" class="w-[300px]">{$t('user.isQuickTips')}</p>
          </Popover>
        </div>
        <div class="flex col-span-2 gap-[1rem]">
          <p class="shrink-0 max-sm:text-xs mt-[0.75rem]">
            <span class="text-blue-300">*</span>{$t('user.selfIntro')}
          </p>
          <textarea
            bind:value={intro}
            disabled={!$editMode}
            placeholder={$t('user.placeholder')}
            class={cx([
              'w-full max-sm:text-xs transition-all outline-none border-[1px] focus:border-[#165DFF] resize-none rounded-[8px] p-[0.75rem_1rem] bg-[#FAFAFA] h-[10rem]',
              $editMode
                ? 'bg-transparent border-gray-200'
                : 'border-transparent',
            ])}
          />
        </div>
      </div>
      <div class="w-full h-[1px] mb-[2rem] bg-[#E5E6EB]" />
      <UserInfoTitle title={$t('user.attachment')} />
      <div
        class="sm:flex sm:justify-center bg-[#FAFAFA] rounded-[1rem] max-sm:rounded-[4px] py-[2rem] max-sm:p-[18px] items-center flex-col gap-[1rem]"
      >
        {#if $editMode}
          <div
            on:click={() => fileInput.click()}
            class="flex sm:hidden gap-[1rem]"
          >
            <img src={uploadSvg} alt="upload" />
            <div>
              <p class="text-sm font-bold my-[4px]">{$t('user.upload')}</p>
              <p class=" text-text-3 text-xs">
                {$t('user.resumePopover')}
              </p>
              {#if resume}
                <p class="text-xs mt-[4px]">{resume.name}</p>
              {/if}
            </div>
          </div>
          <p class="font-bold max-sm:hidden text-lg">{$t('user.upload')}</p>
          <p class="px-[3rem] max-sm:hidden text-text-3 text-xs text-center">
            {$t('user.resumePopover')}
          </p>
          {#if resume}
            <p class="max-sm:hidden">{resume.name}</p>
          {/if}
          <div
            class="cursor-pointer max-sm:hidden border-[1px] border-[#0A84FF] text-[#0A84FF] p-[0.5rem_2rem] hover:bg-[#0A84FF] hover:text-white transition-all rounded-[0.5rem]"
            on:click={() => fileInput.click()}
          >
            {resume ? $t('user.reselect') : $t('user.select')}
          </div>
          <input
            on:change={() => {
              const file = fileInput.files[0];
              if (file && file.size > 20 * 1024 * 1024) {
                fileInput.value = '';
                Message.error($t('user.resumeTooLarge'));
              } else {
                resume = fileInput.files[0];
              }
            }}
            bind:this={fileInput}
            type="file"
            class="hidden"
          />
        {:else if $recruitment && $userInfo.applications[0]?.recruitment_id === $recruitment.uid && $userInfo.applications[0].resume}
          <div
            on:click={downloadResume}
            class="cursor-pointer flex justify-center items-center sm:flex-col gap-[8px]"
          >
            <img src={word} alt="简历" />
            {#await getRecruitmentById($userInfo.applications[0].recruitment_id) then res}
              <p class="max-sm:text-sm">
                {$parseTitle(res.data.name)}-{$userInfo.name}-{$t(
                  'user.resume'
                )}
              </p>
            {/await}
          </div>
        {:else}
          <p class="font-bold text-lg max-sm:text-sm text-gray-400 select-none">
            {$t('user.noResume')}
          </p>
        {/if}
      </div>
    {:else}
      <p class="text-center text-gray-250 text-2xl my-[2rem]">暂无个人信息</p>
    {/if}
    <Modal
      className="w-[524px] max-sm:w-[280px] flex flex-col gap-[1rem] text-center p-[20px_20px]"
      visible={showSignUpModal}
      onCancel={() => (showSignUpModal = false)}
    >
      <p>{$t('user.signUpTips')}{$parseTitle($recruitment.name)}</p>
      <p>{$t('user.signUpTips1')}</p>
      <div class="flex gap-[1rem] justify-center">
        <Button
          onClick={signUp}
          highlight
          className="p-[7px_30px] text-sm rounded-full"
          >{$t('user.signUp')}</Button
        >
        <Button
          onClick={() => (showSignUpModal = false)}
          className="p-[7px_30px] text-sm rounded-full"
          >{$t('user.cancel')}</Button
        >
      </div>
    </Modal>
  </div>
</div>
