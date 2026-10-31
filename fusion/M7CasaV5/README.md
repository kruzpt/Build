# M7 — Casa V5: azul/branco alinhados e sem brim

Corrige o degrau da V4: **fundo azul e fachada branca têm o mesmo contorno
exterior**, sem o recuo de 0,80 mm herdado do antigo fundo separado. São uma
única casa impressa, com azul de 0,80 mm e moldura branca de 5,20 mm, espessura
total de 6 mm e frase azul de 0,60 mm. A janela mantém o fundo azul acabado.

**Brim desligado nos quatro pratos**, por preferência expressa do utilizador.
A torre de priming mantém-se para as duas trocas de cor na casa. A torre não
é o brim da peça; não apagar ou deslocar os corpos coloridos.

## Compatibilidade e dimensões

| Parâmetro | V5 | Origem |
|---|---|---|
| Altura montada / base | 95 mm / 85 × 85 mm | Preservados da V2 |
| Espessura azul / branco | 0,80 / 5,20 mm | Preservadas da V4 |
| Contorno exterior das duas cores | Idêntico, incluindo telhado e laterais | Correção V5 |
| Relevo da frase | 0,60 mm | Preservado |
| Ranhura inclinada da base | 6,30 mm | Base V2 inalterada |
| Folga lateral dos rebaixos m/7 | 0,20 mm por lado | Projeto V2, a testar fisicamente |

Ao alargar o fundo azul até ao contorno branco, o bordo inferior antigo
interferia com o fundo da ranhura inclinada. Foi retirado **apenas 0,728 mm
no bordo inferior escondido, igualmente nas duas cores**. Isso conserva os
contornos alinhados, a face frontal, a posição das janelas/frase e a altura
montada; evita alterar a base ou levantar a casa inteira.

**Base, m e 7 são STL byte a byte iguais aos da V2/V4**, e podem ser reutilizados.
A entrada da nova casa nessa base foi verificada em 43 posições, sem colisões.
Isto é validação geométrica, não uma montagem física já experimentada.

## Projeto de impressão

Abrir **m7-casa-v5-alinhada-A1-AMS-4-pratos.3mf como projeto**. A1, bico de
0,4 mm, PLA, PEI texturado, camada/primeira camada de 0,20 mm, sem suportes.
Slots: **1 branco, 2 azul, 3 ciano**. Casa deitada, azul contra o prato.
Se já tens a base e as letras V2/V4, imprime apenas o **prato 1**.

Os quatro corpos coloridos desse prato formam uma única casa. O corpo
`acabamento-azul-janelas` são quatro áreas azuis locais à altura de 0,60–0,80 mm:
não imprimir separadamente nem mover para o prato. Não separar os corpos ou
ativar orientação automática. Preferir o 3MF para preservar estas definições.

| Prato | Conteúdo | Estimativa | Material incl. torre/purga | Trocas |
|---|---|---:|---:|---:|
| 1 | Casa UNIDA - azul branco frase azul | 1 h 28 min | 24.86 g | 2 |
| 2 | Base azul - encaixes V2 | 2 h 06 min | 40.75 g | 0 |
| 3 | m branco original para colar | 0 h 08 min | 0.21 g | 0 |
| 4 | 7 ciano original para colar | 0 h 08 min | 0.14 g | 0 |
| **Total** | | **3 h 50 min** | **65.97 g** | **2** |

Estimativas do Bambu Studio 02.08.02.61; não tempos ou consumos medidos.
Perfis completos Generic PLA A1, bico 220 °C, limite volumétrico 8 mm³/s;
adequar às bobinas e ao bico realmente instalado. Não foi imposta correção
de fluxo não calibrada. Sem ironing e sem purga no preenchimento.

## Sequência e acabamento preservados

- **Z=0,20–0,80 mm:** quatro camadas azuis. Só os fundos das quatro janelas
  recebem acabamento de topo na última; a área azul coberta pelo branco
  fica sem acabamento de topo dedicado.
- **Z=1,00–6,00 mm:** branco. A última camada é acabada em toda a moldura,
  incluindo sob as letras futuras: Monotonic a 25 mm/s, sem percursos de
  preenchimento interno ou esparso nessa camada.
- **Z=6,20–6,60 mm:** frase azul. Branco completamente terminado antes dela.

Duas trocas: azul → branco → azul. O m e o 7 estão em pratos monocromáticos
próprios para evitar introduzir branco nas primeiras camadas azuis da casa.
`Interface shells` continua ativo para o acabamento branco sob a frase.
O corpo azul oculto tem topo zero mas quatro camadas sólidas inferiores;
**não aplicar topo zero à fachada branca ou ao objeto completo**.

Casa com três paredes/15% Gyroid; base com quatro paredes/20% Gyroid,
conservados. Brim type `no_brim` em todos os pratos. Confirmadas exportação,
reabertura e fatiamento nativos sem avisos de impressão, suportes ou brim
nas peças. A torre pode ter a sua própria base de estabilização.

## Montagem e limites

Apresentar a casa na base a seco, na direção da ranhura inclinada; não forçar
uma peça empenada. m/7 mantêm os rebaixos de 0,80 mm e os reservatórios da
V2; aplicar pouca cola no interior depois de testar o encaixe.

Verificados: sete STL fechados, contornos azul/branco coincidentes dentro
da tolerância numérica, um único conjunto conectado, altura de 95 mm,
43 posições de entrada, base/letras antigas preservadas e sequência de cor
no G-code. **Sem ensaio físico da V5**. O acabamento continua a depender da
calibração e do filamento; não se promete superfície sem linhas de impressão.

## Ficheiros e reprodução

Inclui 3MF, sete STL, vistas CAD montada e frente/verso, pratos, relatórios e
script opcional `M7CasaV5.py + geometry.json`. Fusion não foi executado neste
ambiente; não se fornece um F3D validado. Os geradores dependem dos auxiliares
e dados existentes no checkout Build. Versões anteriores preservadas.

```sh
python fusion/tools/generate_m7_house_v5.py
python fusion/tools/build_m7_house_v5_3mf.py
python fusion/tools/build_m7_house_v5_3mf.py --package-only
```
