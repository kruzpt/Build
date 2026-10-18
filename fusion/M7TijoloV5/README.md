# M7 — tijolo Natal 2026 V5, placa única

Projeto completo para Bambu Lab A1, bico 0,4 mm e AMS: um tijolo com moldura e
uma placa decorativa única para colar. Esta versão substitui a montagem dos
símbolos soltos da V4. Os ficheiros antigos estão preservados.

## Abrir e imprimir

Abrir **m7-tijolo-v5-A1-AMS-2-pratos.3mf como projeto** no Bambu Studio, carregando
as suas configurações. Não importar apenas a geometria para um projeto vazio.
Confirmar a correspondência dos quatro filamentos no AMS antes de enviar.

| Prato | Conteúdo e orientação | Filamentos |
| --- | --- | --- |
| 1 | Corpo com moldura, de pé, com os oito furos na vertical | Laranja |
| 2 | Placa completa, fundo laranja apoiado na mesa e relevo para cima | Laranja, dourado Silk, branco e ciano |

A placa do prato 2 é **uma montagem multicolor única**, não quatro objetos a
imprimir separadamente. Não separar os relevos, não os pousar individualmente
na mesa e não rodar a placa com a decoração para baixo. As três camadas iniciais
são inteiramente laranja; as trocas de cor começam no relevo, a Z = 0,80 mm.
O fundo laranja acaba a Z = 0,60 mm. Há torre de purga no prato multicolor.

## Medidas e encaixe

| Elemento | Medida |
| --- | --- |
| Tijolo exterior | 50 × 26 × 70 mm |
| Furos verticais | Oito, atravessantes; profundidade útil reduzida pelo reforço |
| Rebaixo frontal | 47 × 67 mm, profundidade 0,70 mm |
| Placa, fundo laranja | 46,6 × 66,6 × 0,60 mm |
| Folga nominal | 0,20 mm por lado |
| Espaço nominal para cola | 0,10 mm atrás da placa |
| Moldura exterior | 1,50 mm |
| Relevo decorativo | 1,00 mm; espessura total da placa 1,60 mm |
| Parede frontal atrás do rebaixo | 3,00 mm |
| Parede posterior | 3,50 mm |
| Estrela | 30 mm de largura |

A superfície laranja da placa fica alinhada com a moldura quando o espaço
nominal de cola é respeitado; o relevo fica à frente. Os cantos são arredondados
com folga compatível. Todo o verso da placa tem apoio no fundo do rebaixo.

O **m e o 7 são os contornos do STL original** enviado pelo utilizador, com uma
única escala uniforme e a posição relativa original preservada. Não foram
substituídos por uma fonte. A inscrição foi refeita em **Natal 2026**, manuscrito
Z003 Medium Italic, com traços reforçados para o bico de 0,4 mm.

## Perfil de acabamento

Camada e primeira camada de **0,20 mm**, três paredes, topo monotónico,
velocidade de topo de 25 mm/s. Primeira camada: 20 mm/s nas paredes e 30 mm/s
no preenchimento. Brim exterior de 3 mm, afastamento 0,15 mm e compensação
de pé de elefante de 0,10 mm. Mesa configurada: **Textured PEI Plate**.
Sem suportes e sem passar as purgas para dentro dos objetos.

O corpo do prato 1 tem substituições em **Objects**:

- **Quality → Wall generator: Classic**.
- **Quality → Advanced → Order of walls: outer/inner**.
- **Speed → Outer wall: 50 mm/s**; **Inner wall: 100 mm/s**.
- **Speed → Acceleration → Outer wall: 2000 mm/s²**.

A placa conserva **Arachne** para o manuscrito e os detalhes do logótipo.
Ambas as peças usam a ordem exterior/interior. O gerador global mostra Arachne;
selecionar o corpo em Objects para ver Classic. O reforço das duas faces do
corpo procura reduzir a marcação física das divisórias, além dos ajustes de
percurso e aceleração. Não se garante eliminar as riscas sem uma impressão.

| Filamento | Temperatura inicial / restantes | Limite volumétrico |
| --- | --- | --- |
| Laranja, SUNLU PLA+ | 220 / 220 °C | 8 mm³/s |
| Dourado, PLA Silk, intervalo fornecido 190–220 °C | 215 / 215 °C | 5 mm³/s |
| Branco PLA | 220 / 220 °C | 8 mm³/s |
| Ciano PLA | 220 / 220 °C | 8 mm³/s |

O laranja conserva os 220 °C e o fluxo 0,98 do perfil anterior, sem inventar
uma calibração. Verificar o intervalo indicado na bobina e usar a calibração
**Flow Rate / Flow Dynamics** para o SUNLU PLA+ efetivamente utilizado.
O perfil Silk é próprio para o dourado. Os quatro lugares lógicos do projeto
são 1 laranja, 2 dourado, 3 branco e 4 ciano, independentemente do slot físico
que lhes for associado no envio.

## Montagem e acabamento

1. Deixar a placa e a mesa arrefecerem completamente antes de retirar a peça.
   Apoiar a placa ao retirar brim; evitar puxar por um canto.
2. Fazer uma montagem a seco. A placa deve entrar sem ser forçada, com uma
   junta fina contínua. Retirar apenas resíduos ou pé de elefante se houver.
3. Distribuir uma película fina de cola compatível com PLA pelo fundo do
   rebaixo, incluindo apoio junto aos cantos, evitando excesso na junta.
4. Assentar e manter a placa plana até a cola fixar; proteger o relevo durante
   a pressão. Uma placa com cantos levantados deve ser corrigida/reimpressa
   antes da colagem, não puxada à força para dentro da moldura.

Usar o mesmo laranja para corpo e placa; a diferente orientação de impressão
pode provocar alguma diferença de brilho. A moldura protege os cantos e torna
a junta intencional, mas não transforma duas peças numa superfície sem junta.

## Validação e conteúdo

O relatório de geometria confirma malhas fechadas, placa completa ligada,
oito furos, folgas, ausência de colisões no percurso de inserção e os contornos
do logótipo recuperados após exportação. O Bambu Studio oficial 02.08.02.61
exportou, reabriu e fatiou os dois pratos, sem avisos nem suportes. A sequência
do fundo laranja foi verificada no G-code. Relatórios e hashes acompanham os
ficheiros. O 3MF entregue é editável, sem G-code previamente preparado para
enviar diretamente à máquina: fatiar no Studio depois de confirmar o AMS.

Estimativas do fatiador, incluindo preparação, purga e torre:

| Prato | Tempo | Material |
| --- | --- | --- |
| Corpo | 3 h 03 min | 46,23 g |
| Placa completa | 54 min | 8,84 g |
| Total | **3 h 57 min** | **55,08 g** |

Estas verificações não substituem o primeiro protótipo: encaixe, aderência da
cola, cor final e eliminação das riscas **não estão validados fisicamente**.

O pacote inclui o projeto 3MF, cinco STL separados por corpo/material, imagens,
relatórios e **M7TijoloV5.py + geometry.json**, para recriar os corpos BRep num
novo documento Fusion. Executar o script dentro do Fusion; não foi executado
neste ambiente e não se entrega um F3D validado. O 3MF funciona de forma
independente. Os scripts de geração na pasta scripts do ZIP são referências
reproduzíveis no checkout Build, onde também estão os seus módulos auxiliares
e os contornos originais; o script Fusion é autónomo com geometry.json.

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_m7_brick_v5.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_m7_brick_v5_3mf.py
```
