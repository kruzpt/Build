# Caixa para a litofania dos avós — conceito V2

[Desenho para validar](../../designs/lithoavos-caixa-led-conceito-v2.png) · [SVG editável](../../designs/lithoavos-caixa-led-conceito-v2.svg)

Esta é uma proposta de montagem para discussão, **ainda sem CAD, STL ou 3MF de impressão**. O 3MF `lithoavos.3mf` enviado pelo utilizador contém uma litofania plana de **160 × 124 × 3 mm**, medida nos vértices da malha (445 952 vértices). A litofania original não é alterada nem publicada aqui.

A placa LED **já chegou**. As fotos do utilizador mostram aproximadamente **120,1 mm no lado curto** e **150,24 mm no paquímetro colocado ao longo do lado maior**. O utilizador indicou que faltam alguns milímetros porque o paquímetro chegou ao limite; por isso, **150,24 mm é apenas um mínimo medido**, e os **156 mm anunciados** continuam uma hipótese, não uma cota verificada. A placa será rodada 90° para iluminar a litofania horizontalmente. A USB-C fica então numa lateral da caixa. A distância entre furos e a espessura total com o difusor ainda aguardam medição; não tomar as cotas publicitárias dos furos como confirmadas.

## Dimensões e disposição propostas

| Elemento | Proposta | Estado |
| --- | ---: | --- |
| Litofania | 160 × 124 × 3 mm | Medida no 3MF |
| Placa LED rodada | pelo menos 150,24 × 120,1 mm | Comprimento completo por medir; anúncio: 156 mm |
| Exterior da caixa | 178 × 142 × 27 mm | A validar visualmente |
| Abertura frontal visível | 156 × 120 mm | Sobrepõe 2 mm da margem da litofania |
| Calha da litofania | 160,4 × 124,4 × 3,4 mm | Folga nominal de 0,2 mm por face lateral |
| Distância LED–verso da litofania | 15 mm | A testar com o LED real aceso |
| Parede nominal | cerca de 3 mm | A modelar após aprovação |
| Abertura lateral USB-C | cerca de 16 × 10 mm | A ajustar ao conector e à ficha do cabo |

**Montagem prevista:** corpo com fundo integrado, litofania colocada na calha frontal, moldura removível e quatro pequenos grampos impressos para reter as bordas da placa LED. Os grampos terão ajuste para um comprimento de **150–158 mm**, a afinar quando a cota completa for conhecida. A moldura prende com quatro parafusos M3 em cantos exteriores à imagem. Os grampos permitem fixar o LED sem depender da distância entre os furos anunciada. O corpo e a moldura devem caber separadamente no prato da A1 e da U1 e ser impressos planos, sem suportes. O interior claro pode ajudar a distribuir a luz; o acabamento e a ventilação dependem do ensaio com o LED ligado.

**Pontos por confirmar antes da geometria final:** espessura total da placa, distância entre furos se forem usados, posição exata do corpo da USB-C em relação à borda, dimensão da ficha do cabo a ligar e uniformidade da imagem com 15 mm de afastamento. A abertura USB será paramétrica e poderá ficar à direita ou à esquerda conforme a rotação da placa.

Depois de aprovada a disposição, criar uma amostra curta da calha e da janela USB-C, testar fisicamente com a placa e a litofania, e só então preparar o corpo inteiro e o projeto de impressão. Este fluxo evita imprimir uma caixa grande com encaixes errados.
