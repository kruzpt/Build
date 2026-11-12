# Coroas de Natal personalizáveis — V1

Projeto aprovado a partir da fotografia do utilizador: coroa aberta com folhas, laço, bagas, texto vermelho e contorno creme. **O formulário gera tanto o texto como os apoios correspondentes na coroa.**

[Pacote completo: formulário e três exemplos 3MF](https://github.com/kruzpt/Build/blob/main/downloads/coroa-natal-v1-pacote-bambu.zip?raw=true)

[Formulário num único ficheiro HTML](https://github.com/kruzpt/Build/blob/main/downloads/coroa-natal-v1-personalizar.html?raw=true)

[Prévia da geometria final](../../designs/coroa-natal-v1-CAD-montagem.png) · [Formulário](../../designs/coroa-natal-v1-formulario.png)

## Como personalizar

1. Descarregar e extrair o ZIP. Abrir `personalizar.html` no Chrome ou Edge. Não abrir o código HTML na página do GitHub.
2. Escrever o nome, uma segunda linha se necessária e o ano opcional. Escolher a letra. As fontes estão incluídas; não é necessário instalá-las.
3. Conferir as vistas **Montada**, **Coroa**, **Apoios de colagem** e **Texto separado**. A prévia usa os mesmos contornos que são exportados, não a imagem de conceito.
4. Carregar em **Descarregar 3MF · 2 pratos**.
5. Abrir o ficheiro como **projeto** no Bambu Studio. O prato 01 contém a coroa; o prato 02 contém o texto. Mapear as cores nos rolos reais do AMS Lite e fatiar antes de imprimir.

O formulário funciona sem internet e não envia os nomes para um servidor. Não necessita de Python, Fusion nem instalação de bibliotecas. Foi testado em Chromium; não foi executado remotamente no computador Windows do utilizador.

Para alterar uma personalização posteriormente, usar **Abrir uma personalização guardada** e selecionar um 3MF criado por este formulário. O nome, a segunda linha, o ano e a fonte são recuperados e podem ser alterados. Um 3MF regravado por outro programa poderá perder estes metadados; nesse caso, voltar a introduzir os campos.

As letras exportadas são geometria: a adaptação automática faz-se neste formulário, **não no comando Editar texto do Bambu Studio**.

## Montagem e dimensões

| Característica | Valor do modelo |
| --- | --- |
| Diâmetro exterior da coroa de folhas | 100 mm |
| Altura total, incluindo laço e argola | 109,2 mm |
| Espessura máxima da coroa e apoios | 2,60 mm |
| Espessura do conjunto texto + contorno | 2,12 mm |
| Espessura total montada, sem contar com cola | 4,72 mm |
| Diâmetro interior da argola | 3 mm |
| Apoios de colagem | 2 círculos de Ø 4,90 mm |
| Área nominal de contacto total | Aproximadamente 37,69 mm² |

São **duas peças físicas para colar**, embora o Bambu mostre vários volumes de cor dentro de cada objeto. A base creme do texto une as letras, acentos e linhas. Não é necessário colar letras individualmente.

Os dois apoios são integrados na coroa e acabam num plano comum, à altura de 2,60 mm. O relevo das folhas é retirado apenas nessas zonas. A traseira plana do texto assenta nesses apoios. Fazer primeiro uma montagem a seco, alinhar com a prévia e aplicar pouca cola adequada a PLA. As posições são calculadas para cada composição: **usar a coroa e o texto do mesmo 3MF**.

Nomes curtos podem precisar de prolongamentos decorativos vermelhos com contorno creme para alcançar os apoios. Estes fazem parte da prévia e da peça exportada. Não existem encaixes de pressão nem pinos de alinhamento nesta V1.

## Texto e fidelidade à referência

A composição adapta escala uniforme, centragem, contorno, ligações entre caracteres e apoios. Não comprime as letras horizontalmente. É possível usar duas linhas de nome e um ano de quatro algarismos. Campos vazios, caracteres não suportados, linhas com mais de 24 caracteres e texto demasiado pequeno são recusados.

As fontes incluídas são **Pacifico** e **Leckerli One**, ambas com licença OFL. A fonte exata da fotografia não foi identificada. A V1 aproxima o estilo da referência com geometria vetorial; não é uma réplica garantida da tipografia original. Os contornos e as nervuras são detalhes físicos, não texturas apenas visuais.

## Impressão

Configuração confirmada pelo utilizador: **Bambu A1, AMS Lite, bico de 0,4 mm e PLA**.

- Quatro posições de cor: creme, verde escuro, verde claro e vermelho.
- Perfil completo Generic PLA para A1, herdado de um projeto já validado; não contém calibração específica de um rolo novo.
- Camada de 0,12 mm, primeira camada de 0,20 mm, três paredes, 15% gyroid, topo monotónico e gerador de paredes Arachne.
- Paredes exteriores até 25 mm/s e topo até 18 mm/s.
- PEI texturado, peças com traseira plana na mesa, sem suportes e sem brim por defeito.
- Torre de purga ativa para as trocas de cor. O texto usa apenas creme e vermelho; a coroa usa as quatro cores.

Não foi enviada nenhuma impressão para uma máquina. Imprimir uma unidade de teste antes de produzir várias, para confirmar o acabamento, a argola e a colagem com os materiais reais.

## Verificação

[Testes do formulário](browser-validation.json) · [Verificação de geometria e fatiamento](bambu-validation.json) · [Origem do perfil](profile-source.json)

Foram testadas oito composições, incluindo nomes curtos, nomes em várias linhas, acentos e as duas fontes. As verificações cobrem funcionamento sem rede, exportação e recuperação dos campos, malhas fechadas, ausência de sobreposição entre materiais, união das bases, apoio dos detalhes e área de colagem. Os 3MF são reabertos e fatiados no Bambu Studio 2.9.1.70; os relatórios distinguem os resultados digitais dos testes físicos ainda por fazer.

## Código e reprodução

O HTML distribuído incorpora o código, as fontes e as bibliotecas. Os ficheiros de desenvolvimento estão nesta pasta. `geometry.js` gera os contornos e as malhas; `export3mf.js` escreve o projeto Bambu e os parâmetros de personalização; `app.js` controla o formulário. Bibliotecas e licenças: [THIRD_PARTY.md](THIRD_PARTY.md).

```bash
python build_offline.py
node validate_browser.cjs /tmp/coroa-v1-tests-final
python validate_geometry_and_slice.py --work /tmp/coroa-v1-tests-final --bambu-bin /caminho/bambu-studio
```

Os testes de desenvolvimento usam Playwright/Chromium, NumPy, Pillow, Shapely e trimesh, além dos utilitários já existentes no repositório. Não são dependências para utilizar o formulário distribuído. A execução Fusion não faz parte deste gerador e não é apresentada como tendo sido verificada.
