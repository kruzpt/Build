// Memorial natalicio: arvore com texto plano embutido e cadeiras de tabuas lisas.
// Unidades: mm. Peças separadas via -D 'part="..."' e -D 'style="boards"|"logs"'.
// O modelo de conceito foi aprovado; as juntas ainda requerem prova fisica.
part = "base";
style = "boards";
variant = 1;
chair_texture = false;      // V4: nenhuma imitação de madeira nas cadeiras
$fn = 72;

base_d = 236;
base_h = 6;
tree_h = 200;
tree_t = 5;
tree_base_y = 64;             // arvore na zona traseira do disco
candle_center_y = -70;       // zona livre, sem peca de vela no projeto
candle_clear_d = 50;
ink_h = 0.56;                 // primeiras camadas: letras e borda, planas na frente
fit_clearance = 0.28;         // folga lateral nominal das espigas
chair_w = 60;
chair_print_scale = 0.75;     // cadeiras menores; todas as juntas escalam juntas
chair_origin_x = 70;
chair_origin_y = -6;
grain_comp = 1/chair_print_scale; // conserva riscos visiveis depois da reducao
side_t = 3.4;
slat_gap = chair_w-2*side_t; // 53.2 mm

// Mensagem editavel: manter linhas curtas e voltar a fatiar depois da alteracao.
line_1 = "Esta";
line_2 = "Luz";
line_3 = "Brilha";
line_4 = "em memória";
line_5 = "dos que festejam";
line_6 = "connosco a partir";
line_7 = "do céu...";
line_8 = "...sei que estarias";
line_9 = "aqui hoje se o céu";
line_10 = "não fosse tão longe...";

