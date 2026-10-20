# Ovo falso M V1 — galinheiro

Ovo de imitação para colocar no ninho, fechado e oco, impresso numa só peça.
Não requer colagem nem tampa. A forma é uma aproximação de um ovo de galinha,
com uma extremidade mais larga e outra mais estreita.

## Dimensões e construção

- Altura: **57 mm**.
- Diâmetro máximo: **43 mm**.
- Parede: **2 mm nominais**, obtidos por um desfasamento interior do perfil.
- Cavidade interior: aproximadamente **41,6 cm³**.
- Pequeno plano na extremidade mais larga: aproximadamente **7,6 mm** de diâmetro.
- Uma peça, branca, sem preenchimento na cavidade.

O tamanho comercial M dos ovos refere-se ao peso (53 a menos de 63 g), não
a dimensões normalizadas. Estas medidas são uma aproximação de um ovo M,
não uma cópia medida de um exemplar fornecido. Por ser oco, este modelo
não tem o peso de um ovo real.

O STL contém duas superfícies fechadas: a exterior e a que limita a cavidade.
É um único corpo com uma cavidade selada. **Não separar em objetos/peças
nem eliminar a superfície interior**: isso faria perder a cavidade.

## Imprimir na A1

Abrir `ovo-falso-M-v1-A1-PLA-1-prato.3mf` **como projeto**, mantendo os perfis.

- Bambu Lab A1, bico de 0,4 mm, prato Textured PEI, PLA branco.
- Extremidade mais larga em baixo; uma peça por prato.
- Camadas de **0,16 mm**, primeira camada de **0,20 mm**.
- Três paredes, Arachne; preenchimento esparso **0%**.
- Paredes exteriores 35 mm/s, interiores 70 mm/s, topo 25 mm/s.
- Brim exterior de 4 mm para aderência.
- Suportes normais ajustados ao contorno (`Snug`), ângulo 30°,
  **apenas a partir do prato**; distância superior de 0,20 mm.
- Uma cor; sem torre de purga ou trocas de filamento.

Os suportes ajudam a imprimir a curva da extremidade inferior e são
removidos por fora. Não foram gerados suportes no interior do ovo.
Podem ficar pequenas marcas junto à base após os remover.

Usar o projeto incluído para conservar o suporte exterior e a orientação.
Ao importar apenas o STL, manter a cavidade e verificar estes parâmetros.
Não usar modo vaso: o ovo precisa de ficar fechado nas duas extremidades.

## Validação e utilização

O STL foi verificado como estanque, com orientação coerente das faces,
dimensões corretas e uma cavidade real. O projeto foi exportado, reaberto e
fatiado no Bambu Studio oficial 02.08.02.61, sem avisos. A análise do G-code
confirma ausência de preenchimento esparso e suportes apenas junto à base.
Os números exatos de altura dos suportes, tempo e consumo estão em
`bambu-validation.json`. O desenho mostra o perfil e o corte reais do modelo.

Não foi feita uma impressão física nem um ensaio de resistência. Para
iniciar, imprimir uma unidade e confirmar que a casca resiste à pressão
normal e que o topo ficou fechado. Retirar o brim e os suportes, deixando
a superfície sem pontas. Se aparecer uma fissura ou se partir, retirar do
ninho. A espessura de 2 mm não é uma garantia de resistência a qualquer carga.

O PLA é adequado como ponto de partida num ninho abrigado. Evitar exposição
ao sol/calor intenso e lavar com água morna, sem água a ferver.

## Ficheiros

- `ovo-falso-M-v1-A1-PLA-1-prato.3mf`: projeto editável configurado para A1.
- `ovo-falso-M-v1-oco.stl`: geometria com a cavidade já modelada.
- `ovo-falso-M-v1-dimensoes.png`: exterior, medidas e corte da parede.
- `geometry-validation.json` e `bambu-validation.json`: verificações.
- `build_ovo_falso_m_v1.py`: gerador; usa os auxiliares em `fusion/tools/`
  do repositório, numpy, trimesh, manifold3d, Pillow e o Bambu Studio oficial.

Para reproduzir a partir do checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/qr-tools/bin/python fusion/tools/build_ovo_falso_m_v1.py
```

Aceita `--bambu-bin`, `--profiles` e `--work-dir`. `--package-only` volta a
criar o ZIP a partir dos ficheiros existentes. O 3MF entregue está por fatiar:
o Bambu Studio calcula o G-code ao abrir e fatiar o projeto.
