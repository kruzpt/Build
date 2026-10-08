# Clínica Essencial V4 — QR de 64 mm

Extraia `essencial-fusion-v4-qr64.zip`, adicione a pasta `EssencialV4` em
**Utilities → Scripts and Add-Ins → Scripts → + / Add** no Fusion e execute.
Cria um documento novo, com progresso e cancelamento entre etapas.

## Alterações

- Ambos os campos QR passaram de **52 para 64 × 64 mm**, incluindo a margem
  branca de quatro módulos por lado.
- A placa passou de **180 para 200 mm de largura**, mantendo 220 mm de altura
  e 5 mm de espessura. Isto permite aumentar os QR sem invadir as zonas NFC.
- Instagram em cima e Google em baixo, símbolos à esquerda e contactless
  à direita. Os campos são x=49..113 mm, y=81..145 e y=4..68 mm.
- As duas etiquetas têm centros (133,113) e (133,36) mm. A coluna foi movida
  20 mm para a direita; o texto da clínica foi ajustado para dar espaço.
- O logótipo mantém a posição e os contornos da V3.

| Código | Matriz incluindo margem | Passo de cada módulo |
| --- | --- | --- |
| Instagram | 45 × 45 | 1,422 mm |
| Google | 41 × 41 | 1,561 mm |

Os retângulos em relevo têm um recuo técnico de 0,01 mm nas bordas; o traço
mínimo preto resultante é cerca de 1,402 mm no Instagram e 1,541 mm no Google.
O relevo continua com 0,6 mm. Módulos pretos sobre branco, superfície mate e
margens brancas limpas são necessários para uma boa leitura. Bico de 0,4 mm
e camada de 0,2 mm são pontos de partida; teste uma amostra antes da placa.

## Mantido da V3 Fast

- Duas peças, com um corpo sólido por componente: placa e base.
- **Apenas dois sketches e duas extrusões para os QR**, independentemente
  do aumento de tamanho; não se aumentou o número de operações de QR.
- Base de 160 × 70 × 18 mm e língua 120 × 5 × 12 mm. O encaixe mantém
  ranhura 120,6 × 5,5 mm, entrada alargada e espaço de 0,8 mm no fundo.
- Etiquetas NFC de Ø25 mm, cavidades Ø25,8 mm, entre Z=3,0 e Z=3,8 mm.
- Piso e teto das cavidades fechados no CAD, sem tampas adicionais.

**Pausa após terminar Z=3,8 mm, antes da primeira camada do teto.** Com todas
as camadas de 0,2 mm, incluindo a primeira, pause depois da camada 19 e antes
da 20. Confirme na pré-visualização do slicer. Programe a etiqueta superior
para Instagram e a inferior para Google, teste e cole-as no piso das cavidades.

Imprima a placa deitada, face decorada para cima. Não gere suportes dentro
das cavidades. Confirme espessura da etiqueta (até cerca de 0,6 mm neste draft),
temperatura admissível e bridging do teto numa amostra. Consulte também as
instruções detalhadas em `fusion/EssencialV3/README.md` no GitHub.

A silhueta total da placa, com círculo e língua, ocupa cerca de **210 × 270 mm**
em XY; verifique a área útil da impressora antes de fatiar.

## Validação

QR descodificados para os mesmos endereços no esquema publicado; contornos,
folgas, separação das zonas e altura de pausa verificados na cloud. A rotina
de QR é testada com API simulada para confirmar duas extrusões e as novas
dimensões dos módulos. A execução real no Fusion e a impressão continuam
pendentes. O PNG é um esquema, não um render CAD.

Regenerar com as dependências QR: `python fusion/tools/generate_essencial_v4.py`.