module rounded_rect_2d(w,h,r) {
    offset(r=r) square([w-2*r,h-2*r],center=true);
}
module path_2d(pts,d) {
    for(i=[0:len(pts)-2]) hull() {
        translate(pts[i]) circle(d=d);
        translate(pts[i+1]) circle(d=d);
    }
}
module tree_body_2d() {
    union() {
        scale([0.9,1]) polygon(points=[
            [0,167],[13,146],[9,146],[25,126],[19,126],
            [38,105],[30,105],[50,82],[40,82],[60,60],
            [48,60],[68,39],[53,39],[63,5],[-63,5],
            [-53,39],[-68,39],[-48,60],[-60,60],[-40,82],
            [-50,82],[-30,105],[-38,105],[-19,126],
            [-25,126],[-9,146],[-13,146]
        ]);
        // Star overlaps the tree point; no loose island.
        translate([0,179]) polygon(points=[for(i=[0:9])
            let(a=90+i*36,r=i%2==0?20:10) [r*cos(a),r*sin(a)]]);
        // The star joins the tree point with enough overlap for one solid print.
        translate([0,169]) square([7,12],center=true);
        // Two inserts into blind slots in the base.
        translate([-30,2.5]) square([14,5],center=true);
        translate([ 30,2.5]) square([14,5],center=true);
    }
}
module tree_border_2d() {
    difference() {
        tree_body_2d();
        offset(delta=-1.35) tree_body_2d();
    }
}
module line_text(s,y,size,font="Liberation Sans:style=Bold",delta=0.14) {
    translate([0,y]) offset(delta=delta)
        text(s,size=size,font=font,halign="center",valign="baseline");
}
module tree_letters_2d() {
    // Typeface and breaks chosen for reliable 0.4 mm FDM strokes.
    // The front prints against the bed, so the artwork must be mirrored here.
    mirror([1,0,0]) {
    line_text(line_1,128,9.8,"Liberation Serif:style=Bold Italic",0.07);
    line_text(line_2,114,11.5,"Liberation Serif:style=Bold Italic",0.07);
    line_text(line_3,99,12.5,"Liberation Serif:style=Bold Italic",0.07);
    line_text(line_4,87,8.2,"Liberation Sans:style=Bold",0.10);
    line_text(line_5,75,6.3);
    line_text(line_6,63,7.1);
    line_text(line_7,51,8);
    line_text(line_8,39,7.1);
    line_text(line_9,27,7.1);
    line_text(line_10,15,6.8);
    }
}
module tree_ink_2d() {
    intersection() {
        tree_body_2d();
        union() { tree_border_2d(); tree_letters_2d(); }
    }
}
module tree_cream() {
    difference() {
        linear_extrude(height=tree_t) tree_body_2d();
        translate([0,0,-0.02]) linear_extrude(height=ink_h+0.02) tree_ink_2d();
    }
}
module tree_brown() {
    linear_extrude(height=ink_h) tree_ink_2d();
}
module text_coupon_ink_2d() {
    mirror([1,0,0]) line_text("dos que festejam",-2.5,6.3);
}
module text_coupon_cream() {
    difference() {
        linear_extrude(height=2.4) rounded_rect_2d(96,21,2);
        translate([0,0,-0.02]) linear_extrude(height=ink_h+0.02) text_coupon_ink_2d();
    }
}
module text_coupon_brown() {
    linear_extrude(height=ink_h) text_coupon_ink_2d();
}
module joint_coupon() {
    translate([-15,0,0]) difference() {
        linear_extrude(side_t) rounded_rect_2d(18,12,1.4);
        translate([0,0,-0.1]) linear_extrude(side_t+0.2)
            square([3.8,3.8],center=true);
    }
    translate([11,0,0]) {
        linear_extrude(3.2) rounded_rect_2d(14,8,1);
        translate([7+1.65,0,0]) linear_extrude(3.2)
            square([3.3,3.2],center=true);
    }
}
module base_final() {
    difference() {
        cylinder(d=base_d,h=base_h);
        for(x=[-30,30])
            translate([x-(14+fit_clearance*2)/2,tree_base_y-(tree_t+fit_clearance*2)/2,1])
                cube([14+fit_clearance*2,tree_t+fit_clearance*2,base_h+0.2]);
    }
}
function back_x(h) = -25 - (h-61)*0.19;
module side_frame_solid_2d() {
    union() {
        path_2d([[-44,10],[-37,6],[-20,3],[0,3],[20,3],[37,6],[44,10]],6);
        path_2d([[-27,7],[-21,39],[-25,61],[-32,98]],10);
        path_2d([[25,7],[28,38],[28,60]],9);
        path_2d([[-23,42],[29,42]],9);
        path_2d([[-24,61],[27,61],[34,62]],8.5);
        path_2d([[-20,17],[26,17]],5.5);
    }
}
module side_slots_2d(which="boards") {
    // Each slot receives a 3.2 mm tab from a crosspiece.
    for(h=[67,78,89]) translate([back_x(h),h]) square([3.8,3.8],center=true);
    for(x=(which=="logs"?[-14,0,14]:[-11,11]))
        translate([x,42]) square([3.8,3.8],center=true);
    translate([26,17]) square([3.8,3.8],center=true);
}
module side_profile_2d(which="boards") {
    difference(){side_frame_solid_2d();side_slots_2d(which);}
}
// Veios contínuos, ligeiramente ondulados, orientados pelo comprimento das
// travessas. Os nós são laços concêntricos, não círculos estampados.
function beam_points(pts,row,seed) = [
    for(j=[0:len(pts)-2]) for(k=[0:12])
        let(a=pts[j], b=pts[j+1], t=k/12,
            dx=b[0]-a[0], dy=b[1]-a[1], ll=sqrt(dx*dx+dy*dy),
            px=a[0]+dx*t, py=a[1]+dy*t,
            wave=.22*sin((px+py)*29+seed+row*24)+.11*sin((px-py)*67+seed),
            shift=row*1.55+wave)
        [px-dy/ll*shift, py+dx/ll*shift]
];
module beam_veins(pts,rows=2,seed=0) {
    for(row=[-rows:rows]) path_2d(beam_points(pts,row,seed),.68*grain_comp);
}
module grain_ring(cx,cy,rx,ry,phase=0) {
    path_2d([for(a=[0:12:360])
        let(wobble=1+.035*sin(3*a+phase)+.018*sin(5*a-phase))
        [cx+rx*wobble*cos(a),cy+ry*wobble*sin(a)]],.65*grain_comp);
}
module small_beam_knot(cx,cy,phase=0) {
    grain_ring(cx,cy,3.7,1.0,phase);
    grain_ring(cx,cy,6.1,1.8,phase+35);
}
module side_grain_2d(which="boards") {
    intersection() {
        offset(delta=-0.65) side_profile_2d(which);
        union() {
            beam_veins([[-40,9],[-24,6],[-7,4],[16,5],[39,9]],1,12);
            beam_veins([[-27,8],[-22,38],[-26,61],[-32,97]],2,44);
            beam_veins([[25,8],[28,38],[28,59]],2,91);
            beam_veins([[-22,42],[3,42],[28,42]],1,122);
            beam_veins([[-22,61],[4,61],[32,62]],2,169);
            beam_veins([[-17,17],[4,17],[24,17]],1,211);
            small_beam_knot(-9,5.2,18);
            small_beam_knot(9,61.5,83);
            if(which=="logs") small_beam_knot(-26,42,154);
        }
    }
}
module chair_side(which="boards",hand="A") {
    // Both print ornament face up. One is mirrored for outward grain after assembly.
    if(hand=="A") {
        linear_extrude(side_t) side_profile_2d(which);
        if(chair_texture)
            translate([0,0,side_t]) linear_extrude(0.48*grain_comp) side_grain_2d(which);
    } else {
        mirror([1,0,0]) {
            linear_extrude(side_t) side_profile_2d(which);
            if(chair_texture)
                translate([0,0,side_t]) linear_extrude(0.48*grain_comp) side_grain_2d(which);
        }
    }
}
module crosspiece_2d(depth=11) {
    union() {
        rounded_rect_2d(slat_gap,depth,1.3);
        for(s=[-1,1]) translate([s*(slat_gap/2+1.65),0])
            square([3.3,3.2],center=true);
    }
}
function knot_x(variant) = variant==1?-11:variant==2?4:13;
function knot_y(variant,depth) = variant==2?depth*.09:variant==3?-depth*.08:0;
function plank_wave(x,y,seed,kx,ky) = y + .28*sin(x*23+seed+y*13)
    +.11*sin(x*59-seed+y*7)
    +(y<ky?-1:1)*1.35*exp(-pow((x-kx)/9,2)-pow((y-ky)/3.8,2));
