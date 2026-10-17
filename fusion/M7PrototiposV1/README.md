# M7 — um protótipo da casinha e um do tijolo

Os dois projetos Bambu Studio têm **um exemplar de cada peça necessária**.
Abra os 3MF como projetos, conservando perfis, cores e orientação. Impressora:
**Bambu Lab A1, bico 0,4 mm, PLA, mesa PEI texturada**. Não redimensione as peças.

## Ficheiros principais

- `m7-casa-v1-A1-AMS-3-pratos.3mf`: casinha completa, três pratos.
- `m7-tijolo-v1-A1-AMS-4-pratos.3mf`: tijolo completo, quatro pratos.
- `m7-prototipos-v1-pacote.zip`: ambos os projetos, 12 STL, imagens reais,
  este guia, dados geométricos e script opcional do Fusion.

As imagens com `CAD` no nome mostram a geometria efetivamente fornecida,
incluindo a fonte manuscrita adaptada à impressão. As imagens conceptuais
anteriores continuam preservadas no repositório.

## Casinha — três pratos

| Prato | Conteúdo e filamento | Estimativa | Tempo |
| --- | --- | ---: | ---: |
| 1 | Fachada branca com frase azul; m branco separado | 16,81 g | 54 min |
| 2 | Base com dois apoios e fundo da janela, tudo azul | 53,77 g | 2 h 41 min |
| 3 | 7 ciano para colar | 0,10 g | 7 min |
| Total | | **70,69 g** | **3 h 42 min** |

Há **uma troca de cor no prato 1**, depois de terminar a espessura branca
de 4 mm. Os pratos 2 e 3 são monocromáticos. O m não exige uma troca adicional,
pois é uma peça branca solta no prato 1, impressa antes do relevo azul.

| Elemento | Medida real do modelo |
| --- | --- |
| Altura vertical montada | 95 mm |
| Base, largura × profundidade | 85 × 85 mm |
| Fachada, largura máxima × comprimento inclinado | 75 × 97,51 mm |
| Fachada branca / relevo azul | 4 / 0,6 mm |
| Fundo azul opaco da janela | 2 mm |
| Ranhura da base, medida perpendicularmente à fachada | 6,30 mm |
| Folga total nominal para as duas placas de 6 mm | 0,30 mm |
| Inclinação em relação à mesa | 70° |
| Base plana / espessura dos dois apoios traseiros | 6 / 4 mm |

A diferença entre 97,51 mm e 95 mm resulta da inclinação e do encaixe na
base. A largura de 75 mm inclui o beiral. A base tem um fundo de 2 mm por
baixo da ranhura. O fundo azul fica ligeiramente recuado do contorno branco,
com cerca de 0,8 mm de margem visual.

### Montagem da casinha

1. Retire os brims da fachada, da base e do fundo azul. Limpe apenas rebarbas;
   não lixe os contornos para mudar as dimensões.
2. Apresente o fundo azul encostado à traseira branca, tapando os quatro vãos.
   Experimente o conjunto na ranhura, deslizando na direção da inclinação.
   Deve entrar sem forçar ou fletir a fachada.
3. Cole o fundo à fachada com uma película fina de cola, fora dos vãos da
   janela. Mantenha o fundo alinhado e a margem branca uniforme.
4. Com a cola curada, volte a montar. Para uma oferta permanente, fixe o conjunto
   à ranhura e aos dois apoios traseiros com pouca cola. Há folga para montagem
   e colagem; os apoios não são presilhas elásticas.
5. Cole o m branco e o 7 ciano nos respetivos rebaixos na frente da base.

Experimente com o telemóvel real e a respetiva capa antes da apresentação.
Foram verificados modelos geométricos de 145 × 65 × 8, 165 × 80 × 14 e
180 × 90 × 17 mm e o equilíbrio estático ideal. A resistência, a aderência
à mesa e a estabilidade ao tocar no ecrã continuam por testar fisicamente.
Esta versão **não inclui um canal dedicado para o cabo de carregamento**.

## Tijolo — quatro pratos

| Prato | Conteúdo e filamento | Estimativa | Tempo |
| --- | --- | ---: | ---: |
| 1 | Corpo terracota com rebaixos, furos na vertical | 38,56 g | 3 h 09 min |
| 2 | Árvore e estrela, dourado silk | 0,62 g | 11 min |
| 3 | m e inscrição Natal 2026, branco | 0,19 g | 8 min |
| 4 | 7 ciano | 0,07 g | 7 min |
| Total | | **39,44 g** | **3 h 34 min** |

Todos os pratos são monocromáticos. A árvore, a estrela, o m, o 7 e a
inscrição são impressos deitados e colados depois. Não existe uma placa
inteira de decoração a cobrir a frente do tijolo.

