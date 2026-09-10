"""Focused CPU checks; run with Blender's bundled Python (NumPy included)."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
import subprocess
import sys

import numpy as np

from denoise_lightmaps import _prefilter_fireflies, denoise_with_guides, rasterize_guides


def plane(size=64):
    y, x = np.mgrid[:size, :size]
    position = np.stack((x * .05, y * .05, np.zeros_like(x)), axis=-1).astype(np.float32)
    normal = np.zeros_like(position); normal[:, :, 2] = 1
    return {'position': position, 'normal': normal, 'chart_id': np.zeros((size, size), np.int32),
            'texel_size': np.full((size, size), .05, np.float32), 'coverage': np.ones((size, size), bool)}


def donor(path, uv_channel=2, edit=None, normal=(0, 0, 1)):
    document = {'asset': {'version': '2.0'}, 'scenes': [{'nodes': [0]}], 'scene': 0,
                'nodes': [{'translation': [5, 3, -2], 'scale': [2, 3, 1], 'mesh': 0}],
                'meshes': [{'primitives': []}], 'buffers': [], 'bufferViews': [], 'accessors': []}
    binary = bytearray()

    def add(values, kind, component=5126):
        values = np.asarray(values, dtype='<f4' if component == 5126 else '<u2')
        binary.extend(b'\0' * (-len(binary) % 4))
        view = len(document['bufferViews'])
        document['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': values.nbytes})
        binary.extend(values.tobytes())
        index = len(document['accessors'])
        document['accessors'].append({'bufferView': view, 'componentType': component, 'count': len(values), 'type': kind})
        return index

    p = add([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], 'VEC3')
    n = add([normal] * 4, 'VEC3')
    uv = add([[0, 1], [1, 1], [1, 0], [0, 0]], 'VEC2')
    # Primitive/material boundaries must not split a physically shared UV chart.
    for indices in ([0, 1, 2], [0, 2, 3]):
        document['meshes'][0]['primitives'].append({'attributes': {'POSITION': p, 'NORMAL': n, f'TEXCOORD_{uv_channel}': uv},
                                                  'indices': add(indices, 'SCALAR', 5123)})
    document['buffers'] = [{'byteLength': len(binary)}]
    if edit:
        edit(document)
    binary.extend(b'\0' * (-len(binary) % 4))
    encoded = json.dumps(document).encode(); encoded += b' ' * (-len(encoded) % 4)
    path.write_bytes(struct.pack('<IIIII', 0x46546C67, 2, 28 + len(encoded) + len(binary), len(encoded), 0x4E4F534A)
                     + encoded + struct.pack('<II', len(binary), 0x004E4942) + binary)


class DenoiseTests(unittest.TestCase):
    def test_configurable_uv_channel_orientation_and_inverse_transpose_normal(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'donor.glb'
            donor(path, uv_channel=1, normal=(2**-.5, 2**-.5, 0))
            guides = rasterize_guides(path, 8, uv_channel=1, flip_v=False)
            np.testing.assert_allclose(guides['position'][0, 0], [5.125, 5.8125, -2])
            expected = np.array([1/2, 1/3, 0]); expected /= np.linalg.norm(expected)
            np.testing.assert_allclose(guides['normal'][0, 0], expected, atol=1e-7)
            with self.assertRaisesRegex(ValueError, 'TEXCOORD_2'):
                rasterize_guides(path, 8)

    def test_unsupported_donors_fail_explicitly(self):
        cases = [
            lambda d: d.update(animations=[{}]),
            lambda d: d.update(skins=[{}]),
            lambda d: d.update(extensionsRequired=['EXT_meshopt_compression']),
            lambda d: d['buffers'][0].update(uri='external.bin'),
            lambda d: d['meshes'][0]['primitives'][0].update(targets=[{}]),
            lambda d: d['meshes'][0]['primitives'][0].update(extensions={'KHR_draco_mesh_compression': {}}),
            lambda d: d['nodes'][0].update(extensions={'EXT_mesh_gpu_instancing': {'attributes': {}}}),
            lambda d: d['accessors'][0].update(sparse={'count': 1}),
            lambda d: d['accessors'][0].update(sparse={}),
            lambda d: d['accessors'][0].update(extensions={'UNKNOWN_attribute': {}}),
            lambda d: d['nodes'][0].update(extensions={'UNKNOWN_node_transform': {}}),
            lambda d: d['meshes'][0].update(extensions={'UNKNOWN_mesh': {}}),
            lambda d: d['meshes'][0]['primitives'][0].update(extensions={'UNKNOWN_primitive': {}}),
            lambda d: d['accessors'][d['meshes'][0]['primitives'][0]['indices']].update(type='VEC3', count=1),
            lambda d: d['accessors'][0].update(count=999999),
            lambda d: d['nodes'][0].update(scale=[0, 1, 1]),
            lambda d: d['nodes'][0].update(children=[0]),
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'donor.glb'
            for edit in cases:
                donor(path, edit=edit)
                with self.subTest(edit=edit), self.assertRaises(ValueError):
                    rasterize_guides(path, 8)

    def test_mirrored_mesh_without_normals_matches_authored_normal_frame(self):
        def reflected(document, remove_normals=False):
            document['nodes'][0]['scale'] = [-2, 3, 1]
            if remove_normals:
                for primitive in document['meshes'][0]['primitives']:
                    primitive['attributes'].pop('NORMAL')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'donor.glb'
            donor(path, edit=lambda d: reflected(d))
            authored = rasterize_guides(path, 8)
            donor(path, edit=lambda d: reflected(d, True))
            generated = rasterize_guides(path, 8)
        np.testing.assert_array_equal(generated['position'], authored['position'])
        np.testing.assert_allclose(generated['normal'], authored['normal'], atol=1e-7)
        np.testing.assert_allclose(generated['normal'][0, 0], [0, 0, 1])

    def test_cli_preserves_raw_and_uses_explicit_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            guides = plane(16)
            rng = np.random.default_rng(17)
            values = np.ones((16, 16, 4), np.float32)
            values[:, :, :3] = .4 + rng.normal(0, .04, (16, 16, 3))
            values[:, :, 3] = 0  # Fully covered geometry may have zero AO.
            coverage = np.ones((16, 16), bool); coverage[5:7] = False
            np.save(folder/'raw.npy', values); np.save(folder/'coverage.npy', coverage)
            np.savez_compressed(folder/'guides.npz', **guides)
            before = (folder/'raw.npy').read_bytes()
            args = [sys.executable, str(Path(__file__).with_name('denoise_lightmaps.py')),
                    str(folder/'raw.npy'), str(folder/'filtered.npy'), '--guides', str(folder/'guides.npz'),
                    '--coverage', str(folder/'coverage.npy'), '--save-guides', str(folder/'used.npz')]
            completed = subprocess.run(args, check=True, capture_output=True, text=True)
            self.assertTrue(json.loads(completed.stdout)['alphaUnchanged'])
            result = np.load(folder/'filtered.npy')
            np.testing.assert_array_equal(result[~coverage], values[~coverage])
            np.testing.assert_array_equal(result[:, :, 3], values[:, :, 3])
            self.assertLess(np.std(result[coverage, :3]), np.std(values[coverage, :3]))
            self.assertEqual((folder/'raw.npy').read_bytes(), before)
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)

    def test_sparse_external_chart_ids_are_compacted_without_mutating_guides(self):
        guides = plane(); guides['chart_id'][:] = 2**30
        values = np.full((64, 64, 4), .5, np.float32)
        result = denoise_with_guides(values, guides)
        np.testing.assert_allclose(result, values, atol=1e-7)
        self.assertTrue((guides['chart_id'] == 2**30).all())

    def test_isolated_warm_fireflies_and_pairs_are_removed_without_touching_gradient(self):
        guides = plane()
        y, x = np.mgrid[:64, :64]
        rgb = np.stack((.12 + x * .002, .10 + y * .001, .08 + (x + y) * .0005), axis=-1).astype(np.float32)
        before = rgb.copy()
        spike = np.array([.8, .32, .06], np.float32)
        rgb[16, 16] += spike
        rgb[32, 32:34] += spike
        result = _prefilter_fireflies(rgb, guides, guides['coverage'], row_chunk=17)
        np.testing.assert_allclose(result[16, 16], before[16, 16], atol=.002)
        np.testing.assert_allclose(result[32, 32:34], before[32, 32:34], atol=.002)
        unchanged = np.ones((64, 64), bool); unchanged[16, 16] = False; unchanged[32, 32:34] = False
        np.testing.assert_array_equal(result[unchanged], before[unchanged])
        np.testing.assert_allclose(rgb[16, 16], before[16, 16] + spike)
        rgba = np.concatenate((rgb, np.full((64, 64, 1), .37, np.float32)), axis=2)
        filtered = denoise_with_guides(rgba, guides)
        np.testing.assert_allclose(filtered[16, 16, :3], before[16, 16], atol=.004)
        np.testing.assert_allclose(filtered[32, 32:34, :3], before[32, 32:34], atol=.004)
        np.testing.assert_array_equal(filtered[:, :, 3], rgba[:, :, 3])

    def test_firefly_prefilter_preserves_contacts_thin_light_strips_and_smooth_maxima(self):
        guides = plane()
        y, x = np.mgrid[:64, :64]
        for luminance in (np.where(x < 32, .08, .8),
                          np.where(x == 32, .8, .08),
                          .1 + .7 * np.exp(-((x - 32) ** 2 + (y - 32) ** 2) / 32)):
            rgb = np.repeat(luminance[:, :, None], 3, axis=2).astype(np.float32)
            result = _prefilter_fireflies(rgb, guides, guides['coverage'])
            np.testing.assert_array_equal(result, rgb)

    def test_firefly_statistics_do_not_cross_chart_normal_or_distance_boundaries(self):
        rgb = np.full((64, 64, 3), .1, np.float32); rgb[32, 32] = .9
        for guard in ('chart_id', 'normal', 'position', 'coverage'):
            guides = plane()
            if guard == 'chart_id':
                guides[guard][32, 32] = 1
            elif guard == 'normal':
                guides[guard][32, 32] = [0, 1, 0]
            elif guard == 'position':
                guides[guard][32, 32, 2] = 100
            else:
                guides[guard][31:34, 31:34] = False
            result = _prefilter_fireflies(rgb, guides, guides['coverage'])
            np.testing.assert_array_equal(result, rgb, err_msg=guard)

    def test_raster_reflects_gltf_v_and_applies_node_transform(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'donor.glb'; donor(path)
            guides = rasterize_guides(path, 8)
        self.assertTrue(guides['coverage'].all())
        self.assertEqual(len(np.unique(guides['chart_id'])), 1)
        np.testing.assert_allclose(guides['position'][0, 0], [5.125, 3.1875, -2])
        np.testing.assert_allclose(guides['position'][7, 7], [6.875, 5.8125, -2])
        np.testing.assert_allclose(guides['normal'][3, 4], [0, 0, 1])
        np.testing.assert_allclose(guides['texel_size'], 3 / 8)

    def test_noisy_constant_plane_smooths_without_changing_ao_or_input(self):
        random = np.random.default_rng(1729)
        values = np.empty((64, 64, 4), np.float32)
        values[:, :, :3] = [.6, .5, .4] + random.normal(0, .06, (64, 64, 3))
        values[:, :, 3] = random.uniform(0, 1, (64, 64))
        before = values.copy()
        result = denoise_with_guides(values, plane())
        self.assertLess(np.std(result[:, :, :3] - [.6, .5, .4]), np.std(values[:, :, :3] - [.6, .5, .4]) * .6)
        np.testing.assert_allclose(result[:, :, :3].mean(axis=(0, 1)), [.6, .5, .4], atol=.006)
        np.testing.assert_array_equal(result[:, :, 3], before[:, :, 3])
        np.testing.assert_array_equal(values, before)
        self.assertTrue(np.isfinite(result).all())

    def test_adjacent_unrelated_charts_never_mix_even_without_luminance_guard(self):
        guides = plane(); guides['chart_id'][:, 32:] = 1
        values = np.ones((64, 64, 4), np.float32)
        values[:, :32, :3] = [.9, .1, .1]; values[:, 32:, :3] = [.1, .2, .9]
        result = denoise_with_guides(values, guides, noise_sigma=10)
        np.testing.assert_allclose(result, values, atol=5e-7)

    def test_world_distance_and_normal_guards_protect_folded_connected_chart(self):
        values = np.ones((64, 64, 4), np.float32); values[:, :32, :3] = .1; values[:, 32:, :3] = .9
        for guard in ('position', 'normal'):
            guides = plane()
            if guard == 'position':
                guides['position'][:, 32:, 2] += 100
            else:
                guides['normal'][:, 32:] = [0, 1, 0]
            result = denoise_with_guides(values, guides, noise_sigma=10)
            np.testing.assert_allclose(result, values, atol=2e-7, err_msg=guard)

    def test_sharp_lighting_contact_stays_sharp_while_each_side_smooths(self):
        random = np.random.default_rng(810)
        values = np.ones((64, 64, 4), np.float32)
        values[:, :32, :3] = .08; values[:, 32:, :3] = .8
        target = values.copy()
        values[:, :, :3] += random.normal(0, .025, (64, 64, 3))
        result = denoise_with_guides(values, plane(), noise_sigma=.025)
        self.assertLess(np.mean(result[:, 31, :3]), .10)
        self.assertGreater(np.mean(result[:, 32, :3]), .78)
        self.assertLess(np.std(result[:, :, :3] - target[:, :, :3]), np.std(values[:, :, :3] - target[:, :, :3]) * .6)

    def test_majority_black_atlas_cannot_hide_noise_in_illuminated_chart(self):
        random = np.random.default_rng(192)
        values = np.zeros((64, 64, 4), np.float32)
        values[:, :, 3] = .4
        values[48:, :, :3] = .5 + random.normal(0, .06, (16, 64, 3))
        for separate_chart in (False, True):
            guides = plane()
            if separate_chart:
                guides['chart_id'][48:] = 1
            result = denoise_with_guides(values, guides)
            self.assertLess(np.std(result[48:, :, :3] - .5), np.std(values[48:, :, :3] - .5) * .6)
            np.testing.assert_array_equal(result[:44, :, :3], values[:44, :, :3])
            self.assertLess(float(result[47, :, :3].mean()), .01)
            self.assertGreater(float(result[48, :, :3].mean()), .48)
            np.testing.assert_array_equal(result[:, :, 3], values[:, :, 3])

    def test_invalid_coverage_is_untouched_and_nonfinite_input_is_rejected(self):
        guides = plane(); guides['coverage'][20:24, :] = False
        values = np.full((64, 64, 4), .5, np.float32); values[20:24, :, :3] = 40
        result = denoise_with_guides(values, guides, noise_sigma=100, row_chunk=17)
        np.testing.assert_allclose(result, values, atol=1e-7)
        values[0, 0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, 'finite'):
            denoise_with_guides(values, guides)


if __name__ == '__main__':
    unittest.main()