module plank_knot(cx,cy,depth,phase=0,factor=1) {
    for(i=[0:3])
        grain_ring(cx,cy,(3.5+i*2.45)*factor,
            (0.9+i*.88)*min(1,depth/10.2)*factor,phase+i*21);
}
module crosspiece_grain_2d(depth=11,which="boards",variant=1) {
    kx=knot_x(variant);
    ky=knot_y(variant,depth);
    intersection() {
        offset(delta=-1) rounded_rect_2d(slat_gap,depth,1.3);
        union() {
            difference() {
                union() {
                    for(i=[0:floor((depth-2.2)/1.65)])
                        let(y=-depth/2+1.1+i*1.65)
                        path_2d([for(x=[-slat_gap/2:1.2:slat_gap/2])
                            [x,plank_wave(x,y,31+i*27+variant*43,kx,ky)]],.66*grain_comp);
                }
                translate([kx,ky]) scale([10.8,min(3.4,depth*.31)]) circle(r=1);
                if(depth>11 && variant!=3) translate([variant==1?16:-16,depth*.12])
                    scale([5.8,depth*.17]) circle(r=1);
            }
            plank_knot(kx,ky,depth,12+variant*33);
            if(depth>11 && variant!=3)
                plank_knot(variant==1?16:-16,depth*.12,depth,118+variant*19,.55);
        }
    }
}
module chair_piece(which="boards",kind="back",variant=1) {
    depth = kind=="seat" ? (which=="logs"?13:19) : (kind=="bar"?6:10.2);
    if(which=="logs" && kind!="bar") {
        linear_extrude(2.4) crosspiece_2d(depth);
        for(i=[0:5]) translate([0,0,2.4+i*.5])
            linear_extrude(.51) offset(delta=-.2-i*.40) rounded_rect_2d(slat_gap,depth,1.3);
        if(chair_texture)
            translate([0,0,5.4]) linear_extrude(.48*grain_comp)
                intersection(){crosspiece_grain_2d(depth,which,variant);offset(delta=-1.8) rounded_rect_2d(slat_gap,depth,1.3);}
    } else {
        linear_extrude(3.2) crosspiece_2d(depth);
        if(chair_texture)
            translate([0,0,3.2]) linear_extrude(.48*grain_comp) crosspiece_grain_2d(depth,which,variant);
    }
}
module wood_coupon() {
    linear_extrude(2.4) rounded_rect_2d(slat_gap,19,1.3);
    translate([0,0,2.4]) linear_extrude(.48*grain_comp)
        crosspiece_grain_2d(19,"boards",2);
}

