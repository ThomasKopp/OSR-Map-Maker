"""Dependency-free geometry primitives used by model and renderer code."""
from __future__ import annotations

import math

Point = tuple[float, float]
Box = tuple[float, float, float, float]


def rects_overlap(a: Box, b: Box, padding: float = 0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (
        ax - padding < bx + bw
        and ax + aw + padding > bx
        and ay - padding < by + bh
        and ay + ah + padding > by
    )


def point_in_polygon(x: float, y: float, points: list[Point]) -> bool:
    if len(points) < 3:
        return False
    inside = False
    previous_x, previous_y = points[-1]
    for current_x, current_y in points:
        if (current_y > y) != (previous_y > y):
            slope_x = (previous_x - current_x) * (y - current_y) / (previous_y - current_y) + current_x
            if x <= slope_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def rotate_xy(x: float, y: float, cx: float, cy: float, degrees: float) -> Point:
    radians = math.radians(degrees)
    dx, dy = x - cx, y - cy
    return (
        cx + math.cos(radians) * dx - math.sin(radians) * dy,
        cy + math.sin(radians) * dx + math.cos(radians) * dy,
    )


def points_bounds(points: list[Point]) -> Box:
    if not points:
        return 0.0, 0.0, 0.25, 0.25
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    left, top = min(xs), min(ys)
    right, bottom = max(xs), max(ys)
    return left, top, max(0.25, right - left), max(0.25, bottom - top)


def quadratic_curve_points(start: Point, control: Point, end: Point, steps: int = 18) -> list[Point]:
    points: list[Point] = []
    for index in range(max(2, steps) + 1):
        t = index / max(2, steps)
        inv = 1 - t
        points.append(
            (
                inv * inv * start[0] + 2 * inv * t * control[0] + t * t * end[0],
                inv * inv * start[1] + 2 * inv * t * control[1] + t * t * end[1],
            )
        )
    return points
