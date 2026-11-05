# Teste laranja V3 — folga da costura normal

Parte do V2, que o utilizador confirmou ter melhorado a superfície e os cantos.
Altera apenas **`seam_gap`: 15% → 20%**. Este parâmetro refere-se à costura normal,
e é distinto do campo **Scarf slope gap** mostrado nas definições do filamento.
Esse campo foi conservado e a scarf continua em **None**.

Fluxo laranja 0,931, três paredes, sobreposição 10%, direção de enchimento 0° e
preenchimento de lacunas 25 mm/s permanecem iguais. Geometria, posição e pintura
da costura estão preservadas byte a byte. O Gcode foi comparado no Bambu Studio
02.09.01.70: os percursos do topo não mudam; a abertura XY da costura externa
na última camada aumenta de aproximadamente **0,06 para 0,08 mm**.

É uma alteração pequena para tentar reduzir a saliência na costura. O resultado
físico não está comprovado: uma folga excessiva também pode abrir uma pequena
fenda. Não foram alteradas retração ou temperatura para este ensaio.

O ficheiro contém apenas a amostra laranja, sem os relevos decorativos. Abra
como projeto e volte a fatiar com o mesmo filamento e calibração dinâmica que
já usou. As estimativas exatas e verificações estão em `bambu-validation.json`.
Sem brim, suportes ou torre. O projeto de produção continua separado.
