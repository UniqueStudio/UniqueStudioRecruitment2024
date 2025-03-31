<script lang="ts">
  import cx from 'clsx'
  import { t } from "../../utils/t";
  import Popover from '../public/Popover.svelte';
  export let necessary: boolean = false;
  export let name: string;
  export let content: string;
  export let editMode: boolean = false;
  export let tips: string = "";
  export let isDisabled: boolean = false;
</script>

<div class="flex gap-[1rem] items-center max-lg:my-[1.5rem]">
  <p class="  max-sm:text-sm shrink-0">{@html necessary ? `<span class="text-blue-300">*</span>` : " "}{name}</p>
  {#if tips!==""}
  <Popover direct="top" questionDirection="end" style="white" className="w-full" shouldShow={editMode}>
    <input
      disabled={isDisabled}
      placeholder={editMode ? $t('user.placeholder') : ""}
      class={cx(["p-[4px_12px] w-full rounded-[8px] max-sm:text-sm text-text-1 bg-[#FAFAFA] h-[48px] max-sm:h-[42px] transition-all outline-none border-[1px]  focus:border-[#165DFF]", editMode && !isDisabled ? "bg-transparent border-gray-200" : "border-transparent"])}
      bind:value={content}
      slot="children"
    />
    <p slot="content" class="w-[180px]">
      {tips}
    </p>
  </Popover>
  {:else}
    <input
      disabled={isDisabled}
      placeholder={editMode ? $t('user.placeholder') : ""}
      class={cx(["p-[4px_12px] w-full rounded-[8px] max-sm:text-sm text-text-1 bg-[#FAFAFA] h-[48px] max-sm:h-[42px] transition-all outline-none border-[1px]  focus:border-[#165DFF]", editMode && !isDisabled ? "bg-transparent border-gray-200" : "border-transparent"])}
      bind:value={content}
    />
  {/if}
</div>

