from functools import reduce
from itertools import accumulate, pairwise
import json
import math
from typing import List, Literal, NamedTuple
import xml.etree.ElementTree as ET


R = 6371e3

# Use official data for elevation gained, to not rely on the GPS tracks innaccuracy
ELEVATION_GAINED = [
    200,
    2500,
    3850,
    2700,
    1600,
    4100,
    850,
    1150,
    3300,
    3800,
    1400,
    1800,
    2400,
    3800,
    3950,
    500,
    2200,
    3900,
    3500,
    5450,
    1000,
]

STAGE_TYPES: List[Literal["flat", "hilly", "moutain", "tt", "ttt"]] = [
    "ttt",
    "hilly",
    "moutain",
    "hilly",
    "flat",
    "moutain",
    "flat",
    "flat",
    "hilly",
    "moutain",
    "flat",
    "flat",
    "hilly",
    "moutain",
    "moutain",
    "tt",
    "flat",
    "moutain",
    "moutain",
    "moutain",
    "flat",
]


class Coordinates(NamedTuple):
    lat: float
    lon: float
    elevation: float


def parse_point(point: ET.Element) -> Coordinates:
    lat = float(point.attrib["lat"])
    lon = float(point.attrib["lon"])
    elevation = float(point.find("ele").text)

    return Coordinates(lat, lon, elevation)


def distance(x: Coordinates, y: Coordinates) -> float:
    phi1 = x.lat * math.pi / 180
    phi2 = y.lat * math.pi / 180
    delta_phi = (y.lat - x.lat) * math.pi / 180
    delta_lambda = (y.lon - x.lon) * math.pi / 180

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * (
        math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return c * R


class RawPoint(NamedTuple):
    distance_delta: float
    elevation: float


class Point(NamedTuple):
    distance: float
    elevation: float


def parse_stage_points(stage: ET.Element) -> List[Point]:
    coordinates = (
        parse_point(point) for point in stage.find("trkseg").findall("trkpt")
    )
    raw_points = (
        RawPoint(distance(a, b), b.elevation) for (a, b) in pairwise(coordinates)
    )

    return list(
        map(
            lambda point: Point(round(point.distance), round(point.elevation)),
            accumulate(
                raw_points,
                lambda acc, point: Point(
                    acc.distance + point.distance_delta, point.elevation
                ),
                initial=Point(0.0, 0.0),
            ),
        )
    )


class StageStatistics(NamedTuple):
    total_distance: float
    min_elevation: float
    max_elevation: float


def stage_statistics_lambda(acc: StageStatistics, curr: Point) -> StageStatistics:
    return StageStatistics(
        min_elevation=min(acc.min_elevation, curr.elevation),
        max_elevation=max(acc.max_elevation, curr.elevation),
        total_distance=curr.distance,
    )


def stage_statistics(points: List[Point]):
    return reduce(
        stage_statistics_lambda,
        points,
        StageStatistics(0, 0, 0),
    )


if __name__ == "__main__":
    tree = ET.parse("data/tour-de-france-2026.gpx")
    root = tree.getroot()

    stages = []
    race_max_distance = 0
    race_min_max_elevation = 0
    race_max_max_elevation = 0
    for idx, stage in enumerate(root.findall("trk")):
        points = parse_stage_points(stage)
        statistics = stage_statistics(points)
        race_max_distance = max(race_max_distance, statistics.total_distance)
        race_max_max_elevation = max(race_max_max_elevation, statistics.max_elevation)
        race_min_max_elevation = min(race_min_max_elevation, statistics.max_elevation)

        stages.append(
            {
                "number": idx + 1,
                "name": stage.find("desc").text,
                "distance": statistics.total_distance,
                "elevation_gained": ELEVATION_GAINED[idx],
                "max_elevation": statistics.max_elevation,
                "type": STAGE_TYPES[idx],
                "points": points,
            }
        )

    with open("src/lib/assets/stages.json", "w") as file:
        file.write(
            json.dumps(
                {
                    "max_max_elevation": race_max_max_elevation,
                    "min_max_elevation": race_min_max_elevation,
                    "max_distance": race_max_distance,
                    "stages": stages,
                }
            )
        )
