# M7 — Tijolo V6: placa com mais folga, sem brim

Revisão aprovada após o ensaio da V5: a placa entrava justa e levantava ao
colar. O fundo laranja passa de **46,6 × 66,6 para 46,4 × 66,4 mm**, mantendo
**0,60 mm de espessura**. No rebaixo existente de 47 × 67 mm, a folga nominal
passa de **0,20 para 0,30 mm por lado**.

O recuo foi aplicado ao contorno completo, incluindo cantos, por um offset
interior de 0,30 mm relativamente ao rebaixo. A placa mantém o centro original.
**Decoração sem escala ou deslocação:** estrela, árvore, m/7 originais e Natal
2026 permanecem nas mesmas posições e com o mesmo tamanho da V5.

**O corpo do tijolo não foi alterado.** O STL do corpo e os três STL de relevo
são byte a byte iguais aos da V5. Se o corpo já está impresso, pode ser
reutilizado; imprimir apenas o **prato 2** desta revisão.

## Dimensões

| Elemento | V5 | V6 |
|---|---|---|
| Corpo exterior | 50 × 26 × 70 mm | Igual |
| Rebaixo | 47 × 67 × 0,70 mm | Igual |
| Placa laranja | 46,6 × 66,6 × 0,60 mm | **46,4 × 66,4 × 0,60 mm** |
| Folga nominal por lado | 0,20 mm | **0,30 mm** |
| Espaço para cola atrás da placa | 0,10 mm | Igual |
| Relevo decorativo | 1,00 mm | Igual |
| Espessura total da placa | 1,60 mm | Igual |

Valores de projeto, não medições físicas. A folga adicional procura evitar
compressão nas bordas; não corrige uma placa que já esteja empenada fora
do tijolo. Não foi aplicado redimensionamento global, que reduziria também
os detalhes e alteraria a espessura.

## Imprimir

Abrir **m7-tijolo-v6-folga-A1-AMS-2-pratos.3mf como projeto**. Bambu A1,
bico de 0,4 mm, camada e primeira camada de 0,20 mm, PEI texturado.
**Sem brim nos dois pratos**, conforme a preferência do utilizador.
Sem suportes. Torre de priming ativa no prato multicolor; não purgar para o
preenchimento. Não separar os corpos coloridos da placa nem colocá-los
individualmente sobre o prato.

| Prato | Conteúdo | Estimativa | Material incl. torre/purga | Trocas |
|---|---|---:|---:|---:|
| 1 | Corpo com moldura | 3 h 02 min | 46.12 g | 0 |
| 2 | Placa decorativa multicolor | 0 h 53 min | 8.67 g | 11 |
| **Total** | | **3 h 55 min** | **54.79 g** | |

Estimativas Bambu Studio 02.08.02.61, não tempos/pesos medidos. A orientação
é a da V5: corpo com oito furos verticais; placa com o fundo laranja apoiado
no prato e os relevos para cima. Primeiras três camadas da placa só em laranja,
até Z=0,60 mm; relevos de Z=0,80 até 1,60 mm.

Slots lógicos: **1 laranja, 2 dourado Silk, 3 branco e 4 ciano**. Perfis
conservados da V5: laranja SUNLU PLA+ a 220 °C; dourado Silk a 215 °C,
intervalo de bobina anteriormente fornecido 190–220 °C; branco/ciano a 220 °C.
Limites volumétricos 8 mm³/s nos PLA normais e 5 mm³/s no Silk. Adequar às
bobinas reais e confirmar os slots físicos no envio.

Mantidos três perímetros, 15% Gyroid, cinco camadas de topo/quatro de fundo,
perfil de topo Monotonic line a 25 mm/s, primeira camada a 20/30 mm/s.
Corpo com Classic, exterior/interior, exteriores 50 mm/s, interiores 100 mm/s
e aceleração exterior de 2000 mm/s²; Arachne conserva os detalhes da placa.
A única mudança de impressão transversal à V5 é a remoção do brim.

## Montar

1. Deixar arrefecer e retirar a placa sem a dobrar.
2. Apresentar sem cola no corpo V5/V6. Deve assentar completamente, sem
   pressionar as bordas ou arquear o centro. Confirmar a folga no exemplar real.
3. Se levantar também fora do tijolo, tratar o empeno antes de colar.
4. Aplicar uma película fina de cola compatível com PLA no fundo do rebaixo,
   evitando excesso nas bordas. A folga traseira nominal continua em 0,10 mm.
5. Assentar sem forçar e manter plana enquanto a cola fixa, protegendo o relevo.

## Validação e conteúdo

Verificados os cinco STL fechados, placa conectada com os relevos, dimensões,
contorno da placa dentro do rebaixo, 25 posições de entrada por componente
sem colisões, preservação dos contornos originais m/7 e identidade dos STL
reutilizados. Projeto exportado, reaberto e os dois pratos fatiados sem avisos,
suportes ou brim nas peças. A torre pode ter a sua própria base de estabilização.

**Sem ensaio físico da V6.** A nova folga foi aprovada, mas precisa de confirmação
na impressão; a alteração não garante corrigir empeno ou problemas de fluxo.

Pacote: 3MF, cinco STL, vistas CAD, relatórios e script opcional
`M7TijoloV6.py + geometry.json`. Fusion não foi executado neste ambiente;
não é um F3D validado. Os geradores dependem dos auxiliares e dados do
checkout Build. As versões anteriores foram preservadas.

```sh
python fusion/tools/generate_m7_brick_v6.py
python fusion/tools/build_m7_brick_v6_3mf.py
python fusion/tools/build_m7_brick_v6_3mf.py --package-only
```
