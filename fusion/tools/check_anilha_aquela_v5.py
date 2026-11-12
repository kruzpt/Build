"""Independently check native 3MF poses and deposited V5 color paths."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from build_pintos_pla_3mf import read_project
from build_m7_prototypes_v1_3mf import plate_meshes
from check_anilha_lobito_v5_toolpaths import paths
from generate_anilha_aquela_v5 import ROOT,FOLDER,PREFIX,COLORS,BROWN,GREEN,BLACK


def shape(loops):
    s=Polygon()
    for loop in loops:s=s.symmetric_difference(Polygon(loop))
    return s


def main(work):
    geometry=json.loads((FOLDER/'geometry.json').read_text())
    masks={k:shape(v) for k,v in json.loads((FOLDER/'validation-regions.json').read_text()).items()}
    checks={};reviews=[];views=[]
    for kind in ['lobo','acessorios']:
        report=json.loads((FOLDER/f'bambu-validation-{kind}.json').read_text())
        target=ROOT/'downloads'/report['project']
        assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256']
        blobs,cfg,_=read_project(target);native=plate_meshes(blobs,cfg)
        colors=COLORS if kind=='lobo' else [BROWN,GREEN,BLACK]
        selected=[p for p in geometry['parts'] if (p['piece']=='lobo')==(kind=='lobo')]
        poses={};errors=[]
        for p in selected:
            ref=trimesh.load(ROOT/'downloads'/p['file'],force='mesh')
            col=colors.index(p['color'])+1
            mesh=next(m for plate in native for _,c,m in plate if c==col)
            assert np.array_equal(ref.faces,mesh.faces)
            fit=np.linalg.lstsq(np.c_[ref.vertices,np.ones(len(ref.vertices))],mesh.vertices,rcond=None)[0]
            error=float(np.max(np.linalg.norm(np.c_[ref.vertices,np.ones(len(ref.vertices))]@fit-mesh.vertices,axis=1)))
            assert error<.003 and np.allclose(fit[:3].T@fit[:3],np.eye(3),atol=.00001)
            if p['piece'] in poses:assert np.allclose(fit,poses[p['piece']],atol=.003)
            poses[p['piece']]=fit;errors.append(error)
        with ZipFile(work/kind/'slice/validation.3mf') as z:
            for i,plate in enumerate(native):
                code=z.read(f'Metadata/plate_{i+1}.gcode').decode()
                assert hashlib.sha256(code.encode()).hexdigest()==report['plates'][i]['gcode_sha256']
                rows=[r for r in paths(code) if r['feature']!='Prime tower']
                layers=sorted(set(r['layer'] for r in rows))
                assert abs(layers[0]-.2)<1e-6 and max(np.diff(layers))<.12001
                assert not any(r['feature'].startswith(('Support','Brim')) for r in rows)
                outer=max(r['speed'] for r in rows if r['feature']=='Outer wall')
                top=max(r['speed'] for r in rows if r['feature']=='Top surface')
                assert outer<=25.001 and top<=18.001
                expected={1,2,3,4} if kind=='lobo' else [{1},{2,3}][i]
                assert {r['tool'] for r in rows}==expected
                piece='lobo' if kind=='lobo' else ['anilha','folhas'][i]
                pose=np.eye(4);pose[:3]=poses[piece].T;inverse=np.linalg.inv(pose)
                for r in rows:
                    p=np.array(r['points']);r['points']=(np.c_[p,np.ones(len(p))]@inverse.T)[:,:3]
                if piece=='lobo':
                    # Shrink masks by half a nominal line width to exclude
                    # legitimate wall centers immediately beside a boundary.
                    board=masks['board'].buffer(-.22)
                    letters=masks['letters'].buffer(-.22)
                    gray_bad=sum(LineString(r['points'][:,:2]).intersection(board).length for r in rows if r['tool']==2)
                    black_bad=sum(LineString(r['points'][:,:2]).intersection(letters).length for r in rows if r['tool']==1)
                    assert gray_bad<.001 and black_bad<.001,(gray_bad,black_bad)
                    # Every letter/accent must receive white over its full depth.
                    letter_parts=list(masks['letters'].geoms) if hasattr(masks['letters'],'geoms') else [masks['letters']]
                    letter_parts=[p for p in letter_parts if p.area>.3]
                    assert len(letter_parts)>=6
                    white=[(r,LineString(r['points'][:,:2])) for r in rows if r['tool']==4]
                    counts=[]
                    for part in letter_parts:
                        ll=sorted({r['layer'] for r,line in white if line.intersection(part.buffer(-.18)).length>.10})
                        assert len(ll)>=11,(part.bounds,ll)
                        counts.append({'area_mm2':part.area,'white_layers':len(ll),'first_top_z_mm':min(ll),'last_top_z_mm':max(ll)})
                    eye=masks['right_eye_white'].buffer(-.15)
                    eye_layers=sorted({r['layer'] for r,line in white if line.intersection(eye).length>.1})
                    assert len(eye_layers)>=5,eye_layers
                    pupil=masks['right_pupil'].buffer(-.25)
                    white_pupil=sum(line.intersection(pupil).length for r,line in white)
                    assert white_pupil<.001,white_pupil
                    cfg_print=json.loads(blobs['Metadata/project_settings.config'])
                    checks.update({'gray_paths_on_plaque_mm':gray_bad,'black_paths_under_letter_cores_mm':black_bad,
                                   'letters_and_accent':counts,'right_eye_white_layers':eye_layers,
                                   'right_pupil_white_paths_mm':white_pupil,
                                   'black_to_white_flush_mm3':float(cfg_print['flush_volumes_matrix'][3]),
                                   'flush_multiplier':cfg_print['flush_multiplier'],
                                   'flush_into_objects':cfg_print['flush_into_objects']})
                if piece=='folhas':
                    forbidden=sum(LineString(r['points'][:,:2]).intersection(masks['hidden_leaf'].buffer(-.03)).length for r in rows if r['tool']==3)
                    assert forbidden<.001,forbidden
                    checks['hidden_leaf_black_paths_mm']=forbidden
                reviews.append({'piece':piece,'layers':len(layers),'tools':sorted(expected),
                                'outer_speed_max_mm_s':outer,'top_speed_max_mm_s':top,
                                'max_native_transform_error_mm':max(errors),
                                'gcode_sha256':hashlib.sha256(code.encode()).hexdigest()})
                views.append((piece,rows,colors))
    sheet=Image.new('RGB',(1600,1070),'#f4f6f8');draw=ImageDraw.Draw(sheet)
    font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    draw.text((35,25),'Aquelá V5 · percursos reais do Bambu Studio',font=font(34),fill='#23384C')
    panels={'lobo':(35,100,740,865),'folhas':(850,100,700,570),'anilha':(1010,740,400,215)}
    for piece,rows,colors in views:
        x,y,w,h=panels[piece];p=np.concatenate([r['points'] for r in rows])[:,:2]
        lo,hi=p.min(0),p.max(0);scale=min((w-30)/(hi[0]-lo[0]),(h-30)/(hi[1]-lo[1]))
        for r in sorted(rows,key=lambda r:r['layer']):
            pp=(r['points'][:,:2]-(lo+hi)/2)*scale;pp[:,1]*=-1;pp+=np.array([x+w/2,y+h/2])
            draw.line([tuple(q) for q in pp],fill=colors[r['tool']-1],width=max(1,round(.4*scale)))
        draw.text((x,y+h),piece.capitalize(),font=font(24),fill='#23384C')
    draw.text((35,1020),'Largura gráfica dos traços: 0,4 mm · não é uma fotografia da impressão',font=font(24),fill='#536276')
    sheet.save(ROOT/'designs'/f'{PREFIX}-percursos.png')
    report={'color_checks':checks,'plates':reviews,'physical_print_tested':False}
    (FOLDER/'toolpath-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path,required=True)
    main(p.parse_args().work_dir)
