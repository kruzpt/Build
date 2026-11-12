# Coroa de Natal personalizável — proposta V1

Estado: conceito visual para aprovação. Ainda não existe modelo de impressão, formulário funcional ou 3MF desta proposta.

[Imagem da proposta](../../designs/coroa-natal-personalizavel-v1-conceito.png)

## Objetivo e decisões confirmadas

Recomeçar a partir da fotografia fornecida pelo utilizador e aproximar o desenho o mais possível dessa referência: coroa aberta de folhas estreitas sobrepostas, contorno creme recortado, laço e bagas vermelhas, texto manuscrito vermelho com contorno creme. Não substituir o centro aberto por um disco ou usar uma placa retangular para o nome.

O utilizador confirmou nesta conversa:

- Diâmetro de 100 mm para a coroa, excluindo a argola.
- Personalização através de um formulário que gera um novo 3MF para abrir no Bambu Studio.

A imagem foi gerada como proposta estética; não é uma renderização de CAD, nem prova de medidas, resistência, montagem ou qualidade de impressão. A fonte original não foi identificada. A letra mostrada na proposta ainda terá de ser reproduzida através de uma fonte vetorial adequada e comparada visualmente antes da entrega.

## Dimensões e construção propostas

| Parâmetro | Valor | Estado |
| --- | --- | --- |
| Diâmetro exterior da coroa de folhas | 100 mm | Confirmado pelo utilizador; não medido na fotografia |
| Altura total com laço e argola | A determinar no desenho vetorial | Não confirmada |
| Espessura da coroa com relevo | Cerca de 3 mm | Proposta; validar no CAD |
| Espessura do conjunto texto + contorno | Cerca de 2 mm | Proposta; validar no CAD |
| Furo útil da argola | 3 mm | Proposta para fio fino |
| Número de peças para montagem | 2 | Proposta: coroa com laço e conjunto do texto |
| União | Colagem em zonas planas de contacto | Proposta; contactos por dimensionar |
| Cores | Creme, verde escuro, verde claro e vermelho | Proposta com quatro filamentos |

As espessuras são objetivos de desenho, não medidas extraídas da imagem. A espessura total montada dependerá da sobreposição nas zonas de colagem.

Proposta de preparação: um prato para coroa/laço/bagas, outro para o conjunto do texto em duas cores. Ambos os conjuntos terão a face traseira plana. Esta divisão permite imprimir coroas em série e variar só os nomes. Será possível avaliar posteriormente a colocação das duas peças no mesmo prato. A decisão final depende da geometria e do fatiamento; ainda não há estimativas de tempo ou material.

## Personalização dinâmica prevista

O formulário deverá permitir nome, segunda linha opcional e ano opcional. A alteração deverá regenerar a geometria, e não apenas trocar uma etiqueta no projeto:

1. Compor os caracteres com uma fonte incluída no projeto, preservando acentos, ligações e proporções.
2. Ajustar escala uniforme e posição à área disponível, com pré-visualização antes de exportar. Disponibilizar duas linhas para textos longos, sem comprimir as letras horizontalmente.
3. Recalcular o contorno creme a partir da nova forma das letras.
4. Garantir que nome, ano e acentos fazem parte de um conjunto imprimível, através da base creme e de ligações discretas quando necessárias.
5. Verificar contactos suficientes com a coroa para colagem. Um nome curto que não alcance a coroa exige rever a composição ou acrescentar ligações desenhadas; aumentar ou diminuir a fonte, por si só, não resolve esse requisito.
6. Bloquear a exportação ou indicar uma composição alternativa quando o texto ficar demasiado fino ou não houver união suficiente.
7. Gerar o 3MF com os volumes e cores separados para abrir no Bambu Studio.

O ficheiro exportado representa o texto escolhido nessa geração. A personalização automática será feita no formulário; não se promete que o editor nativo do Bambu Studio mantenha relações paramétricas entre o nome, o contorno e os contactos.

## Verificações antes de entregar o projeto final

- Aprovar a proposta estética e comparar a futura prévia vetorial/CAD com esta imagem e a fotografia original.
- Confirmar impressora, bico e materiais atuais antes de selecionar o perfil. A A1 com AMS usada anteriormente é contexto, não uma confirmação nova.
- Experimentar nomes curtos, longos, com acentos e em várias linhas; verificar ligações e espessuras mínimas.
- Verificar malhas, cotas, sobreposições de montagem e distribuição das cores.
- Abrir e fatiar o 3MF no Bambu Studio e inspecionar percursos, detalhes, encaixe no prato e trocas de cor. Sem brim por defeito, conforme preferência guardada.
- Distinguir validação digital de teste físico; entregar uma amostra antes de considerar o desenho validado para produção.

O passo seguinte é a aprovação visual desta proposta, segundo o fluxo de novas peças definido em [AGENTS.md](../../AGENTS.md). Não foram produzidos ficheiros STL/3MF finais nesta fase.
