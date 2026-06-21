<script lang="ts">
	import StageChart from '$lib/components/organisms/StageChart.svelte';

	import stagesRaw from '$lib/assets/stages.json?raw';
	import { isNone, some, type Option } from '$lib/option';

	let stages = $derived(JSON.parse(stagesRaw));
	let maxElevation: Option<number> = $derived(some(stages.max_max_elevation));
	let maxDistance: Option<number> = $derived(some(stages.max_distance));

	let width = $state(300);

	let minHeight = 0;
	let maxHeight = 200;
	let heightResolution = 250;

	let minElevation = -100;

	let heightCoeff = $derived((maxHeight - minHeight) / (stages.max_max_elevation - minElevation));
	let heightOffset = $derived(minHeight - heightCoeff * minElevation);

	// Scale down the maxHeight depending of the max elevation of the stage compared to the stage
	// with the highest elevation to make sure all charts have the same elevation resolution when
	// elevation scale is shared.
	const scaleHeight = (stageMaxElevation: number): number => {
		if (isNone(maxElevation)) {
			return maxHeight;
		}

		const roundedMaxElevation = Math.ceil(stageMaxElevation / heightResolution) * heightResolution;
		return heightOffset + heightCoeff * roundedMaxElevation + 20;
	};
</script>

<h2 class="text-xl p-2 text-center">Tour de France 2026</h2>
<div bind:clientWidth={width} class="flex flex-col gap-2 p-1 max-w-6xl justify-center mx-auto mb-4">
	{#each stages.stages as stage, idx}
		<div class="flex flex-col">
			<div class="py-1 text-sm text-center font-light opacity-85">
				S{idx + 1}:
				{stage.name} <span class="italic opacity-70">({stage.elevation_gained}m D+)</span>
			</div>
			<StageChart
				points={stage.points}
				{width}
				height={scaleHeight(stage.max_elevation)}
				{maxDistance}
				yAxisResolution={heightResolution}
			/>
		</div>
	{/each}
</div>
