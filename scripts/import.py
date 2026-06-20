from functools import reduce
from itertools import accumulate, pairwise
import json
import math
from typing import List, Tuple
import xml.etree.ElementTree as ET

tree = ET.parse("data/tour-de-france-2026.gpx")
root = tree.getroot()

R = 6371e3


def parse_point(point: ET.Element):
    lat = float(point.attrib["lat"])
    lon = float(point.attrib["lon"])
    elevation = float(point.find("ele").text)

    return (lat, lon, elevation)


def distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    phi1 = a[0] * math.pi / 180
    phi2 = b[0] * math.pi / 180
    delta_phi = (b[0] - a[0]) * math.pi / 180
    delta_lambda = (b[1] - a[1]) * math.pi / 180

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * (
        math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return c * R


def parse_stage_points(stage: ET.Element) -> List[Tuple[float, float]]:
    coordinates = (
        parse_point(point) for point in stage.find("trkseg").findall("trkpt")
    )
    raw_points = ((distance(a, b), b[2]) for (a, b) in pairwise(coordinates))
    points = list(
        map(
            lambda point: (round(point[0]), round(point[1])),
            accumulate(
                raw_points,
                lambda distance, point: (distance[0] + point[0], point[1]),
            ),
        )
    )
    return points


stages = []
max_distance = 0
max_elevation = 0
for idx, stage in enumerate(root.findall("trk")):
    points = parse_stage_points(stage)
    max_distance = max_distance if max_distance >= points[-1][0] else points[-1][0]

    local_max_elevation = reduce(
        lambda max, point: max if max >= point[1] else point[1], points, 0.0
    )
    max_elevation = (
        max_elevation if max_elevation >= local_max_elevation else local_max_elevation
    )

    stages.append(
        {"number": idx + 1, "name": stage.find("desc").text, "points": points}
    )

with open("src/lib/assets/stages.json", "w") as file:
    file.write(
        json.dumps(
            {
                "stages": stages,
                "max_elevation": max_elevation,
                "max_distance": max_distance,
            }
        )
    )
