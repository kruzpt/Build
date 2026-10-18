# Paleta de Natal V3 — oito cavidades periféricas

Revisão solicitada: cavidades menores a acompanhar o contorno, em vez de quatro
reservatórios no centro. Mantém 140 × 200 mm, abertura de polegar de 28 × 44 mm
e as dimensões propostas dos seis enfeites. As versões anteriores são preservadas.

## Geometria

- Oito cavidades de Ø24 mm, profundidade 6 mm; cerca de 2 ml úteis cada
  (2,68 ml até ao bordo, calculados pelo volume CAD).
- Fundo de 3 mm, paredes locais de 2,4 mm, canto interior arredondado de 1,5 mm.
- Altura máxima 9 mm. Centro plano livre para mistura de tintas.
- Centros distribuídos por comprimento de arco numa curva interior ao contorno
  elíptico, com rebordos separados. A gravação não invade as cavidades.
- Para colocar tinta diretamente; não são encaixes dimensionados para frascos
  comerciais. A redução de diâmetro deixa de servir os potes previstos na ideia
  inicial, cujas dimensões também não tinham sido verificadas fisicamente.

## Referências consultadas

Consulta em 18/10/2026, através de fontes públicas acessíveis nesta rede:

- [Watercolor Palette, Michael Scherotter](https://github.com/mscherotter/wcpal):
  documentação e fonte OpenJSCAD com reservatórios para tintas e áreas de mistura.
- [Muddy Waters mini travel watercolour palette](https://github.com/mrmonkington/muddywaters):
  documentação de paleta paramétrica com reservatórios pequenos, áreas de mistura
  e tampa articulada; número de reservatórios configurável.

A comparação favoreceu reservar zonas distintas para tintas e mistura. A forma
oval, a disposição periférica e as dimensões desta V3 são desenho próprio segundo
o pedido; não foram copiadas geometrias ou dimensões dos projetos de referência.
As referências são projetos de fabricantes amadores, não normas dimensionais
de potes ou certificações. A pesquisa geral está limitada aos destinos permitidos
pela rede do ambiente.

## Ficheiros e reprodução

- `designs/kit-natal-paleta-v3-CAD-dimensoes.png`: vistas do CAD e secção cotada.
- `downloads/kit-natal-paleta-v3-dimensoes.pdf`: folha A4 para partilhar.
- `downloads/kit-natal-paleta-v3-8-cavidades.stl`: corpo único fechado.
- `downloads/kit-natal-paleta-v3-A1-PLA.3mf`: projeto nativo A1, bico 0,4 mm.

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_kit_natal_palette_v3.py --build-3mf
python -B fusion/tools/export_kit_natal_dimension_sheet.py --version v3
```

O gerador valida malha fechada, fundo fechado de cada cavidade, separação dos
rebordos e posição na mesa. O projeto foi exportado, reaberto e fatiado pelo
Bambu Studio 02.08.02.61: camada 0,20 mm, 3 paredes, preenchimento 100%, sem
suportes nem mudanças de filamento. Estimativa: 86,93 g, 3 h 41 min, 1,39 € de
PLA castanho a 16 €/kg. Não inclui energia, trabalho, acessórios ou enfeites.

Ainda sem impressão física: testar com água antes de colocar tinta. Malha fechada
não garante que a impressão seja estanque. Os seis enfeites continuam propostas
dimensionais, sem novos STL nesta revisão. Os relatórios JSON guardam resultados
e hashes desta versão.
