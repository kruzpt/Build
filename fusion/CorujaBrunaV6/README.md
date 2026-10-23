# Coruja BRUNA V6 — mãos brancas sem novas trocas de cor

As duas mãos que seguram o livro, incluindo as pequenas pontas inferiores,
passam do castanho para o **mesmo filamento branco da cara, páginas e faixa**.
Mantêm os contornos pretos e o relevo da V5.

A mudança foi feita na geometria: as superfícies das mãos estão agora entre
Z=3,00 e Z=3,40 mm, exatamente nas quatro camadas brancas já existentes.
A base sob as mãos continua preta. Pintar as paredes da peça antiga no
fatiador pode introduzir branco em mais alturas e aumentar as trocas; neste
projeto só as capas superiores usam branco.

## Impressão

- **CORUJA-A1-bico-0.2-4-cores.3mf**: abrir como projeto no Bambu Studio.
  Bambu A1, bico 0,2 mm, camadas 0,10 mm; quatro filamentos: castanho,
  branco, dourado e preto. Associar o segundo filamento ao PLA branco do AMS.
  Verso plano no prato, sem suportes. Não é necessário pintar as mãos.
- **ACESSORIOS-A1-bico-0.4-2-pratos.3mf**: bico 0,4 mm, camadas 0,16 mm.
  Prato 1: anilha castanha. Prato 2: lenço em verde/castanho/preto, impresso
  como uma única peça para colar. As malhas destes acessórios são idênticas
  às da V5; peças já impressas podem ser reutilizadas.
- Frente: aproximadamente **50 × 45,8 × 3,6 mm**, incluindo a faixa BRUNA.
  Anilha: abertura 25 × 18 mm, altura 20 mm. Encaixe do lenço mantém
  folga lateral de 0,20 mm e espaço de 0,15 mm para cola.

Os quatro STL de cores da frente compõem uma só montagem multicolor.
Não são peças individuais para colar. O ficheiro com sufixo `creme.stl`
contém agora as superfícies associadas ao **branco** no projeto 3MF.
O STL monocor é uma alternativa para inspeção da frente, sem lenço.

## Verificação e comparação

Exportação, reabertura e fatiamento nativos no Bambu Studio 02.08.02.61,
STL estanques, frente unida e sem colisões entre cores/peças montadas.
Sem suportes nem avisos do fatiador. Os relatórios `bambu-validation-*.json`
contêm os valores finais e os hashes dos ficheiros entregues.

A frente mantém **12 trocas de filamento**, tal como a V5, e cerca de **3h04**
de impressão. Estas estimativas são para uma coruja e incluem torre/purga;
podem variar com a versão do fatiador e os perfis de filamento.
**Ainda não foi impressa fisicamente.**

`CAD.png` mostra as malhas efetivamente exportadas com o branco atualizado.
A ilustração-fonte continua a ser a da V4; os scripts atribuem às mãos a nova
cor e altura, sem alterar o livro ou as restantes penas.

Para reproduzir dentro do repositório com os módulos auxiliares e Python
com numpy, OpenCV, Pillow, manifold3d e trimesh:

```sh
python fusion/tools/generate_coruja_bruna_v6.py
python fusion/tools/build_coruja_bruna_v6_3mf.py
```
