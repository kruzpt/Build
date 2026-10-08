# Clínica Essencial V3 Fast

A V3 original criava **628 sketches e 628 extrusões só para os QR**
(352 Instagram + 276 Google). Esta versão cria **dois sketches e duas
extrusões**, preservando todos os retângulos, dimensões e endereços.

Os sketches são resolvidos depois de desenhar os contornos e permanecem
ocultos. Os QR são unidos à placa no fim, para que os restantes cortes e
decorações trabalhem sobre uma peça mais simples. Há uma janela de progresso
com cancelamento entre etapas e atualização da interface.

## Executar

Não execute duas instâncias ao mesmo tempo. Se a V3 antiga ainda estiver
a executar, espere que termine ou cancele quando a aplicação permitir.
Se for necessário reiniciar o Fusion, tenha atenção a outros documentos
com alterações por guardar.

Extraia `essencial-fusion-v3-fast.zip`, adicione a pasta `EssencialV3Fast`
em **Utilities → Scripts and Add-Ins → Scripts → + / Add** e execute.
Cria um documento novo. Quando terminar, guarde como `.f3d`.

O progresso pode ficar parado enquanto uma operação geométrica está a ser
calculada: não é uma medição contínua nem há cancelamento dentro do cálculo
do kernel. Se surgir erro, a mensagem indica a etapa e o traceback.

## Modelo preservado

- Duas peças: placa e base, um corpo sólido em cada componente.
- Símbolos Instagram e Google, QR respetivos e ondas contactless.
- Logótipo com serifas curvas, estrelas e sem barra central.
- Duas cavidades internas de Ø25,8 mm para etiquetas de Ø25 mm.
- Pausa após Z=3,8 mm, antes do teto, com a placa deitada, face para cima.
- Mesmas folgas de encaixe da V3 e relevo dos QR de 0,6 mm.

As instruções completas de impressão/cores/etiquetas estão em
`fusion/EssencialV3/README.md` no repositório. Confirme a espessura da etiqueta,
a pausa no slicer e o bridging do teto numa amostra antes da placa completa.

## Validação

Os retângulos emitidos pela rotina de QR foram comparados com os da V3,
e testes com uma API simulada verificam que há uma única extrusão por QR.
Os testes de geometria da V3 também são aplicados ao código otimizado.
O ZIP corresponde ao script atual.

Não foi possível executar Autodesk Fusion na cloud: a redução de operações
foi verificada, mas o tempo real e a conclusão no Fusion precisam de ser
confirmados na máquina do utilizador.

Regenerar: `python fusion/tools/optimize_essencial_v3.py`.
