# Base Premium — substituição compatível com a placa A1

Script independente: cria **apenas a base**, num documento novo do Fusion.
Não altera a placa, os QR, o logótipo ou as cavidades NFC.

Extraia o ZIP e adicione a pasta `EssencialBasePremium` em **Utilities →
Scripts and Add-Ins → Scripts → + / Add**. Execute, guarde como `.f3d`
e exporte o componente em mm, à escala 100%.

## Desenho revisto

- Exterior **160 × 70 × 18 mm**, conservando a área de apoio.
- Cantos exteriores **R12 mm** e bordos superiores exteriores **R2 mm**.
- Chanfro frontal **8 × 8 mm a 45°**; a frente fica com 10 mm de altura.
- Topo horizontal com 18 mm de altura na zona da ranhura. Placa vertical.
- Um único sólido. Rosa da marca como cor de apresentação, quando disponível.

O raio superior é aplicado antes de cortar o chanfro e a ranhura. Assim,
o arredondamento não altera o encaixe. O chanfro é cortado de forma explícita,
sem depender da seleção automática de arestas tangentes. As arestas de
transição do chanfro não recebem um fillet adicional.

O desenho segue a imagem conceptual, mas as medidas e a geometria deste
script são a referência de fabricação; a imagem não é um render CAD.

## Encaixe preservado de EssencialA1Reviews

| Elemento | Medida |
| --- | --- |
| Língua existente da placa | 120 × 5 × 12 mm |
| Ranhura útil | **120,6 × 5,5 mm** |
| Profundidade total da ranhura | **12,8 mm** |
| Folga na espessura | 0,25 mm por lado |
| Folga nas extremidades | 0,30 mm por lado |
| Folga no fundo | 0,80 mm |
| Entrada alargada | 121,6 × 6,5 mm, profundidade 1 mm |
| Material sólido por baixo | 5,2 mm |

A ranhura permanece centrada. Coordenadas locais: X=19,7…140,3 mm,
Y=32,25…37,75 mm, piso Z=5,2 mm. A entrada alargada começa em Z=17 mm;
é a mesma entrada em degrau da base anterior, não um novo encaixe inclinado.

Imprima **fundo plano na mesa e ranhura para cima**, em placa separada.
Não precisa de pausa NFC. Não escale a peça para ajustar o encaixe.
Teste com a língua impressa: a folga geométrica não elimina a variação
de impressão, material ou calibração.

## Validação e limites

Os testes comparam as medidas com o script existente, verificam o afastamento
do chanfro e arredondamentos à ranhura, e exercitam o corte da ranhura com
uma API simulada.
O script verifica no próprio Fusion o sólido, o envelope exterior e as
dimensões da face do fundo da ranhura, falhando com indicação da etapa se
não corresponderem. Não requer bibliotecas externas no Fusion.

A execução com o kernel real do Fusion e o encaixe físico ainda precisam
de confirmação. Os parâmetros estão no início do código; altere-os e execute
de novo para regenerar. As features na timeline usam medidas fixas.
