<script lang="ts">
	interface Props {
		isSelected?: boolean;
	}

	let { isSelected = false }: Props = $props();
</script>

<svg width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg">
	<rect
		class="transition-colors duration-500"
		x="0.333374"
		width="14"
		height="14"
		rx="2"
		stroke={isSelected ? "transparent" : "#E5E6EB"}
		fill={isSelected ? "#165DFF" : "white"}
	/>
	<path
		fill-rule="evenodd"
		clip-rule="evenodd"
		d="M10.16 4.13777C9.95295 3.93136 9.61375 3.94585 9.42506 4.16918L6.32318 7.84049L5.19915 6.6667C5.00517 6.46414 4.68255 6.46071 4.48432 6.65911L4.13109 7.01264C3.93895 7.20494 3.93565 7.51553 4.12367 7.71186L5.97487 9.645C6.12125 9.79786 6.34087 9.83732 6.52502 9.76223C6.62695 9.73913 6.72272 9.68394 6.79587 9.59736L7.07511 9.26686L7.38862 8.95308L7.36291 8.92623L10.5406 5.16517C10.7085 4.96641 10.696 4.67208 10.5117 4.48838L10.16 4.13777Z"
		fill="white"
	/>
</svg>
