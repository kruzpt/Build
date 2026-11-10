// Gorro de Natal personalizavel V1
// Unidades: milimetros
// Exemplos de linha de comandos:
// openscad -o nome.stl -D 'parte="nome"' -D 'perfil="curto"' -D 'nome="Lia"' GorroNatalPersonalizavelV1.scad

$fn = 96;

parte = "completo";      // corpo, branco, nome, completo
perfil = "medio";        // curto, medio, comprido
nome = "Tomás";

espessura_base = 3.0;
altura_branco = 0.8;
altura_nome = 0.8;
altura_dobra = 0.5;
diametro_furo = 5.0;
fonte = "Z003:style=Medium Italic";

function tamanho_nome(p) = p == "curto" ? 20.0 : p == "comprido" ? 12.5 : 16.0;
function deslocamento_nome_y(p) = p == "comprido" ? 12.5 : 13.0;

module neve_2d() {
    intersection() {
        union() {
            for (x = [-29.5, -9.8, 9.8, 29.5])
                translate([x, 12.5]) circle(r = 12.8);
        }
        translate([-44, 0]) square([88, 27]);
    }
}

module corpo_gorro_2d() {
    hull() {
        translate([-34, 19]) circle(r = 4.5);
        translate([-25, 53]) circle(r = 7.0);
        translate([-9, 78]) circle(r = 7.5);
        translate([3, 86]) circle(r = 6.0);
        translate([15, 80]) circle(r = 6.0);
        translate([28, 62]) circle(r = 5.0);
        translate([32, 52]) circle(r = 4.0);
    }
}

module ponta_branca_cheia_2d() {
    union() {
        hull() {
            translate([8, 80]) circle(r = 9.0);
            translate([23, 72]) circle(r = 8.5);
            translate([34, 65]) circle(r = 8.0);
        }
        translate([34, 65]) circle(r = 8.0);
    }
}

module ponta_branca_2d() {
    difference() {
        ponta_branca_cheia_2d();
        translate([34, 65]) circle(d = diametro_furo);
    }
}

module silhueta_2d() {
    difference() {
        union() {
            neve_2d();
            corpo_gorro_2d();
            ponta_branca_cheia_2d();
        }
        translate([34, 65]) circle(d = diametro_furo);
    }
}

module dobra_2d() {
    intersection() {
        union() {
            hull() {
                translate([-28, 51]) circle(r = 1.15);
                translate([-12, 55]) circle(r = 1.15);
            }
            hull() {
                translate([-12, 55]) circle(r = 1.15);
                translate([4, 56.5]) circle(r = 1.15);
            }
            hull() {
                translate([4, 56.5]) circle(r = 1.15);
                translate([20, 54]) circle(r = 1.15);
            }
        }
        difference() {
            corpo_gorro_2d();
            ponta_branca_cheia_2d();
        }
    }
}

module texto_2d() {
    // O offset engrossa os tracos finos da letra manuscrita para FDM a 0,4 mm.
    translate([0, deslocamento_nome_y(perfil)])
        offset(r = 0.35)
            text(nome,
                 size = tamanho_nome(perfil),
                 font = fonte,
                 halign = "center",
                 valign = "center",
                 spacing = 0.92);
}

module corpo_vermelho() {
    union() {
        linear_extrude(height = espessura_base) silhueta_2d();
        // 0,02 mm de sobreposicao interna evita duas cascas coplanares no STL.
        translate([0, 0, espessura_base - 0.02])
            linear_extrude(height = altura_dobra + 0.02) dobra_2d();
    }
}

module detalhes_brancos() {
    translate([0, 0, espessura_base])
        linear_extrude(height = altura_branco)
            union() {
                neve_2d();
                ponta_branca_2d();
            }
}

module nome_vermelho() {
    translate([0, 0, espessura_base + altura_branco])
        linear_extrude(height = altura_nome) texto_2d();
}

module modelo_completo() {
    union() {
        corpo_vermelho();
        detalhes_brancos();
        nome_vermelho();
    }
}

if (parte == "corpo") corpo_vermelho();
else if (parte == "branco") detalhes_brancos();
else if (parte == "nome") nome_vermelho();
else modelo_completo();
