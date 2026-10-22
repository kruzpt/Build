# Coruja BRUNA V1 — anilha para lenço

Primeiro projeto imprimível inspirado na fotografia fornecida. A coruja,
incluindo a faixa BRUNA, mede **50 mm de altura por cerca de 35,5 mm de largura**.
É uma adaptação em relevo vetorial, com planos de diferentes alturas e contornos
curvos; não é uma cópia da escultura orgânica da fotografia. O nome BRUNA foi
mantido da referência. Não inclui o texto abaixo da peça na fotografia.

## Construção

- Frente: base castanha de **2,4 mm**; relevo máximo **4,48 mm**.
- Quatro cores na frente: castanho, creme, dourado/ocre e preto.
- Olhos com aros, íris douradas, pupilas pretas e pontos de brilho em creme.
- Sobrancelhas, bico, penas das asas, pequenas linhas de penas na face,
  livro aberto, chama e letras em relevo. Alguns detalhes finos da referência
  foram simplificados para a escala de 50 mm e bico de 0,4 mm.
- Lenço verde numa peça separada: aproximadamente 20 × 10 × **1,2 mm**.
  Entra num rebaixo de **0,4 mm**, com **0,20 mm de folga por lado**;
  posição nominal de montagem: inserção 0,25 mm, espaço inferior para cola 0,15 mm.
- Anilha castanha: abertura oval livre **25 × 18 mm**, altura **20 mm**,
  parede radial mínima **2,5 mm**, plano de colagem atrás da coruja.
- Exterior da anilha: **30 × 24,5 × 20 mm**, incluindo a face de colagem.
- Profundidade total montada: aproximadamente **29 mm**.

As cores da frente são impressas juntas com AMS; **não se colam separadamente
as letras, os olhos ou as penas**. Só o lenço verde e a anilha são colados.
O dourado é um tom de PLA comum no projeto; o uso de PLA Silk requer adequar
o perfil ao fabricante e não foi validado nesta versão.

## Projetos Bambu

Abrir os 3MF **como projetos**, preservando os perfis incluídos.

1. `anilha-coruja-bruna-v1-frente-A1-AMS-4-cores.3mf`
   — um prato com a frente completa. Filamentos 1 castanho, 2 creme,
   3 dourado/ocre, 4 preto. Manter as quatro partes como uma montagem.
2. `anilha-coruja-bruna-v1-acessorios-A1-2-pratos.3mf`
   — prato 1 anilha castanha; prato 2 lenço verde. Cada prato usa apenas
   uma cor. Os perfis são 1 castanho e 2 verde; após imprimir a frente,
   pode trocar o creme do segundo canal por verde e confirmar o mapeamento.

Assim, o projeto da frente tem quatro perfis de filamento, e o dos acessórios
tem dois. Nenhum prato precisa de cinco cores ou de trocar um rolo durante
a impressão. A torre de purga só é usada na frente multicolor.

Perfis A1/bico de 0,4 mm, PLA, Textured PEI. Camadas **0,16 mm**, incluindo
a primeira, Arachne, três paredes na frente, quatro na anilha. Paredes
exteriores 35 mm/s, interiores 70 mm/s, topo 25 mm/s, pequenos perímetros
20 mm/s. Preenchimento 20% na frente, 30% na anilha, 100% no pequeno lenço.
Brim de 2 mm com afastamento de 0,15 mm. **Sem suportes** em todos os pratos.
Topo Monotonic, interface shells ativo, ironing desligado e sem purga no
preenchimento, nos objetos ou nos suportes.

As espessuras de cada cor já estão modeladas em relevo. Não substituir este
modelo por uma imagem colorida aplicada a uma superfície nem mudar cada
STL para um objeto independente pousado no prato: isso perde as alturas
relativas e a sobreposição correta das peças da frente.

## Montagem

1. Retirar o brim com cuidado, especialmente junto das pontas das orelhas.
2. Experimentar o lenço verde no rebaixo, sem forçar. Usar uma quantidade
   pequena de cola compatível com o plástico, aplicada com um palito no fundo.
   Os espaços para cola reduzem o excesso, mas não impedem que saia se encher
   demasiado o rebaixo. Fixar até a cola curar.
3. A face de trás da coruja é plana. Colar aí a face plana da anilha,
   com o eixo de passagem do lenço na vertical. O apoio fica centrado na
   largura da coruja e ocupa a faixa de **12 a 32 mm acima do ponto inferior**
   da coruja (centro a 22 mm). A face plana de contacto tem cerca de
   **12,8 × 20 mm**. Não há pinos, encaixe de pressão ou rebaixo atrás.
4. Depois da cura, testar com o lenço real. A abertura foi escolhida como
   ponto de partida para um lenço enrolado; não foi medida no lenço do cliente.

## Validação

Os seis STL foram relidos e verificados como malhas estanques, com orientação
coerente. Os volumes de cores distintas e as peças montadas não se atravessam.
A frente multicolor forma um conjunto conectado; o lenço e a anilha são
cada um uma peça única. A altura da frente é 50 mm, incluindo o nome.

Os dois projetos foram exportados, reabertos e fatiados no Bambu Studio oficial
02.08.02.61. Os três pratos ficaram sem avisos de impressão e sem suportes.
Os componentes nativos correspondem aos STL por volume e inércia. O topo dos
dois brilhos dos olhos está presente no G-code final em Z=4,48 mm.

Estimativas para **uma unidade**, incluindo brim, preparação e purga:

| Prato | Tempo aproximado | PLA estimado | Trocas de cor |
| --- | --- | --- | --- |
| Frente AMS | 1 h 12 min | 12,36 g | 16 |
| Anilha | 35 min | 5,24 g | 0 |
| Lenço verde | 8 min 28 s | 0,16 g | 0 |
| Total | 1 h 56 min | 17,76 g | 16 |

Os valores exatos constam dos relatórios JSON. A verificação do fatiador
não substitui um ensaio físico: a colagem, a resistência das pontas, o ajuste
do lenço verde e a retenção do lenço de escuteiro ainda não foram testados.
Imprimir uma unidade antes de produzir em quantidade.

## Edição e reprodução

Inclui seis STL, dois 3MF, GLB montado com cores e imagens da geometria real.
Os dois scripts em `fusion/tools/` geram a geometria e os projetos a partir
do checkout, usando os módulos auxiliares já existentes no repositório.

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_coruja_bruna_v1.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_coruja_bruna_v1_3mf.py
```

O gerador Bambu aceita `--bambu-bin`, `--profiles`, `--work-dir` e
`--package-only`. Requer numpy, Pillow, trimesh, manifold3d, cv2 e Bambu Studio.

`CorujaBrunaV1.py` e `geometry.json` juntos permitem reconstruir os contornos
como corpos BRep num documento novo do Fusion. Esse script opcional **não
foi executado no Fusion** e não é um ficheiro F3D validado. Os projetos 3MF
não dependem dele. As imagens são renderizações CAD das peças efetivamente
exportadas, não fotografias de um exemplar impresso.
