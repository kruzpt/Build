# Aquelá V5 — menor, nome sem contorno preto e olho simplificado

[Pacote completo](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v5-pacote.zip?raw=true) · [Vista da geometria](../../designs/anilha-aquela-v5-montada-CAD.png) · [Percursos do Bambu Studio](../../designs/anilha-aquela-v5-percursos.png)

Esta revisão mantém o lobo da referência aprovada, a tabuleta irregular e as três peças para colar. O pedido de retirar 10 mm à largura e à altura foi aplicado ao **conjunto visível**, de aproximadamente 62 × 65 para **52 × 55 mm**. A abertura para o lenço não foi reduzida.

## Alterações

- Nome **Aquelá** sem contorno preto. O branco das letras passa de 0,72 para **1,44 mm**, sobre apoio castanho, sem preto sob a sua projeção.
- A base estrutural da frente passa a castanho. O verso e parte da espessura lateral ficam castanhos; o preto mantém-se nos detalhes do lobo e na decoração da madeira.
- Removidos os traços cinzentos da tabuleta e pequenos fragmentos brancos do limite entre pelo e madeira. O cinzento continua no lobo.
- Olho do lado direito da imagem com uma área branca maior e contínua e pupila simples. Retirados os brilhos brancos das pupilas.
- Folhas ajustadas ao lobo menor, mantendo as nervuras visíveis e a área escondida em verde, plana para colar. A margem de transição escondida é de 0,45 mm.
- Anilha V2 reutilizada sem alterar a geometria ou a abertura interior.

## Medidas nominais

| Elemento | Medidas |
|---|---|
| Conjunto visível, de frente | 52 × 55 mm |
| Lobo e tabuleta | 46,13 × 55 × 4,88 mm |
| Folhas | 52 × 40,62 × 2,96 mm |
| Anilha exterior | 29 × 22 × 25 mm |
| Passagem do lenço | 25 × 18 mm |
| Face plana das folhas para colagem | Z = 2,00 mm |

A redução em X e Y usa fatores diferentes, próximos entre si, para retirar exatamente 10 mm a cada dimensão do conjunto. As espessuras foram mantidas. As dimensões exportadas variam menos de 0,002 mm por discretização da malha; não são tolerâncias garantidas da impressora.

## Ficheiros Bambu

Abrir como **projeto**, conservando os volumes de cor na mesma montagem.

1. [Lobo e tabuleta — A1 / AMS, quatro cores](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v5-LOBO-A1-04-AMS-4-cores.3mf?raw=true): filamentos 1 preto, 2 cinzento, 3 castanho e 4 branco.
2. [Acessórios — A1 / AMS, dois pratos](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v5-ACESSORIOS-A1-04-AMS-2-pratos.3mf?raw=true): filamentos 1 castanho, 2 verde e 3 preto. Prato 1: anilha. Prato 2: folhas.

Confirmar o mapeamento dos rolos no AMS ao mudar de projeto. Não imprimir os STL de cada cor separadamente: são volumes de um único objeto, apoiados na respetiva base. Os STL `completo-monocor` são alternativas de uma cor.

As folhas V4 têm outro tamanho; usar **as folhas V5 com esta frente**. Quem já tem a anilha castanha V2 pode reutilizá-la e imprimir apenas o prato 2 dos acessórios.

## Impressão e colagem

Bambu A1, bico 0,4 mm, PLA, camada 0,12 mm e primeira camada 0,20 mm. Sem suportes ou brim. Paredes exteriores até 25 mm/s e topo até 18 mm/s. Os perfis Generic PLA são pontos de partida, não uma calibração dos rolos atuais.

A purga não é feita dentro das peças nem do infill. Foi conservado o cálculo de purga do Bambu para estas cores, com multiplicador 1,0; preto → branco usa 587 mm³. A maior espessura branca e a remoção do apoio preto reduzem a transparência do fundo, mas não garantem ausência de contaminação entre filamentos. Se o branco continuar sujo, testar a purga com os rolos reais.

Alinhar horizontalmente os centros do lobo e das folhas e apoiar ambos na mesma linha inferior. Colar o verso plano do lobo na zona verde plana. No verso das folhas, centrar a face plana da anilha e colocar o seu bordo inferior a aproximadamente **7,8 mm da base das folhas**. Não colar sobre as nervuras salientes. A passagem do lenço fica orientada de cima para baixo.

Estimativas do Bambu: frente cerca de 2 h 10 min; folhas cerca de 1 h 03 min; anilha cerca de 1 h 16 min. Os relatórios JSON guardam os valores exatos. São estimativas, sem incluir manuseamento ou colagem.

## Verificação

- Malhas fechadas, volumes de cor sem interseções significativas e três peças compatíveis na montagem digital.
- Contacto plano de colagem: aproximadamente 1235 mm² entre frente e folhas e 517 mm² entre anilha e folhas.
- Projetos exportados, reabertos e fatiados em Bambu Studio 02.09.01.70. Sem avisos de impressão, suportes ou brim nos três pratos.
- Comparação dos volumes e das posições relativas entre os STL e o 3MF.
- Leitura dos percursos reais para verificar as sete partes do nome (seis letras e acento), o branco no olho, a ausência de cinzento na tabuleta e de preto sob as letras e no centro escondido das folhas.

**A V5 ainda não teve teste físico de impressão ou colagem.** O resultado de opacidade depende do filamento branco e da purga real.

Os scripts em `fusion/tools/*anilha_aquela_v5*.py` reproduzem a revisão no checkout completo do repositório, com as dependências das versões anteriores. Consultar `geometry.json`, `bambu-validation-lobo.json`, `bambu-validation-acessorios.json` e `toolpath-review.json` para as verificações desta entrega.
