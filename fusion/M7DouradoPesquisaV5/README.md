# Dourado — pesquisa e revisão dos percursos

Material confirmado pela fotografia da etiqueta: **Amazon Basics Silk PLA,
Gold, 1,75 mm**, com bico **190–220 °C**. Os 215 °C usados são admissíveis;
a etiqueta não demonstra que a temperatura seja a causa das acumulações.

## Fontes consultadas em 06/11/2026

1. [OrcaSlicer #13917 — Duplicate extrusion of thin outer walls with Arachne](https://github.com/OrcaSlicer/OrcaSlicer/issues/13917).
   Relato técnico em Orca 2.4.0-alpha/X1C de deposição duplicada em paredes
   estreitas. Os comentários incluem um exemplo simplificado, análise das
   coordenadas e relações entre larguras interior/exterior. O autor relata
   não conseguir reproduzir a duplicação com uma parede. Foram discutidos
   ajustes de larguras e uma correção no código. É outro programa/versão e
   outra geometria: não demonstra que a árvore no Bambu tenha esse mesmo bug.
   Não foi usado o relatório de IA anexado ao tópico como fonte técnica.
2. [PrusaSlicer #8405 — Overextrusion on small tool paths in painted objects](https://github.com/prusa3d/PrusaSlicer/issues/8405).
   Relato em Prusa 2.4.2/Toolchanger. Foram sugeridos desativar a deteção de
   paredes finas e ajustar largura exterior; a melhoria descrita inicialmente
   era no fatiador. O próprio autor questionou se isso explicava as bolhas
   físicas. O tópico também considera retração em troca de ferramenta e a
   introdução do Arachne. Não é uma receita validada para a nossa A1. A
   deteção de paredes finas já estava desativada no nosso perfil.
3. [PrusaSlicer #7949 — Duplicate center perimeter generated for 3 perimeter wall](https://github.com/prusa3d/PrusaSlicer/issues/7949).
   Relato antigo de centro impresso duas vezes. Discutem deteção de paredes
   finas e um gerador posterior. Reforça a necessidade de examinar o G-code,
   não prova duplicação no nosso caso.
4. [Bambu Studio #12532 — Slicer leaves hanging filament that gets caught on nozzle](https://github.com/bambulab/BambuStudio/issues/12532).
   Caso em H2D/Bambu 2.8.2.61, inicialmente associado a Silk, também observado
   noutro material. A investigação posterior relaciona-o com zonas coloridas
   sem material suficiente por baixo. A nossa árvore assenta numa base
   laranja sólida e o teste já reproduziu o defeito sem branco/ciano. Não
   justifica aplicar a solução desse caso ao nosso projeto.

Os relatos são evidência de mecanismos possíveis e de abordagens de
investigação, não soluções universais. As wikis oficiais Bambu/Prusa e a
pesquisa Google não puderam ser lidas: o proxy deste ambiente devolveu 403.
Os tópicos acima foram efetivamente lidos no GitHub, permitido pela rede.
Não se apresenta como consultada a documentação que ficou bloqueada.

## Verificação na nossa árvore

Foram comparados 1, 2, 3 e 5 perímetros em Arachne e uma variante com uma
parede/topo concêntrico. Uma parede remove os contornos interiores; o topo
concêntrico preenche a região restante e, nesse fatiamento, evita o
preenchimento de lacunas. As camadas internas continuam a precisar de
preenchimento sólido; o número de paredes muda a estratégia, não a malha.

Também se procuraram sobreposições de centros de extrusão na última camada
da amostra C anterior: **389 segmentos examinados**, sem candidatos segundo
os limites em `duplicate-check.json`. O teste compara cordas quase
colineares, não a cobertura física completa das linhas, e não cobre todas
as camadas. Não confirma o bug referido nos tópicos externos nem exclui
sobreposição da largura dos cordões ou problemas nos arranques.

## Próximo teste prioritário

[Prato V5 — 5, 3, 2 e 1 parede](../M7DouradoParedesV5/README.md), com velocidade
uniforme de 25 mm/s, temperatura de 215 °C, fluxo 0,9702, topo concêntrico e
as mesmas restantes condições entre amostras. Nos preenchimentos novos,
a velocidade é limitada a 25 mm/s para manter a comparação uniforme.

Este teste é preferível agora a alterar simultaneamente paredes e temperatura.
A cópia a [205 °C](../M7DouradoTemperaturaV4/README.md) está preparada como ramo
separado: conserva a matriz de velocidades V3 e cinco paredes. Não misturar
os resultados dos dois planos como se só variasse um parâmetro.

Não há ainda um resultado físico da opção de uma parede. O fatiamento
verificado não garante eliminar as marcas.
