# Clínica Essencial — placa QR e NFC

Projeto de uma placa de balcão para impressão 3D e edição no Autodesk Fusion.

## Ficheiros

- **[V4 — download com QR de 64 mm](downloads/essencial-fusion-v4-qr64.zip?raw=true)**
- [V4 — código Fusion](fusion/EssencialV4/EssencialV4.py)
- [V4 — esquema atualizado](designs/essencial-v4-qr64-esquema.png)
- [V4 — dimensões e impressão](fusion/EssencialV4/README.md)
- **[V3 Fast — download da versão otimizada](downloads/essencial-fusion-v3-fast.zip?raw=true)**
- [V3 Fast — código e indicação de progresso](fusion/EssencialV3Fast/EssencialV3Fast.py)
- [V3 Fast — instruções](fusion/EssencialV3Fast/README.md)
- **[V3 — dois QR, símbolos e etiquetas NFC encapsuladas](fusion/EssencialV3/EssencialV3.py)**
- [Download do pacote Fusion V3](downloads/essencial-fusion-v3.zip?raw=true)
- [V3 — esquema frontal](designs/essencial-v3-esquema.png)
- [V3 — instruções de pausa e montagem](fusion/EssencialV3/README.md)
- [Placa Fusion com QR Instagram integrado](fusion/EssencialV2Instagram/EssencialV2Instagram.py)
- [Download: Fusion + STL QR + imagem](downloads/essencial-fusion-instagram.zip?raw=true)
- [STL: pastilha QR independente](downloads/instagram-qr-51mm.stl?raw=true)
- [QR Instagram — imagem](designs/instagram-qr.png)
- [Instruções de impressão e contraste do QR](fusion/README-Instagram.md)
- [Script V2 — duas peças e nova coluna](fusion/EssencialV2/EssencialV2.py)
- [Instruções e medidas do encaixe V2](fusion/EssencialV2/README.md)
- [Download do pacote Fusion V2](downloads/essencial-fusion-v2.zip?raw=true)
- [Script Python para Fusion](fusion/EssencialDraft/EssencialDraft.py)
- [Como executar no Fusion](fusion/README.md)
- [Download do pacote Fusion](downloads/essencial-fusion-draft.zip?raw=true)
- [Desenho conceptual](designs/clinica-essencial-conceito-v1.png)
- [Download do desenho em ZIP](downloads/clinica-essencial-draft.zip?raw=true)

![Conceito inicial](designs/clinica-essencial-conceito-v1.png)

O desenho conceptual mostra a primeira proposta. O script inclui uma alteração
posterior: logótipo a prolongar-se para fora do canto superior esquerdo, com a
mesma espessura da placa. Por isso, a imagem não representa exatamente o CAD.

## Estado do draft

A **V4** aumenta os QR para 64 × 64 mm. A placa fica com 200 × 220 mm para
dar espaço aos símbolos, às zonas NFC e à coluna. Mantém a construção
otimizada dos QR, duas peças, as medidas da base/encaixe e a pausa após
Z=3,8 mm. Ambos os QR do esquema descodificam para os mesmos destinos.

A **V3 Fast** mantém a geometria da V3, mas gera os QR em duas extrusões
conjuntas em vez de 628 operações individuais. Inclui cálculo adiado dos
sketches e janela de progresso/cancelamento entre etapas. A igualdade dos
retângulos QR foi verificada; o tempo real no Fusion continua por confirmar.

A **V3** reorganiza a frente em duas linhas: Instagram/Google à esquerda,
respetivo QR no centro e símbolo contactless à direita. Não tem inscrições
“QR”/“NFC”. Mantém duas peças e inclui duas cavidades internas para etiquetas
NFC redondas de 25 mm, a inserir numa pausa após Z=3,8 mm. O E e as estrelas
foram redesenhados com curvas a partir da referência, sem barra central.
O logótipo é uma aproximação manual, não o vetor original. Consulte as
instruções antes de imprimir; ponte do teto, execução no Fusion e leitura
física ainda precisam de validação.

A variante **EssencialV2Instagram** inclui um QR funcional para
`https://www.instagram.com/clinicaessencial_setubal/`, em relevo e unido à
placa. O PNG e a projeção superior do STL foram descodificados para confirmar
o endereço; a impressão física e a execução da variante no Fusion continuam
pendentes. Use módulos pretos sobre fundo branco.

Placa de 180 × 220 × 5 mm, base separada, alojamento traseiro para etiqueta NFC
de 26 mm e zona reservada para QR. Na V2 sem Instagram, o QR não contém um endereço e a
etiqueta NFC tem de ser comprada e programada à parte. Letras são textos de
sketch, não sólidos para impressão. O logótipo é uma aproximação geométrica.

O utilizador confirmou que o script V1 executou no Fusion. A V2 substitui
os blocos por vértebras arredondadas com projeções curvas, tendo em conta um
bico de 0,4 mm. Cria duas peças, cada uma com um corpo sólido: placa e base.
A base tem uma ranhura de 5,5 mm para uma língua de 5 mm, com entrada alargada
e espaço no fundo. A V2 ainda precisa de execução no Fusion e teste físico
do encaixe; o draft não está validado para impressão final.

Os ficheiros entregues ficam neste repositório: scripts em `fusion/`, desenhos
em `designs/` e pacotes em `downloads/`.