// Visual assembly only. For printing, export each named part separately.
module chair_assembly(which="boards") {
    color("#986039") multmatrix([
        [0,0,-1,-chair_w/2+side_t],[-1,0,0,0],[0,1,0,base_h],[0,0,0,1]])
        chair_side(which,"A");
    color("#986039") multmatrix([
        [0,0,1,chair_w/2-side_t],[1,0,0,0],[0,1,0,base_h],[0,0,0,1]])
        chair_side(which,"B");
    for(i=[0:2]) let(h=[67,78,89][i]) color("#aa6e40") multmatrix([
        [1,0,0,0],[0,0,-1,-back_x(h)+1.6],[0,1,0,base_h+h],[0,0,0,1]])
        chair_piece(which,"back",i+1);
    for(i=[0:(which=="logs"?2:1)])
        let(x=(which=="logs"?[-14,0,14]:[-11,11])[i])
        color("#aa6e40") translate([0,x,base_h+42-1.6]) chair_piece(which,"seat",i+1);
    color("#aa6e40") multmatrix([
        [1,0,0,0],[0,0,-1,-26+1.6],[0,1,0,base_h+17],[0,0,0,1]])
        chair_piece(which,"bar");
}
module preview() {
    color("#f0e2c4") base_final();
    multmatrix([[-1,0,0,0],[0,0,1,tree_base_y-tree_t/2],[0,1,0,1]]) {
        color("#f4e5c8") tree_cream();
        color("#513420") tree_brown();
    }
    translate([-chair_origin_x,chair_origin_y,base_h*(1-chair_print_scale)])
        rotate([0,0,10]) scale([chair_print_scale,chair_print_scale,chair_print_scale]) chair_assembly("boards");
    translate([chair_origin_x,chair_origin_y,base_h*(1-chair_print_scale)])
        rotate([0,0,-10]) scale([chair_print_scale,chair_print_scale,chair_print_scale]) chair_assembly("boards");
}

if(part=="base") base_final();
else if(part=="tree_cream") tree_cream();
else if(part=="tree_brown") tree_brown();
else if(part=="text_coupon_cream") text_coupon_cream();
else if(part=="text_coupon_brown") text_coupon_brown();
else if(part=="joint_coupon") scale([chair_print_scale,chair_print_scale,chair_print_scale]) joint_coupon();
else if(part=="wood_coupon") scale([chair_print_scale,chair_print_scale,chair_print_scale]) wood_coupon();
else if(part=="side_A") scale([chair_print_scale,chair_print_scale,chair_print_scale]) chair_side(style,"A");
else if(part=="side_B") scale([chair_print_scale,chair_print_scale,chair_print_scale]) chair_side(style,"B");
else if(part=="back") scale([chair_print_scale,chair_print_scale,chair_print_scale]) chair_piece(style,"back",variant);
else if(part=="seat") scale([chair_print_scale,chair_print_scale,chair_print_scale]) chair_piece(style,"seat",variant);
else if(part=="bar") scale([chair_print_scale,chair_print_scale,chair_print_scale]) chair_piece(style,"bar");
else if(part=="preview") preview();
else assert(false,str("Unknown part: ",part));
