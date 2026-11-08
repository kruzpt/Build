# Arrefecimento de saliências — limiar de 25% e ventoinha a 100%

**Registado:** 08/11/2026.

**Fonte:** UpLike Digital, um canal diferente do Clube das ferramentas.

**Link enviado:** https://www.facebook.com/share/r/1DzNeH9sFZ/

**Reel identificado:** https://www.facebook.com/reel/1474408334711746

## O que a fonte mostra

O vídeo de aproximadamente 41 segundos compara o acabamento de saliências
num vaso recortado. O autor indica na descrição ter usado PLA rosa bebé da
Voolt3D. A interface mostra uma A1 mini, bico de 0,4 mm, e o perfil de material
Generic PLA @BBL A1M. Isso não equivale a um teste com o nosso SUNLU PLA+ laranja.

Na configuração de filamento, separador de arrefecimento, são mostrados:

| Definição | Valor final mostrado |
| --- | --- |
| Arrefecimento forçado para saliências e pontes | Ativo |
| Limite de saliência de arrefecimento | **25%** |
| Velocidade da ventoinha para saliências | **100%** |
| Limite de saliência para arrefecimento participante | 100%, outro campo visível |

A descrição destaca as duas definições de 25% e 100%. A interface já apresenta
100% de ventoinha antes da seleção do limiar; não se deve deduzir uma alteração
de potência anterior que não ficou demonstrada. O campo de arrefecimento
participante é distinto e não foi incluído na proposta de alteração abaixo.

Aos cerca de 32 segundos, a prévia apresentada contabiliza **7,74 g de suporte**
e 50,51 g de material total. Não está demonstrado que o ensaio tenha sido feito
sem suportes, nem quais as regiões/objetos que consomem esses apoios.
O próprio autor ressalva que saliências grandes podem exigir suportes ou outra
orientação. A afirmação de pouca alteração no tempo pertence à comparação do
autor, não é uma estimativa obtida nos nossos projetos.

## Significado do parâmetro

No código oficial do Bambu Studio, `overhang_fan_threshold` corresponde a
`Cooling overhang threshold`. O limiar é expresso como a percentagem da largura
da linha que fica sem apoio na camada inferior. Reduzir de 50% para 25% faz o
reforço de arrefecimento começar em saliências menores.

`overhang_fan_speed` define a potência específica nessas zonas; a proposta
mantém os restantes limites de ventilação e o comportamento da primeira camada.
O campo `overhang_threshold_participating_cooling` é outro parâmetro, relacionado
com a participação das saliências na desaceleração para arrefecimento.

Referência de semântica:
https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp

## Comparação com os nossos ficheiros

Consulta em 08/11/2026:

| Definição | Laranja calibrado / Gallardo V4 laranja | Vídeo |
| --- | --- | --- |
| Limiar de reforço da ventoinha | **50%** | **25%** |
| Ventoinha para saliências | **100%** | **100%** |
| Ventoinha normal mínima / máxima | 60% / 80% | 60% / 80% visíveis |
| Reforço de arrefecimento | Ativo no projeto do Gallardo | Ativo |

Para o nosso laranja, a alteração a testar seria apenas o limiar **50% → 25%**.
Não é necessário aumentar novamente a ventoinha de saliências: já está a 100%.
O perfil JSON reutilizável guarda o limiar e a potência; a ativação efetiva do
reforço foi confirmada no projeto completo do Gallardo.

## Avaliação para os nossos projetos

- É uma opção plausível para reduzir a queda/encurvamento de linhas de PLA em
  saliências graduais, incluindo zonas curvas do lobito e detalhes do Gallardo.
- Aumentar o arrefecimento não cria apoio para um elemento que começa isolado
  no ar. Conservar os suportes necessários no Gallardo durante este teste.
- Não generalizar o resultado do PLA rosa a todos os materiais, especialmente
  ao dourado silk, sem avaliar brilho e ligação entre camadas.
- Nos perfis de filamento, esta configuração de arrefecimento é reutilizável,
  mas uma variante de teste deve permanecer distinguível do perfil calibrado
  que já está aprovado pelo utilizador.

## Proposta de teste e estado

Comparar 50% e 25% com a mesma peça/amostra e o mesmo laranja, mantendo fluxo
0,931, temperatura, velocidades, orientação e suportes. Avaliar as zonas em
balanço, a textura, o brilho e a ligação entre camadas. Se houver vantagem
física, considerar guardar uma variante do perfil laranja com o novo limiar.

**Estado:** vídeo revisto visualmente; parâmetros e coluna de suporte confirmados.
Ficheiros dos nossos perfis consultados. Nenhum perfil ou projeto foi alterado,
nenhum teste novo foi fatiado ou impresso e não se reivindica melhoria física
nos nossos materiais.
