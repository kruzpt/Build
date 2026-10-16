# Universo do Saber V6 — placa de 7 mm e base sem bisel inferior

A V6 é um **novo conjunto completo de duas peças**, conforme a prévia aprovada
`universo-saber-suporte-v6-proposta-bisel-branco.png`. A placa branca ganha
1 mm de espessura e conserva o mesmo tipo de bisel. A base azul mantém o
reforço frontal e perde o bisel inferior que exigia suportes e deixava marcas.

**Imprima os dois pratos da V6.** As peças e a posição dos encaixes foram
atualizadas e não devem ser combinadas com as peças V4/V5 já impressas.
As versões anteriores ficam preservadas.

## Medidas e encaixes

| Elemento | Medida |
| --- | --- |
| Placa branca | 200 × 80 × **7 mm** |
| Relevo azul | 0,8 mm; espessura total nessa zona de 7,8 mm |
| Base azul | **111 × 80 × 6 mm** |
| Batentes da base | mais 4 mm; altura máxima de 10 mm |
| Ranhura azul, para a placa branca | **7,30 mm** |
| Ranhura branca, para a base azul | **6,30 mm** |
| Folga nominal total em cada encaixe | **0,30 mm**, ou 0,15 mm por face |
| Inclinação do telemóvel | **70°** em relação à mesa |
| Altura útil acima do apoio | aproximadamente **165,2 mm** |
| Janela do cabo | **18 × 20 mm**, cantos de raio 3 mm |
| Travessa frontal de reforço | **10 × 6 mm** |

O comprimento azul aumenta 1 mm para conservar a janela e a travessa com
a placa mais espessa. A janela e os batentes avançam 1 mm. A posição do
encaixe foi recalculada para que o bisel branco e a aresta traseira azul
assentem na mesma mesa, mantendo a inclinação de 70°.

Não redimensione as peças no Bambu Studio. Imprima primeiro a amostra
`amostra-encaixe-030.stl`. Cada amostra inclui uma peça de 7 mm e outra de
6 mm, com as respetivas ranhuras. Incluem-se também variantes de folga
total de 0,20 e 0,40 mm. No ficheiro conjunto, estão por essa ordem da
esquerda para a direita.

## Impressão no Bambu Studio

Abra `universo-saber-suporte-v6-A1-AMS-2-pratos.3mf` como **projeto**.
Ambas as peças estão deitadas, com o relevo e os batentes para cima.

| Prato | Configuração | Filamento estimado | Tempo estimado | Trocas |
| --- | --- | ---: | ---: | ---: |
| 1 — Placa branca e relevo azul | 3 paredes, 15% gyroid | 58,11 g | 2 h 27 min | 1 |
| 2 — Base azul | 4 paredes, 25% gyroid | 33,40 g | 1 h 31 min | 0 |
| Total | | **91,51 g** | **cerca de 3 h 58 min** | **1** |

O perfil usa A1 com bico de 0,4 mm, Generic PLA, camadas de **0,20 mm**, cinco
camadas superiores, quatro inferiores, Arachne, superfície superior monotónica
a 40 mm/s e brim de 3 mm. A primeira camada usa 30 mm/s. O limite volumétrico
do filamento é 8 mm³/s.

**Os suportes estão desativados nos dois pratos.** O Bambu Studio oficial
**02.08.02.61** exportou, reabriu e fatiou o projeto sem avisos. Os percursos
dos dois pratos foram inspecionados por código e não contêm trajetos de
suporte. A placa branca tem 39 camadas e a base 50.

As quatro paredes e os 25% gyroid da base são uma configuração específica do
objeto; o perfil global mostra os valores do prato 1. Confirme as posições
dos filamentos branco e azul no AMS antes de imprimir. As estimativas podem
variar com o filamento e a versão do Bambu Studio.

## Montagem e carregamento

Monte por deslize lateral, alinhando as duas ranhuras. A janela mantém-se
fechada pela travessa de reforço. Passe a ficha do cabo pela janela antes
de ligar o telemóvel.

Foram verificadas geometricamente as seguintes combinações de espessura do
telemóvel com capa e caixa plástica da ficha, assumindo uma porta centrada:

| Telemóvel com capa | Largura × espessura da caixa da ficha |
| --- | --- |
| 8 mm | 10 × 5 mm |
| 10 mm | 12 × 6 mm |
| 14 mm | 12 × 8 mm |
| 17 mm | 12 × 8 mm |

As trajetórias até à porta foram verificadas em 116 posições no total.
Uma caixa de 16 × 10 mm também pode ser passada pela zona central da janela
antes da ligação. Estas dimensões não confirmam todos os modelos de cabo;
fichas em cotovelo, magnéticas ou mais volumosas podem precisar de ajustes.

## Ficheiros e Fusion

O pacote inclui o projeto 3MF, os STL separados, as amostras, as imagens e a
pasta `UniversoSaberStandV6` com o script Fusion e `geometry.json`.

Para editar no Fusion, copie a pasta completa para os scripts e execute
`UniversoSaberStandV6.py`. O script cria um novo documento montado e separa
os materiais em três componentes. Com `SHOW_ASSEMBLED=False`, mostra as
peças deitadas. A sintaxe foi verificada, mas o script ainda não foi executado
numa instalação real do Fusion. O 3MF fornecido não depende dessa execução.

Os STL de branco e relevo partilham a mesma origem. Importe-os como partes
do mesmo objeto para conservar o alinhamento e atribuir as cores. O STL
`costas-completas` reúne os dois volumes sem atribuição de cores. O ficheiro
`montado-referencia-nao-imprimir` é apenas uma referência visual.

Todos os STL são sólidos fechados, com orientação consistente. Foram
verificados o percurso de montagem em 42 posições, as colisões, os contactos
na mesa e o equilíbrio estático ideal com três tamanhos de telefone.
O encaixe real, a aderência à mesa, o cabo e a resistência da impressão ainda
dependem de teste físico. Não foi feita análise estrutural por elementos finitos.
