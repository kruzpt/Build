# Panda V2 — correção da pose, prévia para validar

[Ver frente e costas da geometria V2](../../designs/anilha-panda-u1-CAD-v2.png)

Esta revisão corrige os braços do CAD V1 de acordo com a imagem de referência enviada pelo utilizador. A pata do lado esquerdo da imagem repousa na bochecha; o braço do lado direito avança à frente do bambu e a pata envolve o caule. O tubo para o lenço continua atrás do corpo, com furo oval de 25 × 18 mm no eixo vertical Z.

A geometria de quatro cores foi gerada com `build_geometry.py`, e `render_preview.py` produziu a imagem a partir das malhas reais. A união total é uma malha fechada e conexa. Todos os pontos inferiores são cortados em Z=0, deixando as faces de contacto planas; as curvas do volume crescem acima desse plano. A altura continua 56,3 mm.

**Estado:** prévia para validação visual. O 3MF V1 continua anterior a esta correção e não deve ser confundido com a pose V2. Ainda não foram feitos fatiamento V2 nem impressão física.
