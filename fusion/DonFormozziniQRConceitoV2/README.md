# Don Formozzini — três opções com QR demonstrativo

Revisão do esboço a pedido do utilizador: **três opções de placa, cada uma com
um padrão QR completo e visível**, em vez da caixa vazia da primeira proposta.

## Opções

| Opção | Aspeto | Medidas indicativas | Imagem |
| --- | --- | --- | --- |
| **1 — Clássica** | Vertical, marfim e preto, rebordo dourado discreto | Placa cerca de 160 × 110 mm; base 125 × 65 mm | `designs/don-formozzini-qr-opcao-1-classica.png` |
| **2 — Pá de pizza** | Silhueta de pá com pega, terracota e letras claras | Cerca de 190 × 130 mm; base 140 × 65 mm | `designs/don-formozzini-qr-opcao-2-pa-de-pizza.png` |
| **3 — Panorâmica** | Horizontal escura, nome à esquerda e QR à direita, detalhe dourado | Placa cerca de 180 × 115 mm; base 190 × 60 mm | `designs/don-formozzini-qr-opcao-3-panoramica.png` |

As imagens apresentam uma perspetiva e uma vista frontal de cada proposta.
Mantêm o nome Don Formozzini, o subtítulo do restaurante e o convite neutro
**Partilhe a sua experiência**. Não foi acrescentado Instagram sem uma conta
confirmada. As paletas foram contidas para uma futura adaptação à impressão.

### Opção 3 — revisão com a nova referência do utilizador

Imagem atualizada: `designs/don-formozzini-qr-opcao-3-panoramica-logotipo-v2.png`.

O utilizador enviou uma captura com o logótipo circular preto, nome branco e
detalhes verde/branco/vermelho. Esta revisão representa essa identidade num
medalhão à esquerda da placa panorâmica. À direita mantém-se o QR dummy e a
mensagem passa a **Partilhar a sua experiência**, em duas linhas.
As opções 1 e 2 e a primeira versão da opção 3 foram conservadas.

A captura identifica também `www.donformozzini.pt`; esse endereço foi fornecido
visualmente pelo utilizador, mas não foi consultado/validado nesta revisão e
não foi convertido em destino do QR. A localização da proposta continua a ser
Setúbal, conforme o pedido, sem transferir a referência Azeitão de outra
miniatura da captura para a placa.

Para o fabrico, o medalhão pode ser um módulo de quatro cores
(preto/branco/verde/vermelho) e os detalhes dourados peças separadas. Essa
divisão ainda não foi modelada nem validada; o render é uma proposta visual.

## QR dummy

O QR usado como referência visual foi gerado especificamente para este
esboço. O ficheiro `designs/don-formozzini-qr-dummy-sem-link.png` codifica apenas:

```text
DEMONSTRACAO - DON FORMOZZINI - SEM LIGACAO
```

A leitura desse ficheiro fonte foi verificada com OpenCV. Não contém uma URL
e não leva ao Google, a uma conta de Instagram ou a outro site.

Os códigos nas visualizações foram reproduzidos pelo gerador de imagens a
partir dessa referência; a leitura de cada render não foi validada. Servem
apenas para avaliar a presença e proporção do QR no desenho. Cada imagem
identifica-o como **QR demonstrativo — sem destino final**.

O QR final será gerado de novo a partir de uma ligação confirmada e terá de
ser testado quanto à leitura, dimensão dos módulos, contraste e margem livre.
Não utilizar estas imagens ou o dummy como ficheiro de produção de uma placa
com ligações reais.

## Estado

Conceitos visuais, sem CAD/STL/3MF, fatiamento ou teste físico. A tipografia
caligráfica é uma interpretação visual da referência; a reprodução vetorial
do logótipo e os traços mínimos serão trabalhados no projeto aprovado.
As cotas, espessuras, encaixes e estabilidade ainda não são especificações de
fabrico confirmadas.

A pesquisa e a referência da pizzaria estão documentadas na pasta
`DonFormozziniQRConceitoV1`. A opção escolhida pode ser desenvolvida depois da
aprovação visual e da confirmação do destino do QR.
