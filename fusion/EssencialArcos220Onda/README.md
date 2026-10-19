# Clínica Essencial — V2 com onda, altura total 220 mm

Nova versão do expositor com a **onda em altura** pedida pelo utilizador.
A base fica mais baixa ao centro e sobe suavemente nas laterais. A frente
branca e o fundo verde foram adaptados ao mesmo perfil, com línguas lisas
escondidas. Mantêm-se 220 × 80 × 220 mm no conjunto, dois QR reais, friso
dourado e fundo nervurado. Sem NFC ou WhatsApp.

**Usar as três peças estruturais V2 juntas**: frente, fundo e base. Não misturar
as placas estruturais V1 com a base V2. Os relevos dourados e pretos conservam
a posição e os QR da V1, mas já estão incluídos no novo projeto completo.

## Abrir o projeto e imprimir

Abrir `essencial-arcos-220-v2-onda-A1-AMS-3-pratos.3mf` **como projeto**, mantendo
as definições. A1, bico 0,4 mm, **camadas de 0,16 mm**, incluindo a primeira.
Associar os quatro materiais aos slots físicos do AMS antes de fatiar/enviar.

| Prato | Conteúdo | Cores |
| --- | --- | --- |
| 1 | Frente deitada, verso na mesa, cartões e relevos para cima | Branco, dourado, preto |
| 2 | Fundo deitado, verso na mesa, nervuras para cima | Verde |
| 3 | Base com aberturas para cima e friso dourado por baixo | Verde e dourado |

Não separar os materiais da montagem de cada prato. Não pousar os relevos
individualmente na mesa. A torre do prato 1 tem posição verificada para não
interferir com a peça ou o brim. Não mover objetos/torre sem voltar a fatiar.

## Onda, encaixes e dimensões

- Conjunto: **220 mm de largura × 80 mm de profundidade × 220 mm de altura**.
- Base: **12 mm ao centro até aproximadamente 22 mm nas laterais**; a borda
  inferior é plana. Friso dourado inferior de 1,2 mm.
- Perfil suave: altura `12 + 10 × (1 − exp(−(x/40)²))`, com x em mm a partir
  do centro. É uma superfície contínua em altura, não apenas uma curva em planta.
- Transição branca/verde com folga vertical nominal de 0,1 mm nos ombros
  ondulados; as línguas ficam escondidas pela parte frontal da base.
- Placas com núcleo de 3,2 mm, sem alterar os campos QR de 64 × 64 mm.
- Línguas branca/verde de 140/160 mm de largura, 3,2 mm de espessura.
- Ranhuras de 140,6/160,6 × 3,6 mm: folga de 0,2 mm por lado na espessura
  e 0,3 mm por extremidade. Fundo fechado a Z=4 mm.
- A profundidade das aberturas acompanha a onda: aproximadamente **8–18 mm**.
  As pontas das línguas ficam nominalmente a Z=4,2 mm, com 0,2 mm de folga
  ao fundo; não são línguas simples de 7,8 mm em toda a largura nesta versão.
- Nervuras: relevo de 1 mm, largura 1,25 mm, passo 3,2 mm; terminam no perfil
  ondulado visível. As partes que entram nas ranhuras são lisas.

As placas entram verticalmente. Foram verificadas 124 posições de inserção
sem colisões e o envelope montado. Centro de gravidade estático projetado com
margem de cerca de 30 mm no contorno da base, com aproximações de massa:
não é ensaio de empurrão, queda ou resistência.

Imprimir primeiro `essencial-arcos-220-v2-onda-amostra-encaixes.stl`: bloco
com duas ranhuras e duas pequenas línguas, três sólidos com faces planas na
mesa. Usar o mesmo filamento, camada de 0,16 mm e orientação das peças finais.
A amostra testa folga local, não o empeno de uma língua de 140/160 mm ou a
coincidência de toda a onda. Arrefecer completamente as peças grandes antes
de retirar da mesa, remover brim, testar montagem a seco e só depois colar
com uma película fina de adesivo compatível com PLA. Não forçar peças empenadas.

## Qualidade e materiais

As camadas de 0,16 mm reduzem os degraus visíveis na onda; não os eliminam.
A base é construída desde baixo, sem superfícies suspensas nem suportes.
Os ombros das placas imprimem no plano XY, com o verso plano na mesa.

- Frente/fundo: Arachne, três paredes, 15% gyroid, cinco camadas de topo e
  cinco de fundo, espessura mínima de topo de 1 mm conforme o perfil.
