# M7 — tijolo Natal 2026 V2, com 7 pincelado

A V2 altera o **tijolo** para aproximar o 7 da referência enviada: barra
superior inclinada com extremidades arredondadas, três recortes largos no
traço descendente e bordo direito irregular. O contorno foi desenhado para
ser imprimível com bico de 0,4 mm. A casinha permanece na versão V1.

## Downloads

- Projeto: `m7-tijolo-v2-A1-AMS-4-pratos.3mf`.
- Pacote: `m7-tijolo-v2-pacote.zip` — projeto, seis STL, script Fusion,
  contornos, instruções, imagens do CAD e relatórios.
- Imagem real: `m7-tijolo-v2-CAD.png`.
- Pormenor do símbolo: `m7-tijolo-v2-logo.png`.

Abra o 3MF como **projeto** no Bambu Studio. Confirme as bobinas no AMS e
mantenha as dimensões e a orientação fornecidas.

## Alterações e medidas

| Elemento | V1 | V2 |
| --- | --- | --- |
| Corpo do tijolo, largura × profundidade × altura | 50 × 26 × 70 mm | 50 × 26 × 70 mm |
| Largura da estrela | 24 mm | **30 mm** |
| Largura do conjunto m7 | 10 mm | **14 mm** |
| Forma do 7 | Diagonal simples | Contorno pincelado |
| Dimensões do 7 | Cerca de 3,6 × 4,2 mm | **5,33 × 7,25 mm** |
| Espessura das peças para colar | 1,20 mm | 1,20 mm |
| Rebaixos de posicionamento | 0,20 mm | 0,20 mm, redesenhados |
| Folga lateral por lado | 0,15 mm | 0,15 mm |
| Folga no fundo para cola | 0,05 mm | 0,05 mm |

A estrela tem uma abertura central um pouco mais ampla. O m e o 7 mantêm
pelo menos 0,35 mm de separação nominal do contorno dourado. Os seus
rebaixos também não se sobrepõem. Árvore, inscrição e oito furos do tijolo
mantêm as dimensões anteriores.

**O novo corpo, a estrela, o m e o 7 devem ser usados juntos, todos V2.**
Os rebaixos da V1 não servem para os novos tamanhos. Se já imprimiu a V1,
pode reaproveitar a árvore e a inscrição “Natal 2026”: os dois STL da V2
são cópias exatas dos anteriores. As versões V1 continuam preservadas.

## Pratos e perfil

O projeto imprime um exemplar de cada peça necessária, em quatro pratos:

1. Corpo terracota, com os furos na vertical e brim de 3 mm.
2. Árvore e estrela, em dourado silk e deitadas.
3. m e inscrição “Natal 2026”, em branco e deitados.
4. 7 pincelado, em ciano e deitado.

Cada prato é monocromático: **zero trocas de cor durante a impressão**.
Estimativa total: **39,49 g e cerca de 3 h 34 min**, segundo o Bambu Studio
oficial 02.08.02.61. A estimativa inclui os quatro pratos e pode variar
com o filamento e a versão do programa.

Foi conservado o perfil A1 / bico 0,4 mm da V1: camada de 0,20 mm,
três paredes, cinco camadas superiores, quatro inferiores, 15% gyroid,
paredes Arachne e topo monotónico a 35 mm/s. O dourado usa Generic PLA Silk
a 215 °C, limite de 5 mm³/s e topo a 25 mm/s, dentro do intervalo
190–220 °C indicado para a bobina. Os suportes estão desativados.

## Montagem

Experimente primeiro as peças a seco, sem forçar. Os rebaixos destinam-se
a posicionar e colar; não são encaixes por pressão. Aplique pequenas gotas
de cola no verso, com palito, e evite que a cola transborde. Retire a estrela
da mesa fria sem a dobrar, especialmente em PLA silk.

O m e o 7 continuam separados para evitar desperdício com trocas de cor.
A inscrição tem nove caracteres separados; uma fita de pintor de baixa
aderência sobre as faces visíveis pode ajudar a levantá-los mantendo o
espaçamento, antes de os apresentar aos respetivos rebaixos.

## Verificação

Os seis STL são malhas fechadas e orientadas corretamente. Corpo, estrela,
árvore, m e 7 são peças únicas; a inscrição tem nove componentes. Foram
verificadas as folgas, as colisões entre peças e 105 posições de inserção
nos rebaixos. O projeto foi exportado, reaberto e fatiado pelo Bambu Studio
sem avisos e sem gerar percursos de suporte em nenhum dos quatro pratos.

O percurso exterior da última camada do 7 foi inspecionado: os três recortes
permanecem no percurso gerado, e não apenas na imagem do modelo. A imagem
`m7-tijolo-v2-7-percurso.png` mostra o contorno e a linha central do percurso
na orientação escolhida pelo programa para a mesa. O símbolo pode estar
rodado no prato; a forma não foi espelhada.

`geometry-validation.json` e `bambu-validation-tijolo.json` registam os
resultados. Os 3MF são projetos editáveis, sem G-code pré-gerado para enviar
diretamente à impressora. O protótipo físico e a colagem continuam por testar.

O 7 é uma interpretação vetorial manual da referência, com detalhes
dimensionados para impressão; não foi fornecido um vetor oficial da marca.

## Fusion

Copie a pasta `M7TijoloV2`, incluindo `M7TijoloV2.py` e `geometry.json`,
para os scripts do Fusion e execute. O script cria um documento novo com
o tijolo montado e os componentes por cor. A sintaxe foi verificada; a
execução no Fusion ainda não foi testada. Os STL e o projeto Bambu não
dependem da execução do script.
