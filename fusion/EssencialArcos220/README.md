# Clínica Essencial — arcos, 220 mm de altura

Projeto novo baseado na proposta aprovada: frente branca assimétrica, fundo
verde nervurado e base verde com friso dourado. Apenas Instagram e avaliações
Google. **Sem NFC, cavidades NFC ou WhatsApp.** Não substitui os ficheiros
EssencialA1Reviews mais antigos, que têm outro desenho e NFC.

## Ficheiros e abertura

Abrir **essencial-arcos-220-v1-A1-AMS-3-pratos.3mf como projeto** no Bambu Studio,
mantendo as configurações. Selecionar Bambu A1 com bico 0,4 mm e associar os
quatro filamentos aos slots físicos do AMS. Fatiar antes de enviar à máquina.
O 3MF é editável; não contém um G-code para enviar sem rever o AMS.

| Prato | Conteúdo | Cores usadas |
| --- | --- | --- |
| 1 | Frente branca com cartões, letras/raposa douradas e QR/texto pretos | Branco, dourado, preto |
| 2 | Fundo verde, nervuras e língua lisa, tudo numa peça | Verde |
| 3 | Base com ranhuras, verde sobre friso dourado | Dourado e verde |

Todas as peças já estão orientadas. **Não separar os materiais da frente**
nem pousar cada relevo individualmente na mesa: formam uma única peça AMS.
O mesmo se aplica à base/friso do prato 3. Não é necessário colar letras,
módulos QR ou cartões individualmente. A montagem estrutural final tem três
peças: frente, fundo verde e base.

## Medidas finais do CAD

| Elemento | Medida |
| --- | --- |
| Conjunto montado, largura × profundidade × altura | **220 × 80 × 220 mm** |
| Base, incluindo friso | 12 mm de altura |
| Friso dourado | 1,2 mm de altura |
| Placa frontal, sem língua | 192 × 208 mm |
| Placa posterior, sem língua | 192 × 208 mm, deslocada para a direita |
| Placas com línguas, na impressão | 192 × 215,8 mm |
| Espessura estrutural das placas e línguas | 3,2 mm |
| Nervuras da placa verde | 1 mm de relevo, 1,25 mm de largura, passo 3,2 mm |
| Cartões brancos, unidos à frente | 76 × 91 mm, relevo 1 mm |
| Ambos os campos QR, incluindo margem branca | **64 × 64 mm** |
| Relevo preto e dourado da frente | 0,6 mm |
| Espessura máxima frontal, nos QR | 4,8 mm |

Os 220 mm são a altura **total montada**, não apenas a altura de uma placa.
As línguas entram na base, por isso não se somam por inteiro à altura final.
A frente e o fundo foram redimensionados/recompostos; os QR não foram reduzidos
globalmente. A base tem um recorte curvo suave no contorno frontal.

## Encaixes e teste antes das peças grandes

As duas placas entram de cima em ranhuras independentes e paralelas, com os
ombros apoiados no topo da base. As nervuras terminam no ombro; a língua
verde é lisa e fica escondida. A geometria deixa 1 mm entre o verso da frente
e as cristas das nervuras posteriores, evitando colisões.

| Encaixe | Proposta incorporada |
| --- | --- |
| Língua branca | 140 × 3,2 mm, inserção 7,8 mm |
| Ranhura branca | 140,6 × 3,6 mm, profundidade 8 mm |
| Língua verde | 160 × 3,2 mm, inserção 7,8 mm |
| Ranhura verde | 160,6 × 3,6 mm, profundidade 8 mm |
| Folga na espessura | 0,2 mm por lado |
| Folga nas extremidades | 0,3 mm por lado |
| Folga ao fundo | 0,2 mm |
| Material fechado abaixo das ranhuras | 4 mm |

Começar pelo **essencial-arcos-220-v1-amostra-encaixes.stl**: contém um bloco
com duas ranhuras e duas pequenas línguas/pegas, três sólidos separados, todos
já com faces planas na mesa. Importar numa placa nova, sem redimensionar, como
um conjunto de objetos no mesmo filamento. Usar 0,20 mm, sem suportes, o mesmo
material e a mesma orientação das peças finais. O teste verifica folga local;
não simula o empeno de uma placa inteira ou a retidão de uma língua longa.

Depois de imprimir o conjunto, arrefecer completamente antes de retirar da
mesa, sobretudo as placas grandes. Remover brim e resíduos do encaixe.
Montar a seco primeiro. Se entrar sem forçar e a disposição estiver correta,
usar pequenas quantidades de cola compatível com PLA para fixação definitiva.
Não forçar peças com cantos levantados ou ranhuras obstruídas. Ranhuras cegas
imprimem abertas para cima; não há pontes a tapar os encaixes.

## QR definitivos

- Instagram: https://www.instagram.com/clinicaessencial_setubal/
- Google: https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg

Foram reutilizadas as matrizes guardadas no projeto anterior, cujo destino
Google o utilizador já tinha confirmado. Google ECC M e Instagram ECC Q;
45 módulos incluindo margem de quatro módulos por lado, passo **1,422 mm**.
QR pretos, margem/fundo brancos, sem logótipos dentro dos códigos. Entre as
linhas pretas há separação geométrica de 0,02 mm para evitar contactos apenas
num vértice no STL; o menor traço nominal fica em cerca de 1,402 mm. Todas as
ilhas pretas ficam apoiadas na placa branca e unidas a ela na impressão.

