# Caixa para a litofania dos avós — conceito V2

[Desenho para validar](../../designs/lithoavos-caixa-led-conceito-v2.png) · [SVG editável](../../designs/lithoavos-caixa-led-conceito-v2.svg)

Este desenho foi substituído pelo [conceito V3, com a USB acessível na tampa traseira](../LithophaneLedBoxV3/README.md). É um registo histórico, **sem CAD, STL ou 3MF de impressão**. O 3MF `lithoavos.3mf` enviado pelo utilizador contém uma litofania plana de **160 × 124 × 3 mm**, medida nos vértices da malha (445 952 vértices). A litofania original não é alterada nem publicada aqui.

A placa LED **já chegou**. As fotos do utilizador mostram aproximadamente **120,1 mm no lado curto**. O utilizador esclareceu que os **150,24 mm no lado comprido e os 114,73 mm no lado curto são distâncias entre furos de montagem**, não comprimentos exteriores. Os **156 mm de comprimento exterior** continuam a ser apenas a cota do anúncio. A placa será rodada 90° para iluminar a litofania horizontalmente. O V2 punha a USB-C na lateral do corpo; o V3 corrige a montagem para expor a porta no recorte da tampa traseira.

## Dimensões e disposição propostas

| Elemento | Proposta | Estado |
| --- | ---: | --- |
| Litofania | 160 × 124 × 3 mm | Medida no 3MF |
| Placa LED rodada | cerca de 156 × 120,1 mm | Comprimento exterior vem do anúncio; lado curto medido |
| Furação longitudinal | 150,24 mm | Medida pelo utilizador; não é o comprimento exterior |
| Exterior da caixa | 178 × 142 × 27 mm | A validar visualmente |
| Abertura frontal visível | 156 × 120 mm | Sobrepõe 2 mm da margem da litofania |
| Calha da litofania | 160,4 × 124,4 × 3,4 mm | Folga nominal de 0,2 mm por face lateral |
| Distância LED–verso da litofania | 15 mm | A testar com o LED real aceso |
| Parede nominal | cerca de 3 mm | A modelar após aprovação |
| Abertura lateral USB-C | cerca de 16 × 10 mm | A ajustar ao conector e à ficha do cabo |

**Montagem prevista no V2:** corpo com fundo integrado, litofania colocada na calha frontal, moldura removível e quatro pequenos grampos impressos para reter as bordas da placa LED. A moldura prende com quatro parafusos M3 em cantos exteriores à imagem. O corpo e a moldura devem caber separadamente no prato da A1 e da U1 e ser impressos planos, sem suportes. O interior claro pode ajudar a distribuir a luz; o acabamento e a ventilação dependem do ensaio com o LED ligado.

**Pontos que faltavam confirmar no V2:** comprimento exterior da placa, diâmetro dos furos, espessura total, posição exata do corpo da USB-C em relação à borda, dimensão da ficha do cabo e uniformidade da imagem com 15 mm de afastamento.

Depois de aprovada a disposição, criar uma amostra curta da calha e da janela USB-C, testar fisicamente com a placa e a litofania, e só então preparar o corpo inteiro e o projeto de impressão. Este fluxo evita imprimir uma caixa grande com encaixes errados.
