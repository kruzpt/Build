# Coruja BRUNA V2 — relevo curvo, bico de 0,2 mm

## Abrir primeiro o ficheiro da coruja

**`anilha-coruja-bruna-v2-CORUJA-A1-bico-0.2-4-cores.3mf`**

É o projeto da **coruja completa**, num único objeto de montagem com quatro
partes de cor, centrado no prato. Abrir **como projeto**, mantendo os perfis.
O objeto chama-se `CORUJA BRUNA V2 - COMPLETA - 50 mm`.

O outro 3MF, com `ACESSORIOS` no nome, contém só a anilha e o lenço verde.
Na V1 também havia projetos distintos para frente e acessórios; abrir apenas
o dos acessórios não mostra a coruja. O projeto V1 da frente foi reaberto e
fatiado, pelo que não foi reproduzido o problema de visualização comunicado.

Para ver a forma num leitor STL simples, abrir
`anilha-coruja-bruna-v2-CORUJA-COMPLETA-monocor.stl`. Este STL já une a frente
inteira numa só malha sem atribuição de cores; não inclui o lenço verde nem
a anilha. A impressão multicolor deve usar o 3MF da CORUJA.

## O relevo novo

- A frente mantém **50 mm de altura**, incluindo a faixa BRUNA, e cerca de
  **35,5 mm de largura**.
- Espessura máxima de cerca de **9,2 mm**, incluindo a traseira.
- Faces curvas nos discos faciais, corpo e penas, em vez de só extrusões planas.
- Penas das asas sobrepostas com sulcos no eixo e barbas; linhas de penas
  radiais nos discos faciais e pequenos sulcos no castanho exposto.
- Olhos com aro, íris, pupilas e brilho em alturas diferentes; sobrancelhas,
  bico e chama salientes. Os dois brilhos têm aproximadamente 0,76 mm.
- Livro com páginas convexas, linhas gravadas e dobra central.
- Faixa convexa e letras BRUNA que acompanham a curva da faixa.
- Lenço verde com frente arredondada e nó saliente; verso plano para colar.

É uma interpretação paramétrica em baixo-relevo da referência, sem promessa
de reproduzir uma escultura digitalizada. As imagens são renderizações da
geometria efetivamente exportada; não são fotografias de peças impressas.

## Coruja: A1, bico de 0,2 mm

No projeto `CORUJA`, os quatro filamentos são:

1. Castanho.
2. Creme.
3. Dourado/ocre em PLA comum.
4. Preto.

Perfil derivado do preset oficial **0.10mm Standard @BBL A1 0.2 nozzle**.
Camadas de **0,10 mm**, incluindo a primeira; prato Textured PEI; Arachne;
três paredes; preenchimento gyroid 20%; seis camadas de topo e cinco de fundo;
paredes exteriores 20 mm/s, interiores 35 mm/s, topo 15 mm/s, pequenos
perímetros 12 mm/s; fluxo volumétrico máximo **1,5 mm³/s**.

Primeira camada a 15 mm/s, brim exterior de 2 mm com afastamento de 0,15 mm.
**Sem suportes.** A traseira fica virada para o prato e a coruja para cima.
Interface shells ativo; sem ironing; torre de purga ativa; sem purga no
preenchimento, nos objetos ou nos suportes. Não usar modo vaso.

Confirmar que o **bico físico de 0,2 mm está instalado** e corresponde ao
selecionado antes de imprimir. Os filamentos são Generic PLA; adaptar a
temperatura ao fabricante quando necessário. O dourado do projeto não usa
perfil PLA Silk. Os sulcos mais finos têm cerca de 0,22–0,24 mm e precisam
do bico fino para serem melhor reproduzidos.

## Acessórios: A1, bico de 0,4 mm

`anilha-coruja-bruna-v2-ACESSORIOS-A1-bico-0.4-2-pratos.3mf`

- Prato 1: anilha castanha, abertura livre **25 × 18 mm**, altura **20 mm**,
  exterior **30 × 24,5 mm** incluindo a face plana de colagem.
- Prato 2: lenço verde, aproximadamente **20 × 10 mm**, até **2 mm** de espessura.
- Perfil A1/bico de **0,4 mm**, camadas **0,16 mm**, uma cor por prato,
  sem torre de purga ou suportes. Quatro paredes e gyroid 30% na anilha;
  pequeno lenço a 100% de preenchimento.

São dois perfis de filamento neste ficheiro: 1 castanho e 2 verde. Depois da
frente, trocar o creme do segundo canal por verde e confirmar o mapeamento.
Nenhum prato excede quatro cores e nenhum ficheiro pede cinco filamentos.
O projeto dos acessórios mantém o bico de 0,4 mm; não imprimir esse ficheiro
com o bico de 0,2 mm instalado sem mudar de perfil e voltar a fatiar.

