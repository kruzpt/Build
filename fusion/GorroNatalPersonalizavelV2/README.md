# Gorro de Natal personalizável V2

Enfeite plano de duas cores com uma silhueta clássica: copa vermelha curvada
para a direita, aba branca ondulada e pompom branco com furo integrado de 5 mm.
Mede 92 × 84 × 4,6 mm e imprime deitado, sem suportes e sem brim por defeito.

## Editar o nome no Bambu Studio

Cada 3MF contém um volume **Text shape** nativo. Abra o projeto, selecione o
volume `Nome ...`, use a ferramenta de texto e substitua o conteúdo. A fonte
manuscrita original chama-se `Z003`; se não estiver instalada, o Bambu Studio
pede uma substituição. Depois de mudar o nome, confirme visualmente que fica
dentro da aba branca.

Há três projetos para evitar escalas extremas:

| Projeto | Guia | Exemplo | Tamanho inicial |
| --- | --- | --- | ---: |
| curto | 3–5 letras | Lia | 19 mm |
| médio | 6–8 letras | Tomás | 15,5 mm |
| comprido | 9–11 letras | Alexandre | 11,8 mm |

O tamanho não muda automaticamente quando se escreve outro nome. Escolha o
projeto mais próximo do comprimento pretendido e ajuste `Size` apenas se o
texto ultrapassar a zona branca.

## Construção

- corpo vermelho: 3,0 mm;
- dobra vermelha discreta: +0,4 mm;
- aba e pompom brancos: +0,8 mm;
- nome vermelho: +0,8 mm;
- altura total: 4,6 mm;
- bico previsto: 0,4 mm;
- dois filamentos/AMS, sem suportes.

Os STL foram verificados como malhas fechadas. Os projetos foram criados pelo
Bambu Studio 2.9.1.70 e aceites pelo seu comando oficial `--info`. Cada projeto
foi ainda verificado como uma única montagem com três volumes alinhados, dois
extrusores e um único campo `text_info`. Ainda falta o teste físico e a
confirmação da substituição de fonte no computador do cliente.

O SCAD continua incluído como fonte paramétrica e os scripts regeneram as
malhas e os projetos Bambu.
