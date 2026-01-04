<script>
	import { fade, fly } from "svelte/transition";
</script>

<div class="mx-auto mt-[1rem] flex h-full w-[60%] flex-col">
	<p in:fade class="text-[26px] text-white">未知页面</p>
	<div
		in:fly={{ y: 50, duration: 500, delay: 500 }}
		out:fly={{ y: 50, duration: 500 }}
		class="mt-[1rem] h-[200px] w-[full] rounded-[20px] bg-white p-[20px]"
	>
		<p>你好像来到了不存在的页面哦～</p>
	</div>
</div>
