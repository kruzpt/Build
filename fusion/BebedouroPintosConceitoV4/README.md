# Bebedouro para pintos — V4, garrafa medida

Continuação do [conceito V3](../BebedouroPintosConceitoV3/README.md). Mantêm-se dois módulos iguais para cerca de 15 pintos: cada módulo usa uma garrafa reutilizada de 500 ml invertida, um suporte preso à rede e um copo raso roscado no gargalo. O suporte é uma peça com anel inferior fechado e apoio superior aberto em C; o copo é a segunda peça. O conjunto sai dos ganchos para reabastecer.

## Medidas recebidas em 13-11-2026

| Elemento | Valor de projeto | Estado |
| --- | ---: | --- |
| Comprimento total da garrafa | 220 mm | Medido pelo utilizador |
| Diâmetro máximo do corpo | 60 mm | Medido pelo utilizador |
| Diâmetro na zona mais estreita | 51 mm | Confirmado pelo utilizador: 5,1 cm |
| Diâmetro exterior da rosca | 33 mm | Medido pelo utilizador; testar o encaixe antes do copo completo |
| Capacidade nominal | 500 ml | Confirmada anteriormente |
| Bordo da base plástica acima da grelha | 120 mm | Confirmado anteriormente |
| Arame horizontal escolhido acima da grelha | 150 mm | Confirmado anteriormente |

A fotografia identifica uma garrafa com corpo de largura variável e gargalo estreito. Não fornece escala suficiente para obter o passo, o perfil ou a altura útil da rosca, nem o diâmetro do ombro onde o anel inferior apoiará.

## Verificação de espaço

Com a garrafa invertida, se o fundo do copo ficar a `H_c` mm acima da grelha e a boca da garrafa estiver cerca de 5 mm acima do fundo do copo, o ponto mais alto da garrafa fica aproximadamente a **`H_c + 225 mm`**. Por exemplo, com o copo a 25–35 mm da grelha, o topo fica a **250–260 mm**, ainda sem margem para introduzir ou retirar o conjunto. Como o arame de suspensão está a 150 mm, a garrafa ultrapassa-o em cerca de **100–110 mm**. Medir a altura livre até ao teto antes de fechar a posição dos apoios.

O fundo do copo, o afastamento boca–fundo e a profundidade da água são valores de estudo, não medidas aprovadas. A boca deve permanecer aberta e submersa para o nível se regular por vácuo; não perfurar a garrafa para admitir ar. Um ensaio com água tem de confirmar o nível, a estabilidade e o acesso dos pintos.

## Geometria a parametrizar após as medidas em falta

- **Anel inferior:** passagem interior acima da maior saliência do gargalo que o atravessa, mas abaixo do diâmetro do ombro que suporta a garrafa. A medida de 33 mm da rosca não define por si só o furo do anel.
- **Apoio superior aberto:** diâmetro ajustado à secção real onde toca no corpo; não apertar a PET.
- **Copo:** rosca interior de ensaio, aberta no centro para a água sair pela boca da garrafa. Ensaiar primeiro um cupão curto do gargalo. Depois definir largura, profundidade e folga de água do copo.
- **Ganchos e braço:** ajustar ao diâmetro dos arames e à altura livre. Verificar retenção positiva, peso da garrafa cheia e altura de acesso dos pintos.

## Dados pendentes

1. Medir a altura da grelha ao teto da gaiola e o diâmetro do arame escolhido para os ganchos. Medir também o próximo arame horizontal se se pretende subir o conjunto.
2. Foto nítida do gargalo sem tampa com régua/paquímetro: diâmetro exterior da rosca, altura roscada, anel de suporte, diâmetro do ombro e tampa para identificar o passo.
3. Indicar o filamento disponível; PETG continua a ser a proposta para o protótipo lavável, sujeita a teste de estanqueidade e limpeza.

**Estado:** medidas principais registadas e espaço vertical calculado. Ainda não existe CAD/STL/3MF final nem teste físico. O [esquema V4](../../designs/bebedouro-pintos-conceito-v4-medidas-garrafa.svg) mostra as cotas conhecidas e os pontos a medir.
