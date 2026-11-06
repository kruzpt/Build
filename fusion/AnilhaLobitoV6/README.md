# Anilha do lobito V6 — prioridade ao acabamento do rosto

Nova preparação de impressão da mesma geometria da V5, solicitada para
melhorar as linhas visíveis nas curvas e nas zonas superiores da face.
Mantém o corpo cinzento inteiro, as oito peças de cor, as costas planas e
os alojamentos para colagem.

- [Projeto Bambu A1 / AMS — 3 pratos](../../downloads/anilha-lobito-v6-rosto-alta-qualidade-A1-AMS-3-pratos.3mf)
- [Pacote do projeto e documentação](../../downloads/anilha-lobito-v6-rosto-alta-qualidade-pacote.zip)
- [Distribuição dos pratos](../../designs/anilha-lobito-v6-rosto-alta-qualidade-pratos.png)
- [Comparação dos percursos do focinho](../../designs/anilha-lobito-v6-rosto-alta-qualidade-comparacao.png)
- [Aspeto da geometria, conservada da V5](../../designs/anilha-lobito-v5-bochechas-continuas-CAD.png)

## Alterações de qualidade

| Definição | Corpo, prato 1 | Peças de cor, pratos 2 e 3 |
|---|---:|---:|
| Camada normal | 0,12 mm | **0,08 mm** |
| Primeira camada | 0,20 mm | 0,20 mm |
| Parede exterior | Até 30 mm/s | Até **20 mm/s** |
| Parede interior | 50 mm/s | 30 mm/s |
| Topo | Até 20 mm/s | Até **15 mm/s** |
| Padrão do topo | Monotonic line | **Concêntrico** |
| Largura nominal das linhas de topo | 0,42 mm | **0,36 mm** |
| Espessura mínima de topo solicitada | 0,72 mm | **1,0 mm**, 13 camadas solicitadas |
| Pequenos preenchimentos de lacunas | Perfil anterior | Até 15 mm/s |
| Aceleração exterior / topo | 800 mm/s² | **500 mm/s²** |

As paredes exteriores mantêm a largura anterior de 0,42 mm. A linha mais fina
foi aplicada ao preenchimento do topo; o Arachne pode adaptar larguras em
regiões estreitas. O interior das peças de cor passa a 800 mm/s² e as
velocidades em balanço são limitadas a 20 / 20 / 15 / 10 mm/s, com pontes a
20 mm/s. A primeira camada e as costas de colagem conservam a preparação
anterior. Não foi ativado ironing.

**Os valores do rosto estão aplicados por objeto.** No Bambu Studio, o painel
Global continua a mostrar 0,12 mm, correspondente ao corpo. Selecionar um
objeto do prato 2 ou 3, no modo Objetos, mostra o valor de 0,08 mm e as outras
substituições. Não substituir os perfis do projeto pelos valores globais.

## Porque melhora o topo

A redução de 0,12 para 0,08 mm diminui a altura de cada degrau em um terço.
Os anéis das curvas continuam a resultar das camadas; a sua textura não
desaparece completamente. O topo concêntrico acompanha os contornos dos
pequenos patamares e substitui os preenchimentos diagonais visíveis. A linha
nominal de topo de 0,36 mm permite traços mais finos nesses patamares.

A maior parte do arredondado exposto do focinho e dos olhos é formada por
paredes de camadas sucessivas. Por isso foram afinadas a altura de camada,
a velocidade exterior e a aceleração, além do padrão de topo.

Estas escolhas dão prioridade ao acabamento dentro da configuração **A1 com
nozzle de 0,4 mm**. O resultado físico continua a depender do filamento,
calibração e estado da máquina; a prévia não equivale a uma impressão lisa.

## Pratos e montagem

1. **Corpo cinzento**, de pé, 0,12 mm, com os apoios da V5.
2. **Olhos, focinho/bochechas e interiores das orelhas**, costas no prato,
   0,08 mm; branco/preto em AMS, sem apoios nas peças.
3. **Nariz e sobrancelhas**, costas no prato, 0,08 mm; preto, sem apoios.

Sem brim nos objetos. A torre de purga conserva a base própria e foi movida
mais para dentro do prato 2: Y=170 mm. As camadas mais finas aumentam a área
necessária por camada de purga; a nova posição foi verificada no fatiamento.
As peças mantêm as posições originais nos pratos.

Abertura oval 25 × 18 mm; corpo 30 mm, largura 42 mm; folgas dos alojamentos
0,18 mm por lado e 0,15 mm no fundo, como na V5. Se o corpo V5 já foi impresso,
pode ser reutilizado. Remover os apoios, fazer a montagem a seco e colar os
elementos nos alojamentos. O nariz cola no focinho.

Os filamentos continuam a ser os três PLA genéricos da V5, sem alterar
fluxo, temperaturas, retração ou arrefecimento. Mapear cinzento/branco/preto
para os filamentos efetivamente colocados no AMS e manter a calibração
dinâmica de fluxo no envio. Não aplicar os rácios do laranja ou do dourado
do projeto do tijolo a esta anilha.

## Estimativas do fatiador

| Prato | Tempo | Material com purgas e torre | Trocas de cor |
|---|---:|---:|---:|
| 1 | 2 h 31 min | 15.90 g | 0 |
| 2 | 3 h 48 min | 33.50 g | 53 |
| 3 | 0 h 14 min | 0.22 g | 0 |

Total: cerca de **6 h 33 min e 49,6 g**. O prato 2 passa de cerca de
2 h 13 min / 22,0 g na V5 para **3 h 48 min / 33,5 g** na V6.
As camadas adicionais aumentam as trocas branco/preto de 35 para 53;
o aumento de consumo vem sobretudo das purgas. As estimativas variam
com a versão do Bambu, os filamentos e as opções de envio.

## Verificação

- Todos os ficheiros de geometria e de transformações no 3MF conservados
  byte a byte. Não foi remodelada nenhuma superfície ou encaixe.
- Corpo conserva as configurações e os percursos das superfícies exteriores,
  interiores, topos, fundos e pontes da V5.
- Os três pratos são reabertos e fatiados no Bambu Studio **02.08.02.61**.
- G-code verificado para passo de camada de 0,12 / 0,08 / 0,08 mm, primeira
  camada de 0,20 mm, velocidades exteriores e de topo, materiais usados,
  ausência de apoios nas peças de cor e ausência de brim nos objetos.
- Os limites da máquina são verificados pelo fatiador, incluindo a torre.

Resultados e estimativas em `bambu-validation.json`. O projeto entregue é
editável, para voltar a fatiar no Bambu Studio. Nenhum trabalho foi enviado
à impressora. O acabamento e o encaixe físico desta versão precisam de ser
confirmados num exemplar.

## Reproduzir a preparação

Usa a geometria e o 3MF V5 já existentes no repositório:

```bash
python fusion/tools/build_anilha_lobito_v6.py --bambu-bin /caminho/bin/bambu-studio --work-dir /pasta/de/trabalho
```

Dependências: numpy, trimesh, Pillow e os auxiliares de preparação do
repositório. A variável `LD_LIBRARY_PATH` do script corresponde ao ambiente
Linux usado na validação e deve ser adaptada noutro ambiente. Os scripts não
executam Autodesk Fusion nem iniciam impressões físicas.

Os STL incluídos no pacote conservam os nomes V5, pois a geometria é a mesma;
para as novas configurações, abrir o projeto **V6 3MF**.
