# Joana, 12 anos — topper de aniversário

Modelo em relevo inspirado no mundo de Harry Potter, com o nome Joana,
o número 12, castelo, chapéu, lua, estrelas, raio e vassoura.
Os contornos foram derivados do esboço aprovado e simplificados para impressão.
O CAD é uma peça plana com relevo: as texturas e volumes esculpidos da imagem
conceptual não fazem parte desta versão.

## Ficheiros e medidas

- `joana-topper-v1-A1-AMS-4-cores.3mf`: projeto nativo Bambu Studio, já montado.
- `JoanaTopper.py` e `contours.json`: criação de sólidos e sketches no Fusion.
- `joana-topper.svg`: contornos vetoriais a tamanho real, com quatro cores.
- Quatro STL separados por cor, com a mesma origem e alinhamento.
- `joana-topper-v1-completo.stl`: união de todas as cores, para impressão monocromática.
- `joana-topper-v1-CAD.png`: imagem do modelo real, diferente da imagem conceptual.

Largura **180 mm**, altura total **200,3 mm**, incluindo duas hastes de cerca
de **7,7 mm de largura**. Base preta de **2,4 mm**; dourado e castanho sobem
mais **0,8 mm** e o bordô sobe **0,4 mm**. Espessura máxima **3,2 mm**.
Os pormenores muito pequenos foram filtrados; pontas decorativas podem ser
arredondadas pelo fatiador com o bico de 0,4 mm.

## Bambu Studio — impressão com AMS

Abra o **3MF como projeto**, conservando as definições. É um objeto único
com quatro partes, num prato. Não há necessidade de pintar as cores à mão.

| Slot no projeto | Filamento |
| --- | --- |
| 1 | Preto |
| 2 | Amarelo/dourado |
| 3 | Castanho escuro |
| 4 | Bordô |

Mapeie estes quatro slots às bobinas reais do seu AMS ao enviar a impressão.
O projeto usa **Bambu Lab A1, bico 0,4 mm, PLA, Textured PEI**, camada de
**0,20 mm**, três paredes, 20% gyroid, cinco camadas superiores e inferiores,
Arachne, parede exterior a 80 mm/s e superfície superior a 40 mm/s.
Imprime deitado com a frente decorada para cima, sem suportes nem brim.
Mantenha a torre de purga e as purgas entre cores para preservar o amarelo.

O perfil base é Generic PLA @BBL A1, 220 °C no bico, 65 °C na Textured PEI,
fluxo máximo de 12 mm³/s. Ajuste o perfil se as bobinas forem de outro tipo;
PLA dourado silk pode precisar de definições próprias. Fatie depois de ajustar.

O motor oficial Bambu Studio **2.8.2.61** exportou, reabriu e fatiou o 3MF
sem avisos: **16 camadas, sete trocas de filamento**, cerca de **2 h 22 min**
e **58 g de PLA no total**, incluindo purgas. São estimativas, não medições
de impressão. O 3MF entregue é editável e não contém G-code pré-calculado.
O arranjo roda a peça em XY para a acomodar na mesa com a torre de purga;
a largura original do topper continua a ser 180 mm.

## Autodesk Fusion

1. Extraia a pasta `JoanaTopper` do ZIP, conservando o script e `contours.json`
   lado a lado.
2. No Fusion, abra **Utilities → Scripts and Add-Ins → Scripts**.
3. Adicione a pasta `JoanaTopper` pelo botão de adicionar scripts e execute-o.
4. O script abre um documento novo com quatro componentes de cor, sketches
   e extrusões. Guarde o documento como **.f3d**.

Não precisa de bibliotecas Python externas nem de instalar uma fonte.
O nome e a idade são contornos fixos, preservando a tipografia do esboço;
não são campos de texto editáveis. Para outra inscrição, os contornos devem
ser redesenhados.

Para outro tamanho, altere **`TARGET_WIDTH_MM = 180.0`** no início do script.
A escala afeta XY e as hastes; preserva a espessura. Depois de mudar a largura,
execute para criar um novo documento e volte a fatiar o modelo atualizado.
O 3MF fornecido corresponde apenas aos 180 mm. O script tem progresso e
cancelamento entre cores. A execução dentro do Fusion ainda precisa de ser
confirmada; a geometria STL e a montagem/fatiamento Bambu foram verificados.

Para colocar no bolo, cubra as hastes com mangas ou tubos adequados a contacto
alimentar; o filamento e o acabamento desta impressão não foram certificados
para contacto direto com alimentos.

## Acesso ao plugin Fusion e Bambu

A imagem fornecida mostra **um plugin instalado com uma app ligada**.
Nesta sessão, o catálogo de ferramentas e skills não disponibilizou nenhuma
capacidade Fusion/Bambu, e não havia uma skill local correspondente. Não é
possível ativar essa ligação da conta a partir do repositório cloud.

Na página do plugin, utilize **Try now** para o invocar. Se continuar sem
ferramentas, confirme em **Manage** que o plugin/app está disponível na conversa
que irá usar. A implementação aqui usou os scripts Fusion e a CLI oficial
Bambu Studio no ambiente cloud; não foi enviada uma impressão à máquina.

## Reproduzir os ficheiros

```sh
python fusion/tools/generate_joana_topper.py
python fusion/tools/build_joana_topper_3mf.py \
  --bambu-bin /caminho/bambu-studio \
  --profiles /caminho/resources/profiles/BBL
```

O gerador reutiliza os contornos aprovados de `contours.json`. A primeira
conversão da imagem utilizou `--reference IMAGEM.png --width 180`. Os relatórios
`geometry-validation.json` e `bambu-validation.json` distinguem a geometria
verificada das etapas ainda sem teste físico ou execução no Fusion.