Os dois campos foram descodificados a partir de secções dos **STL exportados**.
Foi também medida a cobertura dos módulos na camada superior do G-code:
amostragem na grelha conhecida, sem módulos divergentes, e descodificação das
grelhas resultantes. A imagem sintética bruta dos traços não foi descodificada
diretamente pelo OpenCV; a verificação da cobertura **não é uma simulação
ótica nem prova de leitura física**. Os relatórios distinguem esses resultados.

Testar os dois QR na primeira impressão, com iluminação e distâncias de uso,
antes de entregar ou repetir unidades. O formulário Google pode pedir login
ou mostrar uma avaliação já existente. A verificação local dos destinos não
constitui nova confirmação de disponibilidade dos serviços na Internet.

## Configurações de impressão

- **A1, bico 0,4 mm, camada 0,20 mm** incluindo a primeira.
- **Textured PEI Plate**, sem suportes. Perfis de mesa a 65 °C no PLA
  branco/verde/preto e 55 °C no Silk, tanto na primeira camada como nas restantes;
  confirmar compatibilidade com as bobinas e a temperatura escolhida pelo Studio
  no prato multicolor.
- Três paredes, 15% gyroid, cinco camadas de topo e cinco de fundo nas placas.
- Base: **quatro paredes, 25% gyroid, Classic**, como substituições no objeto
  da montagem do prato 3. A frente conserva **Arachne** para o texto/detalhes.
- **Order of walls: outer/inner**; exteriores 50 mm/s, interiores 100 mm/s;
  aceleração exterior 2000 mm/s². Topo monotónico 25 mm/s, aceleração 1000 mm/s².
- Primeira camada: paredes 20 mm/s, preenchimento 30 mm/s.
- Brim exterior de 3 mm, afastamento 0,15 mm; compensação de pé de elefante
  0,10 mm. Preservar escala 100% para manter os encaixes e a dimensão dos QR.
- Torre de purga configurada com 30 mm de largura; sem purgas no preenchimento
  ou nos suportes. Prato 1 com oito trocas, prato 2 sem trocas, prato 3 com uma.

| Slot lógico | Material | Bico | Limite volumétrico | Preço usado no cálculo |
| --- | --- | --- | --- | --- |
| 1 | PLA branco/marfim | 220 °C | 8 mm³/s | 13 €/kg |
| 2 | PLA verde-sálvia | 220 °C | 8 mm³/s | 16 €/kg, hipótese |
| 3 | PLA Silk dourado | 215 °C | 5 mm³/s | 20 €/kg, hipótese |
| 4 | PLA preto | 220 °C | 8 mm³/s | 16 €/kg, hipótese |

O perfil Silk usa o intervalo 190–220 °C referido anteriormente. Usar o perfil
adequado à bobina real; os outros perfis são Generic PLA, sem calibração de
fluxo específica medida neste ambiente. Só o prato 1 usa três cores; nenhum
prato excede quatro. As primeiras 16 camadas da frente completam o núcleo
branco antes de começarem os relevos coloridos. Os cartões brancos continuam
até 4,2 mm e os seus QR pretos terminam a 4,8 mm.

## Tempo e custo verificados no fatiador

| Prato | Tempo estimado | Material, com purgas/torre |
| --- | --- | --- |
| Frente decorada | 5 h 53 min | 116,41 g |
| Fundo verde nervurado | 6 h 20 min | 126,56 g |
| Base e friso | 5 h 48 min | 120,89 g |
| **Total** | **18 h 02 min** | **363,86 g** |

Total de filamento: **aproximadamente 5,60 €**, usando os preços da tabela.
Inclui torre/purgas e brim, não inclui amostra de encaixes, energia, cola,
trabalho, máquina, embalagem ou portes. O tempo de fatiamento substitui a
estimativa visual anterior de 10–16 h. Pode variar com o Studio e a máquina.

## Validações e limites

Corpos STL fechados; dimensões montadas confirmadas; 124 posições de inserção
sem colisões; contorno de contacto estático com margem projetada de cerca de
30 mm para o centro de gravidade estimado. Este cálculo pressupõe placas
maciças e uma fração média de massa na base, não é FEA nem ensaio de empurrão.
Não valida resistência, queda, estabilidade ao toque ou aderência da cola.

Exportação, reabertura e fatiamento pelo Bambu Studio oficial 02.08.02.61:
três pratos dentro da mesa, zero avisos de impressão, zero suportes gerados,
24/21/60 camadas. Malhas nativas comparadas com os STL por volume e inércia.
Os logs headless podem mencionar falta de Wayland; os resultados de fatiamento
foram verificados separadamente. Relatórios JSON e hashes estão incluídos.

O nome foi recomposto em Nimbus Roman e a raposa segmentada da fotografia de
referência; **não é um logótipo vetorial original exato**. O ficheiro original
vetorial permitiria uma substituição mais fiel sem alterar os encaixes/QR.

O pacote inclui o 3MF, seis STL por material/componente, a amostra de encaixes,
imagens, relatórios e **EssencialArcos220.py + geometry.json**. O script Fusion
recria corpos BRep num documento novo, mas não foi executado neste ambiente;
não é um F3D validado. A frente preta tem muitos perfis QR, pelo que a criação
no Fusion pode ser demorada. O 3MF é independente desse script.

Reprodução no checkout Build (os scripts do ZIP também dependem dos módulos
auxiliares do repositório, fontes e das matrizes guardadas na versão anterior):

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_essencial_arcos_220.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_essencial_arcos_220_3mf.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/verify_essencial_arcos_qr_gcode.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_essencial_arcos_220_3mf.py --package-only
```
