# Clínica Essencial V3 — Instagram, Google e NFC encapsulado

## Executar no Fusion

Descarregue `essencial-fusion-v3.zip`, extraia e adicione a pasta `EssencialV3`
em **Utilities → Scripts and Add-Ins → Scripts → + / Add**. Execute o script
e guarde o documento novo como `.f3d`. Não altera documentos já abertos.

Continuam a existir duas peças: placa com os detalhes unidos e base separada.
As peças são mostradas deitadas lado a lado, prontas para inspeção/exportação.
O script confirma que cada componente tem apenas um corpo sólido.

## Frente

- Linha superior: símbolo Instagram → QR Instagram → ondas contactless.
- Linha inferior: símbolo Google → QR Google → ondas contactless.
- Não existem inscrições “QR” ou “NFC”. Mantém-se o nome da clínica.
- Cada campo QR inclui uma margem branca de quatro módulos, dentro dos 52 mm.
- Logo no canto superior esquerdo, com a silhueta coplanar com a placa.
- Coluna vertebral em relevo, preservada da V2 corrigida.

Destinos:

- Instagram: https://www.instagram.com/clinicaessencial_setubal/
- Google: https://share.google/2xgo7t8ZFrO7ukORw

O QR Google abre a ficha partilhada, não o formulário de nova avaliação.
As ondas contactless são símbolos; as etiquetas eletrónicas são compradas
à parte e devem ser programadas, uma com cada endereço, antes de inserir.

## Etiquetas NFC internas — pausa na impressão

Imprima a placa **deitada, face decorada para cima, fundo em Z=0**. Há uma
cavidade sob cada símbolo contactless, centros (121,112) e (121,47) mm.

| Medida | Valor |
| --- | --- |
| Etiqueta informada pelo utilizador | circular, Ø25 mm, autocolante fino |
| Cavidade | Ø25,8 mm (0,4 mm livres por lado) |
| Piso da cavidade | Z=3,0 mm |
| Altura livre | 0,8 mm |
| Início do teto | Z=3,8 mm |
| Plástico acima da cavidade | 1,2 mm, até Z=5,0 mm |

1. Programe e teste as duas etiquetas; confirme a espessura real (incluindo
   adesivo). Para este draft, use etiquetas com espessura até cerca de 0,6 mm,
   deixando espaço até ao teto. Altere os valores no script se for necessário.
2. No slicer, configure a pausa **depois de terminar Z=3,8 mm e antes de
   começar a primeira camada do teto**. Com TODAS as camadas de 0,2 mm, inclui
   a primeira, isso significa após a camada 19, antes da camada 20. Se o slicer
   coloca a pausa antes da camada selecionada, selecione a camada 20. Confirme
   o resultado na pré-visualização, não apenas pelo número apresentado.
3. Não gere suportes/infill dentro das duas cavidades. Na pausa, o piso e as
   paredes já devem existir e os dois círculos estar abertos na face superior.
4. Cole cada etiqueta no piso da respetiva cavidade. Deve ficar plana, abaixo
   de Z=3,8 mm, sem invadir o percurso do bico. A etiqueta superior é Instagram;
   a inferior é Google. Retome a impressão para fechar as cavidades.
5. Teste a leitura no telemóvel através da face final.

O teto exige uma ponte de cerca de 26 mm. Inspecione bridging no slicer e
faça uma pequena amostra desta região antes de imprimir a placa inteira.
Não se assume que o teto fica bem impresso sem esse teste. Verifique também
a temperatura de serviço da etiqueta junto do fornecedor antes de encapsular.

As cavidades estão completamente fechadas no CAD final: não há tampas extras
nem acesso pela face traseira depois de imprimir.

## Logo e cores

O E foi redesenhado manualmente a partir da imagem: serifas e curvas
assimétricas, sem barra central, duas estrelas de lados curvos e o ponto.
Está gravado 0,6 mm na face do círculo, preservando um único corpo da placa.
É uma aproximação da referência raster, não o ficheiro vetorial original.

Pinte o círculo rosa e o E/estrelas/ponto brancos para reproduzir a marca.
Os símbolos sociais são monocromáticos. Mantenha os módulos QR pretos e as
áreas em volta brancas. Não coloque tinta ou decorações nas margens do QR.
Uma troca de cor por camada pode colorir vários detalhes ao mesmo tempo;
use pintura ou seleção por região para cores independentes.

## Base e impressão

O encaixe da V2 é preservado: língua 120 × 5 × 12 mm, ranhura 120,6 × 5,5 mm,
profundidade 12,8 mm, entrada alargada e 0,8 mm de espaço no fundo. Ajuste a
folga depois de uma amostra. Bico de 0,4 mm; QR de 52 mm com módulos superiores
a 1 mm e relevo de 0,6 mm, ondas contactless com traço de 1,4 mm.

O conjunto da placa ocupa aproximadamente 190 × 270 mm; confirme que cabe
na mesa, rodando no plano XY se necessário, sem mudar o Z de pausa.

## Validação e ficheiros

O PNG `essencial-v3-esquema.png` é um esquema, não um render CAD. As curvas
laterais da coluna são simplificadas; o script mantém as vértebras da V2.
Os QR do esquema foram descodificados para os endereços acima.

A sintaxe, os contornos, a separação dos elementos e o espaço das cavidades
são verificados na cloud. A V3 não foi executada no Fusion; impressão, ponte
do teto, encaixe e leitura física NFC/QR continuam por validar. Se a extrusão
de texto não funcionar com as fontes instaladas, o nome permanece em sketch
e o script avisa. Outros erros aparecem com traceback completo.

Regenerar: `python fusion/tools/generate_essencial_v3.py` com as dependências
de `fusion/tools/requirements-qr.txt`. O script Fusion entregue não precisa
dessas dependências: as matrizes QR e os contornos estão incluídos no `.py`.
