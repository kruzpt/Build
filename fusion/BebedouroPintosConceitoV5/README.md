# Bebedouro V5 — copo com rosca impressa

[Esquema em PNG](../../designs/bebedouro-pintos-copo-rosca-conceito-v5.png) · [Esquema em SVG](../../designs/bebedouro-pintos-copo-rosca-conceito-v5.svg) · [Medidas confirmadas e pendentes](../BebedouroPintosConceitoV4/medidas.json)

O utilizador corrigiu as medidas para **29,25 mm no exterior dos filetes da garrafa** e **7,20 mm da boca à base da rosca**; os 10 e poucos milímetros anteriores referiam-se à base da tampa. O arame da gaiola tem aproximadamente **3 mm** e foi escolhida a **rosca impressa no copo**. Esta V5 detalha o ensaio antes de modelar o conjunto final. A V3 continua a definir o suporte: anel inferior fechado sob o ombro da garrafa, apoio superior aberto em C e braço com ganchos.

## Funcionamento proposto

O copo raso tem fundo contínuo. No centro nasce um colar de rosca interior impressa. A boca da garrafa fica aberta cerca de 5 mm acima do fundo; aberturas na base do colar deixam a água passar para a zona de beber. O nível da água terá de cobrir a boca e ficar abaixo do bordo do copo. Assim, qualquer água que atravesse a folga da rosca continua **dentro** do copo, e a rosca serve para reter a garrafa sem ser tratada como vedação.

Dimensões **apenas de estudo**: copo exterior Ø88 mm, profundidade aproximadamente 15 mm, fundo 3 mm, parede 2,4 mm, boca cerca de 5 mm acima do fundo. A altura do colar e a abertura lateral não estão fechadas. A profundidade e a acessibilidade devem ser verificadas com os pintos; o mecanismo por vácuo exige ensaio com água, garrafa cheia e parcialmente vazia.

## Primeiro ensaio de impressão

Antes do copo completo, imprimir um anel de prova baixo (~9 mm de altura) com diâmetro exterior próximo de 40 mm. A distância de 7,20 mm até à base da rosca dá uma referência para esse cupão, mas não mede sozinha a extensão dos filetes. A rosca interior deve partir do diâmetro maior corrigido de 29,25 mm e ter variantes de folga identificadas. Não criar ainda um filete definitivo a partir apenas destas duas medidas: faltam o diâmetro no vale, passo/avanço e número de entradas. A foto do interior da tampa original pode ajudar a reconhecer o formato; a tampa não será incorporada no produto.

O [primeiro ensaio de rosca V1](../BebedouroPintosRoscaTesteV1/README.md) usava as medidas incorretas e ficou **obsoleto**. O [ensaio V2](../BebedouroPintosRoscaTesteV2/README.md) substitui as cotas antes de qualquer impressão.

O gancho para o arame de aproximadamente 3 mm também pode ser ensaiado numa amostra pequena, com ranhuras de 3,3 / 3,5 / 3,7 mm. É apenas uma proposta de tolerâncias; a fixação final deve ter retenção positiva e suportar a garrafa cheia. As posições de altura 0 e +20 mm usam o arame de 150 mm; +40 mm fica condicionada à folga real sob o teto da frente, perto dos 330 mm.

## Impressão e validação

O copo deverá ser impresso com o fundo no prato, colar para cima, sem suportes sob a zona que contém água. PETG é a proposta para o protótipo; o filamento disponível ainda não foi confirmado. Testar encaixe sem forçar a PET, retenção da garrafa, fluxo, nível, fugas, limpeza e acesso dos pintos. O esquema é uma proposta de geometria, **não é STL/3MF final nem um bebedouro funcional validado**.
