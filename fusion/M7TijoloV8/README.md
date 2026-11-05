# M7 — tijolo V8, placa decorada com fundo de uma parede

Projeto completo pedido após o teste V5 da placa lisa. Mantém a construção com
placa laranja e relevos unidos em AMS; a alternativa de colar cada decoração
diretamente no tijolo continua apenas em estudo.

## O que contém

1. **Corpo do tijolo**, com a geometria e o rebaixo anteriores.
2. **Placa decorada completa:** fundo laranja, estrela e árvore douradas,
   logótipo branco/ciano e texto Natal 2026 branco.

Se já tens o corpo, basta imprimir o **prato 2**. Abrir o 3MF como projeto,
voltar a fatiar e manter a calibração dinâmica ativa no envio.

## Configurações aplicadas

- A1, bico 0,4 mm, camada/primeira camada 0,20 mm.
- Fundo laranja: **uma parede**, Monotonic line, direção 45°, sobreposição 10%.
- A definição de uma parede está na parte laranja. Os relevos conservam três
  paredes solicitadas; o fatiador adapta os traços estreitos à sua largura.
- Fluxo laranja **0,931**, dourado **0,9702**, branco/ciano **0,98**.
- Temperaturas conservadas: laranja/branco/ciano 220 °C, dourado 215 °C.
- Topo 25 mm/s, parede exterior 50 mm/s e 1000 mm/s² após a primeira camada.
- Pintura da costura transferida do teste V5 para a mesma geometria do fundo.
- Sem brim ou suportes nas peças; torre de preparação ativa no multicolor.

A calibração do laranja também passa a ser usada no prato do corpo. O desenho
desse corpo não mudou e o já impresso pode ser reutilizado. A geometria do fundo
continua **46,4 × 66,4 × 0,60 mm**, com folga CAD de 0,30 mm por lado e espaço
de 0,10 mm no fundo para cola. A placa completa tem 1,60 mm com os relevos.

## Verificação

Fatiado no Bambu Studio 02.09.01.70, sem avisos. Confirmados no Gcode:

- Z=0,20 / 0,40 / 0,60 mm: só laranja, uma parede exterior e nenhuma interior.
- O laranja fica concluído antes das mudanças de cor dos relevos.
- Z=0,80–1,60 mm: dourado, branco e ciano, com contornos exteriores e interiores.
- Todos os vértices e índices de triângulos do projeto anterior permanecem iguais.
  Apenas a pintura da costura foi acrescentada aos triângulos do fundo.

As estimativas e o hash do ficheiro estão em `bambu-validation.json`.
O ensaio físico da amostra tinha pequenas marcas; este projeto completo ainda
não foi impresso. Confirmar a qualidade de uma unidade e o encaixe a seco antes
de colar ou produzir uma série.

## Requisito para a alternativa futura

Se se adotar o tijolo inteiro com decorações coladas individualmente,
**Natal 2026 terá de ser uma peça ou, no máximo, duas**. Esse requisito fica
registado; não se mudou para essa arquitetura neste projeto.
