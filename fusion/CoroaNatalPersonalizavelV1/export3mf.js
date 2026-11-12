/* A two-plate Bambu project, without machine G-code or a print-start operation. */
(function(root){
 'use strict';
 const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
 const identity='1 0 0 0 1 0 0 0 1 0 0 0';
 const fmt=n=>Number(n.toFixed(5));
 function create(model,settings,thumbnails=[]){
  const parts=root.CoroaGeometry.meshModel(model),files={},enc=s=>root.fflate.strToU8(s);
  const cfg=JSON.parse(JSON.stringify(settings));
  cfg.filament_colour=model.colors;cfg.filament_multi_colour=model.colors;
  let resources='',configs='';
  parts.forEach((p,i)=>{
   p.id=i+1;
   resources+=`<object id="${p.id}" type="model" name="${esc(p.name)}"><mesh><vertices>`+
    p.mesh.vertices.map(v=>`<vertex x="${fmt(v[0])}" y="${fmt(v[1])}" z="${fmt(v[2])}"/>`).join('')+
    '</vertices><triangles>'+p.mesh.triangles.map(t=>`<triangle v1="${t[0]}" v2="${t[1]}" v3="${t[2]}"/>`).join('')+'</triangles></mesh></object>';
  });
  const groupIds=[parts.length+1,parts.length+2];
  const label=[model.options.name,model.options.second,model.options.year].filter(Boolean).join(' ');
  for(let piece=0;piece<2;piece++){
   const ps=parts.filter(p=>p.piece===piece),name=(piece?'Texto':'Coroa')+' — '+label;
   resources+=`<object id="${groupIds[piece]}" type="model" name="${esc(name)}"><components>`+
    ps.map(p=>`<component objectid="${p.id}" transform="${identity}"/>`).join('')+'</components></object>';
   configs+=`<object id="${groupIds[piece]}"><metadata key="name" value="${esc(name)}"/><metadata key="extruder" value="1"/>`+
    ps.map(p=>`<part id="${p.id}" subtype="normal_part"><metadata key="name" value="${esc(p.name)}"/><metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/><metadata key="extruder" value="${p.color}"/><mesh_stat face_count="${p.mesh.triangles.length}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/></part>`).join('')+'</object>';
  }
  files['3D/3dmodel.model']=enc('<?xml version="1.0" encoding="UTF-8"?>'+
   '<model unit="millimeter" xml:lang="pt-PT" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">'+
   '<metadata name="Application">BambuStudio-02.09.01.70</metadata><metadata name="BambuStudio:3mfVersion">1</metadata>'+
   `<metadata name="Title">Coroa Natal V1 — ${esc(label)}</metadata><resources>${resources}</resources><build>`+
   `<item objectid="${groupIds[0]}" transform="1 0 0 0 1 0 0 0 1 112 115 0" printable="1"/>`+
   `<item objectid="${groupIds[1]}" transform="1 0 0 0 1 0 0 0 1 419.2 115 0" printable="1"/></build></model>`);
  for(let i=0;i<2;i++)configs+=`<plate><metadata key="plater_id" value="${i+1}"/><metadata key="plater_name" value="${i?'02 Texto para colar':'01 Coroa com apoios'} — ${esc(label)}"/><metadata key="locked" value="false"/><metadata key="filament_map_mode" value="Auto For Flush"/><metadata key="gcode_file" value=""/>`+
   (thumbnails[i]?`<metadata key="thumbnail_file" value="Metadata/plate_${i+1}.png"/>`:'')+
   `<model_instance><metadata key="object_id" value="${groupIds[i]}"/><metadata key="instance_id" value="0"/><metadata key="identify_id" value="${100+i}"/></model_instance></plate>`;
  files['Metadata/model_settings.config']=enc('<?xml version="1.0" encoding="UTF-8"?><config>'+configs+'<assemble/></config>');
  files['Metadata/project_settings.config']=enc(JSON.stringify(cfg));
  files['Metadata/coroa_parameters.json']=enc(JSON.stringify({schema:'coroa-natal-v1',version:model.version,options:model.options,metrics:model.metrics,pads:model.pads.map(p=>({center:p.center,contact_mm2:p.verified_contact_mm2})),physical_fit_tested:false},null,2));
  for(let i=0;i<thumbnails.length;i++)if(thumbnails[i])files[`Metadata/plate_${i+1}.png`]=thumbnails[i];
  files['_rels/.rels']=enc('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'+(thumbnails[0]?'<Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>':'')+'</Relationships>');
  files['[Content_Types].xml']=enc('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="png" ContentType="image/png"/><Default Extension="config" ContentType="application/octet-stream"/><Default Extension="json" ContentType="application/json"/></Types>');
  return root.fflate.zipSync(files,{level:6});
 }
 root.CoroaExport={create};
})(globalThis);
