# Saca-rolamentos V1 — protótipo integralmente impresso

**Protótipo mecânico para testes, não ferramenta com carga certificada.**
O fatiamento e a geometria foram verificados; não houve impressão, teste de
extração ou medição da roda real. O acesso atrás do anel interior continua
por confirmar. O gancho pequeno pode não conseguir agarrar o rolamento nessa
roda. Não confundir um fatiamento sem erros com resistência comprovada.

## O que foi construído

Copo fechado reforçado, veio de tração guiado, manípulo/porca rotativa,
anilha de deslizamento, três ganchos substituíveis, eixo e clip impressos.
O manípulo apoia sobre a anilha e o topo do copo; a guia em D impede o veio
de rodar. Ao rodar o manípulo, o veio sobe e traciona o gancho. Não usar
alavancas adicionais no manípulo. O manípulo não é cativo: a força de tração
mantém-no apoiado durante utilização, e pode ser retirado para montagem.

A rosca foi aumentada para Ø30 mm / passo 6 mm, com 26 mm de engate, em vez
dos Ø24 / passo 4 da primeira imagem. É uma rosca especial impressa, **não
uma rosca ISO normalizada**. A imagem CAD deste pacote mostra as malhas reais.
Os scripts e `parameters.json` documentam os parâmetros em milímetros.

## Medidas conhecidas e hipóteses

| Elemento | Medida | Estado |
|---|---|---|
| Roda | Ø63 mm | Referência fornecida; confirmar roda concreta |
| Rolamento 627 | 7 × 22 × 7 mm | Dimensão nominal |
| Copo | Ø54 exterior, cavidade Ø34, altura 53 mm | Proposta |
| Superfície de contacto com o cubo | Anel Ø34 exterior / Ø24 interior | **Confirmar apoio sólido; não carregar nas nervuras** |
| Rosca | Ø30 máximo, Ø27 raiz, passo 6, comprimento 80 mm | Proposta |
| Engate da porca | 26 mm | Proposta |
| Curso de trabalho | Limitar manualmente a 12 mm | **Não existe batente mecânico de fim de curso** |
| Folgas da rosca | 0,35 mm radial; alargamento axial do perfil 0,15 mm | Testar no prato 1 |
| Eixo de articulação | Ø8 mm; furo nominal Ø8,4 mm | Testar encaixe após imprimir |
| Gancho | Três larguras de ponta: 5,4 / 5,8 / 6,2 mm; espessura 3 mm | Hipóteses, não encaixe garantido num furo de 7 mm |

A cabeça de articulação é larga e fica fora do rolamento. Só a haste estreita
e a ponta entram no furo; o eixo de Ø8 mm não precisa de o atravessar.
O gancho assimétrico precisa de ser apresentado com descentramento e inclinação.
Ainda é necessário verificar na roda se há espaço para o inclinar atrás do
anel interior, sem chocar com o espaçador. As larguras da tabela não são o
"diâmetro de passagem": verificar o envelope completo e o movimento real.

## Projetos de impressão

Abrir `saca-rolamentos-v1-A1-PETG-bico-0.4-3-pratos.3mf` **como projeto**.
Perfil de referência: Bambu A1, bico 0,4 mm, camadas 0,16 mm, PETG genérico,
**8 paredes e 100% de enchimento**. Adaptar o perfil de filamento ao PETG real.
Estes parâmetros visam reforçar o protótipo; não garantem resistência máxima
nem substituem ensaios. As pontas estreitas já serão praticamente maciças.

1. **Prato 1 — teste de rosca.** Imprimir primeiro o macho e a porca curtos.
   Confirmar rotação livre à mão, sem forçar. Se prender ou tiver demasiada
   folga, ajustar o gerador antes de gastar material no conjunto maior.
2. **Prato 2 — ganchos, eixo e clip.** Os ganchos são impressos deitados,
   com camadas a acompanhar o seu perfil. Eixo impresso deitado. Suportes
   automáticos nestas peças; retirar com cuidado e rejeitar peças danificadas.
   Testar a ponta na roda **sem aplicar força**, e a articulação na forquilha.
3. **Prato 3 — copo, veio, manípulo/porca e anilha.** Imprimir só depois de
   confirmar os testes anteriores e o apoio do copo. Roscas e copo verticais. O copo usa suportes nas janelas e sob a flange
   inferior; retirar completamente antes de montar. Veio e porca sem suportes
   para preservar as superfícies da rosca.

Todas as peças estão no mesmo filamento, sem trocas de cor. Há brim de 5 mm.
Os STL já têm orientação de impressão, não coordenadas de montagem.

## Montagem e funcionamento

1. Encaixar a cabeça do gancho na forquilha do veio e alinhar os três furos.
   Introduzir o eixo e colocar o clip na ranhura da extremidade. A articulação
   deve mover-se livremente; não confundir folga com um eixo rachado.
2. Passar o veio pelo copo com a face plana alinhada à guia em D. Colocar
   a anilha de deslizamento sobre o copo e enroscar o manípulo à mão.
3. Apresentar o gancho ao rolamento e verificar se entra e agarra atrás do
   anel interior. O espaçador pode impedir este movimento: se isso acontecer,
   parar e rever a ponta; **não forçar para abrir espaço**.
4. Assentar o anel inferior do copo apenas na zona sólida do cubo. O rolamento
   deve ter espaço para sair para o interior do copo sem arrastar a roda.
5. Rodar o manípulo lentamente. Confirmar que o veio sobe sem rodar, o eixo
   não toca no copo, o gancho continua agarrado e o rolamento sai alinhado.
   O copo tem janelas para observar a articulação durante o movimento.
6. Parar se houver flexão visível, estalos, perda de engate ou marcas no cubo.
   Não insistir num rolamento muito preso. Não existe valor de binário seguro
   medido para este protótipo; nem oito paredes justificam aumentar a força.

Puxar pelo anel interior pode danificar o rolamento. O objetivo deste protótipo
é verificar a viabilidade da extração totalmente impressa, não garantir
reutilização do rolamento extraído. Para montagem de rolamentos será preciso
um adaptador que pressione o anel exterior; **não usar o gancho para isso**.
Este pacote contém o extrator, não um adaptador de montagem.

## Verificação realizada

Malhas STL estanques, quatro posições de engate da rosca sem interseção
volumétrica, montagem nominal sem colisões e verificações de folga aos
0, 3, 6 e 12 mm de deslocamento do veio. Não foi simulada a deformação
sob carga nem validado o engate do gancho numa roda real. Exportação,
reabertura e fatiamento nativos no Bambu Studio 02.08.02.61 documentados em
`bambu-validation.json`; resultados dependem dos perfis e versão do programa.

Não há ligação ao Fusion ou ao computador Windows do utilizador: os ficheiros
foram gerados e fatiados neste ambiente. O projeto é fornecido como STL/3MF
com gerador Python, não como documento Fusion nativo.

Para regenerar dentro do repositório (dependências: numpy, OpenCV, Pillow,
trimesh e manifold3d, além dos auxiliares existentes):

```sh
python fusion/tools/generate_saca_rolamentos_v1.py
python fusion/tools/build_saca_rolamentos_v1_3mf.py
```

Alterar `parameters.json` isoladamente não reconstrói os STL: nesta versão
os parâmetros de origem ficam no dicionário `P` e nas funções do gerador.
