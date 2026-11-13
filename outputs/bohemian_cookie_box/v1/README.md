# Caixa Maria V1 — vinil plano, Freddie e Bohemian Rhapsody

[Prévia montada](images/conjunto-CAD.png) · [Face decorativa](images/face-vinil-CAD.png) · [Primeira camada real](images/primeira-camada-vinil-3cores.png)

Protótipo paramétrico para **seis bolachas Maria**, com corpo cilíndrico liso e tampa de rosca. A decoração não tem relevo: preto, roxo e dourado começam todos em **Z = 0**, contra o **PEI liso confirmado pelo utilizador**. A silhueta de palco é simplificada, inspirada na pose de Freddie Mercury; substitui o brasão de detalhe fino. O ponto central é dourado e fechado, não um furo passante.

## O que imprimir primeiro

1. Abrir [testes da rosca e acabamento](caixa-maria-v1-testes-A1-04-PEI-liso.3mf) como **projeto**. Prato 1: um macho e três fêmeas. As fêmeas têm **1 marca = 0,25 mm; 2 marcas = 0,30 mm; 3 marcas = 0,40 mm** de folga radial. São anéis baixos à escala real e usam a geometria da rosca final. No Bambu pode selecionar apenas a fêmea que pretende experimentar.
2. Imprimir a pequena amostra preta do prato 2 para avaliar as marcas circulares no seu PEI e filamento. O padrão concêntrico está confirmado nos percursos, mas o contacto com o PEI liso pode tornar as marcas muito discretas. Não se promete o brilho ou as ranhuras de um disco industrial.
3. Medir o diâmetro máximo de várias bolachas e a altura de uma pilha de seis, considerando o saco alimentar **fechado**. Atualizar os parâmetros antes da impressão final se as medidas não servirem.
4. Usar o projeto [vinil de três cores](caixa-maria-v1-vinil-3cores-A1-04-PEI-liso.3mf): prato 1 corpo preto, prato 2 tampa. Para corpo branco, usar o [projeto opcional de uma cor](caixa-maria-v1-corpo-branco-A1-04-PEI-liso.3mf), sem reimprimir o corpo preto.

A [alternativa com anéis tonais](caixa-maria-v1-aneis-tonais-A1-04-PEI-liso.3mf) acrescenta círculos de cinzento muito escuro, à mesma altura da face. São marcas gráficas de 0,45 mm de largura, não sulcos nem relevo. Esta alternativa usa quatro cores e mais purga. **A versão principal é a de três cores**, com os círculos feitos pelos percursos do próprio preto.

## Parâmetros provisórios

Editar `parameters.scad` e abrir `cookie_box.scad` no OpenSCAD; selecionar `part` para exportar. Os STL das cores têm a mesma origem e devem ser importados juntos como partes de **um só objeto**. Não centrar cada volume de cor separadamente.

| Parâmetro | Valor inicial |
|---|---:|
| `cookie_diameter` — diâmetro máximo da bolacha | 66 mm |
| `stack_height` — altura da pilha de seis | 39 mm |
| `cookie_radial_clearance` — folga por lado, incluindo espaço para saco | 2 mm |
| `top_clearance` — folga superior, incluindo o fecho do saco | 3 mm |
| `wall` / `base` — parede / fundo | 2 / 2,4 mm |
| `thread_radial_clearance` — folga radial da rosca | 0,30 mm |
| `thread_axial_clearance` — folga axial de cada flanco | 0,15 mm |
| `pitch` / `turns` — passo / voltas do filete macho | 3 mm / 1,25 |
| `thread_depth` — altura radial do filete | 0,8 mm |
| `label_diameter` — etiqueta | 44 mm |
| `color_depth` — espessura das regiões coloridas | 0,6 mm |

Resultados: **Ø70 × 42 mm úteis**, corpo liso Ø74 mm, topo da rosca Ø75,6 mm, tampa Ø80,2 mm e altura fechada 46,8 mm. As espessuras e folgas continuam ajustáveis. Os 3 mm superiores só servem se forem suficientes para o saco fechado; não representam uma medição real do conjunto.

