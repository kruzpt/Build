# M7 — Casa V7: acabamento branco contínuo antes da frase

Correção do problema visível no Preview da V6: a última camada branca
terminava antes de mudar para azul, mas ainda tinha pequenos perímetros
nas zonas das letras futuras. Confirmar só a ordem das cores e os tipos de
superfície não detetava essa fragmentação dos percursos.

## Causa e alteração

`Only one wall on top surfaces` estava em `Not apply` na parte branca,
mas a política do objeto completo da casa continuava a herdar `Top surfaces`.
O fatiador gerava perímetros internos associados aos contornos da frase.

Na V7 foi aplicada **ao objeto completo da casa** a substituição:

```text
top_one_wall_type = not apply
```

O perfil global e as configurações dos outros objetos foram preservados.
As malhas e transformações 3D são **byte a byte iguais às da V6**. Azul de
2 mm, branco de 4 mm, casa total 6 mm, frase 0,60 mm, altura montada 95 mm,
contornos alinhados e o ajuste inferior escondido da V5/V6 mantêm-se.
A base e o m/7 não foram redesenhados. O encaixe geométrico verificado
na V6 permanece aplicável; ainda não há ensaio físico desta revisão.

## O que foi verificado de forma adicional

V6 e V7 foram fatiadas no mesmo Bambu Studio 02.08.02.61. Os percursos da
última camada branca (Z=6 mm) foram transformados de volta às coordenadas
da casa e analisados na área ocupada pela frase.

- V6: **393 segmentos de perímetro interno**, além de percursos de topo.
- V7: **zero segmentos de parede na área da frase**, apenas percursos de topo.
- A figura de comparação mostra os percursos reais: azul para topo e vermelho
  para perímetros. É uma visualização do G-code, não uma foto de impressão.

Esta análise é mais específica do que a anterior, que verificava apenas se
havia preenchimento esparso/interno e se o branco terminava antes do azul.

Confirmadas também dez camadas iniciais azuis até Z=2,00 mm, acabamento
azul só nas quatro janelas, branco de Z=2,20 a 6,00 mm e frase azul de
Z=6,20 a 6,60 mm. A última superfície branca é Monotonic a 25 mm/s.
Mantêm-se **duas trocas: azul → branco → azul**.

## Imprimir

Abrir **m7-casa-v7-branco-continuo-A1-AMS-4-pratos.3mf como projeto**.
A1, bico 0,4 mm, PLA, PEI texturado, camadas de 0,20 mm. Slots 1 branco,
2 azul, 3 ciano. Sem suportes ou brim nos quatro pratos; torre de priming
ativa na casa. Corpo azul por baixo, branco e frase voltados para cima.
Não separar os corpos coloridos ou mudar as suas posições relativas.

| Prato | Conteúdo | Estimativa | Material incl. torre/purga | Trocas |
|---|---|---:|---:|---:|
| 1 | Casa unida azul/branco/frase | 2 h 03 min | 31.21 g | 2 |
| 2 | Base azul | 2 h 06 min | 40.75 g | 0 |
| 3 | m branco | 0 h 08 min | 0.21 g | 0 |
| 4 | 7 ciano | 0 h 08 min | 0.14 g | 0 |
| **Total** | | **4 h 26 min** | **72.31 g** | **2** |

Estimativas do fatiador, não tempos/pesos medidos. Se já tens base e letras
V2/V4/V5/V6, imprime apenas o prato 1. Abrir um projeto novo não conserva
alterações feitas apenas noutro projeto local; confirmar os perfis das bobinas
reais e voltar a fatiar após alterações.

O perfil global mantém o nome da V6, porque a alteração é uma substituição
no objeto da casa. Ao selecionar a casa inteira em Objects, `Only one wall
on top surfaces` deve estar em **Not apply**. Selecionar apenas a parte branca
não substitui essa política do objeto.

**Sem teste físico da V7.** Os percursos corrigidos deixam de desenhar os
contornos das letras no acabamento branco, mas podem continuar visíveis
linhas normais de impressão ou problemas de fluxo/retração do filamento.

## Conteúdo

3MF de quatro pratos, relatório, comparação de percursos, imagem dos pratos
e script de reprodução. Não foram gerados novos STL, porque a geometria é a
mesma da V6. Os STL e o script Fusion dessa versão continuam aplicáveis.
O script de reprodução depende do projeto V6 e dos auxiliares no checkout
Build; não executa o Fusion nem envia uma impressão para a máquina.

```sh
python fusion/tools/build_m7_house_finish_v7.py
python fusion/tools/build_m7_house_finish_v7.py --package-only
```
