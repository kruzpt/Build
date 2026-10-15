# Suporte de telemóvel — Universo do Saber V3

A V3 mantém as medidas, o encaixe e o perfil de impressão da V2. Corrige a
transição da lateral esquerda do `U` e redesenha os livros.

## Alterações da V3

- a lateral do `U` liga ao topo através de um arco tangente de 1,3 mm;
- a ligação inferior à curva usa uma transição progressiva de 2 mm;
- desaparece a pequena quebra visível na V2;
- cada lado tem agora **dois livros** empilhados em perspetiva;
- os livros usam contorno azul de **0,9 mm**, adequado ao bico de 0,4 mm;
- o interior branco da placa representa as páginas.

As imagens `universo-saber-suporte-v3-logo-alinhado.png` e
`universo-saber-suporte-v3-livros.png` mostram os contornos reais usados no
STL e no 3MF.

## Medidas e encaixe

- costas: **200 × 80 × 6 mm**;
- base: **110 × 80 × 6 mm**;
- inclinação: **70° em relação à mesa**;
- espaço útil acima do apoio: **171,6 mm**;
- relevo azul: **0,8 mm**;
- ranhura: **6,30 mm** para material de 6,00 mm;
- folga total: **0,30 mm**.

Imprima primeiro `universo-saber-suporte-v3-amostra-encaixe-030.stl`. Não
redimensione as peças no Bambu Studio.

## Projeto Bambu Studio

Abra `universo-saber-suporte-v3-A1-AMS-2-pratos.3mf` como projeto:

1. costas brancas e relevo azul — uma troca de filamento;
2. base azul — nenhuma troca, com pequeno suporte snug no bisel do pé.

Perfil incluído: 0,20 mm, três paredes, 15% gyroid, cinco camadas superiores,
quatro inferiores, Arachne, superfície superior monotónica e brim de 3 mm.
O projeto foi exportado, reaberto e fatiado pelo Bambu Studio 02.08.02.61 sem
avisos. A estimativa é **82,9 g** e aproximadamente **3 h 41 min**.

## Fusion 360 e validação

Copie a pasta `UniversoSaberStandV3` para os scripts do Fusion e execute
`UniversoSaberStandV3.py`. O script passa na verificação sintática, mas ainda
não foi executado numa instalação real do Fusion 360.

Os sólidos, contactos com a mesa, percurso lateral de montagem, alinhamento
do símbolo e três tamanhos de telefone foram novamente verificados por
cálculo. O encaixe e a estabilidade continuam a precisar de teste físico.
