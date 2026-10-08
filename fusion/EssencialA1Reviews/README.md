# Clínica Essencial — Bambu A1 com avaliações Google

Esta é a versão atual para a **Bambu A1**, com o endereço de avaliação
que o utilizador confirmou no navegador e no telemóvel. Mantém o tamanho
reduzido da A1; substitui o QR Google que antes abria a pesquisa.

## Executar

Extraia `essencial-fusion-a1-avaliacoes.zip`. Adicione a pasta
`EssencialA1Reviews` em **Utilities → Scripts and Add-Ins → Scripts → + / Add**
no Fusion e execute. Cria um documento novo. Guarde como `.f3d` e exporte cada
componente separadamente, em mm. Imprima placa e base em placas separadas.

## Dimensões mantidas

| Elemento | Dimensão |
| --- | --- |
| Placa completa, incluindo círculo e língua | **208 × 242 mm** |
| Envelope com brim de 5 mm por lado | 218 × 252 mm |
| Painel retangular | 200 × 198 × 5 mm |
| Base separada | 160 × 70 × 18 mm |
| Ambos os campos QR, incluindo margem branca | **64 × 64 mm** |

Use escala 100% no Bambu Studio, face traseira da placa na mesa, centrada.
Confirme a disposição no perfil da A1 e as zonas reservadas pelo slicer.
Não reduza o modelo globalmente: as etiquetas, o encaixe e os QR mantêm
dimensões de fabricação.

## QR e NFC — endereços definitivos deste draft

- **Superior / Instagram:** https://www.instagram.com/clinicaessencial_setubal/
- **Inferior / Google:** https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg

Grave esses mesmos endereços nas etiquetas NFC superior e inferior antes
de as inserir. O script produz os símbolos e cavidades, não programa etiquetas.
O formulário Google pode pedir login; se a pessoa já avaliou, pode mostrar
a avaliação existente para editar, como aconteceu no teste do utilizador.

O novo Google QR usa correção **M** para manter módulos maiores com este URL
mais comprido. A matriz tem 45 × 45 módulos incluindo margem de quatro módulos
por lado: passo 1,422 mm, traço preto mínimo cerca de 1,402 mm. Instagram
mantém correção Q e o mesmo passo. Não há símbolos/logótipos dentro dos QR.

Use módulos pretos, fundo e margem brancos, acabamento mate e bico de 0,4 mm.
Relevo dos QR: 0,6 mm. Teste a leitura da impressão física antes de entregar.
O JPG incluído tem a mesma matriz do novo Google QR impresso.

## Montagem e pausa NFC

Continuam a existir **duas peças**, um corpo sólido por componente. O encaixe
mantém língua 120 × 5 × 12 mm e ranhura 120,6 × 5,5 mm, com entrada alargada e
folga no fundo. Confirme o encaixe numa amostra.

Etiquetas Ø25 mm: cavidades Ø25,8 mm, com piso em Z=3,0 mm e teto a começar
em Z=3,8 mm. **Pause após terminar Z=3,8 mm, antes da primeira camada do teto.**
Com todas as camadas a 0,2 mm, incluindo a primeira, pause após a camada 19,
antes da 20. Confirme na pré-visualização e não gere suportes nas cavidades.
Cole as etiquetas planas no piso e retome para fechar. O draft reserva 0,8 mm
de altura; confirme a espessura da etiqueta/adesivo e teste o bridging do teto.

O logótipo curvo, coluna, símbolos e disposição são preservados da versão A1.
A criação permanece otimizada, com dois sketches e duas extrusões para os QR,
janela de progresso e cancelamento entre etapas.

## Validação

O utilizador confirmou o destino do link e a leitura do JPG anterior de teste no
telemóvel. Na cloud, a nova matriz Google, o JPG correspondente e os dois QR
do esquema foram descodificados para os endereços acima. Envelope, folgas,
pausa e geometria são verificados por testes; o ZIP corresponde ao script.

A execução desta variante no Fusion, fatiamento A1 e impressão física ainda
precisam de confirmação. O esquema é um desenho de disposição, não render CAD.

Regenerar: `python fusion/tools/generate_a1_reviews.py` com o venv QR.
