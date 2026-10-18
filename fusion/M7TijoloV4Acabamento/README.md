# M7 — ensaio de acabamento das paredes do corpo V4

Perfil preparado para reduzir as marcas físicas alinhadas com as divisórias,
incluindo a face posterior. É uma variante de configuração da geometria V4:
a V5 com placa única e moldura continua a aguardar criação do CAD.

Alterações aplicadas apenas ao objeto do corpo terracota, em **Objects**:

| Secção em inglês | Opção | Valor |
| --- | --- | --- |
| Quality | Wall generator | Classic |
| Quality → Advanced | Order of walls | outer/inner |
| Speed | Outer wall | 50 mm/s |
| Speed | Inner wall | 100 mm/s |
| Speed → Acceleration | Outer wall | 2000 mm/s² |

As paredes exteriores passam a ser depositadas antes das interiores; o gerador
Classic utiliza larguras constantes. A velocidade exterior e a aceleração foram
reduzidas para limitar transições e vibrações. A ligação térmica entre divisórias
e casca continua a existir: não se garante eliminar as marcas só com o perfil.

Mantêm-se camada de 0,20 mm, três paredes, limite volumétrico laranja de 8 mm³/s,
fluxo 0,98 e temperatura de 220 °C. O SUNLU PLA+ precisa de calibração de
**Flow Rate** e **Flow Dynamics** na máquina real; não foi inventado um valor K
nem alterado o fluxo ou a temperatura sem dados da bobina. Mais Wall loops não
engrossa a geometria existente, já quase maciça. Infill/Wall overlap não atua na
união geométrica das divisórias deste corpo, sem preenchimento esparso útil.

Abrir o novo 3MF como **projeto**, preservando os seus ajustes. Selecionar o
objeto do prato 1 para ver as substituições em Objects; a vista Global continua
a mostrar as definições herdadas dos restantes objetos. Imprimir primeiro uma
amostra à escala original com todas as divisórias e cerca de 15 mm de altura,
obtida por corte horizontal no Studio. Se houver boa melhoria, confirmar num
tijolo completo. Se persistirem sulcos, o próximo passo é engrossar a casca no
CAD, mantendo os encaixes e a espessura residual atrás do rebaixo da futura V5.

O relatório JSON regista a reabertura e o fatiamento do prato 1 no Bambu Studio
oficial 02.08.02.61. Sem validação física. Os outros pratos conservam as definições
e a geometria original. O pacote contém o 3MF, este documento, o relatório e o
script reproduzível; não substitui o pacote original V4.
