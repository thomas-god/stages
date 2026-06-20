<script>
	import StageChart from '$lib/components/organisms/StageChart.svelte';

	import stagesRaw from '$lib/assets/stages.json?raw';
	import { isSome, none, some } from '$lib/option';

	let stages = $derived(JSON.parse(stagesRaw));
	let maxElevation = $state(none());
	let maxDistance = $state(some(stages.max_distance));

	let width = $state(300);
</script>

<label class="label">
	Same elevation scale
	<input
		type="checkbox"
		class="toggle"
		bind:checked={
			() => isSome(maxElevation), (v) => (maxElevation = v ? some(stages.max_elevation) : none())
		}
	/>
</label>
<label class="label">
	Same distance scale
	<input
		type="checkbox"
		class="toggle"
		bind:checked={
			() => isSome(maxDistance), (v) => (maxDistance = v ? some(stages.max_distance) : none())
		}
	/>
</label>

<div bind:clientWidth={width} class="flex flex-col gap-1 p-2">
	{#each stages.stages as stage}
		{stage.name}
		<StageChart points={stage.points} {width} height={200} {maxDistance} {maxElevation} />
	{/each}
</div>
