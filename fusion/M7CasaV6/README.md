# M7 — Casa V6: azul de 2 mm, branco de 4 mm, todos os pratos

Revisão pedida pelo utilizador para dar mais presença ao azul e recuperar as
proporções do conjunto apresentado inicialmente ao cliente. O fundo azul passa
**de 0,80 para 2,00 mm**. O branco passa de 5,20 para **4,00 mm**, mantendo
**6 mm de espessura total**, a face frontal e o encaixe na base existente.

Casa unida na impressão, contornos exteriores azul/branco alinhados, sem
degrau. A altura montada continua em 95 mm, base 85 × 85 mm. Frase azul
«O que fazemos / mostra quem somos» com 0,60 mm de relevo. O rebaixo das
janelas passa de 5,20 a **4,00 mm**, com o azul visível acabado no fundo.

## O que foi mantido

- Todos os quatro pratos do projeto: casa unida, base azul, m branco e 7 ciano.
- **Sem brim nos quatro pratos**; torre de priming ativa na casa.
- Base, m e 7 com STL byte a byte iguais aos da V2/V4/V5. Podem ser reutilizados.
- Correção da V5 no bordo inferior escondido: recorte de 0,728 mm nas duas
  cores para não interferir no fundo da ranhura. Contornos coincidentes.
- Encaixes, inclinação, posição da frase e janelas, geometria da base e logótipo.
- Base com quatro paredes/20% Gyroid, tal como no ficheiro V5 publicado.

## Dimensões e sequência

| Elemento | V5 | V6 |
|---|---:|---:|
| Fundo azul | 0,80 mm | **2,00 mm** |
| Moldura branca | 5,20 mm | **4,00 mm** |
| Espessura total da casa | 6,00 mm | 6,00 mm |
| Relevo azul da frase | 0,60 mm | 0,60 mm |
| Altura montada | 95 mm | 95 mm |
| Ranhura da base | 6,30 mm | 6,30 mm |

Valores de projeto, não medições de uma impressão física.

1. **Z=0,20–2,00 mm:** dez camadas azuis sólidas. Isso dá apoio e opacidade
   ao fundo; apenas as quatro janelas recebem acabamento de topo na última
   camada. A zona coberta pelo branco não tem acabamento de topo dedicado.
2. **Z=2,20–6,00 mm:** vinte camadas brancas. Última camada toda acabada em
   Monotonic a 25 mm/s, incluindo sob a futura frase; sem percursos de
   preenchimento interno ou esparso nessa camada.
3. **Z=6,20–6,60 mm:** três camadas da frase azul. Não há mais branco depois.

São **duas trocas: azul → branco → azul**, confirmadas no G-code. A casa
fica numa única peça, sem colar fundo azul e fachada branca.

## Abrir no Bambu Studio

Abrir **m7-casa-v6-azul-2mm-A1-AMS-4-pratos.3mf como projeto**.
Bambu Lab A1, bico 0,4 mm, PLA, PEI texturado, camada e primeira camada de
0,20 mm. Slots: **1 branco, 2 azul, 3 ciano**. Casa deitada com o azul no prato.
Se já tens base/letras V2/V4/V5, imprime apenas o **prato 1**.

| Prato | Conteúdo | Estimativa | Material incl. torre/purga | Trocas |
|---|---|---:|---:|---:|
| 1 | Casa UNIDA - azul 2mm branco e frase | 2 h 04 min | 31.22 g | 2 |
| 2 | Base azul - encaixes V2 | 2 h 06 min | 40.75 g | 0 |
| 3 | m branco original para colar | 0 h 08 min | 0.21 g | 0 |
| 4 | 7 ciano original para colar | 0 h 08 min | 0.14 g | 0 |
| **Total** | | **4 h 27 min** | **72.32 g** | **2** |

Estimativas Bambu Studio 02.08.02.61; não tempos/pesos medidos. O azul mais
espesso e sólido aumenta o tempo/material da casa face à V5. Os outros pratos
conservam a geometria e as definições de impressão.

Não separar/mover os quatro corpos da casa nem usar orientação automática.
`acabamento-azul-janelas` são quatro pequenas áreas em Z=1,80–2,00 mm:
não são peças para imprimir separadamente no prato. Os sete STL são corpos
de material/modelação; o 3MF conserva a montagem e as definições correspondentes.

Perfis completos Generic PLA A1 a 220 °C e limite volumétrico de 8 mm³/s;
adequar às bobinas reais. Casa com três paredes/15% Gyroid no branco,
base quatro paredes/20% Gyroid. Sem suportes, sem ironing e sem purga no
preenchimento. Não foi imposta correção de fluxo não calibrada.

`Interface shells` permanece ativo para terminar o branco sob as letras.
O corpo azul principal tem topo zero e dez camadas sólidas inferiores; o
acabamento local das janelas está num corpo azul de 0,20 mm. **Não aplicar
as definições de topo zero à fachada branca ou ao objeto completo.**
A torre de priming pode ter a sua própria base de estabilização.

## Encaixe e validação

A distribuição de cores mudou dentro do mesmo envelope total. Verificadas
43 posições de entrada na base V2, sem colisões, com ranhura de 6,30 mm e
casa de 6 mm. Isso não substitui o encaixe físico: apresentar primeiro sem
cola, a direito na direção da ranhura inclinada, sem forçar peças empenadas.

m/7 mantêm os rebaixos de 0,80 mm, folga lateral nominal de 0,20 mm por lado e
reservatórios de cola da V2. Aplicar pouca cola no interior depois de testar.

Verificados: sete STL fechados, contornos exteriores coincidentes dentro da
tolerância numérica, casa conectada, altura de 95 mm, base/letras antigas
preservadas e projeto exportado/reaberto/fatiado sem avisos de impressão.
Os quatro pratos não geram suportes ou brim. G-code confirma dez camadas
azuis, branco todo acabado antes da frase e as duas trocas.
**Sem ensaio físico da V6**; opacidade, acabamento e montagem precisam de
confirmação na primeira peça. Não imprimir o fundo azul antigo além desta casa.

## Conteúdo e reprodução

3MF editável com todos os pratos, sete STL, vistas CAD, relatórios e script
opcional `M7CasaV6.py + geometry.json`. Fusion não foi executado neste ambiente;
não é um F3D validado. Geradores dependem dos auxiliares/dados do checkout
Build. Todas as versões anteriores mantêm-se no repositório.

```sh
python fusion/tools/generate_m7_house_v6.py
python fusion/tools/build_m7_house_v6_3mf.py
python fusion/tools/build_m7_house_v6_3mf.py --package-only
```
