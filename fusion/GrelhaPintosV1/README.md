# Grelha para pintos — primeiro protótipo

Referência: STL `Untitled_pinto.stl` enviado pelo utilizador, sem alterar nem
publicar o original. O original mede **217,5 × 180 × 12 mm**, tem grelha de
5 mm de espessura e aberturas de cerca de **6 × 6 mm**. As pernas dão apenas
cerca de 7 mm de afastamento livre sob a malha.

## Alterações deste draft

| Elemento | Novo valor |
| --- | --- |
| Dimensão exterior de cada módulo | **217,3 × 179,8 mm** |
| Altura total em uso | **30 mm** |
| Espessura da grelha | 3,2 mm |
| Aberturas | **6 × 6 mm — não aumentadas** |
| Barras entre aberturas | 1,6 mm |
| Reforços por baixo | 3 barras em cada direção, 4 mm adicionais |
| Pés | 9, em cruz aberta de 12 mm, sem cavidades fechadas |
| Afastamento livre sob a malha, fora dos reforços | 26,8 mm |
| Afastamento sob os reforços | 22,8 mm |

**Folga confirmada pelo utilizador:** este draft reduz **0,2 mm por
placa em ambas as direções**. Na disposição confirmada de 2 × 5, o envelope
passa de 435 × 900 para **434,6 × 899 mm**, ou seja, menos
0,4 mm numa direção e menos 1 mm na outra. As placas continuam justapostas;
não é necessário abrir uma separação de 0,2 mm entre placas. O original também
não define as paredes inclinadas ou dimensões interiores exatas da caixa.

A altura de 30 mm é uma proposta ajustável. A nova peça é única e removível;
a forma dos pés permite imprimir tudo sem suportes e evita pequenos copos
fechados que acumulem sujidade. Não há encaixes de ligação entre módulos.

## Pintos desde o primeiro dia

Não aumentei as aberturas apesar do pedido inicial de melhor escoamento,
porque os pintos começam a usar este piso no primeiro dia. **Manter a abertura
antiga não certifica que ela seja adequada a todos os recém-nascidos.**

Nos primeiros dias use uma cobertura temporária aderente e absorvente,
por exemplo papel de cozinha, e observe o apoio das patas. Evite superfícies
escorregadias. Troque a cobertura quando suja: enquanto estiver colocada,
ela também impede os resíduos de cair através da grelha. A utilização sem
cobertura depende do tamanho real dos pintos e da observação do apoio.

O desenho não foi validado com animais nem para carga de aves adultas.
O aumento de altura ajuda a separar os resíduos que caem, mas não elimina
o entupimento por fezes ou desperdício de ração. Limpeza regular continua
a ser necessária.

## Imprimir e abrir no Fusion

- Pode abrir o STL diretamente no Bambu Studio, em mm, escala **100%**.
- O STL já está orientado para impressão: **face de apoio dos pintos na mesa
  e pés para cima**. Depois de imprimir, vire a peça para usar.
- Bico 0,4 mm, camadas 0,2 mm como ponto de partida. Sem suportes.
- PETG pode ser uma opção mais resistente à lavagem que PLA; confirme
  o comportamento no ambiente aquecido e no método de limpeza que utiliza.
- Imprima **um módulo primeiro** e verifique encaixe, ausência de arestas
  ou fios soltos, flexão e estabilidade antes de imprimir os dez.

Para editar no Fusion, extraia o ZIP e adicione a pasta `GrelhaPintosV1` em
**Utilities → Scripts and Add-Ins → Scripts → + / Add**. O script cria um
documento novo. Os valores no início são em mm; altere-os e execute novamente
para regenerar. A malha é criada num sketch com cálculo adiado e um único
corte, sem uma operação separada para cada buraco. O cálculo desse sketch
ainda pode demorar; o STL permite experimentar sem executar o script.

## Validação e comparação de material

O STL original contém **582 cascas fechadas que se sobrepõem**. Somar os seus
volumes daria uma comparação errada; a referência foi unida geometricamente
antes de medir. `validation.json` regista o hash do original, o volume da
união, o novo volume e a diferença percentual: **cerca de 32,6% menos volume
sólido**, apesar do aumento de altura. São volumes geométricos, não
uma previsão exata de gramas ou tempo do slicer.

O STL novo é verificado como um único sólido fechado, com dimensões corretas
e todas as aberturas atravessadas. O esquema e o STL usam os mesmos parâmetros
do script Fusion. A execução no kernel real do Fusion, a rigidez física e o
apoio dos pintos ainda precisam de confirmação.

Regeneração: `python fusion/tools/generate_pintos_v1.py --reference-stl CAMINHO`
com o ambiente Python de geração de STL. Esse ambiente não é necessário para
executar o script no Fusion.
