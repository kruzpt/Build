# M7 — revisão do processo e do encaixe da placa

Revisão de 05/11/2026 para escolher uma estratégia de impressão repetível.
Base: o 3MF real com zero paredes enviado pelo utilizador, os ensaios físicos
relatados, a geometria do tijolo V6 e o Gcode gerado pelo Bambu Studio 02.09.01.70.
As estimativas geométricas de depósito não são medições das peças impressas.

## Conclusão de trabalho

O centro da placa tem uma base de qualidade conseguida com o fluxo 0,931.
O problema restante pode resultar da combinação de **controlo do bordo**,
**transientes de extrusão** e **tolerância do encaixe**. Não há evidência suficiente para atribuir tudo ao
pequeno traço de Gap infill da última camada.

O V4 piorou o picotado e prende no rebaixo, embora esteja plano fora do tijolo.
Isso aponta para interferência nos bordos e não para arqueamento global como
explicação principal da resistência no encaixe. O teste original com zero
paredes e Monotonic line continua a ser a referência física mais bem-sucedida.

## O que sabemos e o que falta saber

| Evidência | Implicação | Limite |
|---|---|---|
| Fluxo 0,931 melhorou muito a superfície central | Conservar essa calibração como base | Não prova pressão perfeita em movimentos curtos |
| Zero paredes melhorou os cantos face às três iniciais | As paredes internas e o encontro enchimento/perímetro merecem atenção | Zero paredes também altera a construção do contorno |
| V4 acrescentou ligações extrudidas junto ao bordo e ficou mais picotado | A geometria dos retornos influencia a qualidade e o encaixe | Ainda não mede a largura real de cada cordão |
| Placa fica plana fora do tijolo e faz mola ao encaixar | Existe interferência lateral/local | Pode vir da placa, do rebaixo ou de ambos |
| Corpo do tijolo saiu bem e primeira face da placa tinha bom aspeto | Avaria geral ou erro grosseiro da primeira camada têm prioridade menor | Não exclui efeitos locais de temperatura ou pressão |
| Dourado da clínica também teve cantos deficientes | Comparar configurações comuns é útil | Materiais e percursos distintos não demonstram uma causa única |

Fica desconhecido se a saliência está na face inferior ou só em cima: o
utilizador não consegue distinguir esse detalhe. A orientação da fotografia
relativamente à máquina e o resultado do encaixe rodado 180° também não estão
confirmados. Não basear a próxima alteração numa identificação de canto presumida.

## 1. Dimensão CAD e dimensão do plástico

- Rebaixo nominal: **47 × 67 × 0,70 mm**.
- Placa nominal: **46,4 × 66,4 × 0,60 mm**.
- Folga lateral CAD: **0,30 mm por lado**, também nos cantos, pois a placa
  resulta de um offset uniforme do perfil do rebaixo.
- Espaço no fundo para cola: **0,10 mm**.

Não foi encontrado um erro de raios que explique sozinho a interferência.
O raio aproximado da placa é 0,7 mm e o do rebaixo 1 mm.

Com zero paredes, vários centros das linhas do topo chegam a apenas **0,04 mm**
do contorno CAD, mas a largura nominal do cordão é **0,42 mm**. Um modelo simples
do depósito, dependendo da forma da ponta do cordão, admite cerca de
**0,11–0,17 mm além do contorno**. Assim, parte da folga nominal de 0,30 mm pode
ser consumida pelo modo de preencher a placa, antes de qualquer gota local.

Esse cálculo é uma hipótese geométrica de envelope, não uma leitura de paquímetro.
No V4, as ligações extrudidas acrescentadas ao longo dos bordos são compatíveis
com um contorno efetivo mais contínuo e mais apertado, apesar do STL ser igual.

## 2. Há movimentos relevantes nas três camadas

Valores de velocidade abaixo são os pedidos no Gcode. Em trajetos curtos, a
aceleração limita a velocidade realmente atingida.

| Camada | Arranque | Fim | Regime relevante |
|---|---|---|---|
| Z=0,20 | X+/Y−, após desretrair 0,8 mm | X−/Y+, antes do wipe | Fundo 30 mm/s, 500 mm/s² |
| Z=0,40 | X+/Y+, após desretrair 0,8 mm | X−/Y−, antes do wipe | Enchimento sólido pede ~106 mm/s, 6000 mm/s² |
| Z=0,60 | X+/Y−, Gap inicial de ~1 mm | X−/Y+, Gap final de ~1 mm e wipe | Topo 25/1000; lacunas pedem ~121–250/6000 |

Na última camada há ainda um Gap intermédio no canto X+/Y+, com dois segmentos
de **0,111 e 0,050 mm**, largura nominal **0,104 mm**. O mesmo canto já recebe o
arranque rápido da camada intermédia. Logo, o microtraço não é um suspeito isolado.
Todos os quatro cantos têm algum arranque, fim ou movimento particular no conjunto
das três camadas.

O Gcode não mostra sobredosagem explícita de reinício: retração de 0,76 mm durante
o wipe mais 0,04 mm depois, desretração de 0,80 mm e extra de reinício zero.
Não há fundamento para aumentar retração ou alterar K às cegas.

A calibração dinâmica foi confirmada ativa pelo utilizador. É distinta da
calibração do rácio de fluxo e não garante resposta perfeita para todos os
regimes de movimento. Os ramos de timelapse e deteção do bico no Gcode são
condicionais; não se sabe se foram executados em cada impressão.

