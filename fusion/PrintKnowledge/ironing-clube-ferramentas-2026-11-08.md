# Engomagem / ironing — referência e aplicação futura

**Registado:** 08/11/2026.

**Canal:** [Clube das ferramentas](https://www.facebook.com/clubedasferramentas/).

**Vídeo:** “Melhorando a superfície do seu objeto!” — aproximadamente 1 min 38 s.

**Ligação enviada:** https://www.facebook.com/share/v/14xkhwwXdWg/

**Reel identificado:** https://www.facebook.com/reel/1359701022222209/

## Observado no vídeo

O autor compara amostras com diferentes acabamentos e demonstra a opção
**Ironing** no Bambu Studio. O quadro final, aproximadamente aos 95–97 segundos,
mostra estes valores:

| Campo do Bambu Studio | Valor mostrado |
| --- | --- |
| Ironing Type | Top surfaces |
| Ironing Pattern | Rectilinear |
| Ironing speed | **60 mm/s** |
| Ironing flow | **20%** |
| Ironing line spacing | **0,15 mm** |
| Ironing inset | **0,21 mm** |

Estes são os valores da demonstração, não uma calibração nossa. Não foram
estabelecidas com segurança a marca do material, a calibração de fluxo de base
e todas as condições da impressão das amostras apresentadas.

## Princípio e distinções importantes

A engomagem acrescenta percursos de acabamento sobre superfícies superiores
planas, usando o bico quente e uma pequena quantidade de extrusão para reduzir
as marcas entre linhas. Acrescenta tempo e requer uma superfície de topo bem
formada; o resultado depende do material e da combinação dos parâmetros.

- Os **20% são o fluxo da passagem de engomagem**. Não substituem o fluxo
  calibrado do filamento laranja, que continua em **0,931**.
- É uma definição do **processo/objeto**, não um parâmetro a ativar em todos os
  perfis permanentes de filamento.
- `Top surfaces` e `Topmost surface` abrangem áreas diferentes em modelos com
  vários níveis. Confirmar no G-code quais as faces que serão tratadas.
- A função atua no topo virado para cima durante a impressão. A face encostada
  ao prato recebe o acabamento do prato.
- Não corrige de forma geral os degraus de uma superfície curva. Nesses casos,
  a altura de camada e a orientação continuam a ser escolhas fundamentais.
- A combinação deve ser afinada para evitar acabamento irregular, marcas do
  bico ou material acumulado junto das arestas. Em materiais silk, avaliar
  também a alteração de brilho.

## Aplicação proposta às nossas peças

| Peça / material | Interesse e condição |
| --- | --- |
| Base/placa laranja M7 | Bom candidato numa face plana impressa para cima; conservar o fluxo 0,931. |
| Base do QR / Clínica Essencial | Bom candidato na face plana visível, verificando a orientação invertida de impressão do projeto. |
| Dourado silk | Testar separadamente; avaliar brilho e uniformidade além da textura. |
| Rosto arredondado do lobito | Benefício limitado para as curvas; não substitui camadas finas/adaptativas. |
| Gallardo / TOMAS | Benefício provavelmente reduzido nos traços estreitos; não é a prioridade atual. |

É uma etapa de acabamento a avaliar depois das melhorias de fluxo e percursos
que já fizemos. Não substituir automaticamente a solução em linhas que melhorou
a árvore dourada e os restantes relevos.

## Estado da verificação

- **Fonte:** vídeo analisado visualmente; parâmetros do quadro final confirmados.
- **Projetos consultados:** M7 V9, base Essencial V6, lobito V6 e Gallardo V4
  guardavam globalmente `ironing_type = no ironing` na data desta análise.
- **Novo teste de engomagem gerado:** não.
- **Impressão física com estes valores nos nossos materiais:** não realizada.
- **Alterações aos projetos/perfis existentes por causa desta dica:** nenhuma.

## Próximo teste proposto, ainda não criado

Duas amostras pequenas de geometria e material iguais:

1. Referência sem engomagem.
2. Engomagem com 60 mm/s, 20%, espaçamento 0,15 mm e inset 0,21 mm.

Conservar o laranja calibrado, bico, camada, temperatura, orientação e restantes
parâmetros para uma comparação útil. Comparar o centro, as arestas, a textura,
o brilho e o tempo adicional. Se necessário, uma fase posterior compara outra
combinação de velocidade e fluxo, sem alterar vários fatores sem registo.

A indicação de guardar esta informação não foi tratada como autorização para
criar ou imprimir esse ensaio.
