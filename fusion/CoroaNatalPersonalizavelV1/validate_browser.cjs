/* Run with Node and Playwright available; temporary exports stay outside the repository. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const HERE=__dirname,ROOT=path.resolve(HERE,'../..'),WORK=process.argv[2]||'/tmp/coroa-v1-tests';
fs.mkdirSync(WORK,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const context=await browser.newContext({acceptDownloads:true,viewport:{width:1370,height:1060}});
 const page=await context.newPage(),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push(r.url()));
 // All production resources are embedded. Block the network to verify offline use.
 await context.setOffline(true);
 await page.setContent(fs.readFileSync(path.join(ROOT,'downloads/coroa-natal-v1-personalizar.html'),'utf8'));
 await page.waitForFunction(()=>window.CoroaApp&&CoroaApp.model);
 const cases=[
  {key:'clemente-2026',name:'Clemente',second:'',year:'2026',font:'Pacifico'},
  {key:'avo-dulce-2026',name:'Avó',second:'Dulce',year:'2026',font:'Pacifico'},
  {key:'lia',name:'Lia',second:'',year:'',font:'Pacifico'},
  {key:'joao-2026',name:'João',second:'',year:'2026',font:'Pacifico'},
  {key:'maria-alexandra-2026',name:'Maria',second:'Alexandra',year:'2026',font:'Pacifico'},
  {key:'tomas-leckerli-2026',name:'Tomás',second:'',year:'2026',font:'LeckerliOne'},
  {key:'sao-accent',name:'São',second:'José',year:'2026',font:'Pacifico'},
  {key:'short-i',name:'I',second:'',year:'',font:'Pacifico'},
 ];
 const reports=[];
 for(const c of cases){
  await page.evaluate(c=>{for(const k of ['name','second','year','font'])document.getElementById(k).value=c[k];CoroaApp.update();},c);
  assert.equal(await page.locator('#download').isEnabled(),true,c.key+' '+await page.locator('#status').textContent());
  const model=await page.evaluate(()=>CoroaApp.model);
  const pieces=await page.evaluate(()=>CoroaGeometry.meshModel(CoroaApp.model));
  fs.writeFileSync(path.join(WORK,c.key+'-geometry.json'),JSON.stringify(model));
  fs.writeFileSync(path.join(WORK,c.key+'-meshes.json'),JSON.stringify(pieces));
  const event=page.waitForEvent('download');await page.locator('#download').click();const download=await event;
  await download.saveAs(path.join(WORK,c.key+'.3mf'));
  await page.getByRole('button',{name:'Montada',exact:true}).click();
  if(c.key==='clemente-2026')await page.screenshot({path:path.join(ROOT,'designs/coroa-natal-v1-formulario.png'),fullPage:true});
  fs.writeFileSync(path.join(WORK,c.key+'.svg'),await page.evaluate(()=>CoroaGeometry.svg(CoroaApp.model)));
  if(['clemente-2026','avo-dulce-2026','lia'].includes(c.key)){
   await page.locator('#drawing').screenshot({path:path.join(WORK,c.key+'-CAD.png')});
   if(c.key==='clemente-2026'){
    await page.getByRole('button',{name:'Apoios de colagem',exact:true}).click();await page.locator('#drawing').screenshot({path:path.join(WORK,c.key+'-apoios-CAD.png')});
    await page.getByRole('button',{name:'Texto separado',exact:true}).click();await page.locator('#drawing').screenshot({path:path.join(WORK,c.key+'-texto-CAD.png')});
   }
  }
  reports.push({key:c.key,options:model.options,metrics:model.metrics,notes:model.notes,pads:model.pads.map(p=>p.center),browser_export_download:download.suggestedFilename()});
 }
 // A saved project restores its editable inputs; no installed font is required.
 await page.locator('#file').setInputFiles(path.join(WORK,'avo-dulce-2026.3mf'));
 await page.waitForFunction(()=>CoroaApp.model?.options.name==='Avó');
 assert.equal(await page.locator('#second').inputValue(),'Dulce');
 assert.equal(await page.locator('#year').inputValue(),'2026');
 const rejected=[];
 for(const test of [{name:'',second:'',year:'2026'},{name:'ABC',second:'',year:'xx'},{name:'🙂',second:'',year:''},{name:'ABCDEFGHIJKLMNOPQRSTUVWXY',second:'',year:''}]){
  await page.evaluate(c=>{for(const k of ['name','second','year'])document.getElementById(k).value=c[k];CoroaApp.update();},test);
  assert.equal(await page.locator('#download').isEnabled(),false);rejected.push(await page.locator('#status').textContent());
 }
 // User typing invalidates the previous model immediately, then recomputes it.
 await page.locator('#name').fill('Inês');await page.locator('#year').fill('2027');
 await page.waitForFunction(()=>CoroaApp.model?.options.name==='Inês'&&CoroaApp.model?.options.year==='2027');
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
 await page.screenshot({path:path.join(WORK,'mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.equal(requests.filter(u=>/^https?:/.test(u)).length,0);
 assert.notDeepEqual(reports[0].pads,reports[1].pads);
 const report={browser:await browser.version(),offline:true,external_http_requests:0,errors,profile_confirmed_by_user:'A1 + AMS Lite / 0.4 mm / PLA',cases:reports,rejected,restored_saved_project:true,mobile_no_horizontal_overflow:true,physical_print_tested:false};
 fs.writeFileSync(path.join(HERE,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({cases:reports.length,rejected:rejected.length,errors,work:WORK}));
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
