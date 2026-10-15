# Universo do Saber — suporte desmontável, conceito 02

[Ver o esboço V2](suporte-universo-saber-conceito-v2.png).

[Conceito V1 preservado](README-suporte-telemovel-encaixe.md).

## Âmbito

Atualização do plano e da imagem: acrescentar o símbolo US, o texto **Centro de
Estudos / Universo do Saber** e dois motivos de livros a partir da referência
fornecida. Manter duas peças principais desmontáveis, alinhadas e com ambos os
apoios em contacto com a mesa. Reduzir cores simultâneas por camada.

Não foram criados CAD, STL, código Fusion ou projetos Bambu nesta fase.

## Montagem e ângulos propostos

- Costas de aproximadamente **160 × 80 × 6 mm** e apoio transversal de
  aproximadamente **110 × 80 × 6 mm**; os relevos e batentes acrescentam altura.
- Costas a **70° da mesa**, ou seja, 20° inclinadas para trás em relação à vertical.
  Com as peças perpendiculares, o apoio transversal desce cerca de 20° para a
  frente. As duas peças serão dimensionadas na mesma montagem CAD.
- A posição dos encaixes e os chanfros dos pés devem colocar as duas superfícies
  de contacto no mesmo plano, sem depender de uma peça fletir ou de cola.
- Como relação geométrica inicial de eixos sem espessura, uma projeção de 80 mm
  do encaixe até ao extremo dianteiro corresponde a cerca de 29,12 mm entre o
  encaixe e o extremo inferior das costas: `80 / tan(70°)`. Isto não é uma cota
  final: espessura de 6 mm, contactos, chanfros e folgas alteram a posição real.
- Ranhuras abertas em lados opostos, centradas na largura. Partir de 0,3 mm de
  folga total para espessura de 6 mm e ajustar numa amostra. Prever encosto que
  limite a inserção e mantenha a montagem repetível.
- Prever abertura central para cabo, batentes suficientes para o telefone com
  capa e cantos arredondados. Confirmar estabilidade também ao tocar no ecrã.

## Relevos e impressão por cores

Paleta proposta: **marfim, azul escuro e dourado**. Ambas as peças estruturais
passam a marfim; o símbolo, as letras e os livros usam relevos azuis e dourados.

A estratégia a avaliar no CAD é terminar a superfície marfim antes dos relevos,
com uma etapa azul e detalhes dourados acima. Nas áreas douradas pode ser
necessário um suporte azul por baixo para não iniciar geometrias suspensas.
Os livros terão detalhes simplificados, sem filetes demasiado finos para bico
de 0,4 mm; começar com traços de aproximadamente 0,8 mm ou mais.

Esta estratégia não garante uma só cor em cada camada de todo o suporte:
batentes altos e livros podem ter intervalos de altura sobrepostos. Rever
altura, forma e cor dos batentes e a disposição dos relevos, e confirmar a
contagem real de trocas no fatiamento. Não sacrificar a retenção do telefone
para eliminar uma troca de cor. Não aplicar automaticamente os settings do
reel anteriormente discutido; ficaram apenas como técnica opcional a testar.

## Validação futura

1. Conferir a geometria na mesma montagem: ângulos, contacto dos dois pés,
   alinhamento, colisões no encaixe e espaço para telefone, capa e conector.
2. Imprimir uma amostra do encaixe para escolher a folga real.
3. Testar um protótipo com telefone e verificar retenção, equilíbrio e desmontagem.
4. Fatiar para A1/PLA/bico 0,4 mm e contar suportes, trocas, purgas e consumo.

## Limites do esboço

Imagem gerada como conceito visual. Os contactos, proporções e encaixes nas
perspetivas não são uma demonstração mecânica; a montagem CAD deverá corrigir
as inconsistências da ilustração. Não há validação física nem garantia de
encaixe perfeito. O símbolo foi interpretado a partir da fotografia, sem vetor
fornecido. As pequenas áreas claras dos livros podem ser marfim, simplificadas
ou removidas para respeitar as três cores e reduzir trocas.
