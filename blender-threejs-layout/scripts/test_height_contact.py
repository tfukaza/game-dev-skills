import math
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from height_contact import Profile, contact_report


class HeightContactTests(unittest.TestCase):
    def test_continuing_slope_does_not_stop_at_every_anchor(self):
        profile = Profile([[0, 0], [4, 1], [8, 2]])
        self.assertAlmostEqual(profile.evaluate(4)[1], .25)
        for x in (0, 1, 3.7, 4, 6.2, 8):
            self.assertAlmostEqual(profile.evaluate(x)[0], x / 4)

    def test_flat_junctions_and_extrema_do_not_overshoot(self):
        anchors = [[0, 0], [2, 0], [5, 1], [7, 1], [8, -.5]]
        profile = Profile(anchors, flat_ends=True)
        for x in (0, 2, 5, 7, 8): self.assertAlmostEqual(profile.evaluate(x)[1], 0)
        for (a, ya), (b, yb) in zip(anchors, anchors[1:]):
            for i in range(101):
                y = profile.evaluate(a + (b-a)*i/100)[0]
                self.assertGreaterEqual(y, min(ya, yb)-1e-12)
                self.assertLessEqual(y, max(ya, yb)+1e-12)

    def test_derivative_and_station_normals_match_the_surface(self):
        profile = Profile([[0, 0], [2, .3], [7, 3]], flat_ends=True)
        rows = profile.sample(.45, [1.125, 4.75], axis='z')
        self.assertIn(1.125, [row['station'] for row in rows])
        self.assertIn(4.75, [row['station'] for row in rows])
        self.assertLessEqual(max(b['station']-a['station'] for a, b in zip(rows, rows[1:])), .45+1e-12)
        for row in rows[1:-1]:
            x = row['station']; epsilon = 1e-6
            difference = (profile.evaluate(x+epsilon)[0]-profile.evaluate(x-epsilon)[0])/(2*epsilon)
            self.assertAlmostEqual(row['derivative'], difference, places=5)
            self.assertAlmostEqual(sum(v*v for v in row['normal']), 1)
            self.assertAlmostEqual(row['normal'][1]*row['derivative']+row['normal'][2], 0)

    def test_contacts_use_actual_upward_triangles(self):
        triangles = [dict(id='slope', vertices=[[0,0,0],[0,.4,4],[4,1.2,4]]),
                     dict(id='slope', vertices=[[0,0,0],[4,1.2,4],[4,.8,0]]),
                     dict(id='underside', vertices=[[0,2,0],[4,2,0],[0,2,4]])]
        points = [dict(id='seated', position=[1,.3,1]), dict(id='float', position=[1,.5,1]),
                  dict(id='buried', position=[1,.2,1]), dict(id='outside', position=[8,0,8])]
        report = contact_report(points, triangles)
        self.assertEqual([row['state'] for row in report['points']], ['contact','floating','buried','missing'])
        self.assertAlmostEqual(report['points'][1]['gap'], .2)
        self.assertEqual(report['points'][0]['receiver'], 'slope')
        self.assertFalse(report['passed'])

    def test_invalid_inputs_fail_instead_of_silently_flattening(self):
        for anchors in ([[0,0],[0,1]], [[0,0],[1,math.nan]], [[0,0]]):
            with self.assertRaises(ValueError): Profile(anchors)
        with self.assertRaises(ValueError): Profile([[0,0],[1,1]]).sample(0)
        with self.assertRaises(ValueError): Profile([[0,0],[1,1]]).sample(.5, [2])
        with self.assertRaises(ValueError): contact_report([], [])

    def test_cli_json_and_contact_failure_exit(self):
        here=Path(__file__).parent
        data={'profile':{'anchors':[[0,0],[2,1]],'flatEnds':True,'maxStep':1}}
        with tempfile.TemporaryDirectory(dir=here) as directory:
            path=Path(directory)/'input.json'; path.write_text(json.dumps(data))
            command=[sys.executable,str(here/'height_contact.py'),str(path)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            rows=json.loads(result.stdout)['profile']
            self.assertEqual([(r['station'],r['height'],r['derivative']) for r in rows],[(0,0,0),(1,.5,.75),(2,1,0)])
            data['contact']={'points':[{'id':'unsupported','position':[4,0,4]}],'triangles':[]}
            path.write_text(json.dumps(data))
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,1); self.assertEqual(json.loads(result.stdout)['contact']['points'][0]['state'],'missing')
            path.write_text('{}')
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,2); self.assertIn('error',json.loads(result.stderr))


if __name__ == '__main__': unittest.main()
