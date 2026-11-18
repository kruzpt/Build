# Suporte de cana V3 — CAD profissional

![Fechado, aberto e corte](../../designs/suporte-cana-mola-v3-CAD.png)

![Fixação na face larga](../../designs/suporte-cana-mola-v3-fixacao-traseira.png)

Esta revisão traduz o conceito aprovado para sólidos paramétricos reais. O
corpo fixo cria duas faces exteriores contínuas que escondem o eixo; o braço
móvel entra entre elas. A mola de compressão fica centrada por dois discos de
apoio opostos e pilotos centrais independentes do eixo.

## Dimensões atuais

| Elemento | V3 |
| --- | ---: |
| Envelope fechado sem patilha | 68 × 42 × 22 mm |
| Comprimento até à ponta da patilha | aproximadamente 79 mm |
| Cana máxima validada digitalmente | Ø28 mm |
| Folga radial na cavidade | 0,8 mm |
| Insertos TPU | 1,2 mm, recuados 3 mm da entrada |
| Abertura máxima | 45° |
| Eixo oculto integrado | Ø4 mm |
| Mola proposta | Ø exterior até 7 mm |
| Comprimento livre proposto | 12 mm |
| Comprimento sólido máximo exigido | 5,5 mm |
| Berços da mola | Ø8,6 mm com piloto Ø2,4 mm |
| Folga dinâmica entre peças | 0,55 mm |
| Fixação | 2 × M4 escareados, perpendiculares à face larga |

## Verificação

- Zero intersecção entre as duas peças em 81 posições de 0° a 45°.
- Trajetória contínua encontrada para um cilindro Ø28 mm desde a entrada até ao
  centro da cavidade **com os insertos TPU instalados**, com amostras a cada
  2 mm em X e 0,5 mm em Y.
- Os diâmetros Ø8, Ø16 e Ø22 ficam contidos no envelope já verificado de Ø28 mm.
- STEP individuais e STEP do conjunto exportados a partir dos sólidos válidos.

Estas verificações são geométricas. A força da mola, flexão do encaixe oculto,
desgaste, resistência em ambiente marítimo e contacto com canas reais precisam
de cupão e teste físico antes de preparar a versão final de uso.

A cinemática calcula cerca de 6,03 mm de compressão entre fechado e 45°. Por
isso a mola candidata deve ter comprimento livre próximo de 12 mm e comprimento
sólido não superior a 5,5 mm. A constante elástica e a pré-carga continuam por
validar fisicamente; não substituir uma mola apenas pelo diâmetro exterior.

## Revisão crítica antes da impressão

- A mola foi aproximada do eixo para reduzir o curso; a primeira geometria
  exigia compressão excessiva.
- Os munhões do eixo receberam pontas cónicas para reduzir a flexão necessária
  durante o encaixe. Mesmo assim, imprimir primeiro o cupão é obrigatório.
- A cavidade estrutural foi aumentada para que Ø28 mm continue a passar com os
  insertos TPU de 1,2 mm instalados. Os insertos terminam 3 mm antes da entrada
  para não estrangular a passagem.
- A parede encosta à face larga `Z=0`. Os dois M4 atravessam a peça no eixo Z,
  perpendicularmente à parede, e são escareados na face larga exterior `Z=22`.
  Os centros `(16, 35)` e `(60, 35)` mm mantêm os parafusos fora da cavidade da
  cana, do eixo e da mola. Não existem furos nem encaixes na face estreita.
- Não foram abertas bolsas para ímanes nesta revisão. A retenção magnética será
  decidida depois de medir a força da mola, evitando abertura excessivamente
  pesada e ferragens desnecessárias em ambiente marítimo.

## Projeto Bambu Studio

O 3MF tem três pratos: cupão PETG, estrutura completa PETG e dois insertos TPU.
O TPU deve ser alimentado por bobina externa, não pelo AMS Lite. O perfil usa
camada de 0,20 mm, cinco paredes, seis camadas superiores e inferiores, 35%
gyroid, suportes automáticos e sem brim. Os três pratos foram fatiados sem
avisos, mas nenhum encaixe foi ainda testado fisicamente.
