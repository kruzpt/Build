# Clínica Essencial — base QR V10

[Descarregar o 3MF para Bambu A1 / AMS, bico de 0,4 mm](https://github.com/kruzpt/Build/blob/main/downloads/essencial-compacto-v10-dourado-infill-A1-AMS-2-pratos.3mf?raw=true).

O dourado mantém 1,28 mm de espessura, mas passa a ter **duas camadas iniciais em infill gyroid a 15% e seis camadas de fecho**, todas de 0,16 mm. Na V9, as camadas inferiores e superiores do volume dourado sobrepunham-se, tornando sólidas as oito camadas.

Foi retirada apenas a casca inferior dos dois volumes dourados: `bottom_shell_layers = 0` e `bottom_shell_thickness = 0`. Mantêm-se seis camadas superiores / 0,96 mm. O fundo verde continua com as suas camadas inferiores; o verde por baixo do dourado continua sem pele superior.

## Sequência confirmada no fatiamento

| Camada dourada | Altura Z | Percurso interior |
| --- | --- | --- |
| 1 e 2 | 8,48 e 8,64 mm | Infill gyroid a 15% |
| 3 | 8,80 mm | Ponte sobre o infill, início do fecho |
| 4 a 7 | 8,96 a 9,44 mm | Preenchimento sólido interno |
| 8 | 9,60 mm | Superfície superior |

As seis camadas de fecho incluem a ponte inicial. A última camada mantém uma parede exterior; as restantes mantêm três paredes. A costura continua definida para **Traseira** no processo, nos objetos e nos volumes. Mantêm-se a orientação da base, as dimensões, os encaixes, a ausência de brim e de suportes e os perfis de filamento da V9.

No dourado, continuam o flow de 0,9702, a temperatura de 215 °C, paredes e preenchimento sólido interno a 25 mm/s e topo e pontes a 20 mm/s. O infill esparso usa os parâmetros já existentes, atingindo aproximadamente 75,18 mm/s no fatiamento; não foi feita uma nova calibração física do filamento.

## Dois pratos

| Prato | Conteúdo | Tempo estimado | Filamento estimado |
| --- | --- | --- | --- |
| 01 BASE V10 | Base completa | 6 h 51 min | 60,25 g |
| 02 AMOSTRA V10 | Amostra de acabamento e duas linguetas | 2 h 18 min | 20,42 g |

Estimativas do Bambu Studio, incluindo purga e torre. Na base completa, a redução face à V9 é de cerca de 41 minutos e 2,38 g.

**Imprimir primeiro o prato 02 para verificar o acabamento.** A V10 foi reaberta e os dois pratos foram fatiados no Bambu Studio 2.9.1.70, sem avisos de impressão. Os percursos confirmam a sequência acima e uma troca de filamento por prato. As entradas de geometria do 3MF são idênticas às da V9, e as malhas verificadas são fechadas. Esta validação não substitui a impressão da amostra nem confirma ainda a eliminação das marcas observadas.

- [Pré-visualização dos pratos](../../designs/essencial-compacto-v10-dourado-infill-pratos.png)
- [Percursos reais das camadas douradas](../../designs/essencial-compacto-v10-dourado-infill-percursos.png)
- [Relatório de validação](bambu-validation.json)
- [Script de geração e verificação](../tools/build_essencial_compacto_v10_dourado_infill_3mf.py)

Para reproduzir no ambiente de trabalho com as dependências existentes:

```bash
/workspace/.venvs/Build/bin/python fusion/tools/build_essencial_compacto_v10_dourado_infill_3mf.py \
  --bambu-bin /tmp/bambu-studio-2.9.1/squashfs-root/bin/bambu-studio \
  --work-dir /tmp/essencial-v10-validation
```
