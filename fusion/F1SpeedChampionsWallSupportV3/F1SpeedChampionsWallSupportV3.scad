// Primeiro projeto 3D — suporte parede F1 Speed Champions + piloto V3
$fn=160;
parte="completo"; // completo, berco, amostras_piloto

largura_placa=112; altura_placa=42; espessura_placa=4;
distancia_furos=36; diametro_furo=5.5; diametro_rebaixo=10; profundidade_rebaixo=2;
distancia_bercos=62; largura_berco=14;
diametro_pneu=22; folga_radial=.5; espessura_arco=3.2; angulo_berco=175;
passo_pinos=8; diametro_pino=4.75; altura_pino=1.8;

module placa(){
 difference(){
  translate([-largura_placa/2,0,0])cube([largura_placa,espessura_placa,altura_placa]);
  for(x=[-distancia_furos/2,distancia_furos/2]){
   translate([x,-1,31.5])rotate([-90,0,0])cylinder(d=diametro_furo,h=espessura_placa+2);
   translate([x,espessura_placa-profundidade_rebaixo,31.5])rotate([-90,0,0])cylinder(d1=diametro_rebaixo,d2=diametro_furo,h=profundidade_rebaixo+1);
  }
 }
}

function arco(r,a0,a1,n=100)=[for(i=[0:n])let(a=a0+(a1-a0)*i/n)[22+r*cos(a),21+r*sin(a)]];

module perfil_berco(){
 ri=diametro_pneu/2+folga_radial;
 ro=ri+espessura_arco;
 a0=180+(180-angulo_berco)/2;
 a1=360-(180-angulo_berco)/2;
 // Arco inferior + uma nervura retangular curta junto à parede.
 union(){
  polygon(concat(arco(ro,a0,a1),arco(ri,a1,a0)));
  polygon([[0,0],[7,0],[7,18],[10,21],[6.8,21],[4,25],[4,36],[0,36]]);
 }
}

module berco(xc){
 multmatrix([[0,0,1,xc-largura_berco/2],[1,0,0,espessura_placa],[0,1,0,0],[0,0,0,1]])
  linear_extrude(height=largura_berco)perfil_berco();
}

module aba_piloto(){
 x0=-largura_placa/2-28;
 translate([x0,0,0])cube([28,22,3]);
 for(x=[x0+10,x0+10+passo_pinos])translate([x,12,3])cylinder(d=diametro_pino,h=altura_pino);
 hull(){translate([x0+24,0,0])cube([4,9,4]);translate([x0+24,0,0])cube([4,4,17]);}
}

module amostras_piloto(){
 for(i=[0:2]){
  d=[4.65,4.75,4.85][i];translate([i*26,0,0])cube([22,18,3]);
  for(x=[i*26+7,i*26+7+passo_pinos])translate([x,9,3])cylinder(d=d,h=altura_pino);
 }
}

if(parte=="berco")berco(0);
else if(parte=="amostras_piloto")amostras_piloto();
else union(){placa();berco(-distancia_bercos/2);berco(distancia_bercos/2);aba_piloto();}
