# Suporte de parede F1 Speed Champions + piloto V9

Versão aprovada com dois berços encostados à placa. Cada berço usa uma base
exterior reta e uma cavidade semicircular interior para o pneu. A placa do
piloto prolonga-se lateralmente até à base reta do berço esquerdo, formando
um único corpo com a placa de parede.

## Medidas

- placa de parede: 112 × 42 × 4 mm;
- dois furos Ø5,5 mm, separados 36 mm, com rebaixo cónico Ø10 mm;
- centros dos berços separados 62 mm;
- berços: Ø23,2 mm interior, 12 mm de largura e 27 mm de projeção;
- material mínimo sob o pneu: aproximadamente 6,4 mm;
- placa útil do piloto fora da parede: 26 × 14 × 4 mm;
- pinos do piloto: passo 8 mm, Ø4,75 mm nominal e 1,8 mm de altura.

## Testar antes da peça completa

1. Imprimir a amostra do berço e experimentar um pneu traseiro.
2. Imprimir as amostras Ø4,65/4,75/4,85 mm e escolher o encaixe do piloto.
3. Comunicar os resultados antes de imprimir o terceiro prato completo.

O Ø23,2 mm parte de um pneu com cerca de Ø22 mm e acrescenta 0,6 mm de
folga radial. A LEGO não publica o diâmetro do pneu em milímetros, pelo que o
teste físico continua necessário para confirmar diferentes F1 Speed Champions.

## Impressão

O projeto Bambu usa A1 com bico de 0,4 mm, Generic PLA, camada de 0,20 mm,
quatro paredes, 25% gyroid e placa PEI texturada. Não usa brim. Os dois pratos
de teste são impressos sem suportes. A peça completa fica com a face traseira
da placa na mesa e usa suportes automáticos snug apenas onde o fatiador deteta
saliências.

Fatiamento validado no Bambu Studio 2.9.1.70, sem avisos nem trocas de
filamento. Estimativas: 2,95 g / 19 min para o berço, 3,99 g / 21 min para os
pinos e 23,74 g / 1 h 26 min para a peça completa. Só o terceiro prato gera
uma pequena zona de suporte automático.

O SCAD permite exportar `completo`, `berco` ou `amostras_piloto` através da
variável `parte`. As malhas e o projeto Bambu foram validados digitalmente; o
encaixe, os parafusos e a carga na parede ainda precisam de teste físico.
