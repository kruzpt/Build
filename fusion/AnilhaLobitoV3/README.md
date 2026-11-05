# Anilha do lobito V3 — costas lisas, frente com volume

Projeto preparado após aprovação do conceito arredondado e do pedido de costas
lisas para imprimir e colar. O corpo é abaulado e o rosto conserva olhos,
focinho, nariz, bochechas e orelhas com volume. A união foi reconstruída com
apoios planos e dois pequenos pinos de orientação no corpo.

## Medidas e montagem

- Abertura oval **25 × 18 mm**, gerada como a da Coruja BRUNA.
- Corpo **30 mm** de altura, cerca de **42 mm** de largura máxima.
- Altura com orelhas: aproximadamente **38 mm**.
- Verso do rosto plano, com dois pequenos alojamentos de **2,8 mm de diâmetro
  e 1 mm de profundidade**; não há saliência de encaixe por baixo do rosto.
- Corpo com dois pinos de **2,4 mm de diâmetro e 1 mm de projeção**. A diferença
  de diâmetros dá **0,20 mm de folga radial**.
- O posicionamento nominal reserva **0,15 mm para cola** no apoio e no fundo
  dos alojamentos. O encaixe é para orientar a colagem, não para prender à força.

A superfície traseira tem uma base ampla no prato: a secção a Z=0,10 mm mede
cerca de 1113 mm² de cinzento, além de pequenas zonas brancas. Esta orientação
dispensa os suportes que seriam usados com a guia saliente do estudo anterior.
Os alojamentos são pequenas cavidades no verso; o restante apoio é plano.

## Projeto Bambu Studio

Abrir `anilha-lobito-v3-costas-lisas-A1-AMS-2-pratos.3mf` **como projeto**,
para A1 com bico de **0,4 mm**, e voltar a fatiar.

| Prato | Conteúdo | Estimativa | Material com torre/purgas | Trocas |
|---|---|---:|---:|---:|
| 1 | Corpo cinzento, em pé | ~1 h 20 min | ~12,56 g | 0 |
| 2 | Rosto, costas planas no prato | ~5 h | ~51,20 g | 113 |
| Total | Uma anilha | **~6 h 20 min** | **~63,76 g** | **113** |

Estimativas nativas, incluindo preparação calculada. A geometria curva faz
as cores coexistirem em várias alturas, pelo que o rosto usa muitas trocas
mesmo sendo separado do corpo. Para várias unidades, agrupar rostos no mesmo
prato pode amortizar as purgas; este projeto contém uma unidade por prato.

Camada 0,16 mm, primeira 0,20 mm, três paredes e 15% gyroid. Perímetro externo
35 mm/s, topo 25 mm/s e aceleração normal 1000 mm/s². **Sem suportes ou brim**
nas peças; torre de preparação ativa no rosto multicolor.

Slots: 1 cinzento, 2 branco e 3 preto. Os perfis são Generic PLA, com limite
volumétrico de 8 mm³/s. Selecionar os perfis das bobinas reais e manter a
calibração dinâmica de fluxo. O fluxo 0,931 do laranja do tijolo não foi
aplicado a estes materiais.

## Colagem

Deixar as peças arrefecerem e verificar primeiro o encaixe a seco. Os pinos
devem entrar nos alojamentos sem esforço. Aplicar uma camada fina de cola
compatível com PLA na zona plana e posicionar o rosto pelas guias. Evitar
encher os alojamentos de cola. Confirmar que o rosto fica alinhado e deixar
curar segundo as instruções da cola.

## Verificações e limites

- STLs das quatro partes fechados e com orientação consistente.
- Rosto ligado geometricamente e abertura do lenço livre.
- Sem interferência geométrica entre corpo e rosto na posição nominal.
- Malhas importadas pelo Bambu comparadas com os STLs por volume e inércia.
- Dois pratos fatiados no **Bambu Studio 02.09.01.70**, sem avisos, suportes
  ou brim nas peças.

As verificações são digitais. Impressão física, folga real, resistência da
colagem e aperto no lenço ainda não foram testados. A coruja tinha passagem
mais curta; o corpo de 30 mm desta versão pode alterar o atrito no tecido.
Imprimir uma unidade antes de uma série.

O pacote inclui o projeto, quatro STLs separados por material, imagens,
parâmetros, relatório e scripts. Os scripts são geradores de malhas em
milímetros e usam os módulos auxiliares do checkout; não são documentos F3D
nem scripts executados no Autodesk Fusion.