## Montagem

O verde foi redesenhado para esta V2. **Não usar o lenço plano V1 como peça
equivalente**, pois a altura da superfície frontal e o rebaixo mudaram.

O rebaixo frontal tem folga lateral nominal **0,20 mm por lado**. O verso do
lenço fica na posição Z=4,6 mm, deixando **0,20 mm para cola** acima do fundo
do rebaixo, em Z=4,4 mm. A borda exterior é curva; a profundidade visível
de inserção não é constante ao longo do lenço. Experimentar a seco e usar
muito pouca cola compatível com PLA, aplicada com um palito.

A anilha traseira conserva a forma e o apoio da V1, pelo que uma anilha V1
já impressa pode ser reutilizada. Colar a face plana ao verso da coruja,
centrada na largura, na faixa de **12 a 32 mm acima do fundo** da coruja.
A zona plana de contacto tem aproximadamente **12,8 × 20 mm**. Deixar curar
antes de experimentar o lenço real. Não há encaixe de pressão atrás.

## Estimativas de impressão

O relevo curvo mistura cores em mais alturas. O tempo e a purga aumentam
bastante, como autorizado; o bico de 0,2 mm também imprime mais devagar.

| Prato | Bico | Tempo aproximado | Consumo incluindo purga/brim | Trocas |
| --- | --- | --- | --- | --- |
| Coruja | 0,2 mm | **11 h 40 min** | **50,54 g** | **114** |
| Anilha | 0,4 mm | 35 min | 5,24 g | 0 |
| Lenço verde | 0,4 mm | 8 min 37 s | 0,16 g | 0 |

A própria frente usa aproximadamente **5,2 g** no modelo; a maior parte do
consumo total da frente é purga e torre. O tempo estimado inclui a preparação
da máquina. Não foi reduzida a purga entre cores escuras e claras com base
numa calibração inexistente. Em produção, várias corujas no mesmo prato
podem repartir o custo da torre; esse cenário não foi fatiado nesta versão.

## Verificações e limites

- Sete STL exportados e relidos como malhas estanques com faces coerentes:
  quatro partes de cor, um STL unido da coruja, lenço e anilha.
- Verificação geométrica sem interseções de volume entre cores distintas
  ou entre as peças nas posições montadas. A frente tem um único corpo
  de volume positivo; pequenas cavidades internas de operações booleanas
  não são componentes decorativos soltos. O STL monocor preenche essas
  cavidades interiores e preserva a superfície exterior.
- Junções tangentes das malhas foram separadas numericamente em escala
  inferior a 0,001 mm para permitir exportação STL robusta; isso está muito
  abaixo da resolução da impressão e não acrescenta detalhe visual.
- Ambos os 3MF exportados, reabertos e fatiados no Bambu Studio oficial
  **02.08.02.61**, sem avisos de impressão ou percursos de suporte.
- Nozzle de 0,2 mm e camadas de 0,10 mm confirmados no projeto da CORUJA;
  camadas de 0,10 mm confirmadas no G-code. Os acessórios usam 0,4/0,16 mm.
- Quatro componentes de cor efetivamente presentes no único objeto da
  frente; volumes e inércias nativos comparados com os STL de origem.

**Ainda não foi feita uma impressão física.** O encaixe do verde, a colagem,
a resistência das extremidades e o ajuste ao lenço real precisam de um
protótipo. As estimativas de tempo não são uma medição da impressora.

## Ficheiros e reprodução

O pacote inclui os dois 3MF, sete STL, GLB montado com cores, imagens e
relatórios. Abrir o ficheiro `CORUJA` para a frente; abrir `ACESSORIOS` para
as peças a colar. O ficheiro `CORUJA-COMPLETA-monocor.stl` é uma alternativa
direta para visualização e impressão numa só cor.

Os scripts em `fusion/tools/` usam os auxiliares existentes no checkout,
incluindo o gerador V1 apenas como fonte de alguns contornos. Não é preciso
executar scripts para abrir os 3MF. Esta V2 não inclui um F3D nem um script
Fusion BRep validado; as faces curvas são entregues como malhas STL/3MF.

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_coruja_bruna_v2.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_coruja_bruna_v2_3mf.py
```

O segundo script aceita `--bambu-bin`, `--profiles`, `--work-dir` e
`--package-only`. Requer numpy, Pillow, trimesh, manifold3d, cv2 e Bambu Studio.
