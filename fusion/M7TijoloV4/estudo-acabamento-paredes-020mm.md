# M7 — opções de acabamento das paredes, 0,20 mm

Comparação de 18 de outubro de 2026, no Bambu Studio oficial 02.08.02.61,
Bambu Lab A1 com bico de 0,4 mm. O utilizador relatou linhas verticais na
impressão, alinhadas com as divisórias, que se sentem ao passar a unha.
Trata-se de irregularidade física; a causa exata ainda exige ensaio de impressão.

A frente do desenho tem 2,25 mm de espessura, ou 2,05 mm nos rebaixos.
A geometria da frente é plana. Fora dos rebaixos, o G-code imprime essa frente
em linha reta. A coincidência com as divisórias é compatível com marcação
causada pela pressão de deposição e contração nas uniões; o fatiador não simula
esses efeitos térmicos e mecânicos.

## Nome em inglês e localização confirmados

Ativar o interruptor **Advanced** junto às definições de processo.
Em **Quality**, descer à secção **Advanced** e procurar:

**Order of walls → outer/inner**

A referência V4 usa **inner/outer**. A indicação anterior de procurar em
Strength foi corrigida: esta opção pertence a Quality.
A lupa de pesquisa das definições também encontra **Order of walls**.

O caminho e os nomes foram confirmados no código oficial da mesma versão:

- [Tab.cpp: Quality e secção Advanced](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/slic3r/GUI/Tab.cpp#L3263)
- [PrintConfig.cpp: Order of walls e valores apresentados](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp#L2194)

## Fatiamentos comparados

Só o corpo terracota foi fatiado. Todos mantêm o STL, escala, camada de 0,20 mm,
350 camadas, três paredes, velocidades nominais exteriores, temperaturas e
limite de fluxo de 8 mm³/s. O projeto original e os enfeites não foram alterados.

| Variante | Alteração relativamente ao original | Tempo estimado | Material |
| --- | --- | --- | --- |
| Referência | Arachne, inner/outer, aceleração exterior 5000 mm/s² | 3 h 08 min | 38,54 g |
| Outer first | Order of walls: outer/inner | 2 h 59 min | 38,54 g |
| Sandwich | Order of walls: inner wall/outer wall/inner wall | 3 h 03 min | 38,54 g |
| Classic | Wall generator: Classic; conserva inner/outer | 2 h 29 min | 39,71 g |
| Classic + outer first | Classic e outer/inner | 2 h 29 min | 39,71 g |
| Menor aceleração exterior | Outer wall acceleration: 5000 → 2000 mm/s² | 3 h 14 min | 38,54 g |

Valores arredondados ao minuto. Classic isolado dá 2 h 29 min 23 s; combinado
com outer/inner dá 2 h 28 min 32 s. São tempos de fatiador, incluindo a
preparação estimada, não medições de impressões físicas.

Todas as execuções terminaram sem avisos de impressão, sem suportes gerados
e sem trocas de filamento. Os dados exatos e checksums dos G-codes estão em
[estudo-acabamento-paredes-020mm.json](estudo-acabamento-paredes-020mm.json).

## Ensaios recomendados

1. Alterar apenas **Quality → Advanced → Order of walls → outer/inner**.
   O objetivo é depositar o exterior antes das linhas interiores.
2. Se necessário, comparar com **Quality → Wall generator → Classic**,
   conservando as restantes opções do primeiro ensaio. Aplicar ao corpo em
   **Objects**; manter Arachne e as definições existentes nos enfeites.
3. Comparar amostras de cerca de 15 mm de altura, cortadas à escala original.
   Depois de escolher uma variante, confirmar num tijolo completo.

Classic usa larguras constantes nas paredes e preenche intervalos com gap fill;
Arachne usa larguras variáveis. O padrão de deposição muda, bem como o consumo.
A poupança de cerca de 39 minutos torna Classic um candidato interessante,
mas não prova melhoria de acabamento ou encaixes. É necessário verificar a
frente e os rebaixos nas peças impressas.

## Outras definições revistas

- **Calibration → Flow Rate**: calibrar a quantidade de material para o
  SUNLU PLA+ usado. O **Flow ratio** atual é 0,98; não foi escolhido um valor
  novo sem calibração.
- **Calibration → Flow Dynamics**: verificar a calibração de pressão para
  esse filamento. Pode melhorar transições de extrusão; não prova nem garante
  eliminar uma deformação térmica nas divisórias.
- **Filament → Nozzle temperature → Other layers**: o perfil usa 220 °C.
  Manter no primeiro ensaio. O utilizador identificou SUNLU PLA+, mas não
  forneceu a versão exata nem o intervalo da bobina. Uma comparação a 215 °C
  só faz sentido dentro do intervalo indicado e como ensaio separado.
- **Speed → Acceleration → Outer wall**: reduzir de 5000 para 2000 mm/s²
  é uma opção para vibrações e ressaltos, com custo estimado de seis minutos.
  As marcas alinhadas com divisórias não demonstram, por si, um problema
  de vibração; esta alteração não foi priorizada.
- **Infill/Wall overlap**: o corpo não tem preenchimento esparso no fatiamento
  de referência. Alterar esta percentagem não atua sobre a união geométrica
  das divisórias.
- **Precise wall**: existe na secção Quality/Precision desta versão, mas a
  definição está marcada como modo de desenvolvimento no código oficial.
  Não é necessária para o primeiro teste nem substitui controlo de fluxo.

Se o ajuste de percursos e a calibração não resolverem, uma frente mais
espessa no desenho pode diminuir a marcação das divisórias. Aumentar apenas
Wall loops não engrossa a geometria existente, que já fica quase maciça.

## Rastreabilidade

Projeto:
[m7-tijolo-v4-A1-AMS-4-pratos.3mf](../../downloads/m7-tijolo-v4-A1-AMS-4-pratos.3mf).

SHA-256 original, preservado: `d4a23110333dde6e21bb70f19350033b8c202d4fd3971bd99857a872bdea8ddc`.

As variantes existem apenas como ensaios de fatiamento. O relatório não
substitui o projeto original nem afirma validação física das configurações.
