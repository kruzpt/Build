# Biblioteca de filamentos do utilizador — A1

Os perfis de **utilizador** guardados no Bambu Studio ficam disponíveis nos
projetos seguintes. Não é necessário recuperar as configurações de um 3MF
antigo sempre que se muda de peça.

## Instalar o perfil laranja uma vez

1. Descarregar `sunlu-pla-plus-laranja-0931-A1-04.json`.
2. No Bambu Studio, usar **Ficheiro → Importar → Importar configurações…**
   (**File → Import → Import Configs…**) e selecionar esse JSON.
3. Selecionar a impressora **Bambu Lab A1, bico de 0,4 mm**.
4. Na lista de filamentos, escolher o perfil de utilizador:
   **SUNLU PLA+ Laranja 0.931 @BBL A1 0.4**.

A importação guarda o perfil na biblioteca de utilizador do Bambu Studio. Nos
projetos seguintes basta selecioná-lo na lista de filamentos. Se já existir
um perfil com exatamente o mesmo nome, o Bambu pode pedir confirmação para
substituir essa versão; isso é uma decisão apresentada pela própria aplicação.

Este perfil está limitado à **A1 com bico de 0,4 mm**, para a qual dispomos da
calibração. Aplica-se a qualquer projeto compatível, não apenas ao Gallardo
ou às placas M7. Não foi preparada uma calibração para outro bico ou material.

Para usar noutro computador, voltar a importar o JSON, ou recorrer à
sincronização de perfis da conta Bambu quando estiver configurada. Conservar
o JSON também permite recuperar o perfil depois de reinstalar a aplicação.

## Valores recuperados

| Definição | Perfil laranja |
| --- | --- |
| Material identificado no projeto de origem | SUNLU PLA+ laranja |
| Base do perfil | Generic PLA @BBL A1 |
| Fluxo / Flow ratio | **0,931** |
| Temperatura do bico, inicial e seguintes | **220 °C** |
| PEI texturado, inicial e seguintes | **65 °C** |
| Velocidade volumétrica máxima | **8 mm³/s** |
| Ventoinha, mínimo / máximo | **60% / 80%** |
| Cor predefinida | **#C85D2E** |

Os parâmetros de material foram recuperados do laranja calibrado no projeto
M7 V9. O perfil tem um nome estável e não contém nomes de projetos anexados,
identificadores de conta ou credenciais. A cor predefinida é uma opção visual;
o rolo físico tem de ser escolhido no mapeamento do AMS ou alimentação externa.

As camadas, paredes, preenchimento e suportes continuam a pertencer ao
**processo de impressão**. Escolher o laranja não obriga a usar as configurações
da placa M7 ou do Gallardo noutros modelos.

Este ficheiro guarda o fluxo 0,931 e os restantes parâmetros de material.
A calibração dinâmica de fluxo/valor K da impressora é uma configuração
distinta: não foi inventado nem identificado um novo K como calibração deste
perfil. Conservar a utilização habitual da calibração dinâmica, quando aplicável.

## Gallardo já preparado com o laranja

`gallardo-tomas-v4-A1-04-laranja-0931-suportes-ON.3mf` conserva toda a geometria,
posição, orientação do nome e configurações de objeto da V4. Foi aplicado o
perfil laranja e a respetiva cor ao filamento 1. Os suportes Tree Slim continuam
ativos no processo e no objeto. Abrir o 3MF como **projeto** e mapear o filamento
para o rolo laranja antes de imprimir.

Estimativa para o Gallardo com este perfil: **8 h 08 min e 30,7 g de PLA**,
incluindo os suportes, segundo o fatiador.

O perfil importado na biblioteca e o perfil incluído num projeto são coisas
distintas: abrir apenas o 3MF não substitui a importação do JSON para guardar
o material permanentemente como perfil de utilizador.

## Verificação

O formato foi conferido no código oficial do Bambu Studio:

- [Importação e gravação de perfis](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PresetBundle.cpp).
- [Parâmetros do perfil de filamento e cor predefinida](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Preset.cpp).

O importador reconhece `filament_settings_id`, nome e versão, aplica a herança
e grava o perfil de utilizador. A validação local carregou o JSON no Bambu
Studio por CLI e confirmou os parâmetros efetivos. O Gallardo foi novamente
fatiado para verificar o perfil, os suportes, o filamento e os limites de
velocidade. Os resultados e hashes estão em `orange-validation.json`.

**Não foi feita instalação na biblioteca do computador do utilizador**, nem
testada a interface Windows por ligação remota. A importação descrita acima
tem de ser feita uma vez pelo utilizador. Não foi iniciada nenhuma impressão.

## Reprodução

No checkout do repositório, com os projetos de origem presentes:

```sh
python fusion/tools/build_orange_user_filament_v1.py \
  --bambu-bin /caminho/bambu-studio \
  --profiles /caminho/resources/profiles/BBL \
  --work-dir /caminho/temporario
```
