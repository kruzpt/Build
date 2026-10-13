# Joana 12 — V2, vassoura redesenhada e base sem aberturas

A V2 corrige a vassoura fragmentada da primeira conversão e fecha as quatro
aberturas interiores da base, incluindo as pequenas falhas junto ao nome.
O branco da imagem V1 era o fundo a aparecer nos buracos, não um filamento.
Na V2 o interior da silhueta tem uma base preta contínua. O fundo entre as
hastes e à volta da peça continua a ser apenas o fundo da imagem.

A vassoura tem cabo curvo de **2,2 mm**, duas faixas douradas de **1,5 mm**
e três sulcos pretos de **1 mm** na escova. Os sulcos deixam ver a base preta;
não atravessam a peça. Estas formas foram desenhadas em CAD, sem reutilizar
os fragmentos de cor da vassoura anterior.

## Medidas e cores

Mantém **180 × 200,3 mm**, base de **2,4 mm** e relevo até **3,2 mm**.
O nome, o número, as restantes decorações e as hastes mantêm os contornos.
São quatro slots AMS: **1 preto, 2 amarelo/dourado, 3 castanho escuro,
4 bordô**. A V1 fica preservada.

## Impressão e Fusion

Abra `joana-topper-v2-A1-AMS-4-cores.3mf` **como projeto** no Bambu Studio.
É um objeto montado com quatro partes, num único prato, para A1 com bico
0,4 mm e PLA. Confirme as bobinas AMS e fatie antes de imprimir.
Mantém os parâmetros da V1: camada 0,20 mm, três paredes, 20% gyroid,
Arachne, cinco camadas superiores/inferiores, sem suportes, frente para cima.
O perfil base usa Generic PLA, Textured PEI, 220 °C / 65 °C; ajuste se as
bobinas ou a superfície exigirem outros valores. Mantenha a torre de purga.

O 3MF foi exportado, reaberto e fatiado no motor oficial Bambu Studio
2.8.2.61, sem avisos: **16 camadas, sete trocas de filamento**, cerca de
**2 h 21 min e 58 g**, incluindo purgas. O ficheiro é editável e sem G-code
pré-calculado. A impressão física ainda não foi testada.

Para Fusion, extraia a pasta **JoanaTopperV2** do ZIP, conservando
`JoanaTopperV2.py`, `JoanaTopperV2.manifest` e `contours.json` lado a lado.
Adicione a pasta em **Utilities → Scripts and Add-Ins → Scripts** e execute.
O script cria um documento novo com quatro componentes, sketches e extrusões.
A execução dentro do Fusion ainda precisa de confirmação no seu computador.
`TARGET_WIDTH_MM` permite ajustar a largura; o 3MF fornecido é o de 180 mm.

Use mangas ou tubos adequados a contacto alimentar sobre as hastes para
colocar o topper no bolo. A impressão não foi certificada para contacto
alimentar direto.

## Reprodução

```sh
python fusion/tools/refine_joana_topper_v2.py
python fusion/tools/build_joana_topper_3mf.py --version v2 \
  --bambu-bin /caminho/bambu-studio \
  --profiles /caminho/resources/profiles/BBL
```

O primeiro comando deriva a V2 dos contornos V1 preservados; o segundo cria
o projeto nativo e atualiza o ZIP. Os relatórios distinguem a geometria e o
fatiamento verificados da execução Fusion e impressão física ainda pendentes.
