# M7 — tijolo V4, com o 7 extraído do STL original

Esta versão usa o próprio 7 do ficheiro **`Tijolos cr.stl`** enviado pelo
utilizador. O contorno foi separado da placa antiga por uma secção da malha,
sem redesenhar ou suavizar o símbolo. Conserva as irregularidades do traço e
os dois recortes interiores que existem nesse STL.

O 7 foi reduzido com a mesma escala nas duas direções: **40,050%**.
Passa de aproximadamente 13,26 × 18,10 mm para **5,31 × 7,25 mm**, mantendo
as proporções. A espessura foi adaptada a 1,20 mm para a montagem atual.
A estrela continua com 30 mm e o corpo com 50 × 26 × 70 mm.

## Ficheiros e peças a imprimir

Abra **`m7-tijolo-v4-A1-AMS-4-pratos.3mf` como projeto** na Bambu A1,
bico de 0,4 mm. O projeto inclui quatro pratos, cada um de uma só cor:

1. Corpo do tijolo em terracota, com os oito furos na vertical.
2. Árvore e estrela em dourado.
3. m e “Natal 2026” em branco.
4. 7 original em ciano.

**Se já imprimiu a V2 ou V3, substitua apenas o corpo do tijolo e o 7.**
A estrela, o m, a árvore e a inscrição são cópias binárias dos STL anteriores
e podem ser reaproveitados. O corpo precisa de ser substituído porque o
rebaixo do novo 7 tem um contorno diferente. A casinha continua na V1.

Os recortes interiores do 7 são vazios: depois de colado, mostram o
terracota do tijolo. Não correspondem a uma impressão adicional em branco.

## Encaixe e colagem

Os enfeites continuam separados para colar, sem uma placa inteira na frente.
O rebaixo do 7 foi atualizado para o contorno extraído:

| Medida | Valor |
| --- | --- |
| Profundidade do rebaixo | 0,20 mm |
| Folga lateral por lado | 0,15 mm |
| Folga de fundo para cola | 0,05 mm |
| Espessura dos enfeites | 1,20 mm |
| Saliência final sobre a frente | 1,05 mm |

Faça primeiro uma montagem a seco. Retire rebarbas e use pouca cola no
verso, aplicada com um palito, sem forçar os símbolos nos rebaixos. Deixe
arrefecer os enfeites antes de os retirar da mesa, sobretudo a estrela silk.
A inscrição mantém os nove caracteres separados.

## Qualidade e limites da impressão

O perfil conserva camada de 0,20 mm, três paredes, preenchimento gyroid de
15%, cinco camadas superiores, quatro inferiores, paredes Arachne e topo
monotónico a 35 mm/s. O dourado usa Generic PLA Silk a 215 °C, limite de
5 mm³/s, parede exterior a 35 mm/s e topo a 25 mm/s. Os outros PLA usam
limite de 8 mm³/s. Confirme as bobinas atribuídas no AMS antes de imprimir.

O projeto foi exportado, reaberto e fatiado no Bambu Studio oficial
02.08.02.61: quatro pratos sem avisos, sem suportes e sem trocas de cor
durante a impressão. Estimativa do conjunto: **39,5 g e 3 h 34 min**,
com os perfis incluídos.

O STL preserva o contorno original. À escala final, o bico de 0,4 mm
arredonda as irregularidades mais pequenas e altera a largura de alguns
recortes. A imagem `m7-tijolo-v4-fatiador.png` compara o STL com uma
reconstrução dos percursos da última camada, incluindo linhas, arcos e as
larguras indicadas no G-code. Não é uma fotografia da peça nem uma simulação
física do fluxo de plástico. A impressão física e a colagem ainda não foram
testadas nesta versão.

## Origem e verificações

`source-seven.json` guarda apenas os contornos extraídos do 7, o SHA-256
do STL enviado e a transformação de eixos. A placa antiga completa não é
incluída. A extração corresponde ao plano X = −0,50 mm do original; foram
comparadas outras quatro secções entre X = −0,10 e −0,90 mm para confirmar
que a silhueta se mantém através da espessura.

`geometry-validation.json` regista a escala uniforme, a comparação do STL
exportado com o contorno extraído, as malhas fechadas, colisões, 105 posições
de inserção e a identidade das quatro peças reutilizáveis.
`bambu-validation-tijolo.json` regista o projeto, o checksum e o fatiamento.

As imagens disponíveis são:

- `m7-tijolo-v4-comparacao.png`: V3, contorno original extraído e V4,
  apresentados à mesma altura para comparar a forma.
- `m7-tijolo-v4-CAD.png`: modelo montado e detalhe do logótipo.
- `m7-tijolo-v4-fatiador.png`: STL e percursos da última camada.
- `m7-tijolo-v4-pratos.png`: disposição das peças nos quatro pratos.

## Edição e reprodução

O pacote ZIP contém o 3MF, seis STL, imagens, relatórios e a pasta
`M7TijoloV4`. Para editar no Fusion, mantenha `geometry.json` ao lado de
`M7TijoloV4.py` e execute o script, que cria um documento novo. A sintaxe
foi verificada; a execução no Fusion não foi testada. O 3MF e os STL não
dependem da execução desse script.

No repositório, `fusion/tools/generate_m7_brick_v4.py` reconstrói a geometria
a partir do contorno guardado. O argumento opcional `--source-stl` refaz a
extração do STL fornecido. `fusion/tools/build_m7_brick_v4_3mf.py` exporta,
reabre, fatia, compara os percursos e verifica o pacote.
