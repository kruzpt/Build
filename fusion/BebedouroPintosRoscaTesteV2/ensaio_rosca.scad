// Cupao V2 de ensaio da rosca da garrafa de 500 ml. Unidades: mm.
// Prototipo de encaixe, nao e o copo final nem uma rosca PET identificada.
// Boca corrigida: diametro exterior maximo 29.25, boca ate base da rosca 7.20.
// A/B: avanco 9 mm; C/D: avanco 10.5 mm. O numero de entradas (3) e hipotese.
// Nunca forcar a garrafa. Se nao entrar a mao, parar e medir o perfil real.

variant = 0; // 0=A, 1=B, 2=C, 3=D; -1=disposicao de referencia
$fn = 128;
height = 9;
outer_d = 40;
starts = 3;
lead = variant < 2 ? 9 : 10.5;
bore_d = variant % 2 == 0 ? 28.2 : 28.6;
groove_d = variant % 2 == 0 ? 30.1 : 30.5;

module female_grooves(lead_mm,root_d,crest_d){
    // Banda helicoidal com flancos inclinados. Perfil experimental para a
    // primeira prova; nao pressupoe norma de gargalo especifica.
    inner_r=root_d/2-0.08;
    outer_r=crest_d/2;
    a=34;
    b=19;
    for(start=[0:starts-1])
        rotate([0,0,start*360/starts])
            translate([0,0,-2])
                linear_extrude(height=height+4,
                    twist=360*(height+4)/lead_mm,
                    slices=ceil((height+4)/lead_mm*100),convexity=12)
                    polygon(points=[
                        [inner_r*cos(-a),inner_r*sin(-a)],
                        [outer_r*cos(-b),outer_r*sin(-b)],
                        [outer_r*cos( b),outer_r*sin( b)],
                        [inner_r*cos( a),inner_r*sin( a)]
                    ]);
}

module coupon(v){
    l=v<2?9:10.5;
    bd=v%2==0?28.2:28.6;
    gd=v%2==0?30.1:30.5;
    difference(){
        cylinder(d=outer_d,h=height);
        translate([0,0,-.1])cylinder(d=bd,h=height+.2);
        female_grooves(l,bd,gd);
        translate([0,0,-.01])cylinder(d1=bd+1.4,d2=bd,h=.8);
        translate([0,0,height-.79])cylinder(d1=bd,d2=bd+1.4,h=.8);
        // 1/2/3/4 marcas no topo distinguem A/B/C/D, sem letras finas.
        for(k=[0:v])rotate([0,0,k*12])
            translate([outer_d/2-.4,0,height-.55])
                cube([2.2,1.3,1.2],center=true);
    }
}

if(variant<0){for(v=[0:3])translate([(v%2)*50,floor(v/2)*50,0])coupon(v);}
else coupon(variant);
