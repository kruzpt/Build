# Grelha V3 — placas universais com presilhas inferiores

Uma única placa serve para todas as posições do conjunto **2 × 5**. Tem
**dois encaixes fêmea por baixo de cada lado**, nas posições 1/4 e 3/4.
Nos lados junto à caixa, os encaixes ficam vazios. Não há saliências exteriores.

As dimensões são preservadas: **217,3 × 179,8 × 30 mm**, aberturas **8 × 8 mm**,
grelha de 3,2 mm, barras de 1,6 mm e nove pés. A redução continua a ser
**0,2 mm por placa em cada direção**; conjunto **434,6 × 899 mm** com placas
justapostas. A V2 e todos os ficheiros anteriores ficam preservados.

## Funcionamento do encaixe

Cada encaixe tem uma boca aberta por baixo, paredes laterais e uma cavidade
mais larga por dentro. A presilha tem dois braços elásticos, um para cada
placa. As rampas nos ganchos ajudam a inserção; os ganchos ficam atrás de
ressaltos de retenção. A ponte liga os dois braços por baixo das bordas.

Os encaixes têm **paredes de retenção laterais**: não são simplesmente duas
ranhuras abertas para a junta. As paredes impedem que as placas se afastem e que a
presilha deslize para fora. O ressalto impede a saída por baixo sem flexão
dos braços. A retenção é geométrica; a força real precisa de teste.

Uma janela no lado interior de cada reforço dá acesso ao braço da presilha.
Mantém intactas as paredes junto à junta e a cavidade do gancho. Assim é
possível soltar o braço sem o deixar fechado dentro do alojamento.

- Paredes mínimas do encaixe: 0,8 mm.
- Braços da presilha: 1,2 mm de espessura e 6,4 mm de largura.
- Folga tangencial na boca: 0,3 mm por lado.
- Sobreposição nominal do gancho sobre o ressalto: 0,4 mm na presilha padrão.
- Presilha montada fica acima do plano dos pés; não aumenta a altura de 30 mm.

Os reforços locais têm 22 mm ao longo da borda e 4,2 mm para dentro, sem
avançar para fora da placa. Nos lados com margem de 3,85 mm, podem avançar
0,35 mm por baixo das primeiras aberturas; a abertura na superfície de apoio
continua com 8 mm. A limpeza dessas zonas faz-se com a presilha retirada.

## Primeiro imprimir a amostra

O pacote contém:

1. `grelha-pintos-v3-amostra-duas-bordas.stl`: duas peças pequenas separadas,
   com exatamente o mesmo encaixe da placa. Imprima o ficheiro uma vez.
2. Três presilhas: **suave**, **padrão** e **firme**, com alcance do gancho
   de 3,1, 3,2 e 3,3 mm. A diferença é de 0,1 mm; todas usam a mesma boca.
3. `grelha-pintos-v3-placa-universal.stl`: a placa completa.

Imprima os três tipos de presilha **em PETG**, com a orientação do STL:
deitados de lado, perfil dos braços na mesa. Assim, os filamentos acompanham
os braços; não imprima os braços como pequenas torres de camadas. O código
Fusion cria a presilha padrão; os outros dois STL são opções de calibração.

Imprima as duas bordas e, mais tarde, a placa, **face de apoio na mesa e pés
para cima**. Use mm, escala 100%, bico 0,4 mm e, como ponto de partida,
camadas de 0,2 mm. Não há suportes no modelo. O ressalto interior tem um
pequeno avanço de 0,6 mm: confirme a qualidade dessa região na amostra.

Vire as duas bordas para a posição de uso e encoste os lados com encaixe.
Alinhe as bocas, insira a presilha **por baixo** e pressione a ponte. Escolha
a variante que prende sem rachar, permite desmontar e não cai ao levantar
as bordas. Para desmontar, pressione os braços na direção da junta através
das janelas interiores e retire a ponte. Pode usar a unha ou uma pequena
espátula sem ponta afiada; solte um braço de cada vez se for mais fácil.

As presilhas usam retenção elástica; força de inserção, fadiga e tolerâncias
dependem do filamento e da impressão. Não force uma presilha que não entra.
O teste da amostra vem antes de imprimir as dez placas e as 26 presilhas.

## Montar o conjunto

Existem 13 interfaces entre placas em 2 × 5; com duas presilhas por interface,
são **26 presilhas**, todas iguais à variante escolhida. Encoste as placas;
não acrescente uma folga entre todas as peças. Não coloque presilhas nas
bocas junto às paredes da caixa.

A montagem é feita pela face inferior. Monte por filas ou pares antes de
colocar na caixa. Para retirar uma placa do meio, remova primeiro as suas
presilhas por baixo; pode ser necessário levantar o conjunto para lhes aceder.
As presilhas ajudam a manter o piso unido, mas a capacidade de levantar o
conjunto carregado não foi testada. Remova os animais antes da manutenção.

## Código Fusion e validação

Extraia o ZIP e adicione `GrelhaPintosV3` em **Utilities → Scripts and Add-Ins
→ Scripts → + / Add**. Cria um documento novo com três componentes separados:
placa universal, presilha padrão orientada para imprimir e uma borda de amostra
(imprima duas cópias desta borda se a exportar pelo Fusion). Exporte componentes
separadamente, em mm. Não imprima a disposição inteira mostrada no Fusion.

O STL foi verificado como um sólido fechado; a amostra contém dois sólidos
separados. As verificações geométricas confirmam que a presilha montada não
atravessa as bordas, que o gancho e as paredes impedem saídas rígidas, e que
uma deflexão idealizada dos braços deixa passar a presilha durante a inserção.
Estas verificações **não são uma simulação de elasticidade**, nem um ensaio
de força ou desgaste. A execução real no Fusion e os ensaios físicos ainda
precisam de confirmação. Verifique também o apoio dos pintos na grelha.

Os alojamentos acrescentam cerca de 7,1 cm³ por placa em relação à V2.
Ainda assim, a placa tem cerca de 32,4% menos volume sólido que o original;
incluindo dez placas e as 26 presilhas padrão, a redução é cerca de 31,7%.

`validation.json` regista volumes e folgas. A comparação de material usa o
mesmo volume de união do STL original da V2; consumo real vem do slicer.
Regeneração: `python fusion/tools/generate_pintos_v3.py` no ambiente de geração
de STL, usando o código e a referência já registada na V2.
