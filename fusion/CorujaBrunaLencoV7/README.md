# Lenço V7 — apenas o lenço, para bico 0,2 mm

Substitui o lenço de três cores da coruja BRUNA V6. A coruja e a anilha
não foram alteradas nem estão incluídas neste pacote.

- Toda a base, laterais, contorno e pontas são **verdes**, até Z=1,20 mm.
- **Castanho apenas no topo do nó central**, de Z=1,20 a 1,40 mm: duas
  camadas de 0,10 mm, com um pequeno sulco cujo fundo também é castanho.
- Não existe preto nem castanho nas pontas. As duas cores são impressas
  juntas como uma só peça; não é necessário colar o nó à base verde.
- Dimensões: aproximadamente **15,97 × 10,37 × 1,40 mm**.
- O contorno de encaixe e o verso plano correspondem ao lenço V6.
  Mantém a montagem na coruja com o verso do lenço a Z=2,15 mm e a folga
  original para cola. Confirmar a posição antes de aplicar pouca cola.

## Bambu Studio

Abrir **anilha-coruja-bruna-lenco-v7-A1-bico-0.2-2-cores.3mf** como projeto.
Está configurado para Bambu A1, **bico 0,2 mm e camadas 0,10 mm**, verso
plano no prato, suportes desligados. Associar o primeiro filamento ao verde
e o segundo ao castanho no AMS. Imprime o verde primeiro e termina com o
nó castanho: **uma única troca de filamento**.

Estimativa do Bambu Studio 02.08.02.61: **26 min 10 s**, cerca de **0,94 g**
incluindo torre/purga; a peça em si estima 0,14 g. Valores para uma unidade,
dependentes dos perfis de filamento e versão do fatiador.

## Ficheiros e verificações

- 3MF: projeto multicolor pronto, com uma montagem e um prato.
- STL verde e nó castanho: corpos da mesma montagem, com coordenadas comuns.
  Ao importar manualmente, escolher um objeto com várias partes.
- STL completo monocor: alternativa para inspeção ou impressão numa só cor.
- GLB e imagem CAD: geometria real desta versão.
- `geometry.json` e `bambu-validation.json`: dimensões, hashes e resultados.

Verificados: STL estanques, montagem unida, cores sem sobreposição volumétrica,
contorno igual ao da V6, exportação/reabertura/fatiamento nativos no Bambu Studio,
14 camadas de 0,10 mm, uma troca de cor, sem suportes nem avisos do fatiador.
**Ainda não foi impresso fisicamente.**

Para reproduzir dentro do repositório, com os módulos auxiliares existentes
e Python com numpy, OpenCV, Pillow, trimesh e manifold3d:

```sh
python fusion/tools/generate_coruja_lenco_v7.py
python fusion/tools/build_coruja_lenco_v7_3mf.py
```
