// Caixa Maria / Bohemian Rhapsody V1. Unidades: mm.
// Medidas PROVISORIAS; editar parameters.scad ou regenerar a partir do JSON.
include <parameters.scad>
part = "assembly"; // body, lid_black, lid_purple, lid_gold, lid_rings,
                   // lid_complete, male_test, female_test, assembly
with_rings = false;
fit_clearance = thread_radial_clearance;
$fn = segments;
eps=0.02;
inner_r=cookie_diameter/2+cookie_radial_clearance;
root_r=inner_r+wall;
body_h=base+stack_height+top_clearance;
lid_h=lid_face+lid_skirt;
assembly_z=body_h+lid_face;
lid_r=root_r+thread_depth+thread_radial_clearance+lid_wall;
thread_z=body_h-thread_top_margin-thread_base_width/2-turns*pitch;
test_bottom=thread_z-thread_base_width/2-0.6;
function t_f(i,n)=min(1,i*360*turns/n/thread_ramp_degrees,(n-i)*360*turns/n/thread_ramp_degrees);
function tp(i,j,n,clearance,axial,female)=let(start=female?-360:0,a=start+i*(360*turns-start)/n,f=female?1:t_f(i,n),
 r=(j==0||j==3)?root_r+clearance-thread_embed:root_r+clearance+thread_depth*f,
 dz=j==0?-thread_base_width/2-axial:j==1?-thread_crest_width/2-axial:j==2?thread_crest_width/2+axial:thread_base_width/2+axial)
 [r*cos(a),r*sin(a),thread_z+a/360*pitch+dz];
module thread(clearance=0,axial=0,female=false){
 n=ceil(thread_segments_per_turn*(turns+(female?1:0)));
 polyhedron(points=[for(i=[0:n])for(j=[0:3])tp(i,j,n,clearance,axial,female)],
 faces=concat([[0,1,2,3]],
 [for(i=[0:n-1])for(j=[0:3])each [[4*i+j,4*(i+1)+j,4*(i+1)+(j+1)%4],[4*i+j,4*(i+1)+(j+1)%4,4*i+(j+1)%4]]],
 [[4*n+3,4*n+2,4*n+1,4*n]]),convexity=10);
}
module body(){difference(){union(){cylinder(h=body_h-0.5,r=root_r);
 translate([0,0,body_h-0.5])cylinder(h=0.5,r1=root_r,r2=root_r-0.5);thread();}
 translate([0,0,base])cylinder(h=body_h+eps,r=inner_r);}}
module lid_complete(clearance=thread_radial_clearance){difference(){
 cylinder(h=lid_h,r=lid_r);
 translate([0,0,lid_face])cylinder(h=lid_skirt+eps,r=root_r+clearance);
 translate([0,0,lid_h-entry_chamfer])cylinder(h=entry_chamfer+eps,r1=root_r+clearance,r2=root_r+clearance+entry_chamfer+eps);
 intersection(){translate([0,0,assembly_z])rotate([180,0,0])thread(clearance,thread_axial_clearance,true);translate([0,0,lid_face])cylinder(h=lid_skirt+eps,r=lid_r+1);}
}}
// Silhueta simplificada de palco: punho elevado e haste de microfone.
module singer_2d(){
 translate([0,9])scale([0.72,0.72])translate([0,-4.1])union(){
 offset(r=0.12)offset(delta=-0.12)polygon(points=[[-5.9,-6],[-3.2,-5.8],[-1.1,-1.4],[0.5,-1.1],[2.7,-5.7],[5.3,-6],[5.8,-5.2],[4.2,-4.7],[3.1,1.8],[2.5,4.2],[3.8,3.5],[4.8,4.1],[4.6,5.0],[2.8,6.8],[1.6,7.4],[0.9,8.1],[1.2,10],[0.6,11.3],[-0.5,11.5],[-1.3,10.8],[-1.6,9.6],[-1,8.7],[-1.1,7.6],[-2.2,7.3],[-3.4,9.5],[-4.5,12.6],[-4.3,13.5],[-4.9,14.3],[-5.8,14],[-6.1,13.1],[-5.9,12.5],[-4.9,8.7],[-3.6,5.8],[-2.4,4.8],[-1.8,2.1],[-2.0,0.4],[-3.3,-2.3],[-4.6,-4.8],[-5.9,-5.0]]);
 hull(){translate([4.4,4.3])circle(r=.42);translate([6.2,-4.0])circle(r=.42);}
 }}
module gold_2d(){
 singer_2d();circle(r=1.15); // centro visual, nao e um furo passante
 for(i=[0:1])translate([0,-5.0-i*5.0])offset(delta=text_expansion)
 text(i==0?text_line_1:text_line_2,size=text_size,font="DejaVu Sans:style=Bold",halign="center",valign="center",spacing=1);
 // Traços largos, sem brasão de detalhe fino.
}
module gold(){linear_extrude(color_depth)mirror([0,1,0])gold_2d();}
module label(){linear_extrude(color_depth)difference(){circle(d=label_diameter);mirror([0,1,0])gold_2d();}}
module rings(){linear_extrude(color_depth)union(){
 for(r=[label_diameter/2+2:2.4:lid_r-2])difference(){circle(r=r+ring_width/2);circle(r=r-ring_width/2);}
}}
module black(){difference(){lid_complete();gold();label();if(with_rings)rings();}}
module male_test(){translate([0,0,-test_bottom])difference(){intersection(){body();translate([0,0,test_bottom])cylinder(h=body_h-test_bottom+eps,r=lid_r+2);}cylinder(h=body_h+eps,r=inner_r);}}
module female_test(){translate([0,0,-lid_face])difference(){
 lid_complete(fit_clearance);translate([0,0,-eps])cylinder(h=lid_face+eps,r=lid_r+1);
 for(i=[0:(fit_clearance<.275?1:fit_clearance<.35?2:3)-1])rotate([0,0,i*12])
 translate([lid_r-.15,0,lid_h-.6])cylinder(h=.7,r=.45);
}}
if(part=="body")body();
else if(part=="lid_black")black();
else if(part=="lid_purple")label();
else if(part=="lid_gold")gold();
else if(part=="lid_rings")rings();
else if(part=="lid_complete")lid_complete();
else if(part=="male_test")male_test();
else if(part=="female_test")female_test();
else if(part=="assembly"){
 color("white")body();
 translate([0,0,assembly_z])rotate([180,0,0]){
 color([.03,.03,.04])black();color([.25,.05,.32])label();color([.85,.65,.25])gold();if(with_rings)color([.11,.11,.12])rings();}
}
