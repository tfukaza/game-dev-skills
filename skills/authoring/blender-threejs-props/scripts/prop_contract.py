#!/usr/bin/env python3
"""Stable variant parameters and cross-LOD export-fact checks; stdlib only."""
import argparse
import hashlib
import json
import math
import sys


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite number')
    return float(value)


def unit(seed, identity, channel):
    key = json.dumps([str(seed), str(identity), channel], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return int.from_bytes(hashlib.sha256(key).digest()[:8], 'big') / 2**64


def variant(seed, identity, ranges, choices):
    if not isinstance(identity, str) or not identity:
        raise ValueError('Variant IDs must be nonempty strings')
    if set(ranges) & set(choices):
        raise ValueError('A channel cannot be both a range and a choice')
    values = {}
    for name, limits in sorted(ranges.items()):
        if len(limits) != 2:
            raise ValueError('A variant range needs [minimum, maximum]')
        low, high = map(number, limits)
        if low > high:
            raise ValueError('Variant range is reversed')
        values[name] = low + (high - low) * unit(seed, identity, name)
    for name, options in sorted(choices.items()):
        if not isinstance(options, list) or not options:
            raise ValueError('A choice channel needs a nonempty list')
        values[name] = options[min(len(options)-1, int(unit(seed, identity, name)*len(options)))]
    return dict(id=identity, values=values)


def vectors(values, width, count=None):
    if not isinstance(values, list) or (count is not None and len(values) != count):
        raise ValueError('Attribute count does not match POSITION')
    result = [tuple(number(value) for value in row) for row in values]
    if any(len(row) != width for row in result):
        raise ValueError('Wrong vector width')
    return result


def audit(data):
    if data.get('units') != 'm':
        raise ValueError('Convert export facts to metres first (units: m)')
    errors, results, seen = [], [], set()
    for asset in data['assets']:
        identity = asset['id']
        if not isinstance(identity, str) or not identity or identity in seen:
            raise ValueError('Asset IDs must be unique nonempty strings')
        seen.add(identity)
        expected = vectors([asset['dimensions']], 3)[0]
        if min(expected) <= 0:
            raise ValueError('Asset dimensions must be positive')
        tolerance = number(asset.get('boundsTolerance', .02))
        pivot_tolerance = number(asset.get('pivotTolerance', .005))
        if min(tolerance, pivot_tolerance) < 0:
            raise ValueError('Tolerances cannot be negative')
        pivot = asset.get('pivot', 'bottom-center')
        if pivot not in ('bottom-center', 'custom'):
            raise ValueError('Pivot must be bottom-center or custom')
        lods = sorted(asset['lods'], key=lambda item: item['level'])
        levels = [lod['level'] for lod in lods]
        if not levels or any(type(level) is not int or level < 0 for level in levels) or len(set(levels)) != len(levels):
            raise ValueError('LOD levels must be unique nonnegative integers')
        if sorted(asset['requiredLods']) != levels:
            errors.append(f'{identity}: required LOD set differs')
        previous_count, baseline = None, None
        for lod in lods:
            label = f'{identity}/LOD{lod["level"]}'
            positions = vectors(lod['positions'], 3)
            indices = lod.get('indices', list(range(len(positions))))
            if not indices or len(indices) % 3 or any(type(i) is not int or i < 0 or i >= len(positions) for i in indices):
                raise ValueError(label + ': invalid triangle indices')
            matrix = [number(value) for value in lod.get('matrix', [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])]
            if len(matrix) != 16 or [matrix[i] for i in (3,7,11,15)] != [0,0,0,1]:
                raise ValueError(label + ': matrix must be column-major affine')
            used = [[sum(matrix[column*4+row]*positions[i][column] for column in range(3))+matrix[12+row] for row in range(3)] for i in set(indices)]
            low = [min(point[axis] for point in used) for axis in range(3)]
            high = [max(point[axis] for point in used) for axis in range(3)]
            dimensions = [b-a for a, b in zip(low, high)]
            if any(abs(a-b) > tolerance for a, b in zip(dimensions, expected)):
                errors.append(label + ': dimensions differ from contract')
            if pivot == 'bottom-center' and max(abs(low[1]), abs((low[0]+high[0])/2), abs((low[2]+high[2])/2)) > pivot_tolerance:
                errors.append(label + ': bottom-centred pivot drift')
            normals = vectors(lod['normals'], 3, len(positions))
            if any(abs(math.sqrt(sum(v*v for v in row))-1) > .02 for row in normals):
                errors.append(label + ': normals are not unit length')
            uv_names = sorted(lod['uvs'])
            if not uv_names:
                errors.append(label + ': no UV channel')
            for values in lod['uvs'].values(): vectors(values, 2, len(positions))
            tangents = lod.get('tangents')
            if tangents is not None:
                tangent_values = vectors(tangents, 4, len(positions))
                if any(abs(math.sqrt(sum(v*v for v in row[:3]))-1) > .02 or row[3] not in (-1,1) for row in tangent_values):
                    errors.append(label + ': invalid tangent basis')
            surface_ids = lod['surfaceIds']
            if not surface_ids or any(not isinstance(value, str) or not value for value in surface_ids) or len(set(surface_ids)) != len(surface_ids):
                raise ValueError(label + ': semantic surface IDs must be unique nonempty strings')
            if not isinstance(lod['appearanceKey'], str) or not lod['appearanceKey']:
                raise ValueError(label + ': appearanceKey must be nonempty')
            contract = (uv_names, tangents is not None, sorted(surface_ids), lod['appearanceKey'])
            if baseline is None: baseline = contract
            elif baseline != contract: errors.append(label + ': UV/tangent/semantic/appearance contract changed')
            triangle_count = len(indices)//3
            if previous_count is not None and triangle_count > previous_count:
                errors.append(label + ': coarser LOD increased triangle count')
            previous_count = triangle_count
            results.append(dict(asset=identity, level=lod['level'], triangles=triangle_count, bounds=[low,high], dimensions=dimensions))
    if not results:
        raise ValueError('At least one asset is required')
    return dict(passed=not errors, errors=errors, lods=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('variants', 'audit')); parser.add_argument('input')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as stream: data = json.load(stream)
        if args.mode == 'variants':
            if len(set(data['ids'])) != len(data['ids']): raise ValueError('Placement IDs must be unique')
            result = {'variants': [variant(data['seed'], identity, data.get('ranges', {}), data.get('choices', {})) for identity in data['ids']]}
        else: result = audit(data)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result.get('passed', True) else 1
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr); return 2


if __name__ == '__main__': sys.exit(main())
