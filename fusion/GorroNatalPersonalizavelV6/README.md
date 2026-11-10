# Gorro de Natal V6 — argola superior e nome editável

Mantém as curvas Bézier aprovadas da V5 e troca o furo lateral do pompom por
uma argola vermelha no topo. O eixo da argola fica em `x = 2,1 mm`, alinhado
com o centro de massa calculado dos três exemplos, para o gorro ficar direito
quando pendurado.

## Texto editável no Bambu Studio

O nome é novamente uma **Text Shape nativa**. Clique no volume
`Nome editável` e escolha **Editar texto**. A V5 não mostrava esta opção porque
o nome era uma malha fixa.

A V3 guardava `font_index="0"`, que selecionava a primeira fonte da lista e
podia abrir como Arial. A V6 usa a convenção do código atual do Bambu Studio:
`font_index="-1"`, `font_name="Lobster"` e `font_version="2.8"`. Também usa
ângulo 0° e não associa o texto a um ponto de raycast, evitando a rotação
incorreta observada anteriormente.

A geometria aprovada aplicava uma expansão de contorno de 0,32 mm. A Text
Shape guarda agora `Boldness = 0,32 mm`; assim, ao editar o nome, o Bambu
regenera as letras com a mesma espessura visual em vez de voltar ao traço fino.

Antes de abrir o 3MF no Windows:

1. Fechar o Bambu Studio.
2. Extrair o ZIP.
3. Clicar com o botão direito em `Lobster-Regular.ttf`.
4. Escolher **Instalar para todos os utilizadores**.
5. Reiniciar o Bambu Studio e abrir o 3MF como projeto.
6. Confirmar que o campo **Font** mostra `Lobster` antes de alterar o nome.

O Bambu não incorpora o ficheiro da fonte na Text Shape; ela precisa de estar
instalada no computador que faz a edição.

## Três projetos

| Perfil | Exemplo | Tamanho inicial |
| --- | --- | ---: |
| curto | Lia | 15,5 mm |
| médio | Tomás | 14,5 mm |
| comprido | Alexandre | 10,8 mm |

Escolha o perfil conforme o comprimento do novo nome. A edição não reduz
automaticamente o tamanho para qualquer comprimento: confirme visualmente que
o texto permanece dentro da aba branca.

## Geometria e impressão

- dimensões máximas aproximadas: 102,5 × 107 × 4,6 mm;
- argola exterior: Ø14 mm;
- furo superior: Ø5 mm;
- corpo, dobra, argola e nome: vermelho;
- aba e pompom: branco;
- Bambu A1, bico de 0,4 mm;
- sem suportes e sem brim.

Os projetos foram reabertos e reexportados pelo Bambu Studio 2.9.1.70 depois
de receberem a Text Shape. Essa validação confirma a estrutura do ficheiro e
a preservação dos metadados. A edição pela interface Windows e a impressão
física continuam por confirmar no computador do utilizador.
