# Universo do Saber V7 — perfil de acabamento premium

Esta versão conserva **exatamente a geometria da V6**: placa branca de 200 ×
80 × 7 mm, relevo azul de 0,8 mm e base azul de 111 × 80 × 6 mm, com os mesmos
encaixes. A alteração é apenas do perfil de impressão no 3MF de dois pratos.

Abra [o projeto 3MF](../../downloads/universo-saber-suporte-v7-perfil-premium-A1-AMS-2-pratos.3mf)
no Bambu Studio como **projeto**, para a Bambu Lab A1 com bico de 0,4 mm e PLA.
O [esquema dos pratos](../../designs/universo-saber-suporte-v7-perfil-premium-pratos.png)
mostra a disposição das peças. Confirme branco no primeiro filamento e azul no
segundo antes de imprimir.

## Sequência da superfície e cor

No prato 1, a última camada branca é a **35**. O fatiamento mostra a superfície
branca preenchida e depois engomada nessa camada. A única troca para azul vem
na camada **36**, que inicia o relevo. O relevo azul conserva o contorno nítido,
sem engomagem. A superfície ampla da base azul, no prato 2, também é engomada.

## Ajustes do perfil

| Parâmetro | V7 |
| --- | --- |
| Altura de camada | 0,20 mm |
| Camadas sólidas superiores / inferiores | 6 / 5 |
| Parede exterior / interior | 35 / 80 mm/s |
| Superfície superior | 25 mm/s |
| Primeira camada / preenchimento da primeira | 20 / 30 mm/s |
| Engomagem | apenas superfícies superiores escolhidas; ziguezague, 30 mm/s, fluxo 10%, espaçamento 0,15 mm, recuo 0,21 mm |
| Brim e suportes | desativados |
| Torre de purga | ativada para a troca de cor |

O branco foi definido provisoriamente a **205 °C**, fluxo **0,98** e velocidade
volumétrica máxima **8 mm³/s**, com base nas notas guardadas para o PLA branco
usado no lobo Aquela. O utilizador confirmou que vai usar a mesma bobina.
Esses valores ainda não foram confirmados como calibração física para este
suporte. Se usar outra bobina branca, selecione o respetivo
perfil calibrado e volte a fatiar. O azul conserva o Generic PLA da V6; ainda
não há um perfil azul calibrado guardado.

| Prato | Tempo digital | Filamento digital | Trocas |
| --- | ---: | ---: | ---: |
| 1 — Placa branca e relevo azul | 3 h 59 min | 64,13 g | 1 |
| 2 — Base azul | 2 h 19 min | 36,06 g | 0 |
| Total | **cerca de 6 h 17 min** | **100,19 g** | **1** |

O Bambu Studio reabriu e fatiou os dois pratos sem avisos. Foram verificados
os percursos da última camada branca, da troca de cor, da engomagem e a ausência
de suportes. A geometria interna do 3MF é idêntica à V6. O acabamento final,
adesão e encaixe continuam dependentes da impressão real. As estimativas incluem
a preparação calculada pelo fatiador e podem variar no equipamento.

O script [refine_universo_stand_v7_profile_3mf.py](../tools/refine_universo_stand_v7_profile_3mf.py)
recria o 3MF a partir da V6 e executa a verificação digital. O
[relatório](validation.json) guarda o resultado e o SHA-256 do 3MF.
