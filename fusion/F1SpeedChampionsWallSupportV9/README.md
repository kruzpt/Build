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

### Perfil de acabamento dos berços

O projeto `v9-acabamento` é a opção recomendada para a peça completa. Usa
camada de 0,12 mm, resolução geométrica de 0,008 mm e coloca a costura para
trás. As quatro velocidades de overhang ficam limitadas a 25/20/15/10 mm/s.
O reforço de arrefecimento começa aos 25% e usa 100% de ventoinha nessas zonas.

Ao contrário do primeiro perfil, permite que os suportes snug com três camadas
de interface nasçam sobre a própria placa traseira. O G-code confirma suporte
até 27,08 mm de altura, cobrindo a parte inferior das duas curvas. A distância
Z da interface é 0,12 mm. Isto reduz degraus e deformação, embora uma impressão
FDM continue a apresentar linhas de camada e possa deixar textura onde o
suporte toca na peça.

### Perfil de resistência

O projeto `v9-resistencia` é recomendado para pendurar o carro depois de
confirmar os encaixes. Usa camada de 0,16 mm, seis paredes, seis camadas de
topo/fundo e 35% gyroid. Mantém as velocidades reduzidas, a costura traseira,
o arrefecimento de overhang e três camadas de interface. O suporte alcança
27,08 mm e cobre a parte inferior dos berços.

A peça completa fica estimada em 28,31 g e cerca de 2 h 08 min em Generic PLA.
As paredes adicionais têm mais efeito na raiz dos braços do que aumentar apenas
o enchimento. Para PLA+ ou PETG, selecionar um perfil de filamento já calibrado
para o material real; não copiar temperaturas de PLA. Usar duas buchas e
parafusos adequados à parede e não apertar até deformar a placa impressa.

O SCAD permite exportar `completo`, `berco` ou `amostras_piloto` através da
variável `parte`. As malhas e o projeto Bambu foram validados digitalmente; o
encaixe, os parafusos e a carga na parede ainda precisam de teste físico.
