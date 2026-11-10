// V6 — curvas V5, argola superior equilibrada e nome editável no Bambu.
$fn=160;
parte="completo"; nome="Tomás"; perfil="medio";
base=3; branco_h=.8; texto_h=.8; dobra_h=.45;
fonte="Lobster:style=Regular";
passos=28;
function tamanho(p)=p=="curto"?15.5:p=="comprido"?10.8:14.5;

function bz(a,b,c,d,t) =
  [pow(1-t,3)*a[0]+3*pow(1-t,2)*t*b[0]+3*(1-t)*t*t*c[0]+t*t*t*d[0],
   pow(1-t,3)*a[1]+3*pow(1-t,2)*t*b[1]+3*(1-t)*t*t*c[1]+t*t*t*d[1]];
function seg(a,b,c,d,n=passos)=[for(i=[0:n-1])bz(a,b,c,d,i/n)];

module copa_2d(){
  polygon(concat(
    seg([-41,16],[-42,40],[-38,58],[-29,72]),
    seg([-29,72],[-20,86],[-8,93],[2,94]),
    seg([2,94],[12,95],[20,90],[25,84]),
    seg([25,84],[35,76],[42,65],[44,56]),
    seg([44,56],[46,51],[45,47],[42,44]),
    seg([42,44],[39,41],[35,41],[32,44]),
    seg([32,44],[29,47],[29,54],[24,58]),
    seg([24,58],[19,62],[13,57],[15,51]),
    seg([15,51],[17,44],[22,39],[27,35]),
    seg([27,35],[34,29],[37,22],[38,16]),
    [[-41,16]]));
}
module aba_2d(){for(x=[-34,-17,0,17,34])translate([x,11])circle(r=13);}
module pompom(){translate([44,43])circle(r=11.5);}
module argola_topo(){translate([2.1,98])circle(r=7);}
module furo_topo(){translate([2.1,98])circle(d=5);}
module silhueta(){difference(){union(){copa_2d();aba_2d();pompom();argola_topo();}furo_topo();}}
module branco_2d(){union(){aba_2d();pompom();}}

module dobra_2d(){
  pts=seg([-29,44],[-14,51],[4,55],[21,49],40);
  intersection(){
    union(){for(i=[0:len(pts)-2])hull(){translate(pts[i])circle(r=1.05);translate(pts[i+1])circle(r=1.05);}}
    copa_2d();
  }
}
module texto_2d(){translate([0,10])offset(r=.32)text(nome,size=tamanho(perfil),font=fonte,halign="center",valign="center",spacing=.9);}
module corpo(){union(){linear_extrude(base)silhueta();translate([0,0,2.98])linear_extrude(dobra_h+.02)dobra_2d();}}
module branco(){translate([0,0,base])linear_extrude(branco_h)branco_2d();}
module texto3d(){translate([0,0,base+branco_h])linear_extrude(texto_h)texto_2d();}
if(parte=="corpo")corpo();else if(parte=="branco")branco();else if(parte=="nome")texto3d();else union(){corpo();branco();texto3d();}
