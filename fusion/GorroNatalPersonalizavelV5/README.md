# Gorro de Natal V5 — curvas Bézier

Versão aprovada com copa mais larga, ponta caída, concavidade profunda junto ao
pompom e dobra frontal assimétrica. O contorno é composto por curvas Bézier
amostradas em alta resolução.

## Ficheiros de impressão

São fornecidos três projetos Bambu de duas cores:

| Perfil | Exemplo | Tamanho da fonte |
| --- | --- | ---: |
| curto | Lia | 15,5 mm |
| médio | Tomás | 14,5 mm |
| comprido | Alexandre | 10,8 mm |

Nestes 3MF o nome é **geometria estável**, não um `Text shape` editável. Esta
decisão evita a substituição por Arial e o ângulo incorreto encontrados no V3.
Para outro nome, altere `nome` e `perfil` no SCAD e regenere a malha com a fonte
Lobster incluída.

## Impressão

- dimensões máximas: 102,5 × 96,1 × 4,6 mm;
- corpo e nome: vermelho, extrusor 1;
- aba e pompom: branco, extrusor 2;
- furo: 5 mm;
- bico previsto: 0,4 mm;
- sem suportes e sem brim por defeito.

As malhas são fechadas e os projetos foram validados estruturalmente no Bambu
Studio 2.9.1.70. Ainda falta a primeira impressão física.