A tampa encosta intencionalmente a sua face interior no rebordo do corpo, formando o batente axial. Não há sobreposição volumétrica nessa posição. O canal fêmea tem uma extensão de entrada até ao bordo para permitir o movimento; os 1,25 giros referem-se ao **filete macho útil**, não a uma garantia do número exato de voltas de abertura. Entradas chanfradas e flancos próximos de 41° em relação à vertical permitem preparar a peça sem suportes. O encaixe e o esforço de abertura ainda exigem ensaio físico.

## Impressão

- **A1, bico 0,4 mm, PLA, PEI liso**; cama a 55 °C. Camadas de 0,20 mm, três paredes, 20% gyroid, sem suportes nem brim. Compensação de pé de elefante: 0,15 mm.
- Corpo vertical; tampa **com a decoração contra o prato e a rosca para cima**. Os modelos já estão orientados. O texto aparece espelhado na primeira camada vista no prato e fica legível depois de virar a tampa.
- Preto com padrão inferior concêntrico; etiqueta e dourado com preenchimento inferior monotónico. Não há geometria de sulcos no preto da versão principal.
- AMS: **1 preto, 2 roxo, 3 dourado**; na alternativa, **4 cinzento muito escuro**. Confirmar o mapeamento dos rolos antes de imprimir. O projeto de corpo branco usa apenas o filamento 1 branco.
- Foi reutilizado o perfil guardado **Amazon Basics Silk PLA Gold 0.9702 @BBL A1 0.4**. Os restantes são Generic PLA. Se o dourado físico for outro material, escolher o perfil adequado; esta preparação não calibra um novo rolo.
- A face lisa não precisa de engomagem. Reduzir a camada para 0,12/0,16 mm não aumenta por si só a resolução XY das letras encostadas ao prato; o perfil fornecido privilegia primeira camada de 0,20 mm e traços compatíveis com o bico.

As previsões exatas de tempo, material e trocas estão em [estimativas](validation/estimativas.md). **Nenhuma impressão física foi iniciada.**

## Ficheiros e verificação

- `cookie_box.scad` + `parameters.scad`: fonte OpenSCAD editável e autónoma. A fonte DejaVu Sans Bold e a licença estão em `fonts/`; instalar a fonte se o OpenSCAD não a encontrar. Os STL/3MF já guardam as letras como geometria.
- `parameters.json`, `generate.py`, `build_bambu.py`, `export_step.py`: regeneração e validação automatizadas no checkout completo do repositório, com as dependências indicadas nos scripts. Alterar o JSON e executar `generate.py` também atualiza `parameters.scad`; não manter edições divergentes nos dois ficheiros.
- `stl/`: corpo, cores da tampa, versão monocor, testes e amostra preta. O ficheiro `tampa-preto-aneis.stl` é exclusivo da variante de quatro cores; não o misturar com o preto da versão principal.
- `step/`: geometria funcional para intercâmbio CAD. As paredes cilíndricas/cónicas são analíticas; a hélice usa faces amostradas. STEP não contém histórico paramétrico nem regiões de cor da face plana. A fonte editável continua a ser o OpenSCAD.
- `validation/`: solidez das malhas, equivalência com o OpenSCAD, colisões em posições sucessivas de enroscar/desenroscar, capacidade, reabertura dos projetos Bambu, estimativas e análise dos percursos. As imagens da primeira camada são reconstruídas do G-code efetivamente fatiado, não fotografias de uma impressão nem capturas da interface Windows.

Os modelos passaram as verificações digitais; **o ajuste às bolachas, o encaixe impresso e o acabamento do vinil não estão fisicamente validados**. O ficheiro OpenSCAD da sessão anterior não estava disponível; esta versão foi criada a partir do pedido, sem alegar a sua recuperação.

## Barreira alimentar e identidade gráfica

Usar um **saco ou liner removível, fechado e certificado para contacto alimentar**. As bolachas não devem tocar diretamente no PLA. As folgas reservadas precisam de acomodar também as dobras e o fecho da barreira. Não é proposta aplicação de verniz ou resina genérica; a caixa impressa não é apresentada como recipiente alimentar certificado nem como hermética.

Projeto para uso pessoal. Antes de uso comercial da identidade Queen, Freddie Mercury ou “Bohemian Rhapsody”, verificar os respetivos direitos.
