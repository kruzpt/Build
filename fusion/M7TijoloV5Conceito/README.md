# M7 — proposta V5, placa decorativa única

Esboço de 18 de outubro de 2026 para substituir a colagem de símbolos
individuais por uma única placa laranja fina, impressa com toda a decoração.

## Imagens para revisão

- [Proposta visual: montado e vista de montagem](../../designs/m7-tijolo-v5-proposta-placa-unica.png)
- [m extraído diretamente do STL original, ampliado](../../designs/m7-tijolo-v5-m-original-STL.png)

A proposta visual é uma ilustração gerada. O desenho técnico deverá usar os
contornos extraídos do STL, incluindo a estrela fechada da V4 e os oito furos
do tijolo. A imagem ampliada do m é uma representação direta da sua secção,
gerada a partir das coordenadas de `m-original.json`.

## Montagem proposta

Conservar as dimensões exteriores de 50 × 26 × 70 mm e os oito furos verticais.
Criar um rebaixo frontal com fundo fechado e moldura contínua nos quatro lados.
A placa recebe todos os relevos numa única impressão com AMS; só essa placa
é colada ao tijolo. A moldura alinha e protege os cantos, com apoio e cola
também nas extremidades.

Medidas iniciais a validar no CAD e numa amostra de encaixe:

| Elemento | Proposta |
| --- | --- |
| Fundo laranja da placa | 0,60 mm, três camadas de 0,20 mm |
| Profundidade do rebaixo | Cerca de 0,70 mm |
| Espaço nominal para cola | Cerca de 0,10 mm |
| Folga lateral | Cerca de 0,20 mm por lado |
| Moldura | Cerca de 1,5 mm de largura |
| Inscrição | Natal 2026, manuscrito branco em relevo |
| Logótipo | m branco e 7 ciano, com contornos originais |

A frente do corpo terá de conservar espessura suficiente atrás do novo
rebaixo. O redesenho deverá ajustar o interior se necessário, mantendo o
apoio integral da placa. O remate da estrela e da árvore deve conservar uma
separação visível entre os dois contornos.

## Logótipo

Foi encontrado o m no mesmo ficheiro `Tijolos cr.stl` que forneceu o 7 da V4.
A secção é única, conserva a pequena haste no início e não foi redesenhada,
suavizada nem substituída por uma fonte. Mede aproximadamente 18,16 × 14,50 mm
no STL de origem; a escala final e o posicionamento conjunto do logótipo
ficam para o desenho técnico.

`m-original.json` guarda os 674 vértices da secção, a transformação de eixos
e o SHA-256 do STL enviado. A mesma silhueta foi confirmada em cinco planos
ao longo da espessura. A placa antiga completa não é redistribuída.
O 7 conserva a fonte geométrica guardada em M7TijoloV4/source-seven.json.

## Impressão e acabamento a validar

A placa será impressa deitada, com o verso apoiado na mesa. O fundo será
inteiramente laranja até Z = 0,60 mm; os relevos coloridos começam acima desse
plano. Desta forma o fundo termina antes das trocas de cor dos símbolos.
A frente visível é impressa separadamente das divisórias do tijolo, evitando
a sua influência térmica direta durante a deposição da placa.

O projeto de impressão deverá manter camada de 0,20 mm e testar os percursos
Classic + outer/inner no corpo, conforme o estudo de acabamento da V4.
Para a placa, serão priorizados topo monotónico, velocidades estáveis e
arrefecimento antes da remoção. A temperatura e o fluxo do laranja serão
avaliados para o SUNLU PLA+ efetivamente usado; o dourado conserva um perfil
Silk próprio.

Os símbolos já vêm unidos ao fundo, com várias cores nas camadas de relevo.
O AMS terá trocas de cor e purga nessas camadas; a poupança de montagem é o
objetivo principal desta solução. O consumo e os tempos serão medidos após
aprovação do desenho e criação da geometria.

Estado atual: proposta visual e referência geométrica do m, para orientar a
próxima versão do CAD e o respetivo projeto Bambu.
