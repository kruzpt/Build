# Grelha para pintos V2 — aberturas de 8 mm

O utilizador observou que as aberturas de **6 × 6 mm** do STL antigo eram
pequenas e que as patas suportariam uma abertura maior. Confirmou **8 × 8 mm**
para este segundo protótipo. A V1 de 6 mm fica preservada.

## Medidas

| Elemento | V2 |
| --- | --- |
| Exterior de cada placa | **217,3 × 179,8 mm** |
| Conjunto confirmado de 2 × 5 placas | **434,6 × 899 mm** |
| Redução em relação ao STL antigo | **0,2 mm por placa em cada direção** |
| Altura total proposta | **30 mm** |
| Aberturas | **8 × 8 mm** |
| Quantidade de aberturas | 22 × 18 = 396 |
| Barras entre aberturas | 1,6 mm |
| Espessura da grelha | 3,2 mm |
| Reforços inferiores | 3 em cada direção; 4 mm adicionais |
| Pés | 9, em cruz aberta de 12 mm |
| Espaço sob a grelha, fora dos reforços | 26,8 mm |
| Espaço sob os reforços | 22,8 mm |

Cada abertura passa de 36 para **64 mm²**, aproximadamente **78% mais área**.
As posições dos reforços e pés acompanham as novas barras, mantendo-os sob
material sólido e sem fechar as aberturas. A margem exterior mínima real
fica com 3,85 mm em X e 4,30 mm em Y.

As dimensões exteriores, folga, altura, espessuras e quantidade de apoios são
as mesmas da V1. O novo volume sólido é cerca de **39,7% menor que o original**;
consumo de filamento e tempo dependem das definições do slicer.

## Impressão e teste

Abra o STL no Bambu Studio em mm, escala **100%**. Já está orientado para
impressão: **face de apoio dos pintos na mesa, pés para cima**. Vire a peça
depois de imprimir. Não precisa de suportes. Bico de 0,4 mm e camadas de
0,2 mm são um ponto de partida; confirme as barras na pré-visualização.

Imprima primeiro **uma placa**. Confirme o encaixe, estabilidade, flexão,
limpeza e apoio das patas no tamanho real. A observação do utilizador orientou
o aumento, mas esta geometria de 8 mm ainda não foi testada com os pintos nem
para cargas de aves adultas. Retire a peça se os dedos prenderem ou o apoio
for inadequado. Uma abertura maior e mais espaço inferior ajudam o escoamento,
mas a grelha continua a precisar de limpeza.

Para editar no Fusion, extraia o ZIP e adicione a pasta `GrelhaPintosV2` em
**Utilities → Scripts and Add-Ins → Scripts → + / Add**. Execute para criar
um documento novo. O corte das 396 aberturas é feito numa única operação,
com cálculo adiado do sketch. Alterar valores no início do script e executar
novamente regenera o modelo.

## Validação

O STL guardado e reaberto foi verificado como um único sólido fechado e com
as medidas corretas. Os testes medem as 396 aberturas no próprio ficheiro,
a altura dos nove pés, a redução de 0,2 mm e o envelope de 2 × 5 placas.
O esquema, STL e código Fusion usam os mesmos parâmetros.

A comparação de material usa a união geométrica das 582 cascas sobrepostas
do STL original; os valores e hash da referência estão em `validation.json`.
A execução real do script no Fusion e os ensaios físicos ainda precisam de
confirmação. O STL pode ser usado diretamente sem executar o Fusion.

Regeneração: `python fusion/tools/generate_pintos_v2.py --reference-stl CAMINHO`
com o ambiente Python de geração já usado na V1. O original não é publicado.