## 3. Comparação nativa: zero, uma e três paredes

Foi feita uma simulação temporária alterando **apenas a definição do objeto de
zero para uma parede**, preservando o ficheiro original. Não constitui um ensaio
físico e não foi publicada como novo projeto de impressão.

Resultados:

- Uma parede exterior em cada camada, **nenhuma parede interior**.
- Perímetro externo, depois da primeira camada: **50 mm/s e 1000 mm/s²**.
- A costura pintada existente fica num troço reto do bordo.
- Os limites exteriores X/Y do envelope ideal desse perímetro coincidem com
  os limites CAD a menos de **0,001 mm**; esta comparação dos limites não mede
  o desvio de todos os pontos do contorno curvo. O enchimento fica recolhido
  para dentro do perímetro.
- O micro-Gap de 0,111 + 0,050 mm já não aparece nesse canto. Resta um Gap
  interno de aproximadamente 0,68 mm junto a outro canto.
- Simulação sem avisos: **1067,19 s / 2,1931 g**, contra **1063,69 s / 2,1850 g**
  na referência. Diferença: cerca de **4 segundos e 0,008 g**.

Uma parede é, portanto, uma alternativa fundamentada para controlar contorno
e posicionar a costura. Não é equivalente a voltar às três paredes, que incluíam
duas paredes interiores rápidas. A saliência na costura e o acabamento real
continuam por verificar fisicamente.

## Hipóteses e mitigação

| Hipótese | Prioridade atual | Mitigação dirigida |
|---|---|---|
| Enchimento sem perímetro consome folga e deixa bordo irregular | Alta | Avaliar uma parede de contorno; se se mantiver zero, medir o contorno real antes de compensar dimensões |
| Pressão em arranques/retornos, sobretudo na camada intermédia | Alta, por confirmar | Identificar quando surge a saliência; abrandar apenas o regime relevante, conservando fluxo |
| Irregularidade no canto do rebaixo ou soma das tolerâncias | Em aberto | Encaixe da placa lisa rodado 180°; verificar o canto correspondente do tijolo |
| Gap inicial/final rápido produz acumulação | Plausível | Manter Monotonic line e reduzir apenas a velocidade das lacunas num ensaio isolado |
| Microcurl ou temperatura local | Secundária | Observar enrolamento ou toque do bico; testar temperatura/ventilação apenas com essa pista |
| Humidade, entupimento ou folga mecânica geral | Baixa com os dados atuais | Investigar se surgirem sintomas noutras zonas, noutros objetos, ou ligados à posição da máquina |

## Sequência recomendada

1. **Sem imprimir:** rodar a placa lisa 180° no mesmo rebaixo, sem cola ou força.
   Se o sítio que prende acompanhar a placa, investigar placa/percurso; se ficar
   no mesmo canto do tijolo, investigar o rebaixo antes de outra versão da placa.
2. Se houver paquímetro, comparar largura/comprimento reais fora e junto da
   saliência. Não usar apenas a medida do STL como prova da folga física.
3. Se a interferência acompanhar a placa, a opção de fabrico preferida a avaliar
   é **uma parede**, preservando o fluxo e as dimensões. O objetivo é um bordo
   definido e uma costura em zona reta, além de um centro bem impresso.
4. Se a prioridade for conservar estritamente a solução zero paredes, manter
   Monotonic line e escolher um único ensaio: velocidade de lacunas, ou regime
   da camada interna, consoante a camada em que nasce a saliência. Não mudar os
   dois juntamente nem repetir calibrações globais sem evidência.
5. Confirmar numa unidade o encaixe a seco e só depois aplicar ao projeto com
   estrela, árvore e texto. No projeto completo, verificar que a alteração no
   fundo não retira os perímetros dos relevos e das letras.

## Alternativas de projeto e fabrico

- **Engrossar a placa:** útil para rigidez/manuseamento. De 0,6 para 1 mm, a
  rigidez à flexão aumenta aproximadamente 4,6 vezes para o mesmo material.
  Com interferência lateral, também dificulta o encaixe. Não trata a pontinha.
- **Aprofundar o rebaixo:** 1,1 mm deixaria aproximadamente 2,6 mm de parede
  de suporte atrás do rebaixo, aumentando a pequena pala superior em 0,4 mm. Exige reimprimir o
  corpo e validar o topo do rebaixo. Não resolve o contorno por si.
- **Chanfro posterior ou alívio local:** pode ajudar a entrada e acomodar
  irregularidades; o chanfro traseiro não elimina uma saliência na face superior.
  É tolerância de montagem, não prova de correção do processo.
- **Face visível contra o PEI:** o desenho atual tem relevos de 1 mm; invertê-lo
  diretamente criaria ilhas e pontes. Uma frente com cores incrustadas ou relevos
  colados é outra arquitetura, com aspeto e trabalho de montagem diferentes.
- **Acabamento manual localizado:** pode ser económico para poucas unidades;
  para uma série, deve entrar no custo e tempo de produção, sem depender de
  forçar a placa na moldura.

## Estado

Esta revisão não demonstra uma causa física única. Consolida o que funciona,
regista o insucesso do V4 e define verificações capazes de separar as hipóteses.
Os dados numéricos estão em `evidencias.json`.
