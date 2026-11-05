# M7 — teste laranja V4, zero paredes

Parte do **3MF real com zero paredes** enviado pelo utilizador em 05/11/2026.
O teste físico tinha uma boa superfície e encaixava no rebaixo, exceto pela
pequena saliência num canto. O objetivo deste V4 é investigar essa saliência.

## O que estava gravado no ficheiro recebido

- Zero paredes definido **no objeto**; a definição global continua em três.
- Fluxo laranja 0,931, sobreposição 10%, scarf None, costura normal 15%.
- Direção de enchimento **45°** e velocidade de lacunas configurada em **250 mm/s**.
  Portanto, este ficheiro não é o V2, que usava 0° e lacunas a 25 mm/s.
- Placa 46,4 × 66,4 × 0,60 mm, três camadas de 0,20 mm, sem relevos.

O Gcode foi gerado novamente com **Bambu Studio 02.09.01.70**, a mesma versão
do projeto. Confirmou-se que não existem percursos de paredes nas três camadas.

## Percursos encontrados

O padrão **Monotonic line** acrescenta pequenos percursos de **Gap infill**
às linhas do topo. Num canto do prato X+/Y+, existe um percurso adicional de
dois segmentos de aproximadamente **0,111 e 0,050 mm**, com largura nominal
**0,104 mm**. É uma largura muito pequena para o bico de 0,4 mm.

Esses segmentos são emitidos entre linhas do topo, não apenas no arranque ou
no fim da camada. No arranque e no fim do topo existem ainda outros percursos
de lacunas com aproximadamente 1 mm, que usam uma aceleração mais elevada.
Estes movimentos constituem uma hipótese concreta para a irregularidade.
A fotografia não permite estabelecer qual canto físico corresponde ao canto
do Gcode se a peça foi rodada, nem provar a causa física da saliência.

As velocidades pedidas no Gcode chegam a 250 mm/s nas lacunas. Isso **não**
significa que a cabeça atinja essa velocidade em movimentos tão pequenos;
as distâncias e a aceleração limitam a velocidade real.

## Uma alteração no V4

**Padrão de superfície superior: Monotonic line → Monotonic.**

Mantêm-se zero paredes no objeto, direção 45°, fluxo 0,931, temperatura,
retração, velocidades e todas as restantes definições do ficheiro recebido.
Não foi alterada a folga da costura: sem perímetros, esse ajuste não controla
os percursos de preenchimento encontrados.

Com **Monotonic**, o fatiador já não acrescenta esses percursos de lacunas.
O topo passa a conter apenas percursos Top surface, a **25 mm/s e 1000 mm/s²**.
Também muda a ligação entre as linhas do topo. As duas primeiras camadas são
iguais às da referência, movimento a movimento.

A geometria, a configuração do objeto com zero paredes, a pintura da costura
e a posição estão conservadas byte a byte. A quantidade de material muda menos
de 0,01 g. Não foram reduzidas as dimensões nem aumentada a folga de encaixe.

## Impressão e limites

Abrir o V4 como projeto, voltar a fatiar e manter o mesmo laranja e a calibração
dinâmica de fluxo. Contém só a amostra, **sem estrela, árvore ou texto**.
Sem brim, suportes ou torre. Estimativa: **cerca de 18 minutos e 2,19 g**.
Verificar os quatro cantos e o encaixe sem cola depois de arrefecer.

O V4 fatiou sem avisos. Foi verificada a remoção dos percursos adicionais,
mas o resultado físico e a eliminação da pontinha ainda não foram confirmados.
O projeto de produção não foi alterado por este ensaio.

Ver `bambu-validation.json` e a imagem `m7-tijolo-teste-laranja-v4-zero-paredes-percursos.png`.
O script `fusion/tools/build_m7_orange_test_v4.py` reproduz a preparação com
`--source` apontado para o ficheiro original enviado e `--bambu-bin` para o
executável Bambu Studio 2.9.1.70. Requer os módulos auxiliares do repositório.
