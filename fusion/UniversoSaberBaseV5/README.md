# Base reforçada V5 — para as costas já impressas da V4

Esta atualização substitui **apenas a base azul (antigo prato 2)**. Use-a com
o prato 1 da V4 que já está impresso. O novo 3MF tem um único prato e não
contém as costas nem exige reimprimir o logótipo ou os livros.

## Como funciona o reforço

Na V4, o braço esquerdo da abertura em U dependia de uma ligação estreita
entre o recorte do cabo e a ranhura. A V5 une os dois braços da frente com
uma **travessa integral de 10 mm de largura por 6 mm de espessura**.

A ligação original de 1,85 mm continua presente, mas a travessa cria um
segundo percurso de transmissão de carga pelo outro braço. O reforço não
resulta apenas de aumentar o preenchimento. A nova abertura para o cabo é
uma **janela de 18 × 20 mm**, com cantos de raio 3 mm.

As costas, a ranhura de **6,30 mm**, a folga total de **0,30 mm**, o apoio a
**70°**, os batentes e as faces de contacto com a mesa mantêm-se. A base
conserva **110 × 80 × 6 mm**, com altura máxima de 10 mm nos batentes.

## Carregamento

Passe a ficha pequena do cabo pela janela, de baixo para cima, e depois
ligue-a ao telemóvel. O cabo deixa de ser colocado lateralmente por uma
abertura em U; passa através da janela fechada.

A janela mantém espaço abaixo da porta de carregamento. Foram verificadas
por geometria as seguintes combinações, com a porta centrada na largura do
telemóvel. As dimensões da ficha incluem a sua caixa plástica:

| Espessura do telemóvel com capa | Largura × espessura da ficha |
| --- | --- |
| 8 mm | 10 × 5 mm |
| 10 mm | 12 × 6 mm |
| 14 mm | 12 × 8 mm |
| 17 mm | 12 × 8 mm |

Cada trajetória foi verificada em 29 posições até à ligação ao telemóvel.
Também foi testada a passagem de uma caixa de **16 × 10 mm** pela zona
central da janela, antes de ligar o cabo. Os cantos arredondados reduzem o
espaço útil junto às extremidades da abertura.

Isto não confirma todos os modelos de cabo: fichas magnéticas, em cotovelo,
caixas maiores ou portas deslocadas podem precisar de uma abertura diferente.
O encaixe do cabo real e a resistência da impressão ainda não foram ensaiados
fisicamente.

## Projeto Bambu Studio

Abra `universo-saber-base-v5-reforcada-A1-PLA.3mf` como **projeto**:

- Bambu Lab A1 com bico de 0,4 mm;
- um prato, uma base e um filamento PLA azul;
- camada de 0,20 mm, quatro paredes e 25% gyroid;
- cinco camadas superiores, quatro inferiores e superfície monotónica;
- velocidade da superfície superior de 40 mm/s;
- brim de 3 mm e suporte snug apenas no pequeno bisel traseiro do pé;
- sem torre de purga ou trocas de cor.

Exportado, reaberto e fatiado pelo Bambu Studio oficial **02.08.02.61**,
sem avisos de fatiamento: **32,93 g** e aproximadamente **1 h 35 min**.
Selecione no AMS a posição real do filamento azul. A estimativa varia com
o filamento e a versão do Bambu Studio.

## Ficheiros e validação

- `universo-saber-base-v5-reforcada.stl`: a base para impressão;
- `universo-saber-base-v5-reforcada-A1-PLA.3mf`: projeto de um prato configurado;
- pasta `UniversoSaberBaseV5`: script Fusion, geometria e relatórios;
- pasta `imagens`: comparação com a V4 e montagem com as costas existentes.

O STL é um único sólido fechado. A zona do encaixe foi comparada com a V4
e não tem diferenças de volume. Foram verificados 42 estados do percurso
de montagem e a ausência de colisões com as costas, os livros e o telemóvel.
O equilíbrio estático ideal e o apoio na mesa também passaram nas verificações.
Não foi feita análise estrutural por elementos finitos nem ensaio de carga.

Para editar no Fusion, copie a pasta `UniversoSaberBaseV5`, mantenha
`geometry.json` ao lado do script e execute `UniversoSaberBaseV5.py`. O script
cria apenas a base num novo documento, deitada para impressão. A sintaxe foi
verificada, mas o script ainda não foi executado numa instalação real do Fusion.
