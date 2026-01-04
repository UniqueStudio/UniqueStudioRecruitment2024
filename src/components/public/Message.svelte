<script lang="ts">
	import { onMount } from "svelte";
	import { fade } from "svelte/transition";
	// import warning from "../../assets/warning.svg";
	// import success from "../../assets/success.svg";
	// import error from "../../assets/error.svg";
	export let content: string;
	export let type: "warning" | "success" | "error" = "warning";
	export let onClose: () => void;
	let open = false;
	onMount(() => {
		open = true;
		new Promise<void>((resolve) =>
			setTimeout(() => {
				open = false;
				resolve();
			}, 1500)
		).then(() => {
			return setTimeout(onClose, 500);
		});
	});
</script>

<!-- ly: svelte would not apply translate-x-[-50%] when transition-in begins, so i use animate-fly-in, actually it is dumb:( -->
<!-- ly:sometimes(i don't know when) UI would shake when flies in but i don't know why, its fucking confusing. :( -->
{#if open}
	<div
		out:fade
		class="fixed left-[50%] top-[5rem] z-[9999] flex h-[40px] translate-x-[-50%] animate-fly-in items-center gap-[8px] rounded-sm border-[1px] border-gray-border bg-white p-[9px_16px] shadow-1"
	>
		{#if type === "warning"}
			<svg
				width="20"
				height="20"
				viewBox="0 0 20 20"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<g clip-path="url(#clip0_2577_4616)">
					<path
						fill-rule="evenodd"
						clip-rule="evenodd"
						d="M1.66666 9.99999C1.66666 5.39762 5.39762 1.66666 10 1.66666C14.6024 1.66666 18.3333 5.39762 18.3333 9.99999C18.3333 14.6024 14.6024 18.3333 10 18.3333C5.39762 18.3333 1.66666 14.6024 1.66666 9.99999ZM10.8333 7.49999V5.83332H9.16666V7.49999H10.8333ZM9.16666 8.33332V14.1667H10.8333V8.33332H9.16666Z"
						fill="#165DFF"
					/>
				</g>
				<defs>
					<clipPath id="clip0_2577_4616">
						<rect width="20" height="20" fill="white" />
					</clipPath>
				</defs>
			</svg>
		{:else if type === "error"}
			<svg
				width="20"
				height="20"
				viewBox="0 0 20 20"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<g clip-path="url(#clip0_2577_5026)">
					<path
						fill-rule="evenodd"
						clip-rule="evenodd"
						d="M1.66675 10.0001C1.66675 5.39771 5.39771 1.66675 10.0001 1.66675C14.6025 1.66675 18.3334 5.39771 18.3334 10.0001C18.3334 14.6025 14.6025 18.3334 10.0001 18.3334C5.39771 18.3334 1.66675 14.6025 1.66675 10.0001ZM6.7619 7.94053L8.82429 10.0029L6.7619 12.0653L7.94041 13.2438L10.0028 11.1814L12.0652 13.2438L13.2437 12.0653L11.1813 10.0029L13.2437 7.94053L12.0652 6.76201L10.0028 8.82441L7.94041 6.76201L6.7619 7.94053Z"
						fill="#F53F3F"
					/>
				</g>
				<defs>
					<clipPath id="clip0_2577_5026">
						<rect width="20" height="20" fill="white" />
					</clipPath>
				</defs>
			</svg>
		{:else}
			<svg
				width="21"
				height="20"
				viewBox="0 0 21 20"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<g clip-path="url(#clip0_2577_15175)">
					<path
						fill-rule="evenodd"
						clip-rule="evenodd"
						d="M2.16675 10.0001C2.16675 5.39771 5.89771 1.66675 10.5001 1.66675C15.1025 1.66675 18.8334 5.39771 18.8334 10.0001C18.8334 14.6025 15.1025 18.3334 10.5001 18.3334C5.89771 18.3334 2.16675 14.6025 2.16675 10.0001ZM9.66676 13.2619L15.0477 7.88102L13.8692 6.7025L9.66676 10.9049L7.33935 8.5775L6.16084 9.75602L9.66676 13.2619Z"
						fill="#00B42A"
					/>
				</g>
				<defs>
					<clipPath id="clip0_2577_15175">
						<rect width="20" height="20" fill="white" transform="translate(0.5)" />
					</clipPath>
				</defs>
			</svg>
		{/if}
		<p class="whitespace-nowrap">{content}</p>
	</div>
{/if}
