# Universo do Saber V8 — letras com acabamento mais controlado

Este é o perfil recomendado para imprimir o suporte do Universo do Saber na
Bambu Lab A1, bico de 0,4 mm, PLA e AMS Lite. O [3MF de dois pratos](../../downloads/universo-saber-suporte-v8-letras-premium-A1-AMS-2-pratos.3mf)
abre como projeto no Bambu Studio. A [prévia](../../designs/universo-saber-suporte-v8-letras-premium-pratos.png)
mostra a posição das peças. A **geometria é idêntica à V6 e V7**; os encaixes
não mudaram.

A superfície branca é completada e engomada na camada **35**. A única troca
para azul ocorre na camada **36**; o relevo azul ocupa as camadas 36–39 e não é
engomado. A superfície ampla da base azul é engomada no segundo prato. O perfil
mantém as seis camadas sólidas superiores, cinco inferiores, velocidades baixas
nas paredes e ausência de brim e suportes da V7.

## Melhoria das letras relativamente à V7

| Ajuste | V7 | V8 |
| --- | ---: | ---: |
| Preenchimento de espaços estreitos | 250 mm/s configurados, limitados pelo fluxo | **25 mm/s** |
| Contornos curtos | redução automática sem limiar definido | **20 mm/s** até 10 mm |
| Aceleração da parede exterior | 5000 mm/s² | **1000 mm/s²** |
| Preenchimento sólido interno | 250 mm/s configurados, limitados pelo fluxo | **60 mm/s** |
| Parede única nas superfícies de cima do relevo | permitida | desativada onde a largura comportar mais paredes |

O fatiamento V8 mostra preenchimento dos pequenos espaços das letras na última
camada azul, agora a 25 mm/s. Os contornos curtos são depositados a 20 mm/s.
Esses ajustes visam reduzir pequenos vazios e melhorar a regularidade das
bordas. Não eliminam, por si só, um espaço menor do que a resolução física do
bico; o resultado final precisa de confirmação na impressão.

O utilizador confirmou que vai usar a mesma bobina branca do lobo Aquela. O
branco conserva os valores guardados **provisoriamente**: 205 °C, fluxo 0,98 e
limite volumétrico de 8 mm³/s. O azul continua em Generic PLA, pois não há
calibração específica guardada para essa bobina. Confirme os filamentos branco
e azul no AMS antes de iniciar a impressão.

| Prato | Tempo digital | Filamento digital | Trocas |
| --- | ---: | ---: | ---: |
| 1 — Placa branca e relevo azul | 4 h 39 min | 64,13 g | 1 |
| 2 — Base azul | 2 h 40 min | 36,06 g | 0 |
| Total | **cerca de 7 h 19 min** | **100,19 g** | **1** |

O Bambu Studio reabriu e fatiou ambos os pratos sem avisos. Os percursos
confirmam a última camada branca engomada antes da troca, os pequenos espaços
preenchidos nas letras, uma só troca de cor e nenhum suporte. A impressão física
ainda não foi testada. O [relatório digital](validation.json) inclui o SHA-256
do 3MF. O [script](../tools/refine_universo_stand_v8_letters_3mf.py) recria o
perfil a partir da V7 e repete as verificações.
