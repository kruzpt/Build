// Conector modular para cabos de vassoura, em mm.
// FDM: imprimir verticalmente como desenhado, sobre a face plana inferior.
// Os alojamentos têm entrada circular. A ponta de alívio para impressão
// sem suportes fica apenas no interior, escondida pela boca circular.

part = "connector"; // connector | foot

bore_d = 22.7;              // diâmetro pedido para o FURO, não para o cabo
socket_depth = 39;          // comprimento de apoio do cabo horizontal
round_mouth_lip = 3;        // boca circular sem a ponta visível
body_h = 56;
hub_r = 25;
arm_end_x = 55;
arm_end_r = 21;
socket_axis_h = 22;
screw_clear_d = 3.6;       // passagem para parafuso de madeira Ø3–3,5 mm
screw_head_d = 7.2;
eps = 0.03;
$fn = 96;

// Corte ao longo de X: círculo completo e teto de 45° apenas no interior.
module horizontal_socket_x() {
    r = bore_d / 2;
    start_x = arm_end_x + arm_end_r - socket_depth;
    length_x = socket_depth + 2*eps;
    translate([start_x, 0, socket_axis_h]) {
        rotate([0,90,0]) cylinder(h=length_x, r=r);
        // Após a rotação, o eixo local X negativo torna-se Z positivo.
        rotate([0,90,0]) linear_extrude(height=length_x-round_mouth_lip)
            polygon(points=[[0,-r], [-2*r,0], [0,r]]);
    }
}

module connector_body() {
    linear_extrude(height=body_h) union() {
        hull() { circle(r=hub_r); translate([arm_end_x,0]) circle(r=arm_end_r); }
        hull() { circle(r=hub_r); translate([0,arm_end_x]) circle(r=arm_end_r); }
    }
}

module connector() {
    difference() {
        connector_body();

        // Poste vertical passa de baixo a cima por todos os níveis.
        translate([0,0,-eps]) cylinder(h=body_h+2*eps, d=bore_d);

        // Duas tomadas cegas independentes, a 90 graus.
        horizontal_socket_x();
        rotate([0,0,90]) horizontal_socket_x();

        // Parafuso do poste: acesso pelo lado exterior negativo do eixo X.
        translate([-hub_r-eps,0,body_h/2]) rotate([0,90,0])
            cylinder(h=hub_r-bore_d/2+1.8, d=screw_clear_d, $fn=32);
        translate([-hub_r-0.2,0,body_h/2]) rotate([0,90,0])
            cylinder(h=2.8, d=screw_head_d, $fn=40);

        // Um parafuso vertical a partir da face inferior em cada tomada.
        translate([arm_end_x+5,0,-eps])
            cylinder(h=socket_axis_h-bore_d/2+1.8, d=screw_clear_d, $fn=32);
        translate([arm_end_x+5,0,-0.2])
            cylinder(h=2.8, d=screw_head_d, $fn=40);
        translate([0,arm_end_x+5,-eps])
            cylinder(h=socket_axis_h-bore_d/2+1.8, d=screw_clear_d, $fn=32);
        translate([0,arm_end_x+5,-0.2])
            cylinder(h=2.8, d=screw_head_d, $fn=40);
    }
}

// Pé para receber a ponta inferior de cada poste. Furo cego e retenção lateral.
module foot() {
    foot_d = 76;
    foot_h = 22;
    difference() {
        union() {
            cylinder(h=4, d=foot_d);
            translate([0,0,4]) cylinder(h=foot_h-4, d1=foot_d-6, d2=48);
        }
        translate([0,0,3]) cylinder(h=foot_h-3+eps, d=bore_d);
        translate([-30,0,14]) rotate([0,90,0])
            cylinder(h=20, d=screw_clear_d, $fn=32);
        translate([-30.2,0,14]) rotate([0,90,0])
            cylinder(h=4, d=screw_head_d, $fn=40);
    }
}

if (part == "connector") connector();
else if (part == "foot") foot();
