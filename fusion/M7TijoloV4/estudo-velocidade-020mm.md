# M7 — estudo de tempo a 0,20 mm

Comparação de 18 de outubro de 2026, no Bambu Studio oficial **02.08.02.61**,
para a **Bambu Lab A1, bico de 0,4 mm**. Foi fatiado o prato do corpo terracota
do projeto V4. Os enfeites conservam o perfil original.

## Resultado

A melhor opção entre as comparações que conservam o limite de fluxo atual é
imprimir **quatro corpos juntos, por camada**. A estimativa passa de
**12 h 33 min** em quatro impressões separadas para **11 h 37 min** no lote:
cerca de **55 minutos de poupança**, ou **7,36% por corpo**.

A qualidade prevista mantém a mesma resolução e as mesmas velocidades de
deposição das superfícies visíveis. A impressão física do lote ainda precisa
de confirmação, sobretudo quanto a fios entre peças e adesão à mesa.

| Comparação | Tempo para o(s) corpo(s) | Tempo por corpo | Poupança por corpo |
| --- | --- | --- | --- |
| Atual: 1 corpo, fluxo 8 mm³/s | 3 h 08 min | 3 h 08 min | Referência |
| Parede interior: 130 → 200 mm/s | 3 h 08 min | 3 h 08 min | 0% |
| Preenchimento: 15% → 10% | 3 h 08 min | 3 h 08 min | 0% |
| Combinação de preenchimento ativada | 3 h 08 min | 3 h 08 min | 0% |
| Fluxo: 8 → 10 mm³/s | 3 h 04 min | 3 h 04 min | 2,26% |
| Fluxo: 8 → 12 mm³/s | 3 h 03 min | 3 h 03 min | 2,71% |
| 4 corpos, fluxo atual de 8 mm³/s | 11 h 37 min | 2 h 54 min | 7,36% |
| 4 corpos, fluxo de 10 mm³/s | 11 h 20 min | 2 h 50 min | 9,62% |

Tempos arredondados ao minuto; as percentagens usam os segundos sem
arredondamento. A comparação inclui a preparação estimada pelo fatiador.
Os valores referem-se apenas aos corpos, sem os outros três pratos de enfeites.

## Por que o preenchimento não ajuda

O corpo é composto sobretudo por paredes finas entre os oito furos. Com três
paredes de impressão, estas zonas já ficam ocupadas pelos perímetros.
O G-code de referência não contém percursos de preenchimento esparso.
Reduzir a percentagem ou combinar esse preenchimento não muda os percursos
neste modelo. Aumentar a velocidade interior também fica limitado pelo fluxo.

## O que se manteve

- Geometria e escala: 50 × 26 × 70 mm; dados das malhas do 3MF copiados sem alteração.
- Camada normal e inicial: 0,20 mm; 350 camadas.
- Três paredes, paredes Arachne e larguras de linha originais.
- Parede exterior a 60 mm/s e superfície superior a 35 mm/s.
- Mesmas temperaturas, ventilação, retrações, compensações e camadas de topo/fundo.
- Brim exterior do corpo com 3 mm e distância de 0,15 mm.
- Zero trocas de cor e zero percursos de suporte em cada comparação.

Nos testes de um só corpo, os percursos depositados e as velocidades das
paredes exteriores e dos topos são idênticos à referência. No lote, o número
de movimentos e a distribuição das velocidades dessas superfícies são
exatamente quatro vezes os de um corpo. Os comprimentos depositados por corpo
são equivalentes dentro do arredondamento das coordenadas.

As variantes de fluxo alteram o limite do terracota apenas; os outros três
filamentos mantêm os limites originais. Mesmo mantendo os comandos exteriores
iguais, um limite maior exige ensaio do PLA usado: o fatiador não deteta
subextrusão real, variações de brilho ou diferenças de adesão entre camadas.
A poupança de quatro a cinco minutos por corpo não justifica assumir essa
capacidade sem a testar.

## Lote comparado e recomendação

Quatro corpos na mesma orientação vertical, com os oito furos verticais,
em grelha 2 × 2 e impressão por camada. Centros XY em milímetros:
(91, 93), (165, 93), (91, 163) e (165, 163).
A distância mínima entre corpos é de 24 mm antes dos brims.
As quatro caixas envolventes foram confirmadas no resultado do fatiador;
todas têm 50 × 26 × 70 mm e assentam em Z = 0, dentro da mesa.

Recomenda-se conservar o perfil V4 a 0,20 mm e fluxo de 8 mm³/s,
começando por um lote de quatro. Várias peças não exigem aumentar a velocidade.
Mais tempo de arrefecimento entre passagens pode afetar ligeiramente o aspeto;
podem surgir fios entre peças. Conservar os brims e verificar a primeira camada
antes de deixar o lote decorrer permite avaliar o resultado físico.

## Rastreabilidade

Projeto analisado:
[`m7-tijolo-v4-A1-AMS-4-pratos.3mf`](../../downloads/m7-tijolo-v4-A1-AMS-4-pratos.3mf).

SHA-256 do projeto original:
`d4a23110333dde6e21bb70f19350033b8c202d4fd3971bd99857a872bdea8ddc`.

As oito execuções terminaram com sucesso, sem avisos de impressão.
Os resultados em segundos, consumo, caixas envolventes e checksums do G-code
estão em [estudo-velocidade-020mm.json](estudo-velocidade-020mm.json).
O 3MF original mantém o mesmo checksum; estes ensaios não o substituem.
