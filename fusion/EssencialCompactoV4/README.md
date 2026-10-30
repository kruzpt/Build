# Clínica Essencial — compacto V4, base plana e contorno orgânico

Revisão após o ensaio físico da base V3 mostrar patamares no topo ondulado e
uma costura lateral marcada. A V4 **não tem onda em altura**: a base tem topo
horizontal, com contorno orgânico inspirado no desenho do cliente visto de cima.
Mantém verde-azeitona, frente branca, dourado/preto, Instagram e avaliação Google.

**O utilizador confirmou que só a base anterior foi impressa.** Esta versão
reduz também a frente e o fundo; usar o conjunto V4 completo. As placas e
ranhuras V3 **não são intercambiáveis** com estas. Os ficheiros antigos mantêm-se.

## Dimensões e construção

| Elemento | V3 | V4 |
|---|---|---|
| Conjunto: largura × profundidade × altura | 220 × 80 × 220 mm | **200 × 70 × 200 mm** |
| Altura da base | 12–22 mm, topo em onda | **9,60 mm, topo plano** |
| Campo QR com margem branca | 64 × 64 mm | **58,58 × 58,58 mm** |
| Passo dos módulos QR | 1,422 mm | **1,302 mm** |
| Espessura do núcleo das placas | 3,20 mm | 3,20 mm |
| Cartões brancos em relevo | 0,48 mm | 0,48 mm |
| Preto e dourado sobre branco | 0,32 mm | 0,32 mm |
| Friso inferior dourado | 1,20 mm | **0,96 mm** |

A frente/fundo/grafismo foram reduzidos no plano XY por um fator 0,91538;
as espessuras de impressão foram preservadas. A altura das placas acima da
base é 190,40 mm. O branco termina em Z=3,68 mm antes das duas camadas de
cor, em Z=3,84 e 4,00 mm. Mantém-se a raposa limpa, sem a barra dourada errada.

A base tem três paredes, 15% Gyroid, sete camadas superiores/espessura mínima
de 1,12 mm, topo Monotonic a 20 mm/s e paredes exteriores a 35 mm/s, com
aceleração exterior de 1000 mm/s². A costura está em **Back**. Confirmou-se
que a base não foi rodada no prato, para a preferência Back corresponder à
traseira do expositor. Isto desloca a costura; **não garante eliminar o sulco**
se houver um problema de fluxo/retração no filamento real.

O topo plano evita os patamares associados à antiga onda. Continua a ser
impressão FDM: pode mostrar percursos e diferenças de brilho. Esta revisão
não foi impressa fisicamente; não se promete uma superfície lisa como uma
fotografia gerada. Ironing está desligado por predefinição do perfil.

## Projeto Bambu Studio

Abrir **essencial-compacto-v4-azeitona-A1-AMS-3-pratos.3mf como projeto**.
Bambu A1, **bico 0,4 mm**, camadas e primeira camada de **0,16 mm**, sem suportes.
Não separar os corpos coloridos nem alterar as posições da frente e torre sem
fatiar e verificar novamente.

| Prato | Conteúdo | Trocas | Estimativa | Material com torre/brim/purga |
|---|---|---:|---:|---:|
| 1 | Frente branca, QR/legendas pretos e lettering dourado | 3 | 4 h 50 min | 93,42 g |
| 2 | Fundo verde-azeitona nervurado | 0 | 5 h 15 min | 105,09 g |
| 3 | Base plana e friso dourado | 1 | 3 h 45 min | 65,25 g |
| **Total** | | **4** | **13 h 50 min** | **263,76 g** |

Valores do Bambu Studio 02.08.02.61 para uma unidade com estes perfis; a
amostra não está incluída. Em relação à V3, a base poupa cerca de **61% de
material e 59% de tempo**; o conjunto poupa aproximadamente **34% de ambos**.
A massa menor também reduz o lastro; a estabilidade ao toque precisa de teste.

Slots: **1 branco, 2 verde-azeitona, 3 dourado, 4 preto**. Selecionar os perfis
adequados às bobinas reais antes de imprimir. Os fornecidos usam Generic PLA
e Generic PLA Silk no dourado; 220 °C no bico, 8 mm³/s nos PLA normais e
5 mm³/s no Silk. O verde `#737648` é uma referência de visualização, não uma
especificação de cor garantida. Não inclui NFC ou WhatsApp.

## Encaixes e amostra

- Línguas com 3,20 mm de espessura; ranhuras com 3,60 mm, folga de 0,20 mm por lado.
- Língua branca com largura 128,15 mm; verde 146,46 mm, mais 0,60 mm de
  comprimento total nas ranhuras correspondentes para dar folga nas extremidades.
- Fundo das ranhuras em Z=3,20 mm; topo em Z=9,60 mm: profundidade **6,40 mm**.
- Pontas das línguas montadas em Z=3,40 mm: folga inferior de 0,20 mm.
- As placas entram verticalmente; as partes das línguas que entram são lisas.

Imprimir primeiro **amostra-encaixes.stl** no mesmo filamento e com a camada
0,16 mm. Testa folga local, espessura e profundidade, não o empeno de uma placa
longa. Arrefecer, retirar brim e verificar montagem a seco. Testar encaixe,
estabilidade e leitura dos QR no conjunto antes de colar com pouca cola
compatível com o PLA. Não forçar peças empenadas.

## QR e verificações

Instagram: https://www.instagram.com/clinicaessencial_setubal/

Google: https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg

Mesmas matrizes de 45 módulos incluindo quiet zone de quatro módulos;
separação geométrica de 0,02 mm entre linhas antes da redução no plano.
As secções dos STL exportados descodificam para os links acima. A projeção
dos percursos pretos preserva **todos os módulos** em ambos os QR, segundo
amostragem da grelha conhecida. O raster bruto do Instagram não descodificou;
a grelha amostrada não tem divergências e descodifica. Isto não é um teste
ótico ou uma leitura física: **confirmar com telemóvel no primeiro exemplar**.

O G-code confirma as primeiras 23 camadas só em branco e as duas finais
em preto/dourado. O topo verde final está todo a Z=9,60 mm (os fundos das
ranhuras estão a 3,20 mm) e os percursos de topo principal não excedem 20 mm/s.

Verificados: STL estanques, montagem sem colisões, 124 posições de inserção,
envelope nominal, exportação/reabertura/fatiamento nativos, sem suportes nem
avisos de impressão. O centro de gravidade estático aproximado tem margem
mínima de cerca de 18,4 mm na base; não é um ensaio de empurrão ou queda.
Ver relatórios JSON, incluindo `comparison-V3.json` e `base-surface-validation.json`.

Ainda sem ensaio físico da V4. A tipografia e a raposa são uma interpretação
do logótipo de referência, não o vetor original. As imagens fornecidas nesta
versão são vistas da geometria real, não fotografias de uma impressão.

## Ficheiros

3MF de três pratos, seis STL de componente/material, amostra STL, imagens CAD
com dimensões e vista superior da base, relatórios e script opcional Fusion
`EssencialCompactoV4.py + geometry.json`. O script Fusion não foi executado neste
ambiente; não é um F3D validado. Os geradores dependem dos auxiliares/dados
existentes no repositório Build.

```sh
python fusion/tools/generate_essencial_compacto_v4.py
python fusion/tools/build_essencial_compacto_v4_3mf.py
python fusion/tools/verify_essencial_compacto_v4_qr.py
python fusion/tools/build_essencial_compacto_v4_3mf.py --package-only
```
