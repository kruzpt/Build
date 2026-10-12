# Grelha V3 — Bambu A1, PLA, dois pratos

Abra [o 3MF de dois pratos](../../downloads/grelha-pintos-v3-A1-PLA-2-pratos.3mf?raw=true)
**como projeto** no Bambu Studio e conserve as definições incorporadas.

| Prato | Conteúdo | Quantidade a imprimir |
| --- | --- | --- |
| 01 | Uma placa universal | Repita este prato dez vezes para o piso 2 × 5 |
| 02 | 26 presilhas padrão | Um prato para unir as dez placas |

São dois pratos organizados por tipo de peça. Não há pratos de teste nem
cópias repetidas da placa no projeto. As 26 presilhas correspondem a duas
por interface, nas 13 interfaces entre as dez placas.

## Medidas e definições preservadas

A geometria continua exatamente a da V3: placa **217,3 × 179,8 × 30 mm**,
aberturas **8 × 8 mm**, redução de **0,2 mm por módulo** em ambas as direções,
oito alojamentos inferiores e presilha padrão com o mesmo gancho e folgas.
Não foi aplicada escala para organizar os pratos.

| Definição | Placa universal | Presilhas padrão |
| --- | --- | --- |
| Camada | 0,20 mm | 0,16 mm |
| Paredes | 3 | 4 |
| Preenchimento | 20% gyroid | 100% alinhado retilíneo |
| Camadas superiores / inferiores | 5 / 5 | 6 / 6 |
| Parede exterior / interior | 60 / 90 mm/s | 25 / 40 mm/s |
| Brim | Exterior, 3 mm, separação 0,15 mm | Sem brim |
| Suportes | Desligados | Desligados |

Mantêm-se o gerador Arachne, a primeira camada de 0,20 mm, a compensação
do pé de elefante de 0,10 mm e todos os restantes ajustes do projeto anterior.
A impressora é **Bambu Lab A1, bico 0,4 mm**. O perfil **Generic PLA @BBL A1**
usa 220 °C no bico, 65 °C na Textured PEI e fluxo máximo de 8 mm³/s.
As temperaturas devem corresponder à bobina e à superfície utilizadas.

A placa imprime com a face de apoio na mesa e os pés para cima; vire-a
depois da impressão. As presilhas imprimem deitadas de lado. Os parâmetros
das presilhas estão **por objeto**: selecione uma em Objetos para ver
0,16 mm e 100%, mesmo que o painel global mostre 0,20 mm e 20%.

O encaixe em PLA continua sem ensaio físico de retenção ou fadiga. Pode
imprimir uma presilha e testar numa placa antes de repetir a produção;
a [amostra de duas bordas](../../downloads/grelha-pintos-v3-amostra-duas-bordas.stl?raw=true)
também continua disponível separadamente.

## Validação e utilização

O projeto foi exportado, reaberto e os **dois pratos foram fatiados** com
o motor oficial Bambu Studio. A validação verifica dimensões, orientação,
ausência de sobreposição e espaço para brim dentro da área útil da A1.
O G-code de validação tem 150 camadas para a placa e 40 para as presilhas.
O ficheiro entregue é editável, sem G-code pré-calculado: use **Fatiar todos
os pratos** após confirmar a bobina.

O consumo estimado é cerca de **76,4 g por placa** e **8,2 g para as 26
presilhas**. Para dez placas, repita apenas o prato 01; o conjunto fica
perto de 772 g com estas definições, sem contar falhas ou testes.

[Mapa dos dois pratos](../../designs/grelha-pintos-v3-PLA-2-pratos.png).
As miniaturas são vistas superiores da geometria exportada. O relatório
`validation-2-pratos.json` identifica o ficheiro validado pelo seu SHA-256.
O projeto anterior de 13 pratos e o respetivo relatório ficam preservados.

## Reproduzir

Usa exatamente os mesmos três ficheiros de ajustes deste diretório:
`process-overrides.json`, `clip-overrides.json` e `filament-overrides.json`.

```sh
python fusion/tools/build_pintos_pla_3mf.py \
  --layout 2-pratos \
  --bambu-bin /caminho/bambu-studio \
  --profiles /caminho/resources/profiles/BBL
```

Sem `--layout 2-pratos`, o gerador conserva a opção anterior de 13 pratos.
Não precisa do Python para abrir o 3MF e não são enviados trabalhos à impressora.
