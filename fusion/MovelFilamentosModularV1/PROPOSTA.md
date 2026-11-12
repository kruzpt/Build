# Móvel modular para rolos de filamento — conceito V1

[Ver o conceito](../../designs/movel-filamentos-modular-v1-conceito.png)

**Estado em 12/11/2026: guardado e em pausa, por pedido do utilizador, até confirmar o diâmetro dos cabos.** Não avançar com modelação, folgas, cortes ou ficheiros de impressão enquanto se aguarda essa medida.

Atualização do utilizador: **seis rolos por andar**, em pé sobre dois varões; cabos com diâmetro provável de **22 mm**, ainda não confirmado. Sobre os encaixes, escreveu: «Vi a Tua sugestão e assim é 2 horizontais e 1 vertical». Registar essa indicação sem assumir ainda se o vertical é uma passagem única para ambos os sentidos ou um encaixe fechado numa direção.

A imagem guardada corresponde ao conceito inicial de quatro rolos por andar; **não foi redesenhada para os seis rolos**. É uma ilustração, não uma renderização de CAD verificado. Não existem ainda STL, 3MF, lista de cortes final nem capacidade de carga validada.

## Pedido e interpretação inicial

O utilizador pretende construir um móvel com bases e uniões impressas em 3D e ligações em paus/cabos de vassoura, permitindo acrescentar andares. O pedido inicial referia dois encaixes horizontais e dois verticais; após ver a proposta, indicou dois horizontais e um vertical.

O conceito inicial interpreta os horizontais como perpendiculares, a **90°**, formando um canto, e desenha aberturas verticais coaxiais para cima e para baixo. Na retoma, esclarecer a passagem vertical à luz da indicação mais recente do utilizador antes de fixar a construção dos andares intermédios.

As peças impressas seriam os nós de canto e os pés; os cabos formariam os montantes e os quatro lados de cada andar. O utilizador confirmou os rolos **em pé sobre dois varões por andar**, sem um eixo a atravessar o seu furo central.

## Peças propostas

- **Nó de canto:** dois encaixes horizontais a 90° e uma ligação vertical, conforme a última indicação. A forma da passagem vertical e a possibilidade de usar a mesma peça nos quatro cantos serão resolvidas na retoma.
- **Pé alargado:** adaptador impresso que ocupa o encaixe inferior do primeiro andar e aumenta a área de apoio no chão.
- **Tampa superior opcional:** fecha os encaixes que ficam livres no último andar, podendo ser retirada para ampliar o móvel.
- **Fixações transversais:** parafusos/pinos para reter os cabos e limitar a rotação ou o desencaixe. Geometria e ferragens ainda por definir.
- **Diagonal traseira:** elemento de contraventamento para reduzir a deformação lateral do retângulo. Uma tira metálica única pode trabalhar apenas à tração; poderá ser necessário um X de duas tiras ou uma diagonal rígida. A ligação às peças será dimensionada juntamente com o nó.

O conceito prevê **batentes ou outro mecanismo de apoio axial**, a compatibilizar com a passagem vertical escolhida. A retenção da altura dos andares terá de ser definida; não foi validado um tubo de passagem livre. Os encaixes horizontais devem terminar antes da cavidade vertical, com material suficiente a separar as cavidades. Prevêem-se reforços na união dos braços ao corpo vertical.

## Exemplo dimensional, ainda não aprovado

| Parâmetro | Proposta / hipótese | Estado |
| --- | --- | --- |
| Número de andares | 3 | Exemplo para discussão |
| Rolos por andar | 6 | Confirmado pelo utilizador |
| Largura útil entre as uniões | A redimensionar para seis rolos | Os 340 mm da imagem pertencem ao exemplo antigo de quatro rolos |
| Largura exterior | A redimensionar | Os 480 mm da imagem não são a medida final para seis rolos |
| Profundidade exterior | Cerca de 220 mm | Proposta; depende da abertura dos pés |
| Distância entre varões dianteiro/traseiro | Aproximadamente 140–160 mm entre eixos | A definir pelo diâmetro dos rolos |
| Passo vertical entre os eixos dos andares | 260 mm | Proposta; confirmar folga de retirada do maior rolo |
| Diâmetro do cabo | Provavelmente 22 mm | Estimativa do utilizador; aguardar confirmação antes de modelar |
| Material do cabo | Madeira maciça, como hipótese inicial | Por confirmar; tubos metálicos exigem outro detalhe de fixação |
| Comprimento de inserção nos encaixes | Estudar 30–40 mm | Proposta; não é uma dimensão validada |
| Material das peças impressas | PETG a avaliar | Não confirma resistência à carga ou à deformação prolongada |

Ainda não há medidas físicas confirmadas. Os 22 mm são provisórios. A largura dos seis rolos e as folgas entre eles serão usadas para recalcular o vão; não reutilizar automaticamente as larguras do primeiro desenho.

Os rolos têm os eixos orientados ao longo da largura do móvel, como rodas lado a lado. As abas circulares assentam nos dois varões paralelos. Colocar as faces circulares voltadas para a frente mudaria a geometria de apoio e não é a disposição estudada.

A altura total terá de incluir pés, nós, segmentos verticais e a parte dos rolos que sobressai acima do último andar. Não se deve obter uma lista de cortes medindo a imagem de conceito.

## Quantidades do conceito inicial de três andares, por rever

Estas contagens descrevem o esquema original. A divisão dos montantes e os adaptadores dependem da passagem vertical que vier a ser confirmada.

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

**Aguardar a confirmação do diâmetro, conforme pedido explícito.** A capacidade de seis rolos por andar e a posição em pé sobre dois varões já estão confirmadas. Quando o utilizador retomar, esclarecer o material dos cabos e a passagem vertical, obter as medidas do maior rolo e redimensionar a largura antes de preparar uma amostra de encaixe. O número final de andares continua por confirmar.

A avaliação da estrutura terá de considerar o peso dos carretéis além do filamento, a rigidez dos cabos, a orientação das camadas, a retenção das ligações e a deformação prolongada das peças impressas. Para configurações altas, prever um ponto de fixação à parede. A diagonal traseira reduz a deformação lateral; não substitui a verificação da estabilidade contra tombamento.

O fluxo de aprovação de novas peças está em [AGENTS.md](../../AGENTS.md). Nesta fase foi pedido iniciar a ideia; apenas o conceito e as hipóteses de dimensionamento foram preparados.
