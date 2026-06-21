<script lang="ts">
	import StageChart from '$lib/components/organisms/StageChart.svelte';

	import stagesRaw from '$lib/assets/stages.json?raw';
	import { isNone, isSome, none, some, type Option } from '$lib/option';

	let stages = $derived(JSON.parse(stagesRaw));
	let maxElevation: Option<number> = $state(some(stages.max_max_elevation));
	let maxDistance: Option<number> = $state(some(stages.max_distance));

	let width = $state(300);

	let minHeight = 0;
	let maxHeight = 200;
	let heightResolution = 250;

	let minElevation = -100;
	let _maxElevation = stages.max_max_elevation;

	let heightCoeff = $derived((maxHeight - minHeight) / (_maxElevation - minElevation));
	let heightOffset = $derived(minHeight - heightCoeff * minElevation);

	// Scale down the maxHeight depending of the max elevation of the stage compared to the stage
	// with the highest elevation to make sure all charts have the same elevation resolution when
	// elevation scale is shared.
	const scaleHeight = (stageMaxElevation: number): number => {
		if (isNone(maxElevation)) {
			return maxHeight;
		}

		const roundedMaxElevation = Math.ceil(stageMaxElevation / heightResolution) * heightResolution;
		return heightOffset + heightCoeff * roundedMaxElevation + 30;
	};
</script>

<label class="label">
	Same elevation scale
	<input
		type="checkbox"
		class="toggle"
		bind:checked={
			() => isSome(maxElevation),
			(v) => (maxElevation = v ? some(stages.max_max_elevation) : none())
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

<div class="graphs-container p-2">
	{#each stages.stages as stage, idx}
		<!-- <div class="stage-details text-sm" style={`grid-row: ${idx + 1}`}>
			<div>
				{stage.name}
			</div>
			<div>{stage.type}</div>
			<div>
				{(stage.distance / 1000).toLocaleString('fr-FR', { maximumFractionDigits: 0 })} km
			</div>
			<div>
				{stage.elevation_gained} m
			</div>
			<div>{stage.elevation_range}</div>
		</div> -->
		<div class="stage-chart" bind:clientWidth={width} style={`grid-row: ${idx + 1}`}>
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

<style>
	.graphs-container {
		display: flex;
		flex-direction: column;
		/* grid-template-columns: 200px auto; */
	}

	.stage-details {
		grid-column: 1;
	}

	.stage-chart {
		grid-column: 2;
	}
</style>
