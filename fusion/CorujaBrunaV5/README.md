# Coruja BRUNA V5 — emblema ilustrado em camadas

Esta versão segue o estilo ilustrado do emblema do lobo Áquela: contornos
pretos, penas desenhadas e áreas de cor planas em diferentes alturas. Substitui
os volumes arredondados de V2/V3; preserva os ficheiros anteriores.

Em relação à V4, alarga e regulariza o contorno preto nas grandes áreas de
cor. As superfícies coloridas passam a ser capas de 0,40 mm sobre pedestais
pretos, reduzindo as paredes laterais claras expostas junto às penas. Uma margem
preta de pelo menos 0,20 mm separa as cores do perímetro exterior da frente.
A anilha e as três malhas do lenço são idênticas às da V4 e podem ser reutilizadas.

## Dimensões e peças

- Frente: aproximadamente **50 mm de altura × 45,8 mm de largura × 3,6 mm**.
  A faixa BRUNA está incluída na altura. Verso plano, base preta de 2,4 mm.
- Superfícies: castanho a Z=3,0; dourado a Z=3,2; creme a Z=3,4;
  contornos e letras pretas a Z=3,6 mm. São patamares reais de geometria.
  As capas coloridas têm quatro camadas sólidas de 0,10 mm; a tonalidade final
  depende da opacidade do PLA sobre a base preta.
- Lenço: uma montagem de três cores (verde, nó castanho e contorno preto),
  impressa em conjunto e colada como uma única peça, sem montar detalhes soltos.
  Encaixe com 0,20 mm de folga por lado e 0,15 mm para cola sob a peça.
- Anilha castanha: abertura interior 25 × 18 mm, altura 20 mm, exterior
  aproximadamente 30 × 24,5 mm. Colar a zona plana no verso da coruja.
  A anilha mantém a geometria das versões anteriores.

## Abrir no Bambu Studio

1. **CORUJA-A1-bico-0.2-4-cores.3mf**: abrir como projeto. Contém a frente
   completa, com castanho, creme, dourado e preto, bico 0,2 mm e camadas 0,10 mm.
   Imprimir com o verso plano contra o prato, sem suportes.
2. **ACESSORIOS-A1-bico-0.4-2-pratos.3mf**: bico 0,4 mm, camadas 0,16 mm.
   Prato 1: anilha castanha, com a abertura vertical. Prato 2: lenço montado
   em verde/castanho/preto, verso plano no prato. Nenhum prato excede quatro cores.
3. Deixar arrefecer, testar a posição e colar lenço e anilha com pouca cola.
   Não forçar o encaixe; a compensação real depende do filamento e da impressora.

Os quatro STL de cores da frente são corpos de uma só montagem; não são
quatro peças para colar. Para importar manualmente, selecionar os quatro e
aceitar um objeto com várias partes, preservando as coordenadas. Existe também
um STL monocor da frente para inspeção rápida. Esse STL não contém o lenço.

## Origem e validação

A ilustração-fonte é a mesma da V4, incluída no pacote, e foi gerada para este desenho e convertida em contornos reais
com paleta limitada, filtragem de pormenores pequenos e extrusões. O desenho
`CAD.png` e o esquema de peças mostram as malhas efetivamente exportadas,
com as cores e a anilha montadas. A ilustração-fonte tem sombras cromáticas
que foram reduzidas à paleta de filamentos; não é uma fotografia da impressão.

Verificações automáticas: STL estanques, frente unida, ausência de interseções
volumétricas entre cores/peças montadas, altura inferior a 50 mm, exportação,
reabertura e fatiamento nativos no Bambu Studio 02.08.02.61, sem suportes nem
avisos do fatiador. Os relatórios `bambu-validation-*.json` registam os resultados,
estimativas e hashes dos projetos entregues. **Ainda não foi impresso fisicamente.**

Estimativas da frente: **3h04**, **9,78 g incluindo purga/torre**, 12 trocas
 de filamento. São valores do fatiador para uma unidade. A V4 estimava cerca
 de 4h25, 15,26 g e 24 trocas. A anilha estima 35 min e o lenço 31 min.

`contour-validation.json` confirma que as capas estão apoiadas em preto,
respeitam a margem exterior e que as malhas dos acessórios continuam idênticas
às da V4. A construção reduz o efeito observado no contorno; o acabamento
físico deve ser confirmado com uma impressão.

### Reproduzir

Usar Python com numpy, OpenCV, Pillow, trimesh e manifold3d:

```sh
python fusion/tools/generate_coruja_bruna_v5.py
python fusion/tools/build_coruja_bruna_v5_3mf.py
```

Executar dentro deste repositório, que contém os módulos auxiliares importados
pelos scripts. O ZIP inclui os projetos prontos, STL, imagens, GLB, contornos,
relatórios e scripts desta versão; os auxiliares partilhados ficam no repositório.
