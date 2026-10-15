# Suporte de telemóvel — Universo do Saber V2

Esta versão mantém toda a geometria, medidas e perfil de impressão da V1 e
redesenha apenas o logótipo azul.

## Correção do logótipo

- os contornos facetados foram convertidos numa curva densa e suavizada;
- a cabeça é uma circunferência de 192 segmentos;
- a estrela tem dez vértices geométricos exatos;
- a base visual de `U` e `S` fica horizontal, com diferença inferior a
  **0,01 mm**;
- a lateral longa de `U` é uma vertical geométrica;
- o símbolo completo mantém 62 × 57 mm e relevo de 0,8 mm.

O contorno completo usa 3018 vértices. No `US`, o passo médio das curvas fica
próximo de 0,12 mm, abaixo da largura de extrusão de um bico de 0,4 mm. Por
isso, as curvas devem aparecer contínuas na impressão. A imagem
`universo-saber-suporte-v2-logo-alinhado.png` mostra a vista frontal do mesmo
contorno usado no STL e no 3MF, com as linhas de referência.

## Medidas e encaixe

- costas: **200 × 80 × 6 mm**;
- base: **110 × 80 × 6 mm**;
- inclinação: **70° em relação à mesa**;
- espaço útil acima do apoio: **171,6 mm**;
- ranhura: **6,30 mm** para material de 6,00 mm;
- folga total: **0,30 mm**.

Imprima primeiro `universo-saber-suporte-v2-amostra-encaixe-030.stl`. Não
redimensione as peças no Bambu Studio.

## Bambu Studio

Abra `universo-saber-suporte-v2-A1-AMS-2-pratos.3mf` como projeto:

1. costas brancas e relevo azul — uma troca de filamento;
2. base azul — nenhuma troca, com pequeno suporte snug no bisel do pé.

O perfil mantém 0,20 mm, três paredes, 15% gyroid, cinco camadas superiores,
quatro inferiores, Arachne, superfície superior monotónica e brim de 3 mm.
Foi exportado, reaberto e fatiado pelo Bambu Studio 02.08.02.61 sem avisos.
A estimativa é **82,9 g** e aproximadamente **3 h 42 min** para os dois pratos.

## Fusion 360

Copie a pasta `UniversoSaberStandV2` para os scripts do Fusion e execute
`UniversoSaberStandV2.py`. O script passa na verificação sintática, mas ainda
não foi executado numa instalação real do Fusion 360.

Os sólidos, colisões, percurso lateral de montagem e contactos com a mesa
foram novamente verificados por cálculo. O encaixe e a estabilidade continuam
a precisar de teste físico.
