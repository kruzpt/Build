# M7 Casa V3 — teste de acabamento da fachada

Projeto independente para imprimir apenas a fachada branca com a frase azul
«O que fazemos mostra quem somos». Não inclui a base, o fundo, o m ou o 7.
Pode substituir a fachada V1/V2 sem mudar os encaixes ou as dimensões.

## Abrir no Bambu Studio

Abrir `m7-casa-v3-fachada-A1-AMS-1-prato.3mf` como **projeto**, mantendo os
parâmetros nele guardados. A1, bico de 0,4 mm, PLA, prato Textured PEI.
Filamento 1 branco; filamento 2 azul. O terceiro perfil de filamento herdado
não é utilizado por nenhuma peça deste prato.

Imprimir com as letras voltadas para cima. Não imprimir apenas o STL, pois
perderia estes parâmetros e a atribuição das duas cores.

## O que muda neste teste

Alterações aplicadas à parte branca, sem alterar a geometria ou a frase azul:

| Opção em inglês | V2 | V3 |
| --- | --- | --- |
| Top surface pattern | Monotonic line | Monotonic |
| Top surface speed | 35 mm/s | 25 mm/s |
| Only one wall on top surfaces | Top surfaces | Not apply |

`Avoid crossing wall` / `reduce_crossing_wall` ativado no objeto da fachada.
O padrão Monotonic liga mais percursos consecutivos; evita a estratégia de
linhas isoladas usada antes. Manter três paredes também nas superfícies de
topo evita mudanças no número de paredes junto das zonas de acabamento.
Não significa imprimir o topo sem interrupções: a janela e os contornos
continuam a exigir deslocações.

Mantidos: camadas de 0,20 mm, primeira camada de 0,20 mm, cinco camadas de
topo (1 mm), preenchimento gyroid 15%, três paredes, aceleração de topo
2000 mm/s², fluxo e temperaturas anteriores. Não foi aplicada uma correção
de fluxo não calibrada.

`Interface shells` permanece ativado, para que o branco termine também sob
as letras. `Flush into objects' infill`, `Flush into this object` e
`Flush into objects' support` permanecem desativados. Torre de purga ativa.
`Ironing` permanece desligado. Sem suportes.

## O que a validação confirmou

O projeto V2 **já concluía todo o branco antes de começar o azul**. A troca
de cor não ocorre na camada de acabamento branca. O teste não deve ser
apresentado como uma correção de cores misturadas nessa camada.

Foram fatiados a fachada V2 isolada e o novo projeto no Bambu Studio oficial
02.08.02.61. Nos dois casos, a última extrusão branca da peça está em Z=4,00 mm;
a primeira extrusão azul da peça está em Z=4,20 mm. A camada branca final tem
percursos de topo, sem preenchimento interno ou esparso. A análise exclui a
torre de purga, a limpeza e a preparação da máquina.

O novo G-code confirma a velocidade de acabamento de 25 mm/s. Sem avisos,
sem percursos de suporte e com uma única troca de filamento. Os vértices e
triângulos imprimíveis são exatamente iguais aos da fachada e frase V2.
Consultar `bambu-validation.json` para tempos e consumo estimados.

**A melhoria visual ainda não foi confirmada numa impressão.** Linhas do
bico podem continuar visíveis, especialmente com luz rasante. Esta versão
é um teste de percursos e velocidade, específico desta fachada, não uma
regra para todos os projetos nem uma garantia de eliminar as marcas.

## Reprodução

No checkout do repositório, com Python, numpy, trimesh e Pillow disponíveis:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_m7_house_facade_v3.py
```

O script usa os módulos auxiliares existentes em `fusion/tools/` e o 3MF V2
como origem. Requer Bambu Studio oficial e as suas bibliotecas de execução.
Aceita `--bambu-bin` e `--work-dir` para selecionar outras localizações.
O projeto entregue é editável e não contém G-code previamente fatiado;
o Bambu Studio volta a fatiá-lo com os perfis incluídos.
