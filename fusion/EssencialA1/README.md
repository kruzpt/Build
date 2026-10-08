# Clínica Essencial — Bambu A1

Esta versão resolve o tamanho da peça completa, mantendo os QR de 64 mm.
**O QR Google ainda aponta para o antigo link de partilha/pesquisa. O endereço
direto das avaliações está pendente; esta versão não resolve esse destino.**

## Executar e exportar

Extraia `essencial-fusion-a1.zip` e execute a pasta `EssencialA1` em
**Utilities → Scripts and Add-Ins → Scripts → + / Add** no Fusion.
Cria um documento novo com dois componentes, um corpo por componente.

Exporte **cada componente separadamente** em milímetros. Imprima placa e
base em placas de impressão separadas; o conjunto mostrado lado a lado
no Fusion não cabe inteiro na A1 numa única disposição.

## Dimensões reais, incluindo saliências

| Elemento | Dimensão XY |
| --- | --- |
| Painel retangular | 200 × 198 mm |
| Placa completa, com logótipo e língua | **208 × 242 mm** |
| Envelope da placa com brim de 5 mm em cada lado | **218 × 252 mm** |
| Área nominal Bambu A1 | 256 × 256 mm |
| Base separada | 160 × 70 mm |

A redução é uma reorganização do topo, não uma escala global: mantém o tamanho
dos módulos QR, a espessura da placa, as cavidades NFC e as folgas de encaixe.
O logótipo passa a 64 mm de diâmetro, com metade acima do painel. O nome da
clínica fica à sua direita; a coluna mantém a forma e foi movida 8 mm para baixo.

No Bambu Studio, coloque a face traseira da placa na mesa, à escala 100%,
e centre-a. Use brim de até 5 mm como ponto de partida, confirmando o envelope
e eventuais zonas reservadas pelo perfil antes de imprimir. Não reduza a escala
para caber: isso reduz os QR e a folga para as etiquetas de 25 mm.

## QR, etiquetas e encaixe

Mantém dois QR de 64 × 64 mm, margens brancas, símbolos sociais e contactless.
As zonas NFC e os QR mantêm as posições da V4. Cavidades Ø25,8 mm para etiquetas
Ø25 mm, de Z=3,0 a Z=3,8 mm. Pausa após terminar Z=3,8 mm, antes do teto.
Com camadas constantes de 0,2 mm, incluindo a primeira, pause após a 19.ª
camada e antes da 20.ª; confirme esse ponto na pré-visualização do slicer.

O encaixe da base mantém língua 120 × 5 × 12 mm, ranhura 120,6 × 5,5 mm,
entrada alargada e espaço no fundo. Confirme o encaixe e o bridging sobre
as etiquetas numa amostra; instruções completas em `fusion/EssencialV3/README.md`.

## Google: o que falta

O link de partilha abre Google Search, onde podem aparecer anúncios. Para
abrir diretamente o formulário de avaliação, obtenha **Pedir avaliações** na
gestão do Perfil da Empresa, normalmente um link `g.page/r/.../review` ou
`search.google.com/local/writereview?placeid=...`. Não se pode substituir
`placeid` pelo `kgmid` `/g/11f4pqv2c4`: são identificadores diferentes.

Para quem não tem acesso à gestão, um link da ficha aberta no **Google Maps**
pode fornecer um Place ID/CID para investigação. Não basta o nome pesquisado.
Na cloud, a consulta ao Google foi bloqueada pelo proxy com HTTP 403, por isso
não foi possível obter ou verificar o identificador correto daqui.

## Validação

Envelope completo e espaço para brim calculados; geometria/QR/folgas e pausa
verificados por testes na cloud. Os QR do esquema descodificam para os destinos
atuais (Google ainda provisório). Execução no Fusion, fatiamento no perfil da
A1 e impressão física continuam por validar.

Regenerar: `python fusion/tools/generate_essencial_a1.py` com o venv QR.
