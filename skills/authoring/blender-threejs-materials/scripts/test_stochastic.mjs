import assert from 'node:assert/strict';
import {PRESETS,hash,patch,transformSlope,sample} from './stochastic.mjs';
const channels={color:([u,v])=>[.4+.12*Math.sin(u*6),.3+.07*Math.cos(v*5),.2],orm:([u,v])=>[.85,.7+.1*Math.cos(u+v),0],normal:()=>[.65,.45,.965]};
let probes=0,maxJoinDelta=0,maxGradientError=0;
for(const preset of Object.values(PRESETS))for(let a=-5;a<=5;a++)for(let b=-5;b<=5;b++) {
  const size=preset.settings[0],eps=1e-7;
  for(const [gu,gv] of [[a,b+.37],[a+.37,b],[a+.43,b+.57]]) {
    const point=[(gu+.5*gv)*size,.8660254037844386*gv*size];
    const x=sample([point[0]-eps,point[1]],channels,preset),y=sample([point[0]+eps,point[1]],channels,preset);
    for(const role of ['color','orm','normal'])for(let k=0;k<3;k++)maxJoinDelta=Math.max(maxJoinDelta,Math.abs(x[role][k]-y[role][k]));
    probes++;
  }
}
assert.ok(maxJoinDelta<1e-4,`discontinuous cell boundary: ${maxJoinDelta}`);
const H=(u,v)=>.03*Math.sin(2*u)+.05*Math.cos(3*v),eps=1e-5;
for(let q=0;q<4;q++)for(const frequency of [.7,1,1.3])for(const signs of [[-1,-1],[-1,1],[1,1]]) {
  const r={c:[1,0,-1,0][q],s:[0,1,0,-1][q],frequency};
  const uv=[.23,-.37];
  const map=([u,v])=>[frequency*(r.c*u-r.s*v),signs[0]*frequency*(r.s*u+r.c*v)];
  const z=map(uv),grad=[(H(z[0]+eps,z[1])-H(z[0]-eps,z[1]))/(2*eps),(H(z[0],z[1]+eps)-H(z[0],z[1]-eps))/(2*eps)];
  const actual=transformSlope(grad,r,signs);
  const expected=[(H(...map([uv[0]+eps,uv[1]]))-H(...map([uv[0]-eps,uv[1]])))/(2*eps), signs[1]*(H(...map([uv[0],uv[1]+eps]))-H(...map([uv[0],uv[1]-eps])))/(2*eps)];
  for(let k=0;k<2;k++)maxGradientError=Math.max(maxGradientError,Math.abs(actual[k]-expected[k]));
}
assert.ok(maxGradientError<1e-8);
for(let i=-20;i<20;i++){
  assert.deepEqual(hash([i,-i]),hash([i+251,251-i]));
  for(const r of patch([i*.12,-i*.32],PRESETS.courses).regions){assert.equal(r.frequency,1);assert.equal(r.quarter%2,0);}
}
console.log(JSON.stringify({passed:true,boundaryProbes:probes,maxJoinDelta,maxGradientError,normalBasisCases:36}));
