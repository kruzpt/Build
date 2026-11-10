// Rascunho V3 — geometria fiel ao conceito aprovado. Unidades: mm.
$fn=128;
parte="completo"; nome="Tomás"; perfil="medio";
base=3.0; branco_h=0.8; texto_h=0.8; dobra_h=0.45;
fonte_previa="Lobster:style=Regular";
function tamanho(p)=p=="curto"?15.5:p=="comprido"?10.8:14.5;

module aba_2d(){
  for(x=[-34,-17,0,17,34]) translate([x,11]) circle(r=13);
}

module copa_2d(){
  // Percurso exterior curvo, ponta caída e recorte interior junto ao pompom.
  offset(r=5) offset(delta=-5)
    polygon(points=[[-41,16],[-38,39],[-31,60],[-19,77],[-5,87],[8,90],
                    [20,86],[29,77],[36,66],[41,54],[39,47],[35,45],
                    [31,47],[28,53],[25,56],[21,55],[19,51],[20,46],
                    [25,40],[31,34],[36,16]]);
}

module pompom_cheio(){ translate([40,45]) circle(r=11.5); }
module silhueta(){ difference(){union(){aba_2d();copa_2d();pompom_cheio();}translate([40,45])circle(d=5);} }
module branco_2d(){difference(){union(){aba_2d();pompom_cheio();}translate([40,45])circle(d=5);} }

module dobra_2d(){
  intersection(){
    union(){
      hull(){translate([-30,43])circle(r=1.15);translate([-13,49])circle(r=1.15);}
      hull(){translate([-13,49])circle(r=1.15);translate([4,51])circle(r=1.15);}
      hull(){translate([4,51])circle(r=1.15);translate([19,49])circle(r=1.15);}
    }
    copa_2d();
  }
}
module texto_2d(){translate([0,10])offset(r=.32)text(nome,size=tamanho(perfil),font=fonte_previa,halign="center",valign="center",spacing=.9);}
module corpo(){union(){linear_extrude(base)silhueta();translate([0,0,base-.02])linear_extrude(dobra_h+.02)dobra_2d();}}
module branco(){translate([0,0,base])linear_extrude(branco_h)branco_2d();}
module texto3d(){translate([0,0,base+branco_h])linear_extrude(texto_h)texto_2d();}
if(parte=="corpo")corpo();else if(parte=="branco")branco();else if(parte=="nome")texto3d();else union(){corpo();branco();texto3d();}
