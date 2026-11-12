# Aquelá V4 — folhas com a zona oculta só verde

[Descarregar acessórios V4 — Bambu A1 / AMS, bico 0,4 mm](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v4-ACESSORIOS-A1-04-AMS-2-pratos.3mf?raw=true)

[Pacote completo com o lobo aprovado](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v4-pacote.zip?raw=true) · [Comparação V3 / V4](../../designs/anilha-aquela-v4-folhas-comparacao-CAD.png) · [Conjunto montado](../../designs/anilha-aquela-v4-montada-CAD.png)

Foi substituído por verde o material preto que ficava escondido sob o lobo e a tabuleta. A superfície nessa zona **já era plana na V3 e mantém-se a 2,00 mm**; não se alterou a espessura nem se acrescentou relevo. As nervuras e os contornos das folhas expostas mantêm a forma e a cor.

A área a simplificar foi calculada a partir do contorno real do verso do lobo. Conserva-se uma margem de **0,45 mm para dentro desse contorno**, para tolerar pequenos desvios na colagem sem revelar uma interrupção dos detalhes nas bordas. Assim, a zona interior oculta fica integralmente verde, com uma faixa estreita junto ao limite que conserva os detalhes anteriores.

O volume preto geométrico das folhas diminui cerca de **56,5%**, sendo substituído por verde. A geometria exterior total mantém-se. Os ficheiros do lobo, tabuleta, nome **Aquelá** e anilha são os mesmos da V2 aprovada, com hashes verificados.

## O que imprimir

O projeto de acessórios continua com dois pratos:

1. Anilha castanha, modelo anterior sem alterações.
2. Folhas V4, um objeto com dois volumes de cor: verde e preto.

**Se o lobo e a anilha já estão impressos, basta imprimir o prato 02 das folhas V4.** Não imprimir as nervuras separadamente. Abrir o 3MF como projeto completo e manter os volumes alinhados.

A montagem mantém os centros e as bases do lobo e das folhas alinhados. Colar a anilha atrás e o lobo à frente, sobre a zona plana verde. O conjunto continua a ter três peças físicas. Não existem encaixes de pressão.

## Resultado do fatiamento das folhas

| Estimativa | V3 | V4 |
| --- | --- | --- |
| Tempo | 1 h 20 min 04 s | 1 h 14 min 19 s |
| Material na peça | 5,00 g | 4,69 g |
| Material com purgas e torre | 8,80 g | 8,49 g |
| Trocas de filamento | 10 | 10 |

A poupança estimada é de **5 min 45 s e 0,31 g por peça de folhas**. As trocas continuam porque as mesmas camadas ainda contêm preto nas folhas visíveis. A redução do volume preto não equivale à mesma redução de material total ou de purga.

Conservam-se os perfis Generic PLA, camada 0,12 mm, primeira camada 0,20 mm, Arachne, velocidades de acabamento e torre de purga da versão anterior. Sem suportes nem brim. A anilha conserva exatamente as estimativas da V3. Estes perfis não representam uma nova calibração de filamento.

## Verificação

- Malhas fechadas e volumes de cor sem interseção volumétrica.
- Forma exterior, dimensões 62 × 48 × 2,96 mm e face de colagem preservadas.
- Lobo e anilha reutilizados sem alteração dos ficheiros.
- Ausência de colisões na montagem digital.
- Exportação, reabertura e fatiamento dos dois pratos no Bambu Studio 2.9.1.70, sem avisos de impressão.
- **Zero percurso preto dentro da zona interior oculta**, verificado no G-code com a transformação real do objeto no prato.

[Geometria e hashes](geometry.json) · [Relatório Bambu e comparação de consumo](bambu-validation.json) · [Percursos reais](../../designs/anilha-aquela-v4-folhas-percursos.png)

Não foi efetuada impressão ou colagem física desta versão.

## Reprodução

```bash
python fusion/tools/generate_anilha_aquela_v4.py
python fusion/tools/build_anilha_aquela_v4_3mf.py --bambu-bin /caminho/bin/bambu-studio --work-dir /tmp/aquela-v4
python fusion/tools/package_anilha_aquela_v4.py
```
