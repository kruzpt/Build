(function(){
 'use strict';
 const $=id=>document.getElementById(id),fonts={},examples=[{name:'Clemente',second:'',year:'2026'},{name:'Avó',second:'Dulce',year:'2026'},{name:'Lia',second:'',year:''},{name:'Maria',second:'Alexandra',year:'2026'}];
 for(const [name,data] of Object.entries(COROA_ASSETS.fonts)){const bytes=Uint8Array.from(atob(data),c=>c.charCodeAt(0));fonts[name]=opentype.parse(bytes.buffer);}
 let current=null,view='assembled',timer=null,busy=false;
 const values=()=>Object.fromEntries(['name','second','year','font'].map(id=>[id,$(id).value]));
 function render(){if(!current)return;$('drawing').innerHTML=CoroaGeometry.svg(current,view);$('viewnote').textContent=view==='contacts'?'Os círculos assinalam os dois apoios planos. A parte de trás do texto assenta nestas zonas; as nervuras foram retiradas apenas debaixo dos apoios.':view==='text'?'Uma peça: contorno creme e letras vermelhas. As ligações entre linhas, acentos e apoios fazem parte desta geometria.':'Vista frontal da geometria que será exportada. As cores reais dependem dos filamentos.';}
 function update(){clearTimeout(timer);current=null;$('download').disabled=true;$('status').className='message';try{
  current=CoroaGeometry.generate(fonts[$('font').value],values());render();$('download').disabled=false;
  $('status').textContent=current.notes.length?current.notes.join(' '):'Texto unido e dois apoios de colagem calculados. Pronto para gerar o projeto.';
 }catch(e){$('drawing').innerHTML='';$('status').className='message error';$('status').textContent=e.message;}return current;}
 for(const id of ['name','second','year','font'])$(id).addEventListener('input',()=>{current=null;$('download').disabled=true;$('status').textContent='A recalcular texto e apoios…';clearTimeout(timer);timer=setTimeout(update,260);});
 document.querySelectorAll('[data-example]').forEach(b=>b.addEventListener('click',()=>{const x=examples[Number(b.dataset.example)];for(const [k,v] of Object.entries(x))$(k).value=v;update();}));
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{view=b.dataset.view;document.querySelectorAll('[data-view]').forEach(q=>q.setAttribute('aria-pressed',String(q===b)));render();}));
 function thumbnail(model,piece){return new Promise((resolve,reject)=>{
  const canvas=document.createElement('canvas');canvas.width=512;canvas.height=512;const ctx=canvas.getContext('2d');ctx.fillStyle='#f5f3ed';ctx.fillRect(0,0,512,512);
  const im=new Image(),url=URL.createObjectURL(new Blob([CoroaGeometry.svg(model,piece===0?'crown':'text')],{type:'image/svg+xml'}));
  im.onload=()=>{ctx.drawImage(im,32,0,448,480);ctx.fillStyle='#234e3a';ctx.font='16px sans-serif';ctx.fillText(piece?'02 Texto para colar':'01 Coroa com apoios',20,500);URL.revokeObjectURL(url);resolve(Uint8Array.from(atob(canvas.toDataURL('image/png').split(',')[1]),c=>c.charCodeAt(0)));};im.onerror=()=>{URL.revokeObjectURL(url);reject(Error('Não foi possível criar a prévia do prato.'));};im.src=url;
 });}
 $('download').addEventListener('click',async()=>{
  if(busy)return;const model=update();if(!model)return;busy=true;$('download').disabled=true;$('download').textContent='A gerar o projeto…';
  try{await new Promise(r=>setTimeout(r,30));const thumbs=await Promise.all([thumbnail(model,0),thumbnail(model,1)]),bytes=CoroaExport.create(model,COROA_ASSETS.settings,thumbs),url=URL.createObjectURL(new Blob([bytes],{type:'model/3mf'}));
   const a=document.createElement('a');a.href=url;a.download='coroa-natal-v1-'+[model.options.name,model.options.second,model.options.year].filter(Boolean).join('-').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-zA-Z0-9-]/g,'-').toLowerCase()+'-A1-AMS.3mf';a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);
   $('status').textContent='Projeto criado. Abre como projeto no Bambu Studio e fatia os dois pratos.';
  }catch(e){$('status').className='message error';$('status').textContent=e.message;}finally{busy=false;$('download').disabled=false;$('download').textContent='Descarregar 3MF · 2 pratos';}
 });
 $('load').addEventListener('click',()=>$('file').click());
 $('file').addEventListener('change',async()=>{try{
  const file=$('file').files[0];if(!file)return;if(file.size>30000000)throw Error('Escolhe um 3MF deste gerador com menos de 30 MB.');
  const zip=fflate.unzipSync(new Uint8Array(await file.arrayBuffer()),{filter:f=>f.name==='Metadata/coroa_parameters.json'&&f.originalSize<20000}),data=zip['Metadata/coroa_parameters.json'];
  if(!data)throw Error('Este 3MF não contém uma personalização deste gerador.');const saved=JSON.parse(fflate.strFromU8(data));
  if(saved.schema!=='coroa-natal-v1'||!saved.options||!fonts[saved.options.font])throw Error('Formato de personalização não reconhecido.');
  for(const id of ['name','second','year','font'])$(id).value=String(saved.options[id]||'');update();
 }catch(e){$('status').className='message error';$('status').textContent=e.message;}finally{$('file').value='';}});
 window.CoroaApp={update,values,get model(){return current;},fonts};update();
})();
