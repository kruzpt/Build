# Novo ensaio de rosca V3 — após B ficar apertado

O anel **B da V2 não enroscou** na garrafa. Não vale imprimir A ou C, que são mais apertados, nem D, que mantém os mesmos diâmetros de B. Esta revisão coloca **dois testes pequenos em pratos separados** no [3MF para Bambu A1](ensaio-rosca-garrafa-v3-A1-04-PLA.3mf).

| Ordem | Anel | Prato | Função | Medidas |
| --- | --- | ---: | --- | --- |
| 1 | G liso | 1 | Ver se o diâmetro passa pelo gargalo, sem tentar enroscar | Ø interno 29,7 mm; altura 3 mm |
| 2 | E roscado | 2 | Testar maior folga, se G passar | Furo Ø29,0 mm; fundo da ranhura Ø31,1 mm; altura 9 mm |

Para comparar, B tinha furo Ø28,6 mm e fundo da ranhura Ø30,5 mm. E conserva **provisoriamente** as mesmas três entradas e o avanço de 9 mm por volta; esses dados reais da garrafa ainda não foram medidos.

**Procedimento:** imprimir apenas o prato 1, G, em PLA. Experimentar na garrafa vazia, à mão e sem forçar. Se G não passar, parar e confirmar novamente o diâmetro exterior e a calibração dimensional; não imprimir E. Se G passar livremente, imprimir só o prato 2, E, e testar suavemente se começa a enroscar. Se E não começar, o passo/número de entradas/perfil provavelmente não coincide: parar e medir a rosca original, sem imprimir mais variantes por tentativa.

O projeto foi reaberto e fatiado em Bambu Studio CLI para A1, bico 0,4 mm, PLA genérico e PEI liso, camada 0,16 mm. Sem suportes nem brim; sem avisos no fatiamento. Estimativas: **G 13,5 min / 1,15 g** e **E 35,3 min / 4,83 g**. Ajustar o perfil ao PLA realmente carregado. As duas malhas são fechadas; **nenhuma foi testada fisicamente**. Não usar os anéis para fornecer água aos pintos.

O código editável está em [ensaio_rosca.scad](ensaio_rosca.scad), os STL estão em `stl/` e os resultados do fatiador em [validation.json](validation.json).
