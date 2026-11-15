# Memorial de Natal V4 — cadeiras de tábuas lisas

Esta variante mantém as medidas e a montagem da V3: base Ø236 mm, árvore com 200 mm de altura atrás e lugar para uma vela LED Ø50 mm à frente. As duas cadeiras compactas de tábuas continuam em kit, mas **todas as faces das cadeiras são planas, sem veios, nós, riscos ou outro relevo a imitar madeira**. Os encaixes e as posições permanecem iguais; o padrão V3 continua disponível como projeto separado.

## Ficheiros

- `downloads/natal-memoria-cadeiras-v4-tabuas-lisas-A1-PLA.3mf`: projeto Bambu A1 com cinco pratos editáveis.
- `fusion/NatalMemoriaCadeirasV4Lisas/memorial.scad`: fonte paramétrica OpenSCAD, incluindo texto da árvore.
- `fusion/NatalMemoriaCadeirasV4Lisas/stl/`: STL binários neutros de cada peça.
- `fusion/NatalMemoriaCadeirasV4Lisas/stl/joint_coupon.stl`: pequena amostra da junta das cadeiras.
- `designs/natal-memoria-v4-tabuas-lisas.png`: pré-visualização do conjunto a partir dos STL.
- `designs/natal-memoria-v4-tabuas-lisas-detalhe.png`: vista aproximada da cadeira lisa.

## Impressão

O 3MF usa Bambu A1, bico 0,4 mm, PLA e prato PEI liso. Camada 0,12 mm, três perímetros, seis camadas sólidas superiores, cinco inferiores, 15% gyroid e 25 mm/s na parede exterior. Sem suportes nem brim. As temperaturas e o fluxo do filamento são genéricos e devem ser ajustados ao PLA real.

1. Amostra bicolor das letras pequenas.
2. Base creme.
3. Árvore bicolor, texto plano voltado para o prato.
4. Quatro laterais lisas das cadeiras.
5. Travessas lisas: seis de encosto, quatro de assento e duas inferiores.

Se a base e a árvore da V3 já estiverem impressas, basta imprimir **os pratos 4 e 5** desta V4. As dimensões e os encaixes são compatíveis. Testar `joint_coupon.stl` antes de montar e colar as cadeiras. Uma superfície FDM lisa continua a mostrar linhas de camada e de preenchimento, mas não tem o relevo decorativo da V3.

Para editar a mensagem, alterar `line_1` a `line_10` em `memorial.scad`, exportar novamente os STL da árvore e da amostra de texto, e reconstruir o 3MF. O comprimento das linhas não se ajusta automaticamente.

## Validação

Os STL foram exportados pelo OpenSCAD e verificados como malhas fechadas. O 3MF foi reaberto e fatiado digitalmente em cinco pratos sem avisos. A folga das juntas e a leitura das menores letras ainda precisam de impressão física.
