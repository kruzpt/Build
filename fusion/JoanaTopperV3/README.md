# Joana 12 V3 — dourado na vassoura e apoio no bolo

Abra o ficheiro **joana-topper-v3-A1-AMS-4-cores.3mf** como projeto no Bambu
Studio. O nome do objeto e do prato inclui **V3**. As capturas anteriores com
buracos na base e vassoura fragmentada correspondem à V1, que fica preservada.

## Alterações

- Três traços dourados nas cerdas da vassoura e uma ponteira dourada no cabo.
- Topos do nome e do número polidos para fechar pequenos recortes da conversão,
  mantendo as pontas do estilo gótico.
- Duas hastes iguais, sem degraus nas laterais: **8,5 mm de largura**, mesma
  união à travessa e **44 mm de entrada** até ao apoio. Ambas têm ponta de
  6 mm com extremo plano de 1,1 mm.
- Travessa preta de **88 × 6 mm**, com cantos arredondados, unindo as hastes.
  Tem **8 mm de profundidade** para aumentar a superfície que assenta no bolo.
- Base contínua, sem buracos internos nem uma quinta cor.

[Imagem frontal do CAD](../../designs/joana-topper-v3-CAD.png) e
[vista frontal/lateral do apoio](../../designs/joana-topper-v3-apoio.png).
A linha verde desta última imagem é apenas a referência do bolo, não um
filamento a imprimir. O apoio limita a entrada das hastes, mas ainda não foi
testado num bolo; a estabilidade e o afundamento dependem da consistência.

## Medidas e impressão

Largura nominal **180 mm**, altura **200,3 mm**. A base e as hastes continuam
com **2,4 mm de espessura**; a decoração chega aos **3,2 mm**. Apenas o apoio
local chega aos **8 mm**. É uma única peça montada, sem colagem do apoio.

Slots AMS: **1 preto, 2 amarelo/dourado, 3 castanho escuro, 4 bordô**.
Confirme o mapeamento das quatro bobinas. Imprime deitado, frente para cima,
em A1 com bico de 0,4 mm, PLA e Textured PEI, sem suportes. A travessa mais
espessa cresce a partir da mesa, pelo que não exige uma ponte em suspensão.

O perfil mantém camada **0,20 mm**, três paredes, 20% gyroid, Arachne e cinco
camadas superiores/inferiores. Usa Generic PLA, 220 °C no bico / 65 °C na
Textured PEI; adapte às bobinas se necessário e volte a fatiar. Mantenha as
purgas e a torre de purga para as cores.

Exportação, reabertura e fatiamento verificados com Bambu Studio 2.8.2.61,
sem avisos: **40 camadas, dez trocas de filamento**, aproximadamente
**2 h 32 min e 62 g**, incluindo purgas. O ficheiro é editável e sem G-code
pré-calculado. As 40 camadas devem-se ao apoio de 8 mm; o restante topper
termina aos 3,2 mm. São estimativas; a impressão física não foi testada.

Proteja a superfície de apoio com filme próprio para alimentos e as hastes
com mangas/tubos adequados antes de colocar a peça no bolo.

## Fusion e reprodução

Extraia **JoanaTopperV3** do ZIP, deixando o script, manifest e `contours.json`
juntos. Adicione a pasta em **Utilities → Scripts and Add-Ins → Scripts** e
execute `JoanaTopperV3.py`. Cria um documento novo com quatro componentes,
sketches, extrusões e uma extrusão unida para o apoio. `TARGET_WIDTH_MM`
permite mudar a largura sem alterar as espessuras. A execução no Fusion ainda
precisa de confirmação; a geometria STL e o fatiamento nativo foram verificados.

```sh
python fusion/tools/refine_joana_topper_v3.py --stop-depth 8
python fusion/tools/build_joana_topper_3mf.py --version v3 \
  --bambu-bin /caminho/bambu-studio \
  --profiles /caminho/resources/profiles/BBL
```

O gerador também aceita `--stop-depth 2.4` para uma travessa plana. O pacote
publicado usa **8 mm**. As versões V1 e V2 continuam disponíveis separadamente.
