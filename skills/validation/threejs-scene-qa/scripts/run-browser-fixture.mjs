#!/usr/bin/env node
/** Isolated Chromium fixture. Explicit dependency paths; never controls an existing tab. */
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname,extname,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const args=Object.fromEntries(process.argv.slice(2).reduce((out,v,i,all)=>{if(i%2===0)out.push([v,all[i+1]]);return out;},[]));
if(!args['--three-root']||!args['--playwright']||!args['--output']) {
 console.error('Usage: node run-browser-fixture.mjs --three-root /path/to/three --playwright /path/to/playwright/index.mjs --output /tmp/qa-output');process.exit(1);
}
const skill=resolve(dirname(fileURLToPath(import.meta.url)),'..'),three=resolve(args['--three-root']),output=resolve(args['--output']);
const {chromium}=await import(pathToFileURL(resolve(args['--playwright'])).href);
const server=createServer(async(req,res)=>{
 try{
  const path=new URL(req.url,'http://localhost').pathname;
  let root,relative;
  if(path.startsWith('/three/')){root=three;relative=path.slice(7);}
  else if(path.startsWith('/performance/')){root=resolve(skill,'../threejs-performance/scripts');relative=path.slice(13);}
  else{root=skill;relative=path==='/'?'fixtures/scene.html':path.slice(1);}
  const full=resolve(root,relative);if(full!==root&&!full.startsWith(root+sep))throw Error('Bad path');
  const data=await readFile(full);res.setHeader('Content-Type',({'.mjs':'text/javascript','.js':'text/javascript','.html':'text/html','.json':'application/json'})[extname(full)]??'application/octet-stream');res.end(data);
 }catch(e){res.statusCode=404;res.end('Not found');}
});
let browser;
try {
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:640,height:480}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:'+server.address().port);
 await page.waitForFunction(()=>window.fixtureReady,{},{timeout:30000});
 const result=await page.evaluate(()=>window.fixture.run());await mkdir(output,{recursive:true});
 for(const shot of result.shots){const name=shot.view+'-'+shot.mode+'.png';await writeFile(resolve(output,name),Buffer.from(shot.result.png.split(',')[1],'base64'));shot.result.png=name;}
 result.errors=errors;result.browser=browser.version();
 await page.evaluate(()=>window.fixture.dispose());
 await writeFile(resolve(output,'results.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({output,route:result.route,restored:result.restored,shots:result.shots.length,errors}));
 if(!result.route.pass||!result.restored||errors.length)process.exitCode=1;
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
