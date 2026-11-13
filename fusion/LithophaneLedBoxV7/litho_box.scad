// Caixa paramétrica para litofania 160 x 124 x 3 mm.
// Conceito V5 aprovado; espessura LED e tomada USB medidas pelo utilizador.
// Imprimir body com a frente em Z=0, lid e retainer com a face plana em Z=0.

part = "body"; // body, lid, retainer, assembly
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
led_total_thickness = 2.04; // medida indicada para o LED; confirmar difusor
retainer_t = 1.8;
retainer_xy_clearance = 0.2; // por lado

// A USB-C esta no centro da extremidade curta do PCB, lado direito.
usb_port_w = 8.88; // largura exterior da tomada medida
usb_port_h = 3.04; // altura exterior da tomada medida
usb_notch_width_y = 20; // reserva para o corpo da FICHA, ainda nao medido
usb_notch_start_x = 76; // relativo ao centro da placa
usb_body_notch_from_back = 7; // AJUSTAR a altura da porta

litho_pocket_w = litho_w + 2*litho_xy_clearance;
litho_pocket_h = litho_h + 2*litho_xy_clearance;
litho_pocket_d = litho_t + litho_z_clearance;
panel_back_z = front_lip_t + litho_pocket_d;
body_depth = panel_back_z + light_gap + led_total_thickness + rear_seat_depth;
seat_start_z = body_depth - rear_seat_depth;
rear_lid_w = rear_seat_w - 2*rear_lid_xy_clearance;
rear_lid_h = rear_seat_h - 2*rear_lid_xy_clearance;
retainer_w = inner_w - 2*retainer_xy_clearance;
retainer_h = inner_h - 2*retainer_xy_clearance;
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
        // Camara luminosa com espaco para o aro retentor.
        translate([-inner_w/2, -inner_h/2, panel_back_z-eps])
            cube([inner_w, inner_h, seat_start_z-panel_back_z+2*eps]);
        // Rebaixo posterior: deixa uma aba de apoio de 3 mm.
        translate([-rear_seat_w/2, -rear_seat_h/2, seat_start_z-eps])
            cube([rear_seat_w, rear_seat_h, rear_seat_depth+2*eps]);
        // Alivio no bordo traseiro do corpo para ficha USB exterior.
        translate([inner_w/2-eps, -usb_notch_width_y/2, body_depth-usb_body_notch_from_back])
            cube([outer_w/2-inner_w/2+2*eps, usb_notch_width_y, usb_body_notch_from_back+eps]);
    }
}

module lid() {
    difference() {
        translate([-rear_lid_w/2, -rear_lid_h/2, 0])
            cube([rear_lid_w, rear_lid_h, rear_lid_t]);
        // Rebaixo aberto ate a tomada fixa na extremidade curta do LED.
        translate([usb_notch_start_x, -usb_notch_width_y/2, -eps])
            cube([rear_lid_w/2-usb_notch_start_x+eps, usb_notch_width_y, rear_lid_t+2*eps]);
    }
}

module retainer() {
    difference() {
        translate([-retainer_w/2, -retainer_h/2, 0])
            cube([retainer_w, retainer_h, retainer_t]);
        translate([-front_window_w/2, -front_window_h/2, -eps])
            cube([front_window_w, front_window_h, retainer_t+2*eps]);
    }
}

if (part == "body") body();
else if (part == "lid") lid();
else if (part == "retainer") retainer();
else if (part == "assembly") {
    color("#303d49") body();
    color("#e4d9ba") translate([0,0,front_lip_t+litho_t/2])
        cube([litho_w, litho_h, litho_t], center=true);
    color("#a4b4b8") translate([0,0,panel_back_z]) retainer();
    color("#dbe4e9") translate([0,0,seat_start_z]) lid();
}
