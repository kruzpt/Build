"""Read AC3D exterior geometry as data, without executing simulator scripts.

Only polygon geometry and parent transforms are used. The original source
base file declares one more root child than is present; accept that known
end-of-file discrepancy after reading all available objects.
"""
from pathlib import Path
import shlex
import numpy as np
import trimesh

def load_ac(path):
 lines=Path(path).read_text(errors='replace').splitlines();idx=next(i for i,l in enumerate(lines) if l.startswith('OBJECT '));objects=[]
 def node(i,parent):
  kind=lines[i].split()[1];i+=1;name=kind;loc=np.zeros(3);rot=np.eye(3);verts=[];faces=[];materials=[]
  while i<len(lines):
   line=lines[i].strip();i+=1
   if not line:continue
   key=line.split()[0]
   if key=='name':name=shlex.split(line)[1]
   elif key=='loc':loc=np.array(list(map(float,line.split()[1:])))
   elif key=='rot':rot=np.array(list(map(float,line.split()[1:]))).reshape(3,3)
   elif key=='numvert':
    count=int(line.split()[1]);verts=np.array([list(map(float,lines[j].split())) for j in range(i,i+count)]);i+=count
   elif key=='numsurf':
    count=int(line.split()[1])
    for j in range(count):
     assert lines[i].startswith('SURF '),(path,i,lines[i]);i+=1;mat=0
     if lines[i].startswith('mat '):mat=int(lines[i].split()[1]);i+=1
     assert lines[i].startswith('refs '),(path,i,lines[i]);nr=int(lines[i].split()[1]);i+=1
     refs=[int(lines[j].split()[0]) for j in range(i,i+nr)];i+=nr
     for k in range(1,nr-1):faces.append((refs[0],refs[k],refs[k+1]));materials.append(mat)
   elif key=='data':i+=1
   elif key=='kids':
    own=np.eye(4);own[:3,:3]=rot;own[:3,3]=loc;tm=parent@own
    if len(verts) and faces:
     v=verts@tm[:3,:3].T+tm[:3,3];m=trimesh.Trimesh(v,faces,process=True)
     objects.append({'name':name,'mesh':m,'materials':materials,'file':Path(path).name})
    for j in range(int(line.split()[1])):
     if i>=len(lines):
      assert kind=='world' and j==int(line.split()[1])-1
      print('Source root child count exceeds available nodes:',path,j,line);break
     i=node(i,tm)
    return i
  raise ValueError('No kids marker')
 end=node(idx,np.eye(4))
 assert not any(line.strip() for line in lines[end:]),'Unconsumed source objects'
 return objects
