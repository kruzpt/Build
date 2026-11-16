# Universo do Saber V9 — base azul com cobertura reforçada

A foto da base impressa mostrou faixas largas e palpáveis na face azul. O
fatiamento da V8 tinha **25% gyroid** por baixo dessa face e iniciava a
cobertura com uma ponte na camada 25, chegando à superfície na camada 30.
Isto é compatível com marcas da estrutura interna a passar para a superfície,
embora a fotografia, por si só, não prove a causa única.

No [3MF V9 de dois pratos](../../downloads/universo-saber-suporte-v9-base-lisa-A1-AMS-2-pratos.3mf),
a base azul usa **35% gyroid** e **9 camadas sólidas superiores (1,8 mm)**. A
ponte sob a face principal passa para a camada 22, seguida por sete camadas de
preenchimento sólido e pela superfície da camada 30. A engomagem da superfície
continua ativa. São ajustes do perfil: a **geometria e os encaixes permanecem
idênticos à V6/V7/V8**. O [esquema](../../designs/universo-saber-suporte-v9-base-lisa-pratos.png)
mostra os dois pratos.

O prato 1 conserva o perfil V8 para a placa branca e as letras azuis. A última
camada branca, 35, é preenchida e engomada antes da única troca para azul na
camada 36. As letras azuis continuam com os pequenos espaços preenchidos a
25 mm/s e contornos curtos a 20 mm/s. O relevo azul não é engomado.

| Prato | Tempo digital | Filamento digital | Trocas |
| --- | ---: | ---: | ---: |
| 1 — Placa branca e relevo azul | 4 h 39 min | 64,13 g | 1 |
| 2 — Base azul com cobertura reforçada | 3 h 01 min | 42,75 g | 0 |
| Total | **cerca de 7 h 40 min** | **106,88 g** | **1** |

Abra o 3MF como **projeto** no Bambu Studio para A1, bico de 0,4 mm, PLA e AMS
Lite. **Selecione a bobina azul no perfil que acabou de calibrar e volte a
fatiar**: o 3MF ainda guarda o Generic PLA da versão anterior, pois o valor
final da calibração não foi transferido para o ficheiro. O branco conserva os
valores provisórios confirmados para a mesma bobina do lobo Aquela: 205 °C e
flow 0,98. Não é necessário reimprimir a peça branca já terminada.

O Bambu Studio reabriu e fatiou os dois pratos sem avisos. O percurso da base
mostra a ponte, sete camadas sólidas por cima e a superfície engomada. O
acabamento físico V9 ainda não foi testado; as faixas podem também ter
contribuições da bobina, temperatura ou da superfície da peça. O
[relatório digital](validation.json) inclui a verificação e o SHA-256 do 3MF.
O [script](../tools/refine_universo_stand_v9_base_surface_3mf.py) recria o
ficheiro a partir da V8.
