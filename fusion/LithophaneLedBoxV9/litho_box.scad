// Caixa paramétrica para litofania 160 x 124 x 3 mm.
// Conceito V5 aprovado; espessura LED e tomada USB medidas pelo utilizador.
// USB-C perpendicular a placa: a janela fica apenas na tampa opaca.
// Imprimir body com a frente em Z=0, lid com a face plana em Z=0.

part = "body"; // body, lid, assembly
$fn = 48;

// Elementos medidos e dimensões propostas (mm)
litho_w = 160;
litho_h = 124;
litho_t = 3;
outer_w = 178;
outer_h = 142;
front_window_w = 156;
front_window_h = 120;
front_lip_t = 2;
litho_xy_clearance = 0.2; // por lado
litho_z_clearance = 0.4;
inner_w = 166;
inner_h = 130;
rear_seat_w = 172;
rear_seat_h = 136;
rear_seat_depth = 2.5;
rear_lid_xy_clearance = 0.2; // por lado
rear_lid_t = 2.4;
light_gap = 15; // verso da litofania ate face emissora do LED
led_total_thickness = 2.04; // espessura total: face superior luminosa ate base traseira

// Porta USB-C aponta para TRAS da placa, junto da extremidade direita.
usb_port_w = 8.88; // largura exterior da tomada medida
usb_port_h = 3.04; // altura exterior da tomada medida
usb_center_x = 76; // ajustar com a placa real se necessario
usb_center_y = 0;
usb_window_x = 12; // folga para inserir a ficha pela traseira
usb_window_y = 18;

litho_pocket_w = litho_w + 2*litho_xy_clearance;
litho_pocket_h = litho_h + 2*litho_xy_clearance;
litho_pocket_d = litho_t + litho_z_clearance;
panel_back_z = front_lip_t + litho_pocket_d;
body_depth = panel_back_z + light_gap + led_total_thickness + rear_seat_depth;
seat_start_z = body_depth - rear_seat_depth;
rear_lid_w = rear_seat_w - 2*rear_lid_xy_clearance;
rear_lid_h = rear_seat_h - 2*rear_lid_xy_clearance;
eps = 0.02;

module body() {
    difference() {
        translate([-outer_w/2, -outer_h/2, 0])
            cube([outer_w, outer_h, body_depth]);
        // Janela frontal: frente impressa sobre o prato.
        translate([-front_window_w/2, -front_window_h/2, -eps])
            cube([front_window_w, front_window_h, front_lip_t+2*eps]);
        // Assento da litofania, inserida pelas costas.
        translate([-litho_pocket_w/2, -litho_pocket_h/2, front_lip_t-eps])
            cube([litho_pocket_w, litho_pocket_h, litho_pocket_d+2*eps]);
        // Camara luminosa. A litofania e colada na margem escondida.
        translate([-inner_w/2, -inner_h/2, panel_back_z-eps])
            cube([inner_w, inner_h, seat_start_z-panel_back_z+2*eps]);
        // Rebaixo posterior: deixa uma aba de apoio de 3 mm.
        translate([-rear_seat_w/2, -rear_seat_h/2, seat_start_z-eps])
            cube([rear_seat_w, rear_seat_h, rear_seat_depth+2*eps]);
        // Laterais do corpo inteiras, sem abertura para USB.
    }
}

module lid() {
    difference() {
        translate([-rear_lid_w/2, -rear_lid_h/2, 0])
            cube([rear_lid_w, rear_lid_h, rear_lid_t]);
        // Janela FECHADA no plano da tampa, para a porta voltada para tras.
        translate([usb_center_x-usb_window_x/2,
                   usb_center_y-usb_window_y/2, -eps])
            cube([usb_window_x, usb_window_y, rear_lid_t+2*eps]);
    }
}

if (part == "body") body();
else if (part == "lid") lid();
else if (part == "assembly") {
    color("#303d49") body();
    color("#e4d9ba") translate([0,0,front_lip_t+litho_t/2])
        cube([litho_w, litho_h, litho_t], center=true);
    color("#dbe4e9") translate([0,0,seat_start_z]) lid();
}
