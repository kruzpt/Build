"""Publish reviewable geometry previews and a self-contained offline package."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def render_model(parts, size=(850, 490), exploded=False):
    vertices=[]; faces=[]; fills=[]; offset=0
    colors=np.array([[244,229,196],[35,78,58],[113,144,113],[181,22,54]], dtype=float)
    for p in parts:
        v=np.array(p['mesh']['vertices'], dtype=float)
        if p['piece']:v[:,2]+=17 if exploded else 2.6
        vertices.append(v); faces.append(np.array(p['mesh']['triangles'])+offset)
        fills.extend([colors[p['color']-1]]*len(p['mesh']['triangles']));offset+=len(v)
    v=np.concatenate(vertices); f=np.concatenate(faces);col=np.array(fills)
    rz=np.deg2rad(-14);rx=np.deg2rad(48)
    rotz=np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
    rotx=np.array([[1,0,0],[0,np.cos(rx),np.sin(rx)],[0,-np.sin(rx),np.cos(rx)]])
    camera=v@rotz.T@rotx.T
    tris=camera[f]; normals=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0])
    lengths=np.linalg.norm(normals,axis=1);ok=lengths>1e-10
    normals[ok]/=lengths[ok,None]
    visible=ok&(normals[:,2]>.000001)
    lo=camera[:,:2].min(0);hi=camera[:,:2].max(0)
    scale=min((size[0]-40)/(hi[0]-lo[0]),(size[1]-30)/(hi[1]-lo[1]))
    xy=(camera[:,:2]-(lo+hi)/2)*scale+np.array(size)/2
    xy[:,1]=size[1]-xy[:,1]
    pixels=np.full((size[1],size[0],3),[255,253,248],dtype=np.uint8)
    depth=np.full((size[1],size[0]),-np.inf)
    light=np.array([-.3,.2,.9]);light/=np.linalg.norm(light)
    intensity=.60+.40*np.maximum(0,normals@light)
    # A depth buffer is necessary: sorting long text triangles by their centres
    # can wrongly paint the cream base over the red relief in oblique views.
    for i in np.flatnonzero(visible):
        if not visible[i]:continue
        q=xy[f[i]];z=tris[i,:,2]
        xmin=max(0,int(np.floor(q[:,0].min())));xmax=min(size[0]-1,int(np.ceil(q[:,0].max())))
        ymin=max(0,int(np.floor(q[:,1].min())));ymax=min(size[1]-1,int(np.ceil(q[:,1].max())))
        if xmin>xmax or ymin>ymax:continue
        xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
        det=(q[1,1]-q[2,1])*(q[0,0]-q[2,0])+(q[2,0]-q[1,0])*(q[0,1]-q[2,1])
        if abs(det)<1e-9:continue
        a=((q[1,1]-q[2,1])*(xx-q[2,0])+(q[2,0]-q[1,0])*(yy-q[2,1]))/det
        b=((q[2,1]-q[0,1])*(xx-q[2,0])+(q[0,0]-q[2,0])*(yy-q[2,1]))/det
        c=1-a-b;zz=a*z[0]+b*z[1]+c*z[2]
        old=depth[ymin:ymax+1,xmin:xmax+1]
        visible_pixel=(a>=-1e-7)&(b>=-1e-7)&(c>=-1e-7)&(zz>old)
        old[visible_pixel]=zz[visible_pixel]
        pixels[ymin:ymax+1,xmin:xmax+1][visible_pixel]=np.clip(col[i]*intensity[i],0,255).astype(np.uint8)
    return Image.fromarray(pixels)


def sheet(work):
    im=Image.new('RGB',(1650,1240),'#fffdf8');d=ImageDraw.Draw(im)
    font=lambda n:ImageFont.truetype(FONT,n)
    d.text((35,25),'Coroas de Natal V1 · geometria real do gerador',font=font(34),fill='#234e3a')
    d.text((35,78),'100 mm · duas peças para colar · texto, contorno e apoios recalculados em conjunto',font=font(23),fill='#5c6d5f')
    cases=[('clemente-2026','Nome + ano'),('avo-dulce-2026','Três linhas e acentos'),('lia','Nome curto: prolongamentos visíveis')]
    for i,(key,label) in enumerate(cases):
        source=Image.open(work/(key+'-CAD.png')).convert('RGB');source.thumbnail((525,460),Image.Resampling.LANCZOS)
        im.paste(source,(i*550+(550-source.width)//2,130))
        d.text((i*550+28,595),label,font=font(21),fill='#234e3a')
    d.line((30,640,1620,640),fill='#c5cdbe',width=2)
    d.text((35,665),'Montagem: texto sobre os dois apoios planos',font=font(26),fill='#234e3a')
    parts=json.loads((work/'clemente-2026-meshes.json').read_text())
    im.paste(render_model(parts,(900,460),exploded=True),(20,715))
    d.text((940,700),'Peça 1 · coroa + apoios',font=font(23),fill='#234e3a')
    d.text((940,740),'Espessura máxima: 2,60 mm',font=font(21),fill='#5c6d5f')
    d.text((940,805),'Peça 2 · texto + contorno creme',font=font(23),fill='#234e3a')
    d.text((940,845),'Espessura: 2,12 mm',font=font(21),fill='#5c6d5f')
    d.text((940,905),'Dois contactos de Ø 4,90 mm',font=font(23),fill='#234e3a')
    d.text((940,945),'37,69 mm² de área total para cola',font=font(21),fill='#5c6d5f')
    d.text((940,1010),'Montada: 4,72 mm + película de cola',font=font(21),fill='#234e3a')
    d.text((940,1050),'Argola: furo de 3 mm',font=font(21),fill='#234e3a')
    d.text((35,1190),'Prévia calculada das malhas · separação exagerada na vista de montagem · ensaio físico por fazer',font=font(22),fill='#5c6d5f')
    im.save(ROOT/'designs/coroa-natal-v1-CAD-montagem.png')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,default=Path('/tmp/coroa-v1-tests-final'));args=parser.parse_args()
    report=json.loads((HERE/'bambu-validation.json').read_text());cases={r['key']:r for r in report['cases']}
    files=[]
    for key in ['clemente-2026','avo-dulce-2026','lia']:
        source=args.work/(key+'.3mf');assert hashlib.sha256(source.read_bytes()).hexdigest()==cases[key]['sha256']
        target=ROOT/'downloads'/f'coroa-natal-v1-{key}-A1-AMS.3mf';shutil.copyfile(source,target);files.append(target)
    sheet(args.work)
    target=ROOT/'downloads/coroa-natal-v1-pacote-bambu.zip'
    help_text='''COROAS DE NATAL V1 — COMEÇAR AQUI

1. Extrair este ZIP para uma pasta.
2. Abrir personalizar.html no Chrome ou Edge (duplo clique).
3. Escrever o nome, segunda linha e ano opcional. Conferir a prévia.
4. Descarregar o 3MF e abrir como PROJETO no Bambu Studio.
5. Mapear os rolos no AMS Lite e fatiar os dois pratos.

Prato 01: coroa com os apoios personalizados.
Prato 02: letras vermelhas sobre contorno creme, numa só peça.
Colar a peça do texto nos dois apoios planos da coroa.
Usar sempre a coroa e o texto do mesmo ficheiro.

O formulário funciona sem internet; não precisa de instalação de fontes.
Para editar depois, abrir aqui um 3MF exportado por este gerador.
A edição dinâmica não é feita no editor de texto do Bambu Studio.

A1 + AMS Lite, bico 0,4 mm, PLA, PEI texturado. Generic PLA é um ponto
de partida, não uma calibração do teu rolo. Fazer primeiro uma unidade
para testar o acabamento e a colagem. Não houve ainda teste físico.

Fontes: Pacifico e Leckerli One. A fonte exata da fotografia não foi
identificada. Os exemplos correspondem à geometria real mostrada na prévia.
'''
    (HERE/'COMEÇAR-AQUI.txt').write_text(help_text)
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        z.write(ROOT/'downloads/coroa-natal-v1-personalizar.html','personalizar.html')
        z.write(HERE/'COMEÇAR-AQUI.txt','COMEÇAR-AQUI.txt')
        readme=(HERE/'README.md').read_text()
        base='https://github.com/kruzpt/Build/blob/main/'
        def absolute_link(match):
            link=match.group(1)
            if link.startswith('http'):return match.group(0)
            resolved=(HERE/link).resolve().relative_to(ROOT)
            return ']('+base+str(resolved)+')'
        z.writestr('README.md',re.sub(r'\]\(([^)]+)\)',absolute_link,readme))
        for p in files:z.write(p,'exemplos/'+p.name)
        for p in [ROOT/'designs/coroa-natal-v1-CAD-montagem.png',ROOT/'designs/coroa-natal-v1-formulario.png']:
            z.write(p,'imagens/'+p.name)
        for p in list((HERE/'fonts').glob('*OFL.txt'))+list((HERE/'vendor').glob('*LICENSE.txt')):
            z.write(p,'licencas/'+p.name)
        z.write(HERE/'THIRD_PARTY.md','licencas/THIRD_PARTY.md')
    with ZipFile(target) as z:assert z.testzip() is None
    files += [target,ROOT/'downloads/coroa-natal-v1-personalizar.html']
    manifest={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}
    (HERE/'release-files.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for p in files:print(p.name,p.stat().st_size)


if __name__=='__main__':main()
