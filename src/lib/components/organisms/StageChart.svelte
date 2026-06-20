<script lang="ts">
	import { isSome, none, unwrapOr, type Option } from '$lib/option';
	import * as d3 from 'd3';

	const marginTop = 20;
	const marginRight = 50;
	const marginBottom = 30;
	const marginLeft = 50;

	let gx: SVGGElement;
	let gy: SVGGElement;
	let gyGrid: SVGGElement;

	let {
		points,
		width,
		height,
		maxDistance = none(),
		maxElevation = none()
	}: {
		points: [number, number][];
		width: number;
		height: number;
		maxElevation?: Option<number>;
		maxDistance?: Option<number>;
	} = $props();

	let xScale = $derived(
		d3.scaleLinear(
			[
				0,
				unwrapOr(
					maxDistance,
					d3.max(points, (point) => point[0])
				)
			],
			[marginLeft, width - marginRight]
		)
	);
	let xAxis = $derived(
		d3.axisBottom(xScale).tickFormat((value, _idx) => (value.valueOf() / 1000).toString() + ' km')
	);
	let yScale = $derived(
		d3.scaleLinear(
			isSome(maxElevation) ? [0, maxElevation.value] : d3.extent(points, (point) => point[1]),
			[height - marginBottom, marginTop]
		)
	);
	let yAxis = $derived(
		d3
			.axisLeft(yScale)
			.ticks(6)
			.tickFormat((value, _idx) => `${value} m`)
	);

	const area = $derived(
		d3
			.area()
			.x((d) => xScale(d[0]))
			.y0(yScale(yScale.domain()[0]))
			.y1((d) => yScale(d[1]))
	);

	$effect(() => {
		d3.select(gx).call(xAxis, xScale);
		d3.select(gy).call(yAxis, yScale);
		d3.select(gyGrid)
			.selectAll('line')
			.data(yScale.ticks(6))
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
