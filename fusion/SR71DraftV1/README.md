# SR-71A Blackbird — primeiro draft para a Bambu A1

Miniatura estática de exposição, à escala nominal 1:144, com aproximadamente
**227,3 × 117,7 × 28,8 mm** depois de montada. O trem de aterragem está
recolhido. Este é o primeiro modelo imprimível para avaliar a forma, os
detalhes e a montagem; ainda não foi impresso nem montado fisicamente.

## Projeto de impressão

Abra **`sr71-1-144-draft-v1-A1-PLA-2-pratos.3mf` como projeto**, para manter
a orientação e os perfis. Foi preparado para Bambu A1, bico de 0,4 mm,
mesa Textured PEI e PLA preto. Não precisa de AMS.

1. **Prato 1:** metade superior, com a face de união apoiada na mesa.
2. **Prato 2:** metade inferior invertida, duas derivas, dois cones das
   entradas de ar, duas peças das tubeiras e três cavilhas.

São **oito peças principais e três cavilhas**. As duas derivas imprimem
deitadas, os cones com a base circular na mesa e as tubeiras com a face
detalhada virada para cima. Os dois pratos cabem na A1 sem cortar a fuselagem
a meio do comprimento.

| Configuração | Valor |
| --- | --- |
| Camada normal | **0,12 mm** |
| Primeira camada | **0,16 mm** |
| Paredes | 3, Arachne |
| Preenchimento do corpo | 12% gyroid |
| Peças pequenas | 100% |
| Camadas superiores / inferiores | 6 / 5 |
| Parede exterior / topo | 35 / 25 mm/s |
| Primeira camada / preenchimento inicial | 20 / 30 mm/s |
| Limite volumétrico do PLA | 6 mm³/s |
| Bico inicial / restantes camadas | 220 / 215 °C |
| Brim do corpo / peças pequenas | 3 / 2 mm |
| Suportes automáticos | Desativados |

A primeira camada fica a 0,16 mm para ajudar na adesão; as restantes camadas
do modelo usam 0,12 mm. Esta altura constante também evita transições de
camada variável nas superfícies longas. Ajuste a temperatura se a bobina
indicar um intervalo diferente.

O projeto foi exportado, reaberto e fatiado com o Bambu Studio oficial
02.08.02.61. Foram verificados os STL presentes, a colocação na mesa e as
alturas de camada no G-code. O resultado não gerou avisos de impressão,
suportes ou trocas de cor. A estimativa é de **43,0 g e 4 h 26 min**, com
estes perfis.

As cavidades internas têm tetos adaptados para reduzir os apoios. Continuam
a existir pequenas pontes nos furos e nos rebaixos das tubeiras; o bom
acabamento dessas zonas e dos bordos laterais deve ser confirmado na primeira
impressão. Ausência de avisos do fatiador não substitui essa prova física.

## Detalhes presentes

- Linhas gravadas de painéis e de acessos na fuselagem.
- Contornos dos vidros, separação das secções da cabine e pequenos puxadores
  exteriores simplificados.
- Localização da abertura de reabastecimento dorsal baseada na referência.
- Corrugações e linhas das superfícies de controlo nas asas.
- Cones separados, grelhas e juntas das carenagens dos motores.
- Peças traseiras das tubeiras com anéis, núcleo e segmentos em relevo.
- Derivas inclinadas **15° para dentro**, com linha simplificada do leme.

As linhas têm cerca de 0,34–0,42 mm de largura e 0,18–0,24 mm de profundidade.
Algumas dimensões foram reforçadas para FDM: asas com 1,44 mm de espessura
nominal, aproximadamente 1,28 mm nas corrugações; derivas de 1,20 mm. A ponta
frontal é delicada: retire o brim com cuidado e deixe a peça arrefecer.

O detalhe é uma adaptação para esta escala. A disposição de alguns painéis,
as corrugações e a segmentação interna dos motores são simplificadas; não
se pretende reproduzir cada parafuso ou a contagem exata das peças de um J58.
A cabine é fechada e opaca. Insígnias, números de matrícula e avisos pintados
não estão incluídos na impressão; podem ser acrescentados com decalques ou
pintura depois de escolhido um exemplar específico.

## Encaixes e montagem

**Comece pela amostra opcional `sr71-1-144-draft-v1-amostra-encaixes.stl`.**
Contém um pequeno bloco com um furo e uma ranhura, uma cavilha e uma lingueta.
A face com as aberturas do bloco imprime apoiada na mesa, para aproximar as
condições das faces de união. Use o mesmo PLA e perfil, sem suportes. A amostra
não está colocada nos dois pratos principais: pode importá-la para um prato
vazio antes de imprimir o avião.

