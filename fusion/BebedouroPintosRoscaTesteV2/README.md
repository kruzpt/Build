# Ensaio V2 da rosca da garrafa do bebedouro

Este é um **anel de teste de encaixe**, ainda não o copo do bebedouro. [Prévia do anel B](images/anel-B-CAD.png) · [quatro pratos no Bambu](images/pratos-Bambu.png). Corrige as medidas da garrafa indicadas pelo utilizador: **Ø29,25 mm** sobre os filetes e **7,20 mm** da boca à base da rosca. Os cerca de 10,82 mm referem-se à base da tampa, não à base da rosca. **Não imprimir a V1**.

O passo, o diâmetro no vale e o número de entradas da rosca ainda não foram medidos. A fotografia da tampa não permite identificá-los com segurança. Por isso, os quatro anéis são hipóteses para uma prova suave, cada uma num prato separado. Todos assumem provisoriamente três entradas.

| Anel | Prato | Entalhes | Avanço hipotético por volta | Furo central | Fundo da ranhura interior |
| --- | ---: | ---: | ---: | ---: | ---: |
| B | 1 | 2 | 9,0 mm | Ø28,6 mm | Ø30,5 mm |
| A | 2 | 1 | 9,0 mm | Ø28,2 mm | Ø30,1 mm |
| C | 3 | 3 | 10,5 mm | Ø28,2 mm | Ø30,1 mm |
| D | 4 | 4 | 10,5 mm | Ø28,6 mm | Ø30,5 mm |

Os anéis medem Ø40 × 9 mm, têm chanfros de entrada e entalhes para identificação. A geometria da ranhura é experimental; o diâmetro da ranhura não indica o perfil real da rosca da garrafa.

## Como experimentar

1. Abrir o [projeto Bambu A1](ensaio-rosca-garrafa-v2-A1-04-PLA.3mf) e imprimir **apenas o prato 1, anel B**. O perfil é para bico 0,4 mm, PLA genérico, camada 0,16 mm e PEI liso, sem suportes nem brim. O fatiador estima cerca de **35 minutos e 4,9 g** para B. Confirmar o filamento real na impressora.
2. Tentar enroscar B na garrafa vazia **à mão, sem forçar**. Anotar se entra, quantas frações de volta faz e se sai sem marcar o PET.
3. Se B ficar muito solto, testar A. Se começar a enroscar e prender gradualmente, comparar D. Se B nem começar, parar e medir o diâmetro no vale e o passo da rosca antes de imprimir outros anéis.
4. Não usar os anéis para dar água aos pintos. Depois da prova de encaixe, a rosca deve ser integrada no copo e ensaiada novamente no material final.

O modelo editável é [ensaio_rosca.scad](ensaio_rosca.scad), os STL individuais estão em `stl/`, e o [relatório de fatiamento](validation.json) contém as estimativas por prato. Os STL foram verificados como malhas fechadas de uma única peça e o 3MF foi reaberto e fatiado sem avisos. **O encaixe físico e a estanqueidade não foram testados.**
