/** Dependency-free CPU reference plus WebGL2 GLSL. No application mutation. */
export const PRESETS = {
  natural: {settings:[.62,0,.035,.025],blend:[5,.45]},
  courses: {settings:[.90,1,0,.020],blend:[7,.55]}
};
const mod=(a,b)=>a-Math.floor(a/b)*b;
export function hash([x,y]) {
  x=mod(x,251);y=mod(y,251);
  return [[37,17,19],[11,53,67],[71,29,131],[43,101,211]].map(([a,b,s])=>{
    let h=mod(x*a+y*b+s,251);h=mod(mod(h*h,251)*h,251);return(h+.5)/251;
  });
}
export function patch(uv,preset=PRESETS.natural) {
  const [size,half,jitter,gain]=preset.settings;
  const g=[(uv[0]-.5773502691896258*uv[1])/size,1.1547005383792517*uv[1]/size];
  const b=g.map(Math.floor),f=g.map((v,i)=>v-b[i]);
  const upper=f[0]+f[1]>1;
  const cells=upper?[[b[0]+1,b[1]+1],[b[0],b[1]+1],[b[0]+1,b[1]]]:[b,[b[0]+1,b[1]],[b[0],b[1]+1]];
  const weights=upper?[f[0]+f[1]-1,1-f[0],1-f[1]]:[1-f[0]-f[1],f[0],f[1]];
  const regions=cells.map(cell=>{
    const h=hash(cell),q=Math.floor(h[2]*(half?2:4))*(half?2:1);
    const c=[1,0,-1,0][q],s=[0,1,0,-1][q],frequency=1+(h[3]*2-1)*jitter;
    const anchor=[(cell[0]+.5*cell[1])*size,.8660254037844386*cell[1]*size];
    const u=uv[0]-anchor[0],v=uv[1]-anchor[1];
    return {uv:[frequency*(c*u-s*v)+anchor[0]+h[0],frequency*(s*u+c*v)+anchor[1]+h[1]],
      c,s,frequency,quarter:q,brightness:1+(mod(h[3]*17,1)*2-1)*gain};
  });return {regions,weights};
}
export function transformSlope([x,y],{c,s,frequency},signs=[-1,-1]) {
  y*=signs[0];return [frequency*(c*x+s*y),frequency*(-s*x+c*y)*signs[1]];
}
export function sample(uv,textures,preset=PRESETS.natural,normalSigns=[-1,-1]) {
  const p=patch(uv,preset),colors=p.regions.map(r=>textures.color(r.uv));
  let w=p.weights.map((v,i)=>Math.max(v,0)**preset.blend[0]*(1-preset.blend[1]+preset.blend[1]*Math.max(colors[i].reduce((a,c,j)=>a+c*[.2126,.7152,.0722][j],0),.03)));
  const sum=w.reduce((a,b)=>a+b,0);w=w.map(v=>v/Math.max(sum,1e-8));
  const color=[0,0,0],orm=[0,0,0],slope=[0,0];
  p.regions.forEach((r,i)=>{
    const o=textures.orm(r.uv),n=textures.normal(r.uv).map(v=>v*2-1);
    const t=transformSlope([n[0]/Math.max(n[2],.05),n[1]/Math.max(n[2],.05)],r,normalSigns);
    for(let k=0;k<3;k++){color[k]+=colors[i][k]*r.brightness*w[i];orm[k]+=o[k]*w[i];}
    for(let k=0;k<2;k++)slope[k]+=t[k]*w[i];
  });
  const length=Math.hypot(...slope,1);
  return {color,orm,normal:[slope[0]/length*.5+.5,slope[1]/length*.5+.5,.5/length+.5]};
}

