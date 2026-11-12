# Móvel modular para rolos de filamento — conceito V1

[Ver o conceito](../../designs/movel-filamentos-modular-v1-conceito.png)

Estado: estudo inicial. A imagem é uma ilustração de conceito, não uma renderização de CAD verificado. Não existem ainda STL, 3MF, lista de cortes final nem capacidade de carga validada.

## Pedido e interpretação inicial

O utilizador pretende construir um móvel com bases e uniões impressas em 3D e ligações em paus/cabos de vassoura. Pediu dois encaixes horizontais e dois verticais, permitindo acrescentar andares.

Esta proposta interpreta os dois horizontais como perpendiculares, a **90°**, formando um canto. Os dois verticais são coaxiais, um voltado para cima e outro para baixo. Esta disposição ainda precisa de confirmação do utilizador.

As peças impressas seriam os nós de canto e os pés; os cabos formariam os montantes e os quatro lados de cada andar. Os rolos ficariam em pé sobre os dois varões longitudinais da frente e de trás, sem um eixo a atravessar o seu furo central e sem uma prateleira cheia. Caso o utilizador pretenda uma superfície completa impressa em cada andar, esta interpretação terá de ser revista.

## Peças propostas

- **Nó de canto universal:** dois encaixes horizontais a 90° e dois verticais, para cima e para baixo. A mesma peça roda para servir os quatro cantos.
- **Pé alargado:** adaptador impresso que ocupa o encaixe inferior do primeiro andar e aumenta a área de apoio no chão.
- **Tampa superior opcional:** fecha os encaixes que ficam livres no último andar, podendo ser retirada para ampliar o móvel.
- **Fixações transversais:** parafusos/pinos para reter os cabos e limitar a rotação ou o desencaixe. Geometria e ferragens ainda por definir.
- **Diagonal traseira:** elemento de contraventamento para reduzir a deformação lateral do retângulo. Uma tira metálica única pode trabalhar apenas à tração; poderá ser necessário um X de duas tiras ou uma diagonal rígida. A ligação às peças será dimensionada juntamente com o nó.

O interior dos encaixes terá **batentes**. Os cabos de cima e de baixo não devem simplesmente deslizar num tubo sem apoio. Os encaixes horizontais devem terminar antes da cavidade vertical, com material suficiente a separar as cavidades. A forma final terá reforços na união dos braços ao corpo vertical.

## Exemplo dimensional, ainda não aprovado

| Parâmetro | Proposta / hipótese | Estado |
| --- | --- | --- |
| Número de andares | 3 | Exemplo para discussão |
| Rolos por andar | 4 | Exemplo, dependente da largura real dos rolos |
| Largura útil entre as uniões | Cerca de 340 mm | Proposta; não é comprimento de corte dos cabos |
| Largura exterior | Cerca de 480 mm | Proposta; depende dos nós e pés |
| Profundidade exterior | Cerca de 220 mm | Proposta; depende da abertura dos pés |
| Distância entre varões dianteiro/traseiro | Aproximadamente 140–160 mm entre eixos | A definir pelo diâmetro dos rolos |
| Passo vertical entre os eixos dos andares | 260 mm | Proposta; confirmar folga de retirada do maior rolo |
| Diâmetro do cabo | Por medir | Não inferido de um valor comercial nominal |
| Material do cabo | Madeira maciça, como hipótese inicial | Por confirmar; tubos metálicos exigem outro detalhe de fixação |
| Comprimento de inserção nos encaixes | Estudar 30–40 mm | Proposta; não é uma dimensão validada |
| Material das peças impressas | PETG a avaliar | Não confirma resistência à carga ou à deformação prolongada |

Nenhuma medida física foi fornecida até agora. Para avaliar a largura útil, quatro rolos de 75 mm ocupam 300 mm; três intervalos de 10 mm elevam isso a 330 mm. Rolos mais largos exigem aumentar o vão ou reduzir a quantidade.

Os rolos têm os eixos orientados ao longo da largura do móvel, como rodas lado a lado. As abas circulares assentam nos dois varões paralelos. Colocar as faces circulares voltadas para a frente mudaria a geometria de apoio e não é a disposição estudada.

A altura total terá de incluir pés, nós, segmentos verticais e a parte dos rolos que sobressai acima do último andar. Não se deve obter uma lista de cortes medindo a imagem de conceito.

## Quantidades para o exemplo de três andares

| Elemento | Quantidade inicial |
| --- | --- |
| Nós de canto impressos | 12 |
| Pés impressos | 4 |
| Tampas superiores opcionais | 4 |
| Segmentos horizontais longos | 6 |
| Segmentos horizontais curtos | 6 |
| Segmentos verticais entre andares | 8 |
| Diagonais e ferragens | A definir |

Cada andar adicional acrescenta quatro nós, quatro segmentos verticais e quatro segmentos horizontais (dois longos e dois curtos). Os comprimentos finais dependem dos batentes e profundidades de inserção; a distância visível entre peças não é o comprimento de corte.

## Próximo passo

Confirmar o esquema dos encaixes, a posição dos rolos, a capacidade pretendida e o diâmetro/material dos cabos. Medir também diâmetro e largura do maior rolo a guardar. Depois da aprovação do conceito, desenhar o nó com parâmetros, conferir a separação das cavidades e preparar primeiro uma pequena amostra de encaixe e um nó para ensaio.

A avaliação da estrutura terá de considerar o peso dos carretéis além do filamento, a rigidez dos cabos, a orientação das camadas, a retenção das ligações e a deformação prolongada das peças impressas. Para configurações altas, prever um ponto de fixação à parede. A diagonal traseira reduz a deformação lateral; não substitui a verificação da estabilidade contra tombamento.

O fluxo de aprovação de novas peças está em [AGENTS.md](../../AGENTS.md). Nesta fase foi pedido iniciar a ideia; apenas o conceito e as hipóteses de dimensionamento foram preparados.