- Base: quatro paredes, 25% gyroid, Classic, no objeto do prato 3.
- Ordem exterior/interior, exterior 50 mm/s, interior 100 mm/s, topo monotónico
  25 mm/s, aceleração exterior 2000 e topo 1000 mm/s².
- Primeira camada: paredes 20 mm/s, preenchimento 30 mm/s; brim exterior 3 mm,
  afastamento 0,15 mm; compensação de pé de elefante de 0,10 mm.
- Torre de 30 mm, sem purgas no preenchimento. Mesa Textured PEI Plate.
- Slots lógicos: 1 branco, 2 verde, 3 dourado Silk, 4 preto. PLA a 220 °C,
  limite 8 mm³/s; Silk a 215 °C, limite 5 mm³/s, intervalo anterior 190–220 °C.
- Perfis de mesa a 65 °C para branco/verde/preto e 55 °C para Silk; confirmar
  os materiais reais e a temperatura escolhida no prato multicolor.
- O núcleo branco termina nas primeiras 20 camadas antes das trocas do relevo.

O projeto de impressão mantém **verde**. Castanho e bordô são apenas variantes
nas imagens solicitadas; não há outros perfis/material ou modelos distintos
nessas cores neste pacote. Uma mudança real de bobina deve usar o perfil do
filamento escolhido, não apenas outra cor de visualização.

## QR e identidade visual

- Instagram: https://www.instagram.com/clinicaessencial_setubal/
- Google: https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg

Mesmas matrizes da V1: campo de 64 mm com 45 módulos incluindo margem branca
de quatro módulos, passo 1,422 mm e relevo preto de 0,6 mm. Pequena separação
geométrica de 0,02 mm entre linhas evita contactos só num vértice no STL.
Os dois QR foram descodificados de secções dos STL exportados. Ver também o
relatório de cobertura dos módulos do G-code: projeção conjunta das quatro
camadas pretas de relevo, com arcos incluídos, e amostragem na grelha conhecida.
As duas grelhas resultantes descodificam e conservam todos os módulos esperados;
isto não é simulação ótica ou prova de leitura da impressão física. Confirmar leitura
na primeira impressão antes de entregar ou repetir unidades.

O lettering em Nimbus Roman e a raposa derivada da fotografia mantêm a
aproximação da V1; não são um logótipo original vetorial exato. As fotografias
de apresentação geradas são ilustrativas, incluindo os QR visíveis nelas;
usar exclusivamente os QR geométricos do projeto para imprimir.

## Validação, tempos e ficheiros

Ver `geometry-validation.json`, `bambu-validation.json` e
`qr-gcode-validation.json` para verificações, estimativas exatas e hashes.
O fatiamento pelo Bambu Studio oficial 02.08.02.61 confirma reabertura do
projeto, pratos dentro da mesa, sem suportes nem avisos de impressão. Ainda
sem ensaio físico de encaixe, transição, leitura ou estabilidade ao toque.

O preço de filamento usa branco 13 €/kg, verde/preto 16 €/kg e dourado 20 €/kg,
com os três últimos valores como hipóteses. Consumos incluem brim, torre e
purgas; não incluem a amostra, energia, cola, montagem ou máquina.

| Prato | Tempo estimado | Material |
| --- | --- | --- |
| Frente decorada | 6 h 12 min | 114,89 g |
| Fundo nervurado | 6 h 33 min | 123,32 g |
| Base com onda e friso | 9 h 11 min | 166,42 g |
| **Total** | **21 h 56 min** | **404,64 g** |

Filamento total estimado: **6,27 €** aos preços acima. O aumento relativamente
à V1 resulta da base mais alta nas laterais e das camadas de 0,16 mm.

O ZIP contém 3MF, seis STL por componente/material, amostra dos encaixes,
imagens reais do CAD cotadas, fotografias ilustrativas nas três cores, relatórios
e `EssencialArcos220Onda.py + geometry.json` para recriar BRep num documento
novo do Fusion. Este script não foi executado no Fusion neste ambiente e não
é um F3D validado; o 3MF é independente. Os scripts na pasta scripts dependem
dos módulos auxiliares do checkout Build e das matrizes/traçado já guardados.

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_essencial_arcos_220_onda.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_essencial_arcos_220_onda_3mf.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/verify_essencial_arcos_onda_qr.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_essencial_arcos_220_onda_3mf.py --package-only
```
