# Suporte de parede F1 Speed Champions + piloto V3

Primeiro protótipo imprimível para expor os carros LEGO Speed Champions F1
de 2025 na parede. Os pneus traseiros entram por cima e ficam apoiados por
trás em dois berços circulares de 175°. A aba lateral recebe a minifigura.

## Medidas do projeto

- placa de parede: 112 × 42 × 4 mm;
- dois furos Ø5,5 mm, separados 36 mm, com rebaixo cónico Ø10 mm;
- centros dos berços separados 62 mm;
- berço: Ø23 mm interior, 14 mm de largura, parede de 3,2 mm e arco de 175°;
- projeção máxima desde a parede: 40,7 mm;
- aba do piloto: 28 × 22 mm;
- pinos do piloto: passo LEGO de 8 mm e Ø4,75 mm nominal.

O Ø23 mm parte de um pneu com cerca de Ø22 mm e acrescenta 0,5 mm de folga
radial. A LEGO publica as dimensões gerais dos conjuntos, mas não o diâmetro
dos pneus em milímetros. Por isso, o pacote inclui uma amostra de um berço e
três amostras dos pinos, Ø4,65/4,75/4,85 mm.

## Ordem de teste recomendada

1. Imprimir `suporte-f1-v3-amostra-berco-pneu.stl` e experimentar um pneu.
2. Imprimir `suporte-f1-v3-amostras-piloto.stl` e escolher o encaixe que segura
   a minifigura sem forçar as pernas.
3. Só depois imprimir a peça completa. Se o berço ou os pinos precisarem de
   ajuste, alterar as variáveis no início do ficheiro SCAD.

Imprimir a peça completa deitada com a face traseira da placa na mesa. Usar
PLA, altura de camada de 0,20 mm, quatro paredes e 20% a 25% de enchimento.
Não é necessário brim nem suporte na orientação indicada. Confirmar que as
cabeças dos parafusos assentam nos rebaixos e usar buchas adequadas à parede.

## Estado da validação

Os três STL foram exportados em alta resolução e verificados como malhas
fechadas/manifold. O modelo completo é um corpo único. As amostras dos pinos
são deliberadamente três corpos independentes. O encaixe no carro, no piloto
e os parafusos ainda precisam de teste físico antes de pendurar o conjunto.

O ficheiro `F1SpeedChampionsWallSupportV3.scad` é a fonte paramétrica. Mude
`parte` para `completo`, `berco` ou `amostras_piloto` para exportar cada STL.

## Projeto Bambu A1

O ficheiro `suporte-f1-speed-champions-piloto-v3-A1-PLA-3-pratos.3mf` abre
como projeto nativo no Bambu Studio e contém três pratos pela ordem de teste:

1. amostra do berço do pneu;
2. três diâmetros para os pinos do piloto;
3. suporte completo, a imprimir depois de validar os dois encaixes.

Perfil incluído: Bambu Lab A1 com bico de 0,4 mm, Generic PLA, camada de
0,20 mm, quatro paredes, 25% gyroid e placa PEI texturada. Não usa brim.
A placa traseira da peça completa fica apoiada na mesa. Os suportes automáticos
snug estão ativos apenas na peça completa e limitados à placa de impressão.

O fatiamento validado no Bambu Studio 2.9.1.70 não apresentou avisos nem trocas
de filamento. Estimativas: 5,0 g / 25 min para o berço, 4,0 g / 21 min para os
pinos e 26,4 g / 1 h 39 min para o suporte completo. O terceiro prato gera uma
pequena quantidade de suporte; os dois pratos de teste não geram suportes.