| Elemento | Medida |
| --- | --- |
| Corpo, largura × profundidade × altura | 50 × 26 × 70 mm |
| Furos do corpo | 8, conforme o STL original |
| Profundidade dos rebaixos | 0,20 mm |
| Folga lateral nominal dos enfeites | 0,15 mm por lado |
| Espessura dos enfeites e letras | 1,20 mm |
| Folga reservada no fundo para cola | 0,05 mm |
| Largura da estrela | 24 mm |
| Traço da árvore / contorno aproximado da estrela | 2,2 / 1,35 mm |
| Largura total da inscrição | 34 mm |

A estrela ficou com 24 mm, ajustada durante a modelação para o logótipo
ficar dentro dela com separação do dourado. A árvore é uma única peça,
incluindo o topo, sem pequenos segmentos soltos.

O contorno do tijolo foi reconstruído a partir da secção do STL enviado,
conservando nervuras, dimensões e furos. A diferença geométrica calculada
antes dos rebaixos é inferior a 0,06 mm³ em cerca de 32 420 mm³, decorrente
da triangulação. O STL original não foi alterado.

### Colagem do tijolo

1. Faça uma montagem a seco dos enfeites nos contornos rebaixados.
2. Use muito pouca cola, aplicada com palito no verso das peças. A folga
   é de posicionamento e colagem; não se destina a um encaixe por pressão.
3. Retire a estrela do prato frio sem a dobrar. O silk é mais delicado em
   peças finas; não force as pontas durante a colagem.
4. A inscrição tem nove caracteres separados. Uma fita de pintor de baixa
   aderência no topo permite levantar as letras mantendo o espaçamento da
   impressão. Apresente-as aos rebaixos sem esticar a fita e retire-a depois
   de a cola ganhar resistência. Confirme primeiro que a fita não marca o PLA.

Não troque os m/7 entre os dois objetos: os tamanhos e os rebaixos são diferentes.

## Perfil de qualidade

- Camada de **0,20 mm**, cinco camadas superiores, quatro inferiores.
- Paredes Arachne, superfícies superiores em linha monotónica a **35 mm/s**.
- Três paredes e 15% gyroid no perfil geral; base da casa com quatro paredes
  e 20% gyroid. As paredes finas do tijolo ficam maioritariamente preenchidas
  pelos perímetros, independentemente dos 15% de infill.
- Primeira camada a 25 mm/s; limite volumétrico de 8 mm³/s no PLA normal.
- Brim de 3 mm nos corpos maiores, sem brim nas peças pequenas para colar.
- Suportes desativados e **ausência de trajetos de suporte verificada** nos
  sete pratos. Nenhuma peça depende de suportes removíveis.
- Dourado com **Generic PLA Silk, 215 °C, limite 5 mm³/s**, paredes exteriores
  a 35 mm/s e topo a 25 mm/s. Foi respeitado o intervalo 190–220 °C referido
  para o silk; se usar outra bobina, confira o intervalo do fabricante.

As estimativas são do Bambu Studio oficial **02.08.02.61**, com os perfis
incluídos. Os tempos dos pratos, arredondados individualmente, podem não somar
exatamente o total. Confirme o mapeamento das bobinas no AMS em cada projeto.
Um projeto usa branco/azul/ciano e o outro terracota/dourado/branco/ciano;
não é necessário ter as cinco cores carregadas ao mesmo tempo.

## Validação e edição

Os 12 STL foram verificados como malhas fechadas com orientação consistente.
A árvore, a estrela e cada m/7 são peças únicas; as letras da inscrição são
independentes. Foram verificadas 86 posições no percurso de montagem da
casinha, sem colisão com a base, e três casos de equilíbrio estático ideal.
Os dois projetos foram exportados, reabertos e fatiados pelo Bambu Studio,
sem avisos do fatiador. As massas e os percursos resultam desses ficheiros.

`bambu-validation-casa.json`, `bambu-validation-tijolo.json` e
`geometry-validation.json` guardam os resultados. Os 3MF entregues são
projetos editáveis; o G-code de verificação não foi incluído como ficheiro
pronto para enviar à impressora.

O logótipo m7 foi interpretado geometricamente a partir da referência visual
fornecida. Não foi usado um vetor oficial da marca. Compare a aparência nas
imagens CAD e no primeiro exemplar antes de produzir uma série.

Para editar no Fusion, copie a pasta completa `M7PrototiposV1`, com
`M7PrototiposV1.py` e `geometry.json`, para os scripts do Fusion e execute.
O script cria um documento novo, com os dois objetos montados lado a lado,
componentes por cor e operações de extrusão/união/corte. A sintaxe foi
verificada; a execução no Fusion ainda não foi testada. Os 3MF e os STL
não dependem da execução desse script.

Estes ficheiros destinam-se aos **primeiros protótipos físicos**: a impressão
real, as folgas da sua máquina e a colagem serão confirmadas com estes exemplares.
