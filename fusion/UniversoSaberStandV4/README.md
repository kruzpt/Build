# Suporte de telemóvel — Universo do Saber V4

A V4 integra os dois livros em perspetiva e a correção local do `U` aprovados
na segunda prévia da V4. Mantém as peças de encaixe e o perfil de impressão
da V3. As versões anteriores ficam preservadas.

## Alterações aprovadas

- dois livros por lado, com capas em paralelogramo, lombadas arredondadas e
  espessura das páginas visível de frente e de lado;
- contorno azul de **0,9 mm**, com o branco da placa a formar as páginas;
- passagem da lateral esquerda do `U` à curva inferior através de uma
  Bézier tangente, mantendo o resto do símbolo e o alinhamento;
- remoção de microfragmentos do recorte das capas antes de exportar o STL.
  A diferença de área relativamente à prévia é inferior a 0,002 mm² por ícone.

As imagens `universo-saber-suporte-v4-CAD.png`,
`universo-saber-suporte-v4-livros.png` e
`universo-saber-suporte-v4-logo-alinhado.png` mostram a geometria usada nos
ficheiros finais.

## Medidas e encaixe

- costas: **200 × 80 × 6 mm**;
- base: **110 × 80 × 6 mm**, com batentes de mais 4 mm (máximo de 10 mm);
- apoio do telemóvel: **70° em relação à mesa**;
- altura útil das costas acima do apoio: **171,6 mm**;
- relevo azul: **0,8 mm**;
- ranhura: **6,30 mm** para a placa de **6,00 mm**;
- folga nominal total: **0,30 mm**.

As costas brancas, a base azul e as amostras de encaixe são idênticas aos
ficheiros da V3. Se já imprimiu a base da V3, pode reutilizá-la com as novas
costas. Não redimensione as peças no Bambu Studio.

Antes das peças completas, imprima a amostra de encaixe de 0,30 mm. O pacote
inclui também amostras de 0,20 e 0,40 mm para compensar diferenças da
impressora e do filamento.

## Bambu Studio A1 / AMS

Abra `universo-saber-suporte-v4-A1-AMS-2-pratos.3mf` como **projeto**:

1. costas brancas com logótipo, texto e livros azuis — **uma troca de cor**;
2. base azul — **nenhuma troca de cor**.

O projeto usa A1 com bico de 0,4 mm, PLA, camada de 0,20 mm, três paredes,
15% gyroid, cinco camadas superiores, quatro inferiores, Arachne e superfície
superior monotónica a 40 mm/s. Mantém brim de 3 mm. Apenas a base tem pequeno
suporte snug para o bisel traseiro do pé.

Exportado, reaberto e fatiado com o Bambu Studio oficial **02.08.02.61**, sem
avisos de fatiamento. Estimativas do motor:

| Prato | Filamento | Tempo | Trocas |
| --- | ---: | ---: | ---: |
| 1 — Costas e relevo | 54,48 g | 2 h 20 min | 1 |
| 2 — Base | 28,39 g | 1 h 22 min | 0 |
| Total | **82,87 g** | **cerca de 3 h 42 min** | **1** |

As estimativas dependem do filamento e da versão do Bambu Studio. Confirme
o mapeamento de branco e azul para as posições reais do AMS antes de imprimir.

## Fusion 360

Copie a pasta `UniversoSaberStandV4`, incluindo `geometry.json`, para os scripts
do Fusion e execute `UniversoSaberStandV4.py`. O script cria um novo documento
com a montagem e separa costas, relevo e base em três componentes.

O script passou na verificação sintática, mas não foi executado numa
instalação real do Fusion. O 3MF já contém a geometria para impressão e não
depende da execução do script Fusion.

## Validação e ficheiros STL

Todos os STL passaram como sólidos fechados, com orientação consistente.
Foram verificados o percurso lateral de montagem, a ausência de colisões,
as faces de contacto com a mesa e o equilíbrio estático ideal com três
tamanhos de telefone. O encaixe, a aderência e a resistência reais ainda
dependem de um teste físico.

Os STL de branco e relevo azul partilham a mesma origem. Importe-os como
partes de um único objeto se não usar o projeto 3MF. O ficheiro
`montado-referencia-nao-imprimir.stl` serve apenas de referência de montagem.
O ficheiro `costas-completas.stl` reúne costas e relevo sem atribuição de cores.
