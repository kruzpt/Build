// Ensaio V3, apos B nao ter comecado a enroscar. Todas as cotas em mm.
// E: rosca mais solta que B, mesmo avanco hipotetico de 9 mm/volta.
// G: anel liso curto para distinguir diametro de perfil da rosca.
variant = 0; // 0=E, 1=G
$fn = 128;
outer_d = 40;
starts = 3; // HIPOTESE, nao medido
lead = 9; // HIPOTESE, nao medido
e_bore_d = 29.0; // B era 28.6
e_groove_d = 31.1; // B era 30.5
g_bore_d = 29.7; // maior que 29.25 medido na crista PET

module female_grooves(){
    inner_r=e_bore_d/2-0.08;
    outer_r=e_groove_d/2;
    for(start=[0:starts-1])
        rotate([0,0,start*360/starts])
            translate([0,0,-2])
                linear_extrude(height=13,
                    twist=360*13/lead,
                    slices=ceil(13/lead*100),convexity=12)
                    polygon(points=[
                        [inner_r*cos(-34),inner_r*sin(-34)],
                        [outer_r*cos(-19),outer_r*sin(-19)],
                        [outer_r*cos(19),outer_r*sin(19)],
                        [inner_r*cos(34),inner_r*sin(34)]
                    ]);
}

module ring_e(){
    difference(){
        cylinder(d=outer_d,h=9);
        translate([0,0,-.1])cylinder(d=e_bore_d,h=9.2);
        female_grooves();
        translate([0,0,-.01])cylinder(d1=e_bore_d+1.4,d2=e_bore_d,h=.8);
        translate([0,0,8.21])cylinder(d1=e_bore_d,d2=e_bore_d+1.4,h=.8);
        // Cinco entalhes identificam E.
        for(k=[0:4])rotate([0,0,k*12])
            translate([outer_d/2-.4,0,8.45])
                cube([2.2,1.3,1.2],center=true);
    }
}

module gauge_g(){
    difference(){
        cylinder(d=36,h=3);
        translate([0,0,-.1])cylinder(d=g_bore_d,h=3.2);
        translate([0,0,-.01])cylinder(d1=g_bore_d+1,d2=g_bore_d,h=.6);
        // Um entalhe largo identifica o anel liso G.
        translate([17.4,0,2.5])cube([2,4,1.2],center=true);
    }
}

if(variant==0)ring_e(); else gauge_g();
