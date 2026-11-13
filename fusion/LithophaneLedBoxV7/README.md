# Caixa LED para litofania — CAD paramétrico V7

Baseado no [conceito V5 aprovado](../../designs/lithoavos-caixa-led-conceito-v5.png). O modelo é editável em [litho_box.scad](litho_box.scad). Os STL em [`downloads/lithoavos-caixa-led-v7/`](../../downloads/lithoavos-caixa-led-v7/) incluem as medidas que o utilizador acabou de fornecer: **LED com 2,04 mm de espessura e porta USB-C de 8,88 × 3,04 mm**. Falta testar a ficha do cabo e o encaixe físico da placa.

## Peças e montagem

1. **Corpo** (`corpo.stl`): 178 × 142 × 24,94 mm; imprimir com a frente no prato. Janela frontal de 156 × 120 mm e alojamento de 160,4 × 124,4 × 3,4 mm para a litofania original de 160 × 124 × 3 mm.
2. **Aro** (`aro.stl`): 165,6 × 129,6 × 1,8 mm; imprimir plano. Entra pela traseira, apoia-se na margem da litofania e é fixado ao corpo com pequenos pontos de cola. A abertura interna é 156 × 120 mm.
3. **Tampa** (`tampa.stl`): 171,6 × 135,6 × 2,4 mm; imprimir plana. Encaixa no rebaixo de 172 × 136 × 2,5 mm, com folga nominal de 0,2 mm por lado e aba de apoio de 3 mm. O LED é fixado na face interna. Depois dos testes, colar só na aba periférica. Não há parafusos.

A placa LED roda 90° para acompanhar a litofania horizontal. A USB-C fica no centro da extremidade direita da placa, acessível pelo recorte conjunto da tampa e do bordo traseiro do corpo. O cabo liga e desliga pelo exterior. Os furos de montagem da placa não são usados.

## Parâmetros que dependem da peça real

| Variável no SCAD | Valor provisório | Confirmar |
| --- | ---: | --- |
| `led_total_thickness` | 2,04 mm | Confirmado: da face superior luminosa à base traseira da placa |
| `usb_port_w` / `usb_port_h` | 8,88 × 3,04 mm | Medidas exteriores da tomada USB-C |
| `usb_notch_width_y` | 20 mm | Reserva para a ficha USB-C; corpo da ficha ainda não medido |
| `usb_notch_start_x` | 76 mm | Posição da tomada relativamente ao centro da placa |
| `usb_body_notch_from_back` | 7 mm | Altura livre necessária no bordo do corpo |
| Comprimento da placa LED | ≈ 156 mm | Medida do anúncio; a foto confirma apenas o lado curto ≈ 120,1 mm |

A distância geométrica prevista entre o verso da litofania e a face luminosa do LED é 15 mm **se a face traseira da placa tocar na tampa**. A uniformidade da luz precisa de ser vista com o LED aceso.

## Verificação feita

Os três STL foram exportados do SCAD com OpenSCAD; cada um é uma malha fechada de um único sólido. Os limites medidos dos STL coincidem com as cotas acima. Ainda não houve ensaio físico da ficha USB, do encaixe da tampa, da fixação da placa nem fatiamento num perfil da impressora. **Testar a ficha e o LED antes de colar a tampa.**

A litofania pessoal original não foi incluída nem publicada. É inserida no corpo a partir do ficheiro 3MF que já tens.
