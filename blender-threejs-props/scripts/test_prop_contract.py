import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from prop_contract import audit, variant


def fixture():
    box = [[x,y,z] for y in (0,1) for z in (-.5,.5) for x in (-1,1)]
    high = [0,2,1,1,2,3,4,5,6,5,7,6,0,1,4,1,5,4,2,6,3,3,6,7,0,4,2,2,4,6,1,3,5,3,7,5]
    octa = [[-1,.5,0],[1,.5,0],[0,0,0],[0,1,0],[0,.5,-.5],[0,.5,.5]]
    low = [0,2,4,4,2,1,1,2,5,5,2,0,0,4,3,4,1,3,1,5,3,5,0,3]
    lods = []
    for level, positions, indices in [(0,box,high),(1,octa,low)]:
        lods.append(dict(level=level, positions=positions, indices=indices,
                         normals=[[0,1,0] for _ in positions], uvs={'uv0': [[0,0] for _ in positions]},
                         tangents=[[1,0,0,1] for _ in positions], surfaceIds=['body','label'], appearanceKey='red-v1'))
    return {'units':'m','assets':[dict(id='crate', dimensions=[2,1,1], requiredLods=[0,1], lods=lods)]}


class PropContractTests(unittest.TestCase):
    def test_stable_variants_survive_reorder_insertion_and_new_channels(self):
        ranges = {'width':[.96,1.04]}; choices = {'art':['A','B','C']}
        before = {i:variant('yard',i,ranges,choices) for i in ['a','b']}
        after = {i:variant('yard',i,ranges,choices) for i in ['b','new','a']}
        self.assertEqual(before['a'], after['a']); self.assertEqual(before['b'], after['b'])
        added = variant('yard','a',dict(ranges, dent=[0,.02]),choices)
        self.assertEqual(before['a']['values']['width'], added['values']['width'])
        self.assertEqual(before['a']['values']['art'], added['values']['art'])
        self.assertNotEqual(before['a'], variant('other','a',ranges,choices))

    def test_variant_parameters_respect_physical_limits(self):
        for i in range(200):
            result = variant('yard',str(i),{'width':[.96,1.04]}, {'art':['A','B']})['values']
            self.assertGreaterEqual(result['width'], .96); self.assertLessEqual(result['width'], 1.04)
            self.assertIn(result['art'], ['A','B'])

    def test_real_referenced_bounds_and_coarser_topology_pass(self):
        result = audit(fixture())
        self.assertTrue(result['passed']); self.assertEqual([x['triangles'] for x in result['lods']], [12,8])
        self.assertEqual(result['lods'][1]['dimensions'], [2,1,1])

    def test_pivot_drift_and_unused_extreme_vertices_do_not_pass(self):
        data = fixture(); lod = data['assets'][0]['lods'][1]
        lod['matrix'] = [1,0,0,0,0,1,0,0,0,0,1,0,0,.1,0,1]
        self.assertTrue(any('pivot' in e for e in audit(data)['errors']))
        data = fixture(); lod = data['assets'][0]['lods'][1]
        lod['positions'][0][0] = -.5
        lod['positions'].append([-1,.5,0]); lod['normals'].append([0,1,0]); lod['uvs']['uv0'].append([0,0]); lod['tangents'].append([1,0,0,1])
        self.assertTrue(any('dimensions' in e for e in audit(data)['errors']))

    def test_missing_uv_tangents_or_changed_artwork_fail(self):
        for change in ('uv','tangent','art','semantic'):
            data = fixture(); lod = data['assets'][0]['lods'][1]
            if change == 'uv': lod['uvs'] = {}
            elif change == 'tangent': del lod['tangents']
            elif change == 'art': lod['appearanceKey'] = 'unrelated-label'
            else: lod['surfaceIds'] = ['body']
            self.assertFalse(audit(data)['passed'], change)

    def test_invalid_units_and_index_data_are_rejected(self):
        data = fixture(); data['units'] = 'cm'
        with self.assertRaises(ValueError): audit(data)
        data = fixture(); data['assets'][0]['lods'][1]['indices'][0] = 999
        with self.assertRaises(ValueError): audit(data)
        with self.assertRaises(ValueError): variant('x','a',{'size':[1,0]}, {})

    def test_cli_export_facts_and_variant_json(self):
        here=Path(__file__).parent
        with tempfile.TemporaryDirectory(dir=here) as directory:
            path=Path(directory)/'facts.json'; path.write_text(json.dumps(fixture()))
            command=[sys.executable,str(here/'prop_contract.py')]
            result=subprocess.run(command+['audit',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr); self.assertTrue(json.loads(result.stdout)['passed'])
            data=fixture(); data['assets'][0]['dimensions']=[2,2,1]; path.write_text(json.dumps(data))
            result=subprocess.run(command+['audit',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,1); self.assertFalse(json.loads(result.stdout)['passed'])
            data={'seed':'yard','ids':['a'],'ranges':{'width':[.96,1.04]},'choices':{'art':['A','B','C']}}
            path.write_text(json.dumps(data))
            result=subprocess.run(command+['variants',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['variants'][0],variant('yard','a',data['ranges'],data['choices']))
            path.write_text('{}')
            result=subprocess.run(command+['audit',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2); self.assertIn('error',json.loads(result.stderr))


if __name__ == '__main__': unittest.main()
