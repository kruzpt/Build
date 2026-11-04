# M7 — Tijolo V7: fundo laranja contínuo e aceleração mais suave

Correção após a impressão da V6 mostrar contornos dos relevos desenhados
na última camada laranja. A ordem das cores estava correta, mas o acabamento
da placa ainda era dividido pelos desenhos. O pedido adicional de melhorar
as pequenas pontas nos cantos superiores da placa foi considerado sem alterar
fluxo ou temperatura sem calibração.

## Alterações efetivas

- **No objeto completo da placa:** `Only one wall on top surfaces = Not apply`.
  O laranja passa a ser acabado em percursos contínuos antes dos relevos.
- **Aceleração das paredes exteriores: 1000 mm/s²**, em vez de 2000.
  Foi aplicada no perfil geral e nos metadados relevantes, porque o fatiador
  usado não respeitou o valor colocado apenas no objeto/partes. Foi confirmada
  nos comandos M204 das paredes exteriores dos dois pratos.
- Topo mantido a **25 mm/s**. Temperaturas, fluxo, velocidades e arrefecimento
  dos filamentos conservados. A redução de aceleração é um ajuste conservador
  para tornar transições mais graduais; não é prova de que a pontinha desapareça.

A aceleração mais suave também se aplica ao corpo ao imprimir o prato 1 desta
versão. Se já tens um corpo V5/V6, não precisas de o repetir: usa o **prato 2**.

**A geometria e a montagem são byte a byte iguais às da V6**. Mantidos:

| Elemento | V7 |
|---|---|
| Placa laranja | **46,4 × 66,4 × 0,60 mm** |
| Folga nominal no rebaixo | **0,30 mm por lado** |
| Corpo | 50 × 26 × 70 mm, mesmo STL V5/V6 |
| Rebaixo | 47 × 67 × 0,70 mm |
| Espaço nominal para cola atrás da placa | 0,10 mm |
| Espessura total da placa com relevo | 1,60 mm |

Os detalhes m/7, estrela, árvore e Natal 2026 não foram redimensionados.
A verificação geométrica do encaixe da V6 permanece aplicável, mas ainda
é necessário apresentar a placa fria sem cola e confirmar que assenta sem
pressão. A folga adicional não corrige uma placa empenada fora do tijolo.

## Sequência confirmada no G-code

- **Z=0,20 / 0,40 / 0,60 mm:** apenas laranja. Na última camada não há
  perímetros dos desenhos nem gap fill na região interior da placa analisada;
  há apenas percursos de topo. O perímetro exterior normal da placa mantém-se.
- **Z=0,80–1,60 mm:** dourado, branco e ciano, formando os relevos.
- Não há extrusão laranja da peça depois de Z=0,60 mm.

V6 e V7 foram fatiadas no mesmo Bambu Studio 02.08.02.61; a comparação de
percursos mostra o interior da placa na última camada laranja. Azul indica
percursos de topo, vermelho os outros percursos. É desenho do G-code, não
foto nem teste de superfície. A verificação usa coordenadas reconstruídas
pela correspondência com o STL exportado, para excluir torre e movimentos
de preparação.

## Abrir e imprimir

Abrir **m7-tijolo-v7-acabamento-A1-AMS-2-pratos.3mf como projeto**. A1,
bico 0,4 mm, PLA, camada/primeira camada de 0,20 mm, PEI texturado.
Placa com laranja contra o prato e relevos para cima; não separar corpos.
**Sem brim ou suportes** nas peças. Torre de priming mantida no multicolor.

Slots: **1 laranja, 2 dourado Silk, 3 branco, 4 ciano**. As temperaturas
conservadas são 220 / 215 / 220 / 220 °C. Limites volumétricos 8 mm³/s nos
PLA normais e 5 no Silk. Confirmar as bobinas reais antes de enviar.

Recomenda-se **Flow Dynamics Calibration ON** no envio da A1, com os filamentos
reais. Esta opção de envio não equivale a guardar um K calibrado no 3MF.
O flow ratio mantém 0,98 de origem: não é uma medição das bobinas do utilizador.

| Prato | Conteúdo | Estimativa | Material incl. torre/purga | Trocas |
|---|---|---:|---:|---:|
| 1 | Corpo do tijolo | 3 h 10 min | 46.12 g | 0 |
| 2 | Placa multicolor | 0 h 52 min | 8.67 g | 11 |

Estimativas do fatiador, não tempos/pesos físicos. As alterações não são
aplicadas a uma impressão já iniciada ou pausada: é necessário abrir o novo
projeto, fatiar e começar uma nova impressão para usar estes percursos.

## Limites e validação

Os percursos mostram a correção do fundo laranja. A causa exata da pontinha
superior ainda não foi confirmada; pode envolver pressão, fluxo, temperatura
ou arrefecimento local. **Não se garante eliminar essa marca** apenas com
esta revisão, e não foi inventada uma calibração de fluxo ou retração.

Confirmadas exportação/reabertura/fatiamento dos dois pratos sem avisos,
suportes ou brim, geometria V6 preservada, oito camadas na placa, sequência
correta e aceleração exterior de 1000 mm/s² efetiva. O topo conserva linhas
normais de impressão FDM. **Sem ensaio físico da V7.**

Pacote: 3MF completo, relatório, comparação de percursos, pratos e script.
Os STL e o script Fusion da V6 continuam aplicáveis, por a geometria ser a
mesma. O gerador depende dos auxiliares e do 3MF V6 no checkout Build;
não executa o Fusion nem envia trabalhos para a impressora.

```sh
python fusion/tools/build_m7_brick_finish_v7.py
python fusion/tools/build_m7_brick_finish_v7.py --package-only
```
