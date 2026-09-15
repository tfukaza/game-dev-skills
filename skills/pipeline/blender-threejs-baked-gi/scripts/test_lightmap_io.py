"""CPU checks for padding/encoding; no Blender, file writes, or rendering."""
import unittest
import numpy as np
from lightmap_io import pad_empty, choose_encoding_range, encode_rgb8


class LightmapIOTests(unittest.TestCase):
    def test_padding_preserves_valid_black_and_independent_zero_ao(self):
        values = np.zeros((5, 7, 4), np.float32)
        coverage = np.zeros((5, 7), bool)
        values[2, 1] = [.8, .4, .2, 0]
        values[2, 5] = [0, 0, 0, .7]
        coverage[2, [1, 5]] = True
        before = values.copy()
        result, expanded = pad_empty(values, coverage, 3)
        np.testing.assert_array_equal(result[coverage], before[coverage])
        np.testing.assert_array_equal(values, before)
        self.assertEqual(int(coverage.sum()), 2)
        self.assertGreater(int(expanded.sum()), 2)
        np.testing.assert_array_equal(result[2, 0], values[2, 1])

    def test_padding_never_wraps_or_changes_unreached_pixels(self):
        values = np.zeros((5, 5, 4), np.float32); values[0, 0] = [1, .2, .1, .3]
        coverage = np.zeros((5, 5), bool); coverage[0, 0] = True
        result, expanded = pad_empty(values, coverage, 1)
        self.assertEqual(int(expanded.sum()), 4)
        np.testing.assert_array_equal(result[4], values[4])
        np.testing.assert_array_equal(result[:, 4], values[:, 4])
        np.testing.assert_array_equal(pad_empty(values, coverage, 0)[0], values)
        with self.assertRaises(ValueError):
            pad_empty(values, values[:, :, 3], 1)

    def test_range_is_shared_preserves_hdr_and_rejects_silent_clipping(self):
        arrays = [np.array([[.003, .125, .5]]), np.array([[1, 2, 8]])]
        scale = choose_encoding_range(arrays)
        self.assertEqual(scale, 16)
        self.assertGreaterEqual(scale, 8 * 1.2)
        encoded = encode_rgb8(np.concatenate(arrays), scale).astype(np.float64) / 255
        decoded = np.where(encoded <= .04045, encoded / 12.92, ((encoded + .055) / 1.055) ** 2.4) * scale
        np.testing.assert_allclose(decoded, np.concatenate(arrays), atol=.06)
        self.assertGreater(decoded[-1, -1], 7.9)
        with self.assertRaises(ValueError):
            encode_rgb8(arrays[-1], 4)
        with self.assertRaises(ValueError):
            choose_encoding_range([np.array([[-1, .1, .2]])])


if __name__ == '__main__':
    unittest.main()
