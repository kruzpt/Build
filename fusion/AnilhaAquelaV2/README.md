# Aquelá V2 — lobo, folhas e anilha

A V1 substituiu indevidamente o lobo aprovado por outro desenho. Esta V2
recupera os contornos da referência: cabeça de perfil, focinho à direita,
sorriso aberto, pelo recortado, letras arredondadas, tabuleta irregular e
ramos de folhas. O nome foi corrigido para **Aquelá**, com acento no último a.

[Comparação da referência com o modelo real](../../designs/anilha-aquela-v2-comparacao.png)
· [Conjunto montado](../../designs/anilha-aquela-v2-CAD.png)
· [Três peças separadas](../../designs/anilha-aquela-v2-pecas.png)
· [Percursos gerados pelo Bambu Studio](../../designs/anilha-aquela-v2-percursos.png).

As imagens CAD representam a geometria exportada. A textura fotográfica de
pelo e madeira da ilustração não foi reproduzida integralmente: o modelo tem
relevo por alturas, pequenos biséis e alguns veios mais largos na tabuleta.
O relevo das folhas fica apenas na área exposta; a zona coberta pelo lobo é
plana para permitir a colagem. Não é uma escultura de superfícies orgânicas
idêntica à imagem de conceito.
Os pontos brancos dos olhos foram ligeiramente aumentados para se manterem
nos percursos do bico de 0,4 mm.

## Ficheiros para abrir como projeto no Bambu Studio

- [Lobo + tabuleta — A1, bico 0,4 mm, AMS, quatro cores](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v2-LOBO-A1-04-AMS-4-cores.3mf?raw=true).
- [Anilha e folhas — A1, bico 0,4 mm, dois pratos](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v2-ACESSORIOS-A1-04-2-pratos.3mf?raw=true).
- [Pacote com os dois projetos, STL e imagens](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v2-pacote.zip?raw=true).

Existem **três peças físicas**, apesar dos dois ficheiros de projeto. O lobo
e a tabuleta são impressos juntos como um objeto com quatro volumes de cor.
Não imprimir separadamente os STL de cores: as superfícies superiores dependem
da base preta. O STL `lobo-completo-monocor` serve como alternativa de uma só cor.
O GLB mostra o conjunto montado e não é um prato para imprimir.

| Peça | Medidas nominais | Cores |
| --- | --- | --- |
| Lobo + tabuleta | 55 × 65 × 4,88 mm | Preto, cinzento, castanho, branco |
| Folhas, uma peça | 62 × 48 × 2,96 mm | Verde |
| Anilha arredondada retangular | 29 × 22 × 25 mm | Castanho |
| Passagem interior da anilha | 25 × 18 mm, cantos arredondados | — |

## Impressão e montagem

1. Abrir o projeto do lobo como **projeto completo**, mantendo as quatro partes
   alinhadas. Mapear os quatro filamentos para os rolos reais.
2. Imprimir os dois pratos do projeto de acessórios: anilha castanha e folhas
   verdes. Cada prato usa uma única cor; o verde substitui um rolo livre do AMS.
3. Experimentar a passagem do lenço antes de colar. As dimensões foram
   verificadas no modelo; a folga com o lenço real ainda não foi testada.
4. Colar a face plana da anilha ao verso das folhas, centrada. Na montagem CAD,
   a base da anilha fica 9 mm acima da base das folhas.
5. Colar o verso plano do lobo à zona central lisa das folhas. Alinhar os centros
   e as bases das duas peças. A frente do lobo fica voltada para fora e a anilha
   permanece atrás, com a passagem do lenço na vertical.

Usar uma camada fina de cola compatível com PLA e fazer a montagem a seco
primeiro. Não há encaixes de pressão ou pinos; são faces planas para colagem.

Configuração: camada 0,12 mm, primeira camada 0,20 mm, Arachne, três paredes,
Gyroid 15%, seis camadas superiores, sem engomagem, sem suportes e sem brim.
A anilha usa quatro paredes e 30% de preenchimento. Paredes exteriores até
25 mm/s e topo até 18 mm/s. A costura está configurada para trás.

Os perfis de material são **Generic PLA**, com limite volumétrico de 8 mm³/s.
Não representam uma calibração do novo cinzento nem transferem a calibração
de outro filamento. Selecionar o perfil calibrado do rolo, se já existir.

## Verificação efetuada

- Malhas STL fechadas, com orientação consistente; lobo e folhas ligados às
  respetivas bases. Nenhuma cor começa suspensa sobre espaço vazio.
- As seis malhas de cor/peças conservam geometria, escala e posicionamento
  relativo na exportação 3MF. As cores cinzento e preto são distintas.
- Sem colisões volumétricas entre as três peças na montagem CAD.
- Exportação, reabertura e fatiamento no Bambu Studio **2.9.1.70** para A1
  com bico 0,4 mm. Os três pratos cabem na área útil, sem avisos de impressão.
- Revisão dos percursos de extrusão, incluindo movimentos em arco, materiais,
  alturas, velocidades de paredes/topo e ausência de suportes/brim.

Os resultados e estimativas exatas do fatiador estão em
`bambu-validation-lobo.json`, `bambu-validation-acessorios.json` e
`toolpath-review.json`; os hashes identificam os ficheiros verificados.
**Ainda não foi feita impressão ou montagem física.**

## Reprodução

Na raiz do repositório, com numpy, OpenCV, Pillow, trimesh e manifold3d:

```sh
python fusion/tools/generate_anilha_aquela_v2.py
python fusion/tools/build_anilha_aquela_v2_3mf.py --bambu-bin /caminho/bin/bambu-studio --work-dir /tmp/aquela-v2
python fusion/tools/check_anilha_aquela_v2.py --work-dir /tmp/aquela-v2
```

Os utilitários de geometria partilhados estão em `fusion/tools/`. A origem dos
contornos e o respetivo hash estão documentados em `geometry.json`.
