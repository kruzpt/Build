# Paleta de Natal V2 — quatro cavidades integradas

Paleta de 140 × 200 mm, com quatro reservatórios redondos de fundo fechado.
São cavidades para receber a tinta diretamente. Os seis enfeites da proposta
visual anterior conservam as medidas; os seus modelos 3D não fazem parte
deste projeto da paleta.

## Dimensões reais do modelo

| Elemento | Dimensão |
| --- | --- |
| Paleta | 140 × 200 mm |
| Espessura da base | 3 mm |
| Altura máxima nos rebordos | 9 mm |
| Número de reservatórios | 4, disposição 2 × 2 |
| Diâmetro interno de cada reservatório | 36 mm |
| Profundidade interna | 6 mm |
| Espessura das paredes dos reservatórios | 2,4 mm |
| Raio do canto interior no fundo | 2 mm |
| Capacidade geométrica até ao bordo | 6,01 ml |
| Capacidade com 1 mm de margem superior | 4,99 ml, aproximadamente 5 ml úteis |
| Abertura para o polegar | 28 × 44 mm |

Os cantos arredondados facilitam o acesso do pincel e a limpeza. O corpo é
uma peça única, com quatro fundos fechados de 3 mm, sem peças para colar.
A inscrição Feliz Natal é gravada no campo inferior.

## Pesquisa e compatibilidade

A pesquisa geral de produtos foi bloqueada pela política de rede do ambiente.
Foram consultados projetos públicos de suportes, incluindo a tabela de medidas
de [harveyyau/gridfinity-organizers](https://github.com/harveyyau/gridfinity-organizers#-sizing-guide),
que indica 28–35 mm para recipientes de tinta acrílica. Esta é uma referência
comunitária de organização, não uma ficha de fabricante nem prova das medidas
dos mini-potes da fotografia. Não foi possível confirmar diâmetros comerciais
dos potes de 3 ou 5 ml em fontes primárias.

O diâmetro de 36 mm e a capacidade útil de 5 ml são decisões deste desenho,
não um alegado padrão de mercado. A função principal é utilizar tinta
diretamente nas cavidades.

Um recipiente individual de corpo inferior a 35 mm tem folga na zona superior,
mas o canto arredondado reduz o fundo plano a 32 mm de diâmetro. O perfil do
fundo, a conicidade, a tampa e a dobradiça podem limitar a profundidade de
apoio. Potes em tiras ligadas não têm compatibilidade garantida com esta
disposição 2 × 2. Um encaixe específico deve ser ensaiado com o pote real.

## Ficheiros

- [Desenho do kit atualizado](../../designs/kit-natal-pintar-v2-dimensoes-cavidades.png)
- [Desenho técnico da paleta: modelo, planta e secção](../../designs/kit-natal-paleta-v2-CAD-dimensoes.png)
- [PDF para o cliente, duas páginas](../../downloads/kit-natal-pintar-v2-dimensoes-cavidades.pdf)
- [Paleta STL](../../downloads/kit-natal-paleta-v2-4-cavidades.stl)
- [Projeto Bambu A1, um prato e uma paleta](../../downloads/kit-natal-paleta-v2-A1-PLA.3mf)

A imagem do kit é ilustrativa. O desenho técnico da segunda página representa
a geometria que foi efetivamente exportada para STL e 3MF.

## Impressão

Bambu Lab A1, bico de 0,4 mm, PLA castanho. Camadas de 0,20 mm, três paredes,
Classic, ordem outer/inner, preenchimento 100%, cinco camadas de topo e cinco
de fundo, topo monotónico a 25 mm/s. Os fundos maciços foram priorizados para
o uso com tinta. Perfil Generic PLA com limite de 8 mm³/s; confirmar os dados
da bobina efetivamente utilizada. Imprimir com o verso plano na mesa,
reservatórios para cima e brim exterior de 3 mm. Sem suportes e sem AMS.

O projeto foi exportado, reaberto e fatiado no Bambu Studio oficial 02.08.02.61:
sem avisos de impressão, sem suportes gerados e sem trocas de cor.
Estimativa apenas da paleta: **83,89 g e cerca de 3 h 31 min**.
A 16 €/kg, representa **1,34 € de filamento**, antes de eletricidade,
perdas e utilização da máquina. A estimativa anterior de uma base plana era
inferior; esta versão inclui os reservatórios e o fundo maciço.

Malhas fechadas e fundos íntegros foram verificados geometricamente. A
estanquidade física de uma impressão FDM depende do fluxo e da adesão entre
linhas; testar com água e secar antes de colocar tinta. Ainda não houve
ensaio físico de impressão, utilização ou compatibilidade com potes.

## Reprodução

Com o ambiente geométrico do repositório:

```sh
python fusion/tools/generate_kit_natal_palette_v2.py --build-3mf
python fusion/tools/export_kit_natal_dimension_sheet.py --version v2
```

O gerador usa manifold3d, trimesh, numpy, Pillow e os utilitários existentes
em fusion/tools. O PDF usa também reportlab. Os caminhos do fatiador e dos
perfis podem ser fornecidos com --bambu-bin e --profiles.

geometry-validation.json regista os volumes, fundos, cavidades e checksum
do STL. bambu-validation.json regista a comparação geométrica do projeto,
a exportação, reabertura, fatiamento, consumo e checksum do 3MF.
