/* Geometry in millimetres, shared by the offline form and validation scripts. */
(function (root) {
 'use strict';
 const C=root.ClipperLib, SCALE=10000, TAU=Math.PI*2;
 const colors=['#F4E5C4','#234E3A','#719071','#B51636'];
 const P=(x,y)=>({X:Math.round(x*SCALE),Y:Math.round(y*SCALE)});
 const mm=p=>[p.X/SCALE,p.Y/SCALE];
 const area=ps=>ps.reduce((s,p)=>s+C.Clipper.Area(p),0)/(SCALE*SCALE);
 function clean(ps){return C.Clipper.CleanPolygons(ps,3).filter(p=>p.length>=3 && Math.abs(C.Clipper.Area(p))>30);}
 function boolean(a,b,op){
  const c=new C.Clipper(); c.StrictlySimple=true;
  c.AddPaths(a,C.PolyType.ptSubject,true); if(b.length)c.AddPaths(b,C.PolyType.ptClip,true);
  const out=[];c.Execute(op,out,C.PolyFillType.pftNonZero,C.PolyFillType.pftNonZero);return clean(out);
 }
 const union=(...ps)=>boolean(ps.flat(),[],C.ClipType.ctUnion);
 const diff=(a,b)=>boolean(a,b,C.ClipType.ctDifference);
 const intersect=(a,b)=>boolean(a,b,C.ClipType.ctIntersection);
 function offset(ps,d){if(!ps.length)return [];const c=new C.ClipperOffset(2,.012*SCALE),o=[];c.AddPaths(ps,C.JoinType.jtRound,C.EndType.etClosedPolygon);c.Execute(o,d*SCALE);return clean(o);}
 function circle(x,y,r,n=96){return [Array.from({length:n},(_,i)=>P(x+r*Math.cos(TAU*i/n),y+r*Math.sin(TAU*i/n)))];}
 function stroke(points,width){const c=new C.ClipperOffset(2,.012*SCALE),o=[];c.AddPath(points.map(p=>P(...p)),C.JoinType.jtRound,C.EndType.etOpenRound);c.Execute(o,width*SCALE/2);return clean(o);}
 const move=(ps,dx,dy,s=1)=>ps.map(p=>p.map(q=>P(q.X/SCALE*s+dx,q.Y/SCALE*s+dy)));
 function bounds(ps){const a=ps.flat();if(!a.length)throw Error('A forma ficou vazia.');return [Math.min(...a.map(p=>p.X))/SCALE,Math.min(...a.map(p=>p.Y))/SCALE,Math.max(...a.map(p=>p.X))/SCALE,Math.max(...a.map(p=>p.Y))/SCALE];}
 function bezier(a,b,c,d,n=36){return Array.from({length:n+1},(_,i)=>{const t=i/n,u=1-t;return [u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0],u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1]]});}
 function shape(points){const p=points.map(q=>P(...q));if(!C.Clipper.Orientation(p))p.reverse();return [p];}
 function leaf(cx,cy,angle,length,width){
  const pts=[...bezier([-length/2,0],[-length*.22,width*.85],[length*.28,width*.6],[length/2,0]),...bezier([length/2,0],[length*.22,-width*.60],[-length*.3,-width*.7],[-length/2,0]).slice(1)];
  const tr=p=>[cx+p[0]*Math.cos(angle)-p[1]*Math.sin(angle),cy+p[0]*Math.sin(angle)+p[1]*Math.cos(angle)];
  return {body:shape(pts.map(tr)),vein:stroke(bezier([-length*.38,0],[-length*.15,width*.09],[length*.22,-width*.05],[length*.36,0],18).map(tr),.48)};
 }
 function wreath(){
  const dark=[],light=[],veins=[];
  for(let i=0;i<24;i++){
   const a=(i*15+7.5)*Math.PI/180;
   for(let j=0;j<2;j++){
    const r=j?37.9:44.0,theta=a+(j?.066:0),dir=a+Math.PI/2+(j?-.55:.55);
    const q=leaf(r*Math.cos(theta),r*Math.sin(theta),dir,j?11.8:13.0,j?4.35:4.5);
    (j?dark:light).push(q.body);veins.push(q.vein);
   }
  }
  const leaves=union(...dark,...light);
  const rawbase=union(offset(leaves,.65),diff(circle(0,0,41.6),circle(0,0,38.4)));
  const bb=bounds(rawbase),factor=100/Math.max(bb[2]-bb[0],bb[3]-bb[1]);
  const branch=diff(circle(0,0,40.65),circle(0,0,39.35));
  let greenD=move(union(...dark,diff(branch,union(...light))),0,0,factor),greenL=move(diff(union(...light),union(...dark)),0,0,factor);
  let vein=move(union(...veins),0,0,factor);
  // A real open ribbon silhouette, with tails; no infilled disk behind the bow.
  const loopL=shape([...bezier([-1,46],[-12,56],[-29,61],[-21,48]),...bezier([-21,48],[-15,43],[-7,44],[-1,46]).slice(1)]);
  const holeL=shape([...bezier([-5,47],[-12,52],[-23,56],[-20,50]),...bezier([-20,50],[-15,47],[-10,46],[-5,47]).slice(1)]);
  const mirror=ps=>ps.map(p=>p.map(q=>P(-q.X/SCALE,q.Y/SCALE)).reverse());
  const tailL=shape([...bezier([-2,46],[-10,43],[-5,34],[-17,30]),[-13,29],...bezier([-13,29],[-3,32],[-2,39],[2,45]).slice(1)]);
  let bow=union(diff(loopL,holeL),diff(mirror(loopL),mirror(holeL)),tailL,mirror(tailL),circle(0,46,2.7));
  const berries=[];
  for(const degree of [19,58,121,161,199,238,278,316,345]){const a=degree*Math.PI/180,r=40.1*factor;berries.push(circle(r*Math.cos(a),r*Math.sin(a),1.65));}
  const red=union(bow,...berries);
  const ring=diff(circle(0,55.6,3.6),circle(0,55.6,1.5));
  const ringNeck=shape([[-2.4,48],[2.4,48],[2.4,55],[-2.4,55]]);
  let base=union(move(rawbase,0,0,factor),offset(red,.55),ring,ringNeck);
  base=diff(base,circle(0,55.6,1.5));
  greenD=diff(greenD,offset(red,.12));greenL=diff(greenL,offset(red,.12));
  vein=intersect(vein,union(greenD,greenL));
  return {base,greenD,greenL,vein,red,stemRadius:40*factor,diameter:100};
 }
 function fontPaths(font,text,size){
  if([...text].some(ch=>!font.charToGlyphIndex(ch)))throw Error('Há um carácter que esta fonte não suporta. Usa letras latinas, acentos e números.');
  let ps=[],path=[],cur=[0,0];
  const push=()=>{if(path.length>2)ps.push(path.map(p=>P(p[0],-p[1])));path=[];};
  for(const c of font.getPath(text,0,0,size,{kerning:true}).commands){
   const end=[c.x,c.y];
   if(c.type==='M'){push();path=[end];cur=end;}
   else if(c.type==='L'){path.push(end);cur=end;}
   else if(c.type==='Q'){
    const start=cur,n=Math.max(8,Math.ceil((Math.hypot(c.x1-start[0],c.y1-start[1])+Math.hypot(end[0]-c.x1,end[1]-c.y1))/.22));
    for(let i=1;i<=n;i++){const t=i/n,u=1-t;path.push([u*u*start[0]+2*u*t*c.x1+t*t*end[0],u*u*start[1]+2*u*t*c.y1+t*t*end[1]]);}cur=end;
   }else if(c.type==='C'){
    const len=Math.hypot(c.x1-cur[0],c.y1-cur[1])+Math.hypot(c.x2-c.x1,c.y2-c.y1)+Math.hypot(c.x-c.x2,c.y-c.y2);
    path.push(...bezier(cur,[c.x1,c.y1],[c.x2,c.y2],end,Math.max(10,Math.ceil(len/.22))).slice(1));cur=end;
   }else if(c.type==='Z')push();
  }push();return union(ps);
 }
 function components(ps){
  const c=new C.Clipper(),tree=new C.PolyTree();c.AddPaths(ps,C.PolyType.ptSubject,true);c.Execute(C.ClipType.ctUnion,tree,C.PolyFillType.pftNonZero,C.PolyFillType.pftNonZero);
  const result=[];function walk(node){for(const n of node.Childs()){if(!n.IsHole())result.push([n.Contour(),...n.Childs().filter(h=>h.IsHole()).map(h=>h.Contour())]);walk(n);}}walk(tree);return result;
 }
 function closestPoint(ps,point){let best=null;for(const p of ps)for(let i=0;i<p.length;i++){
  const a=mm(p[i]),b=mm(p[(i+1)%p.length]),dx=b[0]-a[0],dy=b[1]-a[1],l=dx*dx+dy*dy;
  const t=Math.max(0,Math.min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/(l||1))),q=[a[0]+dx*t,a[1]+dy*t],d=Math.hypot(q[0]-point[0],q[1]-point[1]);
  if(!best||d<best.d)best={q,d};
 }return best;}
 function connect(ps,width=1.3){
  let whole=union(ps),connections=[];
  for(let loop=0;loop<80;loop++){
   const cs=components(whole);if(cs.length<2)return {paths:whole,connections};
   let best=null;
   for(let i=1;i<cs.length;i++)for(let j=0;j<i;j++){
    for(const p of cs[i][0]){const a=mm(p),b=closestPoint(cs[j],a);if(!best||b.d<best.d)best={a,b:b.q,d:b.d};}
   }
   const link=stroke([best.a,best.b],width);whole=union(whole,link);connections.push(link);
  }throw Error('Não foi possível unir todas as letras. Usa um texto mais simples.');
 }
 function makeText(font,opts){
  const name=(opts.name||'').normalize('NFC').trim(),second=(opts.second||'').normalize('NFC').trim(),year=(opts.year||'').trim();
  if(!name)throw Error('Escreve um nome.');
  if(name.length>24||second.length>24)throw Error('Máximo de 24 caracteres por linha. Divide o nome entre as duas linhas.');
  if(year&&!/^\d{4}$/.test(year))throw Error('O ano deve ter quatro algarismos ou ficar vazio.');
  const texts=[name,...(second?[second]:[]),...(year?[year]:[])];
  const maxH=texts.length===3?15.6:texts.length===2?22:27.5;
  const rendered=texts.map((s,i)=>{
   let p=fontPaths(font,s,32),b=bounds(p),isYear=year&&i===texts.length-1;
   const scale=Math.min((isYear?49:84)/(b[2]-b[0]),(isYear?14:maxH)/(b[3]-b[1]));
   if(32*scale<9)throw Error('Texto demasiado pequeno para o bico de 0,4 mm. Divide o nome em duas linhas ou abrevia-o.');
   p=move(p,-(b[0]+b[2])/2*scale,-b[1]*scale,scale);
   // Small boldening protects thin connections without horizontally distorting glyphs.
   p=offset(p,.10);b=bounds(p);return {p,height:b[3]-b[1],text:s,fontSize:32*scale};
  });
  const gap=1.15,total=rendered.reduce((s,p)=>s+p.height,0)+gap*(rendered.length-1),center=year?-6:-3;
  let y=center+total/2,red=[];
  for(const line of rendered){y-=line.height;line.p=move(line.p,0,y);red.push(line.p);y-=gap;}
  red=union(...red);const connected=connect(offset(red,.75),1.25);
  return {red,base:connected.paths,lines:rendered.map(p=>({text:p.text,font_size_mm:p.fontSize})),connections:connected.connections};
 }
 function generate(font,options){
  const w=wreath(),t=makeText(font,options),bb=bounds(t.base),pads=[],arms=[],notes=[];
  for(const side of [-1,1]){
   const y0=Math.max(-22,Math.min(12,(bb[1]+bb[3])/2));
   let candidate=closestPoint(t.base,[side*55,y0]).q;
   const ay=Math.max(-25,Math.min(15,candidate[1])),ax=side*Math.sqrt(w.stemRadius*w.stemRadius-ay*ay),center=[ax,ay];
   const p=closestPoint(t.base,center).q;
   const curve=bezier(p,[p[0]+side*3,p[1]],[ax-side*3,ay],center,24);
   const arm=union(stroke(curve,1.8),circle(ax,ay,2.9));
   arms.push(arm);pads.push({center,footprint:circle(ax,ay,2.45),contact_mm2:Math.PI*2.45*2.45});
   if(Math.hypot(p[0]-ax,p[1]-ay)>4){
    // Visible spans become matching decorative swashes, rather than bare rails.
    const q=closestPoint(t.red,p).q;
    const flourish=union(stroke(bezier(q,[q[0]+side*3,q[1]],[ax-side*3,ay],center,24),.80),circle(ax,ay,1.75));
    t.red=union(t.red,flourish);
    arms[arms.length-1]=union(arm,offset(flourish,.65));
    notes.push('O texto inclui prolongamentos decorativos laterais para alcançar os apoios.');
   }
  }
  t.base=union(t.base,...arms);
  if(components(t.base).length!==1)throw Error('O conjunto do texto não ficou unido.');
  const footprint=union(...pads.map(p=>p.footprint)),clearance=offset(footprint,.18);
  w.base=union(w.base,offset(footprint,.4));
  w.greenD=diff(w.greenD,clearance);w.greenL=diff(w.greenL,clearance);w.vein=diff(w.vein,clearance);w.red=diff(w.red,clearance);
  if(components(w.base).length!==1)throw Error('A coroa tem uma região sem ligação.');
  // Pads replace decorative relief locally and finish on a common Z plane.
  const part=(name,color,paths,z0,z1,piece)=>({name,color,paths,z0,z1,piece});
  const parts=[part('Coroa · base creme',1,w.base,0,1.4,0),part('Folhas · verde escuro',2,w.greenD,1.4,2.24,0),
   part('Folhas · verde claro',3,w.greenL,1.4,2.24,0),part('Nervuras das folhas',2,w.vein,2.24,2.48,0),
   part('Laço e bagas',4,w.red,1.4,2.6,0),part('Apoios personalizados',1,footprint,1.4,2.6,0),
   part('Texto · contorno creme',1,t.base,0,1.4,1),part('Texto · relevo vermelho',4,t.red,1.4,2.12,1)];
  for(const p of pads){const overlap=area(intersect(p.footprint,t.base));if(overlap<18)throw Error('Área de colagem insuficiente.');p.verified_contact_mm2=overlap;}
  return {version:'1.0',options:{name:options.name,second:options.second||'',year:options.year||'',font:options.font||'Pacifico'},parts,pads,arms,
   notes:[...new Set(notes)],colors,lines:t.lines,metrics:{diameter_mm:100,crown_bounds:bounds(w.base),text_bounds:bounds(t.base),crown_height_mm:2.6,text_height_mm:2.12,assembled_height_mm:4.72,hole_diameter_mm:3,contact_total_mm2:pads.reduce((s,p)=>s+p.verified_contact_mm2,0)},
   physical_fit_tested:false};
 }
 function extrude(ps,z0,z1){
  const vertices=[],triangles=[];
  for(const group of components(ps)){
   const flat=[],holes=[];let count=0;
   for(let i=0;i<group.length;i++){if(i)holes.push(count);for(const p of group[i]){flat.push(p.X/SCALE,p.Y/SCALE);count++;}}
   const start=vertices.length;
   for(const z of [z0,z1])for(let i=0;i<count;i++)vertices.push([flat[i*2],flat[i*2+1],z]);
   const inds=root.earcut(flat,holes,2);
   for(let i=0;i<inds.length;i+=3){let [a,b,c]=inds.slice(i,i+3);const cross=(flat[b*2]-flat[a*2])*(flat[c*2+1]-flat[a*2+1])-(flat[b*2+1]-flat[a*2+1])*(flat[c*2]-flat[a*2]);
    if(cross<0)[b,c]=[c,b];if(Math.abs(cross)>1e-10){triangles.push([start+a,start+c,start+b],[start+count+a,start+count+b,start+count+c]);}}
   let cursor=0;
   for(const p of group){for(let i=0;i<p.length;i++){const a=start+cursor+i,b=start+cursor+(i+1)%p.length;triangles.push([a,b,b+count],[a,b+count,a+count]);}cursor+=p.length;}
  }return {vertices,triangles};
 }
 function meshModel(model){return model.parts.map(p=>({...p,mesh:extrude(p.paths,p.z0,p.z1)}));}
 function svgPath(ps){return ps.map(p=>p.map((q,i)=>(i?'L':'M')+(q.X/SCALE).toFixed(3)+' '+(-q.Y/SCALE).toFixed(3)).join(' ')+'Z').join(' ');}
 function svg(model,view='assembled'){
  let body='';const parts=view==='text'?model.parts.filter(p=>p.piece===1):(view==='crown'||view==='contacts')?model.parts.filter(p=>p.piece===0):model.parts;
  for(const p of parts){const highlight=view==='contacts'&&p.name==='Apoios personalizados';body+=`<path d="${svgPath(p.paths)}" fill="${highlight?'#FFB42A':colors[p.color-1]}" fill-rule="nonzero" stroke="#30281B" stroke-opacity=".12" stroke-width=".09"/>`;}
  if(view==='contacts')for(const pad of model.pads)body+=`<circle cx="${pad.center[0]}" cy="${-pad.center[1]}" r="3.4" fill="none" stroke="#D78200" stroke-width=".6"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-57 -64 114 120" role="img" aria-label="Geometria real da coroa personalizada">${body}</svg>`;
 }
 root.CoroaGeometry={generate,meshModel,svg,svgPath,colors,area,components,intersect,diff,offset,bounds,extrude};
})(typeof globalThis!=='undefined'?globalThis:window);
