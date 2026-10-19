# M7 — Casinha V2, logótipo original e encaixes profundos

Revisão da casinha V1: substitui a interpretação anterior do **m** e do **7**
pelos contornos extraídos do mesmo STL usado no tijolo V4/V5. Escala uniforme
e posição relativa original preservadas; não são caracteres de uma fonte.

A fachada branca, a frase azul «O que fazemos / mostra quem somos», o fundo
da janela, os apoios, a inclinação e os encaixes principais conservam o desenho
V1. Os três STL da fachada, frase e fundo são cópias byte a byte dos antigos.

## O que imprimir

- **Projeto completo:** `m7-casa-v2-A1-AMS-3-pratos.3mf`, seis componentes,
  mesma organização em três pratos da V1.
- **Só peças novas:** `m7-casa-v2-substituicao-A1-AMS-3-pratos.3mf`, apenas
  **m branco, base azul e 7 ciano**, um prato de cada cor. Serve para reutilizar
  a fachada e o fundo já impressos. Todos os pratos são monocromáticos.
- **Teste pequeno opcional:** `m7-casa-v2-amostra-logo.stl`, recorte da frente
  da base com os novos encaixes. Imprime com as cavidades abertas para cima;
  testar com as mesmas letras V2 antes de imprimir a base inteira.

Abrir o 3MF **como projeto**, preservando escala, cores, perfis e orientação.
A1, bico 0,4 mm, PLA, PEI texturada. Não redimensionar o logótipo no fatiador:
a base e as letras são peças correspondentes. Base/m/7 V1 não têm os mesmos
contornos e profundidades dos V2, por isso devem ser substituídos em conjunto.

## Guias e espaço para cola

| Elemento | V2 |
| --- | --- |
| Largura total do logótipo | 18 mm |
| Profundidade principal dos rebaixos | **0,80 mm** |
| Folga lateral nominal | **0,20 mm por lado** |
| Espessura total de cada letra | **1,80 mm** |
| Parte nominal embutida | **0,65 mm** |
| Relevo visível | **1,15 mm** |
| Espaço para cola no fundo principal | **0,15 mm** |
| Reservatório interior adicional | **0,30 mm**, total 1,10 mm abaixo da face |
| Recuo dos reservatórios em relação às letras | 0,35 mm |

A parte posterior das letras entra mais profundamente do que na V1 e o contorno
do rebaixo ajuda a alinhar. Os reservatórios são recortes menores no interior
do fundo das cavidades, deixando uma faixa de apoio periférica. Junto aos
contornos mais próximos do m/7, as folgas das cavidades podem comunicar;
preservou-se a posição relativa do logótipo em vez de afastar as letras.

As reservas adicionais são pequenas: cerca de 13 mm³ no m e 6 mm³ no 7,
além da folga principal. **Não dispensam controlar a cola** nem garantem que
uma gota inteira não saia. Apresentar primeiro sem cola; a letra deve entrar
sem ser forçada. Aplicar pouca cola com um palito/ponta fina no reservatório,
evitando as bordas, e assentar suavemente. A cola e a força aplicada não foram
testadas fisicamente. Não encher a cavidade até ao topo nem usar o encaixe
como prensa. Se houver rebarbas/primeira camada alargada, removê-las antes
de testar, sem alterar a silhueta original do logótipo.

## Dimensões e impressão conservadas

Altura montada 95 mm, base 85 × 85 mm, inclinação de 70°. Fachada de 4 mm,
frase de 0,6 mm em relevo e fundo azul de 2 mm. A ranhura principal de 6,30 mm
e os apoios da fachada não foram alterados. Não se acrescentou canal de cabo.

Camadas de 0,20 mm, três paredes (base com as quatro paredes/20% gyroid já
previstos na V1), Arachne, topo monotónico, cinco camadas de topo e quatro de
fundo. Exteriores 60 mm/s, interiores 130 mm/s, topo 35 mm/s; primeira camada
25 mm/s nas paredes e 40 mm/s no preenchimento. Brim exterior de 3 mm nas
peças estruturais, afastamento 0,15 mm, compensação de pé de elefante de
0,10 mm. Sem suportes. Filamentos Generic PLA A1 branco, azul e ciano,
bico 220 °C e limite volumétrico de 8 mm³/s; adequar à bobina/calibração real.

O projeto completo mantém a fachada com frase azul no prato 1, junto do m
branco; base e fundo azul no prato 2; 7 no prato 3. Há uma troca de cor no
prato 1 completo, depois da espessura branca; no projeto de substituição não
há trocas de filamento, porque só se imprime o m nesse prato.

| Projeto | Tempo estimado | Material |
| --- | --- | --- |
| Completo | Cerca de 3 h 44 min | 70,86 g |
| Só base + m + 7 | Cerca de 2 h 25 min | 41,32 g |

Incluem preparação e consumo previstos pelo Bambu Studio; não incluem o teste
opcional, cola ou trabalho de montagem. Os valores exatos estão nos relatórios.

## Validação e ficheiros

Malhas fechadas, contornos do logótipo confirmados após exportação, 82 posições
de entrada das letras verificadas sem colisões. Ambos os projetos foram
exportados/reabertos/fatiados no Bambu Studio oficial 02.08.02.61, sem avisos
de impressão nem suportes. O projeto de substituição foi verificado com um
único objeto por prato. Estas verificações não substituem a montagem a seco,
o teste de cola e o ensaio com o telemóvel real.

O pacote tem os dois 3MF, seis STL principais, o teste pequeno, desenhos,
relatórios e `M7CasaV2.py + geometry.json` para recriar corpos BRep num novo
documento Fusion. O script Fusion não foi executado neste ambiente e não
se fornece F3D validado. Os 3MF funcionam independentemente do Fusion. Os
scripts de geração incluídos dependem dos módulos auxiliares e dos contornos
originais já guardados no checkout Build.

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/generate_m7_house_v2.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_m7_house_v2_3mf.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_m7_house_v2_3mf.py --package-only
```