export const GLSL = /* glsl */`
#ifndef SURFACE_STOCHASTIC
#define SURFACE_STOCHASTIC
struct SurfaceStochasticPatch {
	vec2 uv0; vec2 uv1; vec2 uv2;
	mat2 j0; mat2 j1; mat2 j2;
	vec2 dx; vec2 dy;
	vec3 weights;
	vec3 brightness;
};

// Integer-valued float arithmetic stays below 65536: no sin hash whose tiny
// cross-platform rounding differences become entirely different cell seeds.
// Cubing modulo prime 251 permutes all residues (gcd(3,250)=1). The 251-cell
// world-space period depends on cell size and UV density; inspect it at the
// intended scene scale rather than assuming it is beyond the visible area.
vec4 surfaceStochasticHash(vec2 cell) {
	vec2 c = mod(cell, 251.0);
	vec4 h = mod(vec4(
		c.x * 37.0 + c.y * 17.0 + 19.0,
		c.x * 11.0 + c.y * 53.0 + 67.0,
		c.x * 71.0 + c.y * 29.0 + 131.0,
		c.x * 43.0 + c.y * 101.0 + 211.0
	), 251.0);
	h = mod(mod(h * h, 251.0) * h, 251.0);
	return (h + 0.5) / 251.0;
}

void surfaceStochasticRegion(vec2 uv, vec2 cell, vec4 settings,
	out vec2 sampleUv, out mat2 jacobian, out float brightness) {
	vec4 h = surfaceStochasticHash(cell);
	float quarter = settings.y > 0.5 ? floor(h.z * 2.0) * 2.0 : floor(h.z * 4.0);
	float c = quarter < 0.5 ? 1.0 : (quarter < 1.5 ? 0.0 : (quarter < 2.5 ? -1.0 : 0.0));
	float s = quarter < 0.5 ? 0.0 : (quarter < 1.5 ? 1.0 : (quarter < 2.5 ? 0.0 : -1.0));
	float frequency = 1.0 + (h.w * 2.0 - 1.0) * settings.z;
	jacobian = mat2(c, s, -s, c) * frequency;
	vec2 anchor = vec2(cell.x + 0.5 * cell.y, 0.8660254037844386 * cell.y) * settings.x;
	sampleUv = jacobian * (uv - anchor) + anchor + h.xy;
	brightness = 1.0 + (fract(h.w * 17.0) * 2.0 - 1.0) * settings.w;
}

SurfaceStochasticPatch surfaceStochasticPatch(vec2 uv, vec4 settings) {
	SurfaceStochasticPatch p;
	p.dx = dFdx(uv); p.dy = dFdy(uv);
	vec2 grid = vec2(uv.x - 0.5773502691896258 * uv.y, 1.1547005383792517 * uv.y) / settings.x;
	vec2 base = floor(grid), f = fract(grid);
	vec2 a, b, c;
	if (f.x + f.y <= 1.0) {
		a = base; b = base + vec2(1.0, 0.0); c = base + vec2(0.0, 1.0);
		p.weights = vec3(1.0 - f.x - f.y, f.x, f.y);
	} else {
		a = base + vec2(1.0); b = base + vec2(0.0, 1.0); c = base + vec2(1.0, 0.0);
		p.weights = vec3(f.x + f.y - 1.0, 1.0 - f.x, 1.0 - f.y);
	}
	surfaceStochasticRegion(uv, a, settings, p.uv0, p.j0, p.brightness.x);
	surfaceStochasticRegion(uv, b, settings, p.uv1, p.j1, p.brightness.y);
	surfaceStochasticRegion(uv, c, settings, p.uv2, p.j2, p.brightness.z);
	return p;
}

vec4 surfaceStochasticColor(sampler2D tex, inout SurfaceStochasticPatch p, vec2 blend) {
	vec4 a = textureGrad(tex, p.uv0, p.j0 * p.dx, p.j0 * p.dy);
	vec4 b = textureGrad(tex, p.uv1, p.j1 * p.dx, p.j1 * p.dy);
	vec4 c = textureGrad(tex, p.uv2, p.j2 * p.dx, p.j2 * p.dy);
	vec3 luminance = vec3(dot(a.rgb, vec3(0.2126, 0.7152, 0.0722)),
		dot(b.rgb, vec3(0.2126, 0.7152, 0.0722)), dot(c.rgb, vec3(0.2126, 0.7152, 0.0722)));
	vec3 w = pow(max(p.weights, vec3(0.0)), vec3(blend.x)) * mix(vec3(1.0), max(luminance, vec3(0.03)), blend.y);
	p.weights = w / max(dot(w, vec3(1.0)), 0.00000001);
	a.rgb *= p.brightness.x; b.rgb *= p.brightness.y; c.rgb *= p.brightness.z;
	return a * p.weights.x + b * p.weights.y + c * p.weights.z;
}

vec4 surfaceStochasticData(sampler2D tex, SurfaceStochasticPatch p) {
	return textureGrad(tex, p.uv0, p.j0 * p.dx, p.j0 * p.dy) * p.weights.x
		+ textureGrad(tex, p.uv1, p.j1 * p.dx, p.j1 * p.dy) * p.weights.y
		+ textureGrad(tex, p.uv2, p.j2 * p.dx, p.j2 * p.dy) * p.weights.z;
}

vec2 surfaceStochasticSlope(vec3 encoded, mat2 jacobian, vec2 normalSigns) {
	vec3 n = encoded * 2.0 - 1.0;
	// Signs convert source normal V into lattice V, then lattice V into TBN V.
	vec2 slope = vec2(n.x, n.y * normalSigns.x) / max(n.z, 0.05);
	slope = transpose(jacobian) * slope;
	slope.y *= normalSigns.y;
	return slope;
}

vec3 surfaceStochasticNormal(sampler2D tex, SurfaceStochasticPatch p, vec2 normalSigns) {
	vec2 a = surfaceStochasticSlope(textureGrad(tex, p.uv0, p.j0 * p.dx, p.j0 * p.dy).xyz, p.j0, normalSigns);
	vec2 b = surfaceStochasticSlope(textureGrad(tex, p.uv1, p.j1 * p.dx, p.j1 * p.dy).xyz, p.j1, normalSigns);
	vec2 c = surfaceStochasticSlope(textureGrad(tex, p.uv2, p.j2 * p.dx, p.j2 * p.dy).xyz, p.j2, normalSigns);
	return normalize(vec3(a * p.weights.x + b * p.weights.y + c * p.weights.z, 1.0));
}
#endif
`;