As cavilhas têm diâmetro de 2,40 mm e comprimento de 4,20 mm; os furos têm
2,70 mm e profundidade conjunta de 4,50 mm. Os encaixes das derivas e dos
cones/tubeiras têm aproximadamente 0,15 mm de folga por lado. São encaixes
de posicionamento **para colar**, sem retenção por pressão.

Faça primeiro uma apresentação a seco, retirando apenas brim e rebarbas:

1. Coloque as três cavilhas numa metade e apresente a outra, conferindo
   nariz, bordos das asas e motores.
2. Cole as metades com pouca cola compatível com PLA, em pontos distribuídos.
   Mantenha-as alinhadas sem apertar as asas finas.
3. Cole os cones e as tubeiras nos respetivos rebaixos. O detalhe das
   tubeiras fica voltado para trás.
4. Monte as derivas na posição indicada na imagem de montagem: os topos
   inclinam-se para o centro do avião. Cada deriva usa duas linguetas.

Os encaixes e 66 posições ao longo das trajetórias de inserção foram
verificados geometricamente. As onze peças montadas não apresentam
interferências no modelo. As tolerâncias reais dependem da calibração e do
filamento; não force a amostra se ficar apertada.

## Imagens e ficheiros

- `sr71-1-144-draft-v1-CAD.png`: modelo e detalhe de um motor.
- `sr71-1-144-draft-v1-vistas.png`: vistas superior, lateral e traseira.
- `sr71-1-144-draft-v1-montagem.png`: vista separada das peças. As cores
  servem apenas para as distinguir; o projeto imprime tudo em preto.
- `sr71-1-144-draft-v1-pratos.png`: disposição real dos objetos nos pratos.
- `sr71-1-144-draft-v1-montado.glb`: montagem digital para inspeção.
- Onze STL das peças e um STL da amostra de encaixe.

`assembly.json` guarda as transformações de montagem, em mm.
`geometry-validation.json` regista as dimensões, as malhas fechadas e as
verificações de interferência e encaixe. `bambu-validation.json` identifica
o 3MF validado e as estimativas. O 3MF entregue é editável e deve voltar a ser
fatiado no Bambu Studio antes da impressão; não é G-code pronto a enviar.

## Referência, autoria e licença

O exterior foi reconstruído a partir dos perfis e contornos do modelo aberto
[FlightGear SR71-BlackBird](https://github.com/FGMEMBERS/SR71-BlackBird),
de **Gerard Robin, com modificações por l0k1**, conforme o README original.
Referência fixada no commit
`1de3f88ab7255b54f8cc22eec36d4632c2ce16a0`.

Foram usados `SR-71A-Blackbird.ac` e `SR-71-Blackbird-Base.ac`, incluídos em
`reference/` com os créditos originais e os respetivos checksums. Os perfis
da fuselagem foram reconstruídos com secções convexas e interpolação; a
envergadura e o comprimento foram ajustados às dimensões gerais de 16,94 m
e 32,74 m. A geometria de impressão, os encaixes, os reforços e os detalhes
FDM são modificações deste draft. Não é um CAD industrial da Lockheed.

Este derivado e os ficheiros de referência são disponibilizados sob a
**GNU GPL versão 2**, cujo texto acompanha o pacote em
`COPYING-GPL-2.0.txt`. Esta indicação aplica-se ao SR-71 e não altera a licença
dos outros projetos independentes do repositório.

## Reprodução a partir das fontes

As fontes extraídas do ZIP foram executadas numa pasta separada: as onze
peças voltaram a ser geradas com as mesmas dimensões e volumes, juntamente
com as imagens. `reproducibility-validation.json` regista essa comparação.

As fontes completas desta geração ficam em `reproducao/` no ZIP, com a
estrutura do repositório. Na raiz dessa pasta, crie as pastas `downloads` e
`designs`, se necessário, e instale `numpy`, `scipy`, `trimesh`, `manifold3d`,
`Pillow` e `opencv-python-headless`. É também necessária a fonte DejaVu Sans
no caminho indicado no script.

`requirements.txt` regista as versões usadas na validação; uma instalação
nova dessas dependências não foi testada neste trabalho.

Execute `python fusion/tools/generate_sr71_draft_v1.py` para gerar as peças e
as imagens. O script lê os dois AC3D como dados; não executa os programas do
simulador. O ficheiro base original declara um filho a mais na raiz; o leitor
aceita especificamente essa discrepância no fim do ficheiro.

Para reconstruir o 3MF, use `python fusion/tools/build_sr71_draft_v1_3mf.py`,
indicando `--bambu-bin`, `--profiles` e `--work-dir` para a instalação local do
Bambu Studio. Os utilitários partilhados necessários estão incluídos. Os
caminhos predefinidos correspondem ao ambiente usado para validar este draft.
