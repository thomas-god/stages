<script lang="ts">
	import { isSome, none, unwrapOr, type Option } from '$lib/option';
	import * as d3 from 'd3';

	const marginLeft = 45;
	const marginRight = 5;
	const marginTop = 0;
	const marginBottom = 20;

	let gx: SVGGElement;
	let gy: SVGGElement;
	let gyGrid: SVGGElement;

	let {
		points,
		width,
		height,
		maxDistance = none(),
		yAxisNegativeOffser = 100,
		yAxisResolution = 250
	}: {
		points: [number, number][];
		width: number;
		height: number;
		maxDistance?: Option<number>;
		yAxisNegativeOffser?: number;
		yAxisResolution?: number;
	} = $props();

	let xScale = $derived(
		d3.scaleLinear(
			[0, unwrapOr(maxDistance, d3.max(points, (point) => point[0]) || 0)],
			[marginLeft, width - marginRight]
		)
	);
	let xTickValues = $derived(
		Array.from({ length: Math.ceil(xScale.domain()[1] / 50 / 1000) }, (_v, idx) => idx * 50 * 1000)
	);
	let xAxis = $derived(
		d3
			.axisBottom(xScale)
			.tickFormat((value, _idx) => (value.valueOf() / 1000).toString() + ' km')
			.tickValues(xTickValues)
	);
	let yScale = $derived(
		d3.scaleLinear(
			[-yAxisNegativeOffser, d3.max(points, (point) => point[1]) || 0],
			[height - marginBottom, marginTop]
		)
	);
	let yTickValues = $derived(
		Array.from(
			{ length: Math.ceil(yScale.domain()[1] / yAxisResolution) },
			(v, idx) => idx * yAxisResolution
		)
	);
	let yAxis = $derived(
		d3
			.axisLeft(yScale)
			.tickFormat((value, idx) => {
				if (yTickValues.length <= 2) {
					return `${value} m`;
				}
				return idx % 2 !== 0 ? '' : `${value} m`;
			})
			.tickValues(yTickValues)
	);

	const area = $derived(
		d3
			.area()
			.x((d) => xScale(d[0]))
			.y0(yScale(yScale.domain()[0]))
			.y1((d) => yScale(d[1]))
	);

	$effect(() => {
		d3.select(gx).call(xAxis);
		d3.select(gy).call(yAxis);
		d3.select(gyGrid)
			.selectAll('line')
			.data(yTickValues)
			.join('line')
			.attr('x1', 0)
			.attr('x2', width - marginRight - marginLeft)
			.attr('y1', (tickValue) => yScale(tickValue))
			.attr('y2', (tickValue) => yScale(tickValue));
	});
</script>

<svg {width} {height} viewBox={`0 0 ${width} ${height}`} role="img" class="h-full w-full">
	<g bind:this={gyGrid} transform="translate({marginLeft} 0)" stroke="currentColor" opacity="0.3" />
	<path d={area(points)} fill="steelblue" />

	<g bind:this={gx} transform="translate(0 {height - marginBottom})" />
	<g bind:this={gy} transform="translate({marginLeft} 0)" />
</svg>
