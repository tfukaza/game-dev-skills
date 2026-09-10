#!/usr/bin/env python3
"""Monotone height profiles and static contacts; stdlib, Y-up, metres."""
import argparse
import bisect
import json
import math
import sys


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite number')
    return float(value)


class Profile:
    def __init__(self, anchors, flat_ends=False):
        self.points = [tuple(finite(v) for v in pair) for pair in anchors]
        if len(self.points) < 2 or any(len(pair) != 2 for pair in self.points):
            raise ValueError('At least two [station, height] anchors are required')
        self.x, self.y = zip(*self.points)
        h = [b - a for a, b in zip(self.x, self.x[1:])]
        if any(value <= 0 for value in h):
            raise ValueError('Anchor stations must increase strictly')
        d = [(b - a) / step for a, b, step in zip(self.y, self.y[1:], h)]
        m = [0.0] * len(self.points)
        for i in range(1, len(m) - 1):
            if d[i - 1] * d[i] > 0:
                w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

        def endpoint(h0, h1, d0, d1):
            slope = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
            if slope * d0 <= 0:
                return 0.0
            return math.copysign(min(abs(slope), 3 * abs(d0)), d0)

        if not flat_ends:
            m[0] = d[0] if len(d) == 1 else endpoint(h[0], h[1], d[0], d[1])
            m[-1] = d[-1] if len(d) == 1 else endpoint(h[-1], h[-2], d[-1], d[-2])
        self.slopes = m

    def evaluate(self, station):
        x = finite(station)
        if x < self.x[0]:
            return self.y[0], 0.0
        if x > self.x[-1]:
            return self.y[-1], 0.0
        i = min(len(self.x) - 2, max(0, bisect.bisect_right(self.x, x) - 1))
        h = self.x[i + 1] - self.x[i]
        t = (x - self.x[i]) / h
        y0, y1, m0, m1 = self.y[i], self.y[i + 1], self.slopes[i], self.slopes[i + 1]
        value = (2*t**3-3*t*t+1)*y0 + (t**3-2*t*t+t)*h*m0 + (-2*t**3+3*t*t)*y1 + (t**3-t*t)*h*m1
        slope = ((6*t*t-6*t)*y0 + (3*t*t-4*t+1)*h*m0 + (-6*t*t+6*t)*y1 + (3*t*t-2*t)*h*m1) / h
        return value, slope

    def sample(self, max_step, stations=(), axis='x'):
        step = finite(max_step)
        if step <= 0 or axis not in ('x', 'z'):
            raise ValueError('maxStep must be positive and axis must be x or z')
        extra = [finite(value) for value in stations]
        if any(value < self.x[0] or value > self.x[-1] for value in extra):
            raise ValueError('Mandatory stations must lie inside the profile')
        breaks = sorted(set(self.x) | set(extra))
        samples = [breaks[0]]
        for a, b in zip(breaks, breaks[1:]):
            count = max(1, math.ceil((b - a) / step))
            samples.extend(a + (b - a) * i / count for i in range(1, count))
            samples.append(b)
        rows = []
        for x in samples:
            height, derivative = self.evaluate(x)
            length = math.hypot(1, derivative)
            normal = [-derivative / length, 1 / length, 0] if axis == 'x' else [0, 1 / length, -derivative / length]
            rows.append(dict(station=x, height=height, derivative=derivative, normal=normal))
        return rows


def floor_hits(point, triangles):
    point = [finite(value) for value in point]
    if len(point) != 3:
        raise ValueError('Contact points need three coordinates')
    hits = []
    for triangle in triangles:
        vertices = [[finite(value) for value in vertex] for vertex in triangle['vertices']]
        if len(vertices) != 3 or any(len(vertex) != 3 for vertex in vertices):
            raise ValueError('A receiver must be a three-vertex triangle')
        a, b, c = vertices
        ab, ac = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        up = ab[2] * ac[0] - ab[0] * ac[2]
        if up <= 1e-12:
            continue
        dx, dz = point[0] - a[0], point[2] - a[2]
        determinant = -up
        u = (dx * ac[2] - dz * ac[0]) / determinant
        v = (ab[0] * dz - ab[2] * dx) / determinant
        if u >= -1e-9 and v >= -1e-9 and u + v <= 1 + 1e-9:
            hits.append(dict(receiver=str(triangle['id']), height=a[1] + u * ab[1] + v * ac[1]))
    return sorted(hits, key=lambda item: (-item['height'], item['receiver']))


def contact_report(points, triangles, tolerance=.01):
    tolerance = finite(tolerance)
    if tolerance < 0:
        raise ValueError('Contact tolerance cannot be negative')
    rows = []
    for sample in points:
        hits = floor_hits(sample['position'], triangles)
        gap = finite(sample['position'][1]) - hits[0]['height'] if hits else None
        state = 'missing' if gap is None else 'floating' if gap > tolerance else 'buried' if gap < -tolerance else 'contact'
        rows.append(dict(id=str(sample['id']), gap=gap, state=state, receiver=hits[0]['receiver'] if hits else None, hits=hits))
    if not rows:
        raise ValueError('At least one contact point is required')
    return dict(passed=all(row['state'] == 'contact' for row in rows), points=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON profile/contact input')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as stream:
            data = json.load(stream)
        result = {}
        if 'profile' in data:
            spec = data['profile']
            result['profile'] = Profile(spec['anchors'], spec.get('flatEnds', False)).sample(spec['maxStep'], spec.get('stations', []), spec.get('axis', 'x'))
        if 'contact' in data:
            spec = data['contact']
            result['contact'] = contact_report(spec['points'], spec['triangles'], spec.get('tolerance', .01))
        if not result:
            raise ValueError('Input needs profile or contact')
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result.get('contact', {}).get('passed', True) else 1
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__': sys.exit(main())
