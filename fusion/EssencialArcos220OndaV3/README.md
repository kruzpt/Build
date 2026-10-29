# Clínica Essencial — V3 verde-azeitona, branco completo antes da cor

Versão revista do expositor de 220 × 80 × 220 mm com base em onda,
frente branca, fundo nervurado verde-azeitona e detalhes dourados/pretos.
Mantém os dois QR de Instagram e avaliações Google; sem NFC e WhatsApp.
Preserva os ficheiros anteriores, com novo prefixo `essencial-arcos-220-v3-azeitona`.

## Alterações pedidas

- Removido o fragmento dourado em forma de letra à esquerda da raposa.
  O traçado anterior tinha três componentes: retirou-se apenas o fragmento
  estreito de 26,98 mm²; mantiveram-se as duas componentes da raposa.
- Cartões brancos integrados na frente: relevo reduzido de 1,00 para **0,48 mm**.
- Preto e dourado na frente: **0,32 mm**, em duas camadas de 0,16 mm.
- Todos os relevos coloridos começam a **Z=3,68 mm** e terminam a Z=4,00 mm.
  Há pequenos pedestais brancos sob o lettering, raposa, linha e nome, para
  os colocar à mesma altura dos cartões. A placa branca tem núcleo de 3,20 mm.
- **23 camadas apenas de branco**, incluindo os pedestais/cartões; só depois
  se imprimem as duas camadas de preto/dourado. Não depende de pintar volumes
  à mão ou de escolher impressão sequencial por objeto.
- Verde-azeitona de visualização `#737648`; a cor física depende da bobina.

## Abrir e imprimir

Abrir **essencial-arcos-220-v3-azeitona-A1-AMS-3-pratos.3mf como projeto**.
A1, bico **0,4 mm**, PLA, camadas **0,16 mm**, incluindo a primeira.
Não separar os materiais nem pousar os relevos individualmente na mesa.
Não alterar as posições da frente e da torre sem verificar o novo fatiamento.

| Prato | Conteúdo | Filamentos | Trocas |
|---|---|---|---:|
| 1 | Frente branca, QR/legendas pretos e lettering/raposa dourados | Branco, dourado, preto | **3** |
| 2 | Fundo nervurado | Verde-azeitona | **0** |
| 3 | Base com onda e friso inferior | Verde-azeitona e dourado | **1** |

Slots lógicos: **1 branco; 2 verde-azeitona; 3 dourado; 4 preto**.
Associar aos slots reais do AMS antes de enviar. O dourado usa Generic PLA Silk
como ponto de partida; os outros usam Generic PLA. Os perfis entregues indicam
220 °C no bico; mesa Textured PEI a 65 °C para branco/verde/preto e 55 °C no
perfil Silk. Confirmar compatibilidade dos perfis com os filamentos reais;
esta configuração não representa calibração das bobinas do utilizador.

Mantidos Interface shells, topo Monotonic, Arachne, três paredes e 15% gyroid
nas placas. Base com quatro paredes, 25% gyroid e Classic. Topo a 25 mm/s,
paredes exteriores a 50 mm/s e primeira camada a 20/30 mm/s. Sem suportes.
Brim de 3 mm e torre de 30 mm, com espaço reservado ao lado da frente.

## Encaixe e montagem

Mantêm-se a base em onda (12 mm ao centro até aproximadamente 22 mm nas
laterais), línguas lisas escondidas e duas ranhuras independentes. Usar as
peças estruturais desta versão como conjunto; não misturar versões ao acaso.

- Línguas branca/verde: 140/160 mm de largura, 3,20 mm de espessura.
- Ranhuras: 140,6/160,6 × 3,6 mm; folga de 0,20 mm por lado na espessura.
- Fundo das ranhuras a 4 mm; folga inferior nominal de 0,20 mm.
- As placas entram verticalmente; o fundo nervurado tem línguas sem nervuras.

Imprimir primeiro a amostra de encaixes STL, com os mesmos filamentos e
camadas de 0,16 mm. A amostra testa folga local, não empeno de uma placa longa.
Arrefecer completamente, retirar brim, testar montagem a seco e leitura dos
QR com telemóvel antes de colar. Usar pouca cola compatível com PLA e não
forçar placas empenadas. Os cartões brancos não são peças para colar.

## QR reais

- Instagram: https://www.instagram.com/clinicaessencial_setubal/
- Avaliação Google: https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg

Mantidas as matrizes anteriores, com campo 64 × 64 mm, 45 módulos incluindo
margem branca de quatro módulos, passo 1,422 mm e separação geométrica de
0,02 mm entre linhas para evitar contactos apenas num vértice no STL.
As secções dos STL exportados descodificam para os links acima.

O relatório `qr-gcode-validation.json` verifica a projeção dos percursos pretos
nas camadas 3,84 e 4,00 mm: **zero módulos divergentes** em ambos os QR,
com amostragem na grelha conhecida e descodificação dos módulos amostrados.
O raster bruto de linhas do Instagram não descodificou diretamente; a grelha
amostrada conserva todos os módulos. **Isto não é um ensaio ótico nem prova
de leitura física.** Confirmar leitura no primeiro exemplar, com boa iluminação,
antes de entregar ou repetir unidades.

O mesmo relatório confirma, pelas extrusões do G-code excluindo torre/custom,
que as camadas 1–23 só usam branco e as 24–25 só usam dourado/preto.

## Validação e estimativas

Malhas estanques, seis corpos de material, montagem sem colisões, 124 posições
de inserção das placas verificadas e envelope nominal preservado. O centro de
massa estático tem margem de cerca de 30 mm na base; não é teste de queda.
Exportação, reabertura e fatiamento nativos no Bambu Studio **02.08.02.61**,
sem suportes nem avisos de impressão. Ver os relatórios JSON e os hashes.

| Prato | Tempo estimado | Consumo incluindo brim/torre/purga |
|---|---:|---:|
| Frente | 5 h 37 min | 110,06 g |
| Fundo nervurado | 6 h 21 min | 124,54 g |
| Base e friso | 9 h 07 min | 166,68 g |
| **Total** | **21 h 05 min** | **401,28 g** |

Estimativas para uma unidade e estes perfis; não incluem a amostra. Ainda
sem impressão, ensaio físico de encaixe/QR ou verificação de cor/opacidade.
Com apenas duas camadas de cor, testar também a opacidade do dourado escolhido.

## Ficheiros e reprodução

ZIP: 3MF, seis STL por componente/material, amostra STL, imagens da geometria
real, relatórios, e `EssencialArcos220OndaV3.py + geometry.json` para recriar os
corpos num documento novo do Fusion. O script Fusion não foi executado neste
ambiente e não é um F3D validado. A tipografia e a raposa continuam a ser uma
aproximação do logótipo, sem vetor original; foi removido o fragmento assinalado.

Os scripts dependem dos auxiliares e dados do repositório Build:

```sh
python fusion/tools/generate_essencial_arcos_220_onda_v3.py
python fusion/tools/build_essencial_arcos_220_onda_v3_3mf.py
python fusion/tools/verify_essencial_arcos_onda_v3_qr.py
python fusion/tools/build_essencial_arcos_220_onda_v3_3mf.py --package-only
```
