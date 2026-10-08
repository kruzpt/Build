# QR 3D — Instagram Clínica Essencial

Destino exato: https://www.instagram.com/clinicaessencial_setubal/

## Placa com QR integrado — continua a ter duas peças

No Fusion, adicione a pasta `EssencialV2Instagram` em **Utilities → Scripts
and Add-Ins → Scripts → + / Add** e execute. Cria um documento novo com a
placa V2 e base. O QR substitui o alojamento vazio por módulos em relevo,
unidos ao mesmo corpo da placa; a base continua a ser a segunda peça.

Este script contém a correção do arco da coluna. A geometria do QR é criada
em filas de retângulos; a geração pode demorar mais do que a V2.

Campo QR: 52 × 52 mm, incluindo margem branca de quatro módulos em cada
lado. Módulos: cerca de 1,156 mm, relevo de 0,6 mm. O QR ocupa x=17..69,
y=30..82 na placa. Não pinte nem decore a margem branca.
Os retângulos têm um recuo de 0,01 mm nas bordas para evitar contactos
geométricos degenerados; o padrão foi verificado após essa alteração.

## STL alternativo — pastilha independente

`instagram-qr-51mm.stl` é uma pastilha de 51,2 × 51,2 mm, cantos arredondados,
base de 0,6 mm e relevo preto de 0,6 mm (total 1,2 mm). Cabe no alojamento
de 52 mm da V2 anterior com 0,4 mm livres por lado, para colagem. Esta opção
acrescenta uma peça; não é necessária se usar o script com QR integrado.

Importe o STL no slicer em **mm**, sem redimensionar os eixos separadamente.
Use fundo branco e módulos pretos. Com camadas de 0,2 mm, imprima as primeiras
3 camadas em branco e mude para preto na primeira camada acima de z=0,6 mm.
Confirme a mudança na pré-visualização do slicer. O STL não contém cores.
A pastilha foi construída como um corpo fechado, unido, sem ilhas soltas.

## Impressão e contraste

O tamanho foi escolhido para bico de 0,4 mm: cada módulo tem cerca de 1,14 mm
na pastilha. Use camadas de 0,2 mm como ponto de partida e superfície mate.
Relevo numa única cor não assegura contraste suficiente para leitura.

Na placa integrada, QR, letras e marcador NFC estão na mesma altura de
relevo; uma mudança para preto nessa altura também colore esses elementos
e as camadas superiores da coluna. Para cores independentes, use pintura
cuidadosa ou atribuição de cores por regiões num slicer multimaterial.
Não passe tinta entre os módulos do QR.

## Verificações e limites

- PNG descodificado por OpenCV: endereço exato confirmado.
- Projeção superior reconstruída a partir do STL exportado: endereço exato
  confirmado, e cada módulo comparado com a matriz QR.
- STL fechado, orientação das faces consistente e um único sólido.
- Script Fusion: sintaxe verificada; execução desta variante ainda pendente.
- Leitura da impressão física: ainda pendente. Teste com o telemóvel antes
  de colar/entregar. A leitura depende do contraste e qualidade da impressão.

O QR abre o endereço diretamente; não depende de um serviço de QR dinâmico.
A geração/validação do código não confirma a disponibilidade do perfil no
Instagram. Para NFC, grave o mesmo endereço na sua etiqueta.

Regenerar os ficheiros: instale `fusion/tools/requirements-qr.txt` num venv
e execute `python fusion/tools/generate_instagram_qr.py`.
