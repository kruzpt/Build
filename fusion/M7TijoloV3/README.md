# M7 — tijolo V3, correção do traço do 7

A V3 corrige o que foi assinalado na referência: o 7 da V2 tinha recortes
fundos e regulares, que davam um aspeto dentado no fatiador. O novo contorno
usa um traço descendente mais largo, bordo direito em curva Bézier e pequenas
saliências arredondadas à esquerda. O topo e o pé também são curvos.

Foram preparados um 3MF completo de quatro pratos, seis STL e uma comparação
dos contornos V2/V3 e dos percursos gerados pelo Bambu Studio.

## O que imprimir

Abra **`m7-tijolo-v3-A1-AMS-4-pratos.3mf` como projeto** na Bambu A1, bico
0,4 mm. Cada prato é de uma só cor:

1. Corpo terracota, com os oito furos na vertical.
2. Árvore e estrela douradas, deitadas.
3. m e “Natal 2026” brancos, deitados.
4. Novo 7 ciano, deitado.

**Se já imprimiu a V2, substitua apenas o corpo e o 7.** A estrela, o m,
a árvore e a inscrição da V3 são cópias exatas dos STL V2 e podem ser
reaproveitados. O novo 7 tem um traço mais cheio, pelo que precisa do seu
novo rebaixo. A casinha não foi alterada. As versões anteriores continuam
preservadas.

## Medidas e montagem

| Elemento | Medida |
| --- | --- |
| Corpo, largura × profundidade × altura | 50 × 26 × 70 mm |
| Estrela / conjunto m7 | 30 / 14 mm de largura |
| 7, largura × altura × espessura | 5,33 × 7,25 × 1,20 mm |
| Profundidade dos rebaixos | 0,20 mm |
| Folga lateral por lado | 0,15 mm |
| Folga de fundo para cola | 0,05 mm |

O novo 7 conserva o tamanho exterior e a posição da V2. A alteração é no
contorno e no respetivo rebaixo. Os enfeites continuam separados para colar,
sem placa inteira sobre a frente do tijolo.

Faça uma montagem a seco e retire apenas rebarbas. Aplique pouca cola no verso,
com palito, e apresente a peça ao respetivo rebaixo sem forçar. A estrela em
silk deve sair da mesa fria sem ser dobrada. A inscrição tem nove caracteres;
fita de pintor de baixa aderência pode ajudar a conservar o espaçamento.

## Perfil e verificação

O perfil conserva a A1 / bico 0,4 mm, PLA, camada de 0,20 mm, três paredes,
cinco camadas superiores e quatro inferiores, paredes Arachne e topo
monotónico a 35 mm/s. O dourado usa Generic PLA Silk a 215 °C, limite de
5 mm³/s e topo a 25 mm/s, dentro do intervalo 190–220 °C da bobina indicada.

São quatro pratos sem trocas de cor durante a impressão. A estimativa é de
cerca de **39,5 g e 3 h 34 min**, com os perfis incluídos. O projeto foi
exportado, reaberto e fatiado pelo Bambu Studio oficial 02.08.02.61 sem
avisos e sem gerar suportes. Confirme as bobinas no AMS antes de imprimir.

Os seis STL são malhas fechadas e com orientação consistente. Foram
verificadas colisões e 105 posições de inserção nos rebaixos. Os tamanhos
e a identidade binária das quatro peças reutilizáveis foram conferidos.

### Comparação com o fatiador

- `m7-tijolo-v3-comparacao.png`: silhuetas reais V2 e V3, à mesma escala.
- `m7-tijolo-v3-fatiador.png`: STL e reconstrução dos percursos da última
  camada do 7, a partir do G-code de validação e das larguras de extrusão
  indicadas pelo Bambu Studio, alinhados na mesma orientação e escala.
- `m7-tijolo-v3-CAD.png`: conjunto montado e pormenor do símbolo.

O contorno foi ajustado após a primeira comparação: detalhes demasiado
finos eram eliminados pelo fatiador. As saliências finais têm uma base mais
alta e arredondada, mantendo o traço largo. O bico de 0,4 mm arredonda as
pontas pequenas; a imagem de percursos permite avaliar esse efeito antes
da impressão. É uma reconstrução dos percursos, não uma fotografia de uma
peça impressa ou uma simulação física da extrusão.

`geometry-validation.json` e `bambu-validation-tijolo.json` guardam as
verificações. A impressão física e a colagem continuam por testar. O contorno
é uma interpretação manual da referência assinalada; não foi fornecido um
ficheiro vetorial oficial da marca.

## Fusion e pacote

`m7-tijolo-v3-pacote.zip` contém o 3MF, os seis STL, este guia, as imagens,
os relatórios e a pasta `M7TijoloV3`. Para editar no Fusion, copie a pasta
completa e execute `M7TijoloV3.py` mantendo `geometry.json` ao lado. O script
cria um documento novo com os componentes montados. A sintaxe foi verificada;
a execução no Fusion não foi testada. O projeto Bambu e os STL são
independentes da execução do script.
