# Coruja BRUNA V3 — proporções da referência e definição em preto

Abrir primeiro **`anilha-coruja-bruna-v3-CORUJA-A1-bico-0.2-4-cores.3mf`**
como projeto. Contém a coruja completa, numa montagem de quatro partes de
cor. O objeto chama-se `CORUJA BRUNA V3 - COMPLETA - 50 mm`.

O ficheiro com `ACESSORIOS` no nome contém a anilha e o lenço com o nó.
O STL `CORUJA-COMPLETA-monocor.stl` permite visualizar ou imprimir a frente
inteira numa única cor, sem depender de um leitor com suporte multicolor.

## Alterações desta tentativa

Os contornos principais foram redesenhados numa grelha comum a partir da
referência fornecida: cabeça menor relativamente ao corpo, orelha direita
mais alta, olhos em alturas diferentes, asas mais compridas e assimétricas,
livro mais estreito, chama de três pontas e faixa mais estreita. A posição
dos olhos acompanha a inclinação da cabeça, aproximadamente 22 graus.

A face creme tem pequenos recortes de penas no bordo e sulcos radiais.
As penas douradas têm superfícies convexas e sulcos; algumas nervuras e
arestas são definidas com **preto incrustado**, sem uma quinta cor na frente.
O bico passou a castanho. As letras acompanham a faixa curva e usam uma
serifa mais próxima da referência. O lenço verde tem um **nó castanho**,
impresso conjuntamente, sem uma peça minúscula adicional para colar.

As imagens mostram a geometria real exportada. Continua a ser uma
interpretação em baixo-relevo de uma única vista, não uma reprodução
tridimensional exata da escultura da fotografia.

## Dimensões

- Coruja completa com BRUNA: **50 mm de altura × cerca de 33,65 mm de largura**.
- Espessura máxima da frente: aproximadamente **9,63 mm**.
- Traseira plana, base castanha nominal de 3,5 mm antes dos rebaixos.
- Detalhes finos em torno de **0,20–0,24 mm**.
- Anilha: abertura oval livre **25 × 18 mm**, altura **20 mm**,
  exterior **30 × 24,5 mm**, incluindo a face de colagem.
- Face plana de colagem da anilha: aproximadamente **12,8 × 20 mm**.

## Projeto da coruja — bico de 0,2 mm

Filamentos 1 castanho, 2 creme, 3 dourado/ocre em PLA comum, 4 preto.
Manter as quatro partes como **uma montagem**; não pousar as partes
individualmente no prato ou alterar as suas alturas relativas.

Perfil oficial de origem: `0.10mm Standard @BBL A1 0.2 nozzle`.
Camadas e primeira camada de **0,10 mm**, Arachne, três paredes, gyroid 20%,
seis camadas de topo e cinco de fundo. Exteriores 20 mm/s, interiores
35 mm/s, topo 15 mm/s, pequenos perímetros 12 mm/s, fluxo volumétrico
máximo 1,5 mm³/s. Textured PEI, brim de 2 mm/afastamento 0,15 mm.

**Sem suportes**, sem ironing e sem purga no preenchimento, nos objetos ou
nos suportes. Torre de purga ativa. A coruja imprime com a traseira no prato.
Confirmar o bico físico de **0,2 mm** antes de imprimir este projeto.
Os perfis são Generic PLA; o dourado não está configurado como PLA Silk.

## Acessórios — bico de 0,4 mm

`anilha-coruja-bruna-v3-ACESSORIOS-A1-bico-0.4-2-pratos.3mf`:

1. Prato 1: anilha castanha, uma cor.
2. Prato 2: **lenço verde e nó castanho numa montagem de duas cores**.
   Não separar a montagem: o nó é impresso por cima do verde.

Filamento 1 castanho e 2 verde, bico **0,4 mm**, camadas e primeira camada
de **0,16 mm**. Quatro paredes/gyroid 30% na anilha; pequeno lenço com
preenchimento 100%. Sem suportes. A torre de purga só gera percursos no
prato do lenço, onde há mudanças de cor.

Depois de imprimir a frente, pode substituir o creme do segundo canal por
verde e confirmar o mapeamento. Nenhum prato ultrapassa quatro cores;
nenhum projeto exige cinco perfis de filamento.

## Montagem

O lenço V3 foi redesenhado: **usar o lenço e o nó desta versão**. O nó já
fica unido ao verde durante a impressão. Só se cola a montagem do lenço
ao rebaixo da coruja, e a anilha ao verso.

O rebaixo do lenço tem folga lateral nominal **0,20 mm por lado**; fundo
em Z=4,8 mm, verso do lenço em Z=5,0 mm, deixando **0,20 mm para cola**.
A superfície circundante é curva, por isso a profundidade de inserção
visível varia. Testar a seco e usar pouca cola compatível com PLA.

A anilha conserva a forma de V1/V2 e pode ser reutilizada. Colar a sua
face plana ao verso, centrada na largura e na faixa de **12 a 32 mm acima
do fundo** da coruja (centro a 22 mm). Deixar curar antes de usar com o lenço.

## Estimativas para uma unidade

| Prato | Bico | Tempo | PLA incluindo purga/brim | Trocas |
| --- | --- | --- | --- | --- |
| Coruja | 0,2 mm | **15 h 06 min** | **66,37 g** | **156** |
| Anilha | 0,4 mm | 35 min | 5,24 g | 0 |
| Lenço com nó | 0,4 mm | 16 min 27 s | 1,39 g | 3 |

A própria frente usa cerca de **4,88 g**; a maior parte do consumo total
vem da purga e da torre. Os detalhes pretos em várias alturas aumentam as
trocas. Não foi reduzida a purga sem uma calibração que assegure a limpeza
entre cores escuras e claras. Os relatórios contêm os valores exatos.

## Validação e limites

Oito STL exportados e relidos como malhas estanques, com faces coerentes:
quatro cores da frente, frente unida, lenço, nó e anilha. Cores e peças
montadas não se atravessam. A frente tem um único corpo de volume positivo.
Foi removida uma apara isolada de **0,00325 mm³**, com cerca de 0,1 mm de
largura, abaixo da resolução imprimível. Pequenas cavidades internas
numéricas são preenchidas na cópia STL monocor; o exterior é preservado.
Junções tangentes foram separadas numericamente em menos de 0,001 mm para
permitir uma exportação STL robusta, muito abaixo da resolução de impressão.

Os dois 3MF foram exportados, reabertos e fatiados no Bambu Studio oficial
**02.08.02.61**, sem avisos de impressão nem percursos de suporte. Os
componentes nativos foram comparados com os STL por volume e inércia.
O projeto da frente confirma bico de 0,2 mm e camadas de 0,10 mm, incluindo
os marcadores de camadas do G-code. Os acessórios usam bico de 0,4 mm.

**Não existe ainda um teste físico.** A colagem, o ajuste do lenço e a
resistência dos detalhes precisam de um protótipo. O ficheiro não garante
um resultado idêntico à fotografia nem ao acabamento de uma escultura.

## Edição e reprodução

O pacote inclui dois 3MF, oito STL, GLB montado, imagens e relatórios.
Os scripts usam os módulos auxiliares existentes em `fusion/tools/`;
os ficheiros Bambu não dependem de executar scripts. Não inclui F3D.

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_coruja_bruna_v3.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_coruja_bruna_v3_3mf.py
```

O segundo script aceita `--bambu-bin`, `--profiles`, `--work-dir` e
`--package-only`. Requer numpy, Pillow, trimesh, manifold3d, cv2 e Bambu Studio.
