# Ensaio V1 da rosca da garrafa do bebedouro

**OBSOLETO — NÃO IMPRIMIR.** O utilizador corrigiu o diâmetro exterior dos filetes para **29,25 mm** e a distância da boca à base da rosca para **7,20 mm**. Os STL e o 3MF desta V1 usam as cotas anteriores e não servem para esta garrafa. Usar o [ensaio V2](../BebedouroPintosRoscaTesteV2/README.md).

Este é um **cupão de encaixe**, ainda não o copo nem o bebedouro. [Prévia do anel B](images/anel-B-CAD.png) · [quatro pratos no Bambu](images/pratos-Bambu.png). A garrafa tem Ø30,44 mm medidos sobre os filetes e 10,82 mm da boca à base da rosca. A fotografia da tampa mostra saliências interiores, mas não permite extrair com segurança o avanço nem o número de entradas. Para reduzir o risco, as quatro hipóteses estão em pratos separados e identificadas por entalhes na borda.

| Anel | Prato | Entalhes | Hipótese de avanço por volta | Furo entre filetes | Fundo da ranhura interior |
| --- | ---: | ---: | ---: | ---: | ---: |
| B | 1 | 2 | 9,0 mm | Ø29,8 mm | Ø31,7 mm |
| A | 2 | 1 | 9,0 mm | Ø29,4 mm | Ø31,3 mm |
| C | 3 | 3 | 10,5 mm | Ø29,4 mm | Ø31,3 mm |
| D | 4 | 4 | 10,5 mm | Ø29,8 mm | Ø31,7 mm |

As quatro variantes assumem provisoriamente **três entradas**. Estes valores são hipóteses de calibração, não uma norma identificada para esta garrafa. O anel tem Ø42 × 12 mm, chanfros de entrada e uma rosca interior de teste. As malhas foram verificadas como fechadas e com uma peça sólida cada.

## Como usar

1. Abrir o [projeto Bambu A1](ensaio-rosca-garrafa-v1-A1-04-PLA.3mf) e **imprimir só o prato 1, anel B**. Está preparado para bico 0,4 mm, PLA genérico, camada 0,16 mm, PEI liso, sem suportes nem brim. O Bambu Studio prevê aproximadamente **46 minutos e 7 g** para esse prato. Escolher o perfil real do filamento antes de iniciar.
2. Experimentar na garrafa vazia, apenas com os dedos e sem forçar. Registar se entra, quantas frações de volta faz, se chega ao fim e se sai sem danificar a PET.
3. Se B entrar demasiado solto, testar A. Se B começar a enroscar e travar progressivamente, testar D para comparar o avanço. Se B nem iniciar, **não forçar**: medir o diâmetro no vale e observar entradas e passo antes de escolher outro anel.
4. Não usar os cupões para dar água aos pintos. Depois de escolher a geometria, gerar o copo completo e repetir o ensaio no material final, pois a contração de PLA e PETG difere.

O código editável é [ensaio_rosca.scad](ensaio_rosca.scad). `build_bambu.py` regenera o projeto Bambu com as dependências do checkout. O [relatório do fatiador](validation.json) inclui tempos e consumos por prato. Os STL individuais estão em `stl/`. Nenhum encaixe ou impressão física foi testado pelo assistente.
