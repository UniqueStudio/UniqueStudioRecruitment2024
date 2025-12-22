<script lang="ts">
  import cx from 'clsx';
  import { scale } from 'svelte/transition';
  import question from "../../assets/question.svg";
  import Modal from './Modal.svelte';
  import { isMobile } from '../../stores/isMobile';
  //ly: now i just finished top & bottom props cuz i'm lazy :)
  export let direct: 'left' | 'right' | 'top' | 'bottom' | 'left-top' =
    'bottom';
  export let style: 'white' | 'black' = 'black';
  export let questionDirection:"front" | "end" = "front";
  export let className: String = '';
  export let isShowImg = true;
  export let shouldShow: boolean = true;
  let box: HTMLDivElement;
  let showContent = false;
  let showModal = false;
  let timerIn: number;
  let timerOut: number;

  const handleMouseMoveIn = () => {
    if (!shouldShow) return;
    clearTimeout(timerOut);
    timerIn = setTimeout(() => {
      showContent = true;
    }, 300);
  };
  const handleMouseMoveOut = () => {
    clearTimeout(timerIn);
    timerOut = setTimeout(() => {
      showContent = false;
    }, 500);
  };
</script>

<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<div
  role="tooltip"
  on:pointerover={handleMouseMoveIn}
  on:pointerout={handleMouseMoveOut}
  bind:this={box}
  class={cx(['relative w-fit max-sm:flex max-sm:gap-[8px]', questionDirection === "end" && "max-sm:flex-row-reverse", className])}
>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  {#if isShowImg}
    <img class="inline sm:hidden" on:click={() => showModal = true} src={question} alt="?" />
  {/if}
  <slot name="children" />
  {#if showContent}
    <div
      transition:scale
      class={cx([
        'absolute z-[90] rounded-[6px]',
        style === 'black' ? 'shadow-drop' : 'shadow-card',
        direct === 'bottom' &&
          'top-[calc(100%_+_12px)]  origin-[top_center] left-[50%] translate-x-[-50%] ',
        direct === 'top' &&
          'bottom-[calc(100%_+_12px)] origin-[bottom_center] left-[50%] translate-x-[-50%]',
        direct === 'left-top' &&
          'bottom-[calc(100%_+_12px)] origin-[bottom_left] left-[0] ',
      ])}
    >
      <div
        class={cx([
          'border-gray-150  w-fit text-center text-sm p-[8px_12px] rounded-[6px]',
          style === 'black' ? 'text-white bg-black' : 'text-black bg-white',
        ])}
      >
        <slot name="content" />
      </div>
      <div
        class={cx([
          'w-0 h-0 absolute border-[8px] border-transparent ',
          direct === 'bottom' && 'top-[-14px] left-[calc(50%_-_8px)]',
          direct === 'top' &&
            'bottom-[-14px] left-[calc(50%_-_8px)] rotate-180',
          direct === 'left-top' &&
            'bottom-[-14px] left-[8px] rotate-180',
          style === 'black' ? 'border-b-black' : 'border-b-white',
        ])}
      ></div>
    </div>
  {/if}
</div>

<Modal className="p-[1rem] text-sm text-center" onCancel={() => showModal = false} visible={showModal}>
  <slot name="content" />
</Modal>
