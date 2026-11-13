# Bebedouro para pintos — V4, garrafa medida

Continuação do [conceito V3](../BebedouroPintosConceitoV3/README.md). Mantêm-se dois módulos iguais para cerca de 15 pintos: cada módulo usa uma garrafa reutilizada de 500 ml invertida, um suporte preso à rede e um copo raso roscado no gargalo. O suporte é uma peça com anel inferior fechado e apoio superior aberto em C; o copo é a segunda peça. O conjunto sai dos ganchos para reabastecer.

## Medidas recebidas em 13-11-2026

| Elemento | Valor de projeto | Estado |
| --- | ---: | --- |
| Comprimento total da garrafa | 220 mm | Medido pelo utilizador |
| Diâmetro máximo do corpo | 60 mm | Medido pelo utilizador |
| Diâmetro na zona mais estreita | 51 mm | Confirmado pelo utilizador: 5,1 cm |
| Diâmetro exterior dos filetes da rosca | 30,44 mm | Leitura do paquímetro confirmada pelo utilizador; passo por determinar |
| Diâmetro do arame para os ganchos | cerca de 3 mm | Estimativa do utilizador; testar a folga do gancho |
| Capacidade nominal | 500 ml | Confirmada anteriormente |
| Bordo da base plástica acima da grelha | 120 mm | Confirmado anteriormente |
| Arame horizontal escolhido acima da grelha | 150 mm | Confirmado anteriormente |

A fotografia identifica uma garrafa com corpo de largura variável e gargalo estreito. Não fornece escala suficiente para obter o passo, o perfil ou a altura útil da rosca, nem o diâmetro do ombro onde o anel inferior apoiará.

## Observações das novas fotografias

- A fita mostra o **arame horizontal superior da frente por volta de 330 mm** da grelha. Mais atrás, o teto curvo sobe acima desse nível. Para o protótipo junto da rede, usar 330 mm como limite conservador provisório; a folga local verdadeira depende de quanto a garrafa fica afastada da frente e da inclinação do teto. Na posição inicial calculada, o topo da garrafa fica a 250–260 mm, deixando cerca de 70–80 mm até essa referência frontal.
- Há outro arame horizontal perto de 300 mm. Mudar o conjunto inteiro do arame de 150 mm para esse arame elevaria o topo da garrafa aproximadamente a 400–410 mm, acima do espaço visível. Para subir o copo com o crescimento dos pintos, a solução a estudar é **usar o mesmo arame de 150 mm e mudar o ponto do gancho no próprio suporte**. As posições 0 e +20 mm dariam topes de cerca de 250–260 e 270–280 mm. Uma terceira posição +40 mm daria 290–300 mm e deixaria apenas 30–40 mm até à referência frontal: mantê-la condicional até ensaiar a montagem e a folga real sob o teto. Estas posições ainda não são geometria aprovada nem testada.
- A leitura do paquímetro foi confirmada: **30,44 mm no exterior dos filetes**. O passo, o número de entradas e a altura útil da rosca continuam desconhecidos. O anel de suporte inferior também depende do diâmetro da saliência abaixo dos filetes. O encaixe do gancho deve ser testado contra o arame de aproximadamente 3 mm.

## Verificação de espaço

Com a garrafa invertida, se o fundo do copo ficar a `H_c` mm acima da grelha e a boca da garrafa estiver cerca de 5 mm acima do fundo do copo, o ponto mais alto da garrafa fica aproximadamente a **`H_c + 225 mm`**. Por exemplo, com o copo a 25–35 mm da grelha, o topo fica a **250–260 mm**, ainda sem margem para introduzir ou retirar o conjunto. Como o arame de suspensão está a 150 mm, a garrafa ultrapassa-o em cerca de **100–110 mm**. Medir a altura livre até ao teto antes de fechar a posição dos apoios.

O fundo do copo, o afastamento boca–fundo e a profundidade da água são valores de estudo, não medidas aprovadas. A boca deve permanecer aberta e submersa para o nível se regular por vácuo; não perfurar a garrafa para admitir ar. Um ensaio com água tem de confirmar o nível, a estabilidade e o acesso dos pintos.

## Geometria a parametrizar após as medidas em falta

- **Anel inferior:** passagem interior acima da maior saliência do gargalo que o atravessa, mas abaixo do diâmetro do ombro que suporta a garrafa. A medida de 30,44 mm nos filetes não define por si só o furo do anel.
- **Apoio superior aberto:** diâmetro ajustado à secção real onde toca no corpo; não apertar a PET.
- **Copo:** **rosca interior impressa**, escolhida pelo utilizador. O diâmetro maior medido é 30,44 mm, mas ainda faltam o diâmetro no vale, a altura dos filetes, o avanço e o número de entradas. Preparar primeiro um cupão de encaixe curto e barato com essas cotas ou variantes de ensaio, antes de imprimir o copo completo. O interior do copo continua aberto para a água sair pela boca da garrafa, que ficará submersa. O copo deve ser desmontável para lavar.
- **Ganchos e braço:** ajustar ao diâmetro dos arames e à altura livre. Verificar retenção positiva, peso da garrafa cheia e altura de acesso dos pintos.

## Dados pendentes

1. Medir o diâmetro exterior do anel de suporte abaixo da rosca, o diâmetro do ombro e a distância da boca à zona do corpo onde ficará o apoio em C.
2. Medir ou ensaiar o diâmetro no vale da rosca, altura útil, avanço e número de entradas. Uma foto do interior da tampa original ajuda a identificar o formato sem a incorporar no bebedouro.
3. Confirmar a altura livre real exatamente na posição onde a garrafa ficará, pois o teto não é plano.
4. Indicar o filamento disponível; PETG continua a ser a proposta para o protótipo lavável, sujeita a teste de estanqueidade e limpeza.

**Estado:** medidas principais registadas em [medidas.json](medidas.json) e espaço vertical calculado. Ainda não existe CAD/STL/3MF final nem teste físico. O [esquema V4](../../designs/bebedouro-pintos-conceito-v4-medidas-garrafa.svg) mostra as cotas conhecidas e os pontos a medir.
