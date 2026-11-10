// Gorro de Natal personalizavel V2 — silhueta classica curvada
$fn = 96;
parte = "completo"; perfil = "medio"; nome = "Tomás";
espessura_base=3.0; altura_branco=0.8; altura_nome=0.8; altura_dobra=0.4;
fonte="Z003:style=Medium Italic";
function tamanho_nome(p)=p=="curto"?19:p=="comprido"?11.8:15.5;

module aba_2d(){
  hull(){ translate([-38,12]) circle(r=8); translate([38,12]) circle(r=8); }
}
module copa_2d(){
  // Contorno exterior e linha inferior da dobra formam uma unica copa solida.
  polygon(points=[[-38,18],[-31,50],[-14,77],[-2,84],[10,83],[25,72],
                  [35,58],[35,46],[38,18]]);
}
module pompom_cheio_2d(){ translate([34,46]) circle(r=11); }
module silhueta_2d(){ difference(){ union(){aba_2d();copa_2d();pompom_cheio_2d();} translate([34,46]) circle(d=5); } }
module branco_2d(){
  difference(){
    union(){
      intersection(){
        union(){ for(x=[-30,-10,10,30]) translate([x,10]) circle(r=12); }
        translate([-44,0]) square([88,25]);
      }
      pompom_cheio_2d();
    }
    translate([34,46]) circle(d=5);
  }
}
module dobra_2d(){
  intersection(){
    union(){
      hull(){translate([-22,55])circle(r=0.9);translate([-3,62])circle(r=0.9);}
      hull(){translate([-3,62])circle(r=0.9);translate([15,64])circle(r=0.9);}
      hull(){translate([15,64])circle(r=0.9);translate([27,57])circle(r=0.9);}
    }
    copa_2d();
  }
}
module texto_2d(){ translate([0,11.7]) offset(r=0.32) text(nome,size=tamanho_nome(perfil),font=fonte,halign="center",valign="center",spacing=0.9); }
module corpo(){ union(){linear_extrude(espessura_base)silhueta_2d();translate([0,0,2.98])linear_extrude(altura_dobra+0.02)dobra_2d();} }
module branco(){translate([0,0,espessura_base])linear_extrude(altura_branco)branco_2d();}
module nome3d(){translate([0,0,espessura_base+altura_branco])linear_extrude(altura_nome)texto_2d();}
if(parte=="corpo")corpo(); else if(parte=="branco")branco(); else if(parte=="nome")nome3d(); else union(){corpo();branco();nome3d();}
