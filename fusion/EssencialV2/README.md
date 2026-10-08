# Clínica Essencial V2 — duas peças

Esta versão preserva o draft anterior e cria um documento novo no Fusion.

## Executar

1. Descarregue e extraia `essencial-fusion-v2.zip`.
2. No Fusion, abra **Utilities → Scripts and Add-Ins → Scripts**.
3. Use **+ / Add** para selecionar a pasta `EssencialV2` e execute o script.
4. Guarde o documento como `.f3d`. Exporte cada componente separadamente para
   STL ou 3MF, confirmando as unidades em milímetros.

Há dois componentes, cada um com exatamente um corpo sólido:

- **01 - Plate and spine**: placa, logótipo e relevo unidos, com língua inferior.
- **02 - Slotted base**: base com ranhura aberta por cima, mostrada ao lado.

As peças aparecem separadas para inspeção. A placa está deitada em XY; a base
também está em XY, com a ranhura para cima. Na montagem, a placa fica vertical
e a língua entra na base até os ombros da placa assentarem na face superior.

## Encaixe

| Dimensão | Valor inicial |
| --- | --- |
| Placa | 180 × 220 × 5 mm, sem contar logótipo/língua |
| Língua | 120 mm de largura × 5 mm de espessura × 12 mm de inserção |
| Base | 160 × 70 × 18 mm |
| Ranhura útil | 120,6 × 5,5 mm |
| Profundidade da ranhura | 12,8 mm |
| Folga na espessura | 0,25 mm em cada lado |
| Folga nas extremidades | 0,30 mm em cada lado |
| Espaço abaixo da língua | 0,8 mm |
| Fundo sólido da base | 5,2 mm |
| Entrada alargada | 121,6 × 6,5 mm nos primeiros 1 mm |

A entrada é um pequeno degrau alargado, não um chanfro. A folga é um ponto de
partida para FDM; a calibração, o material e o pé de elefante podem alterar
o encaixe. Faça uma amostra curta da língua/ranhura no slicer antes de imprimir
as peças inteiras. Evite compensações que eliminem a folga.

Para ajustar, altere `FIT_CLEARANCE_PER_SIDE` e os restantes valores no topo
do `.py` e execute novamente. Os parâmetros gravados no documento servem como
referência; não conduzem todas as dimensões da geometria automaticamente.

## Coluna e impressão com bico de 0,4 mm

A coluna é um relevo lateral estilizado: 7 vértebras cervicais, 12 torácicas
e 5 lombares, mais sacro/cóccix simplificados. Corpos arredondados, projeções
curvas com raiz de pelo menos 2 mm, variação de tamanho e alinhamento suave
substituem os blocos da V1. O espaço nominal entre os corpos é 1 mm e o relevo
é 2,4 mm. Não é um modelo anatomicamente rigoroso.

Os detalhes estão unidos à placa. A placa/logótipo têm 5 mm de espessura;
as letras e o marcador NFC sobressaem 0,6 mm. O logótipo é agora gravado para
evitar corpos de inlay separados. A forma do E continua aproximada.

A placa pode ser impressa deitada; a cavidade NFC na face traseira exige
analisar bridging/suportes no slicer. A base imprime com a ranhura para cima.
Uma cor por peça é suficiente; pintura ou mudança de cor por camada são
opcionais. Verifique a área da mesa: o conjunto placa/logótipo/língua ocupa
cerca de 190 × 270 mm em XY e pode precisar de rotação para caber.

O QR é um alojamento para etiqueta de 52 × 52 mm, não um código funcional.
O alojamento NFC traseiro tem 26 mm de diâmetro; confirme a medida da etiqueta
e a forma de fixação antes de imprimir. A etiqueta eletrónica não é impressa.

## Validação

A sintaxe Python, a disposição das 24 vértebras e as dimensões de encaixe
foram verificadas na cloud. O script verifica no Fusion que cada componente
termina com um corpo sólido. Esta V2 ainda precisa de ser executada no Fusion
e de ter o encaixe confirmado numa impressão de teste.

Se a extrusão de texto não for suportada pela versão/fontes do Fusion, o texto
fica como sketch e surge um aviso; nesse caso não será impresso. Outras falhas
de geometria produzem uma mensagem de erro completa.
