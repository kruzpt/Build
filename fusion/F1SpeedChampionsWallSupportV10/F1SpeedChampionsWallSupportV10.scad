// Suporte parede LEGO Speed Champions F1 + piloto V10
$fn=160;
parte="completo"; // completo, berco, amostras_piloto

largura_placa=112; altura_placa=42; espessura_placa=4;
distancia_furos=36; diametro_furo=5.5; diametro_rebaixo=10; profundidade_rebaixo=2;
distancia_bercos=62; largura_berco=12;
diametro_pneu=22; folga_radial=.6; raio_interior=diametro_pneu/2+folga_radial;
altura_berco=18; projecao_berco=27;
profundidade_piloto=14; espessura_piloto=4;
passo_pinos=8; diametro_pino=4.75; altura_pino=1.8;

module placa(){
 difference(){
  translate([-largura_placa/2,0,0])cube([largura_placa,espessura_placa,altura_placa]);
  for(x=[-distancia_furos/2,distancia_furos/2]){
   translate([x,-1,31.5])rotate([-90,0,0])cylinder(d=diametro_furo,h=espessura_placa+2);
   translate([x,espessura_placa-profundidade_rebaixo,31.5])rotate([-90,0,0])
    cylinder(d1=diametro_furo,d2=diametro_rebaixo,h=profundidade_rebaixo+1);
  }
 }
}

module perfil_berco(){
 difference(){
  square([projecao_berco,altura_berco]);
  translate([raio_interior,altura_berco])circle(r=raio_interior);
  translate([0,altura_berco])square([raio_interior*2,raio_interior+2]);
 }
}

module berco(xc){
 translate([xc-largura_berco/2,espessura_placa,0])rotate([90,0,90])
  linear_extrude(height=largura_berco)perfil_berco();
}

module placa_piloto(){
 x_braco=-distancia_bercos/2-largura_berco/2;
 x0=-largura_placa/2-26;
 comprimento=x_braco+largura_berco-x0;
 translate([x0,0,0])cube([comprimento,profundidade_piloto,espessura_piloto]);
 for(x=[x0+10,x0+10+passo_pinos])
  translate([x,9,espessura_piloto])cylinder(d=diametro_pino,h=altura_pino);
}

module amostras_piloto(){
 for(i=[0:2]){
  d=[4.65,4.75,4.85][i];
  translate([i*26,0,0])cube([22,18,3]);
  for(x=[i*26+7,i*26+7+passo_pinos])translate([x,9,3])cylinder(d=d,h=altura_pino);
 }
}

if(parte=="berco")berco(0);
else if(parte=="amostras_piloto")amostras_piloto();
else union(){placa();berco(-distancia_bercos/2);berco(distancia_bercos/2);placa_piloto();}
