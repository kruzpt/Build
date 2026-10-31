# M7 — Casa V4 unida: azul fino, branco e frase

Revisão pedida pelo utilizador: fundo azul e fachada branca passam a ser
**uma única peça impressa**, sem colar essas duas placas. Mantém a frase
«O que fazemos / mostra quem somos», a inclinação, a altura de 95 mm e os
encaixes da base V2. O tijolo M7 não foi alterado.

O pedido posterior de dar acabamento ao azul visível foi aplicado **só nos
quatro fundos das janelas**, sem terminar também toda a área azul que ficará
oculta sob o branco. Esta diferença de tratamento está guardada nos corpos
coloridos do 3MF. A casa continua a precisar de encaixar na base separada;
o m e o 7 continuam separados para colar nos rebaixos dessa base.

## Dimensões e escolhas

| Elemento | Valor | Estado |
|---|---|---|
| Casa montada / base | 95 mm altura / 85 × 85 mm | Preservados da V2 |
| Espessura total principal da casa | 6,00 mm | Preservada para manter o encaixe |
| Fundo azul | 0,80 mm, quatro camadas | Proposta V4 |
| Branco na moldura principal | Até 5,20 mm | Compensa o azul mais fino |
| Frase azul em relevo | 0,60 mm | Preservada |
| Fundo azul da janela abaixo da face branca | 5,20 mm | Mais profundo que na V2 |
| Núcleo do encaixe da base | 6,30 mm | Base V2 inalterada |

A placa azul mantém o contorno ligeiramente recuado original. O branco também
ocupa a faixa antes azul, exceto nas quatro janelas. Isso mantém a face frontal
na posição original e o mesmo envelope nas superfícies de encaixe; evita
alargar a folga na base ao usar um fundo azul mais fino.

Os contornos do m/7, rebaixos de 0,80 mm e reservatórios de cola são os da V2.
Os STL `base-azul`, `m-branco` e `7-ciano` são cópias byte a byte da V2. Podem
ser reutilizados se já estiverem impressos. Não usar base/letras V1 como
substitutos sem rever os encaixes.

## Abrir e imprimir

Abrir **m7-casa-v4-unida-A1-AMS-4-pratos.3mf como projeto**.
**Bambu A1, bico de 0,4 mm, PLA, PEI texturado**, camada/primeira camada de
0,20 mm. A orientação da casa é deitada: azul no prato, branco e frase por cima.
Sem suportes. Slots: **1 branco, 2 azul, 3 ciano**.

Não separar as partes coloridas nem usar orientação automática. Os sete STL
são corpos de material/modelação; os quatro corpos do prato 1 formam uma
única casa e devem manter as coordenadas relativas. O STL de acabamento das
janelas tem quatro pequenas regiões na altura correta: não é para imprimir
separadamente ou mover para o prato.

### Sequência confirmada nos percursos

1. **Z=0,20 a 0,80 mm:** apenas azul. Quatro camadas sólidas de fundo; não há
   acabamento de topo na área que ficará coberta pelo branco. Na última
   camada azul, só os quatro fundos das janelas recebem percursos de topo.
2. **Z=1,00 a 6,00 mm:** apenas branco. A última camada branca tem acabamento
   Monotonic a **25 mm/s** em toda a moldura, incluindo sob a futura frase;
   nessa camada não há preenchimento esparso nem sólido interno.
3. **Z=6,20 a 6,60 mm:** apenas a frase azul em relevo. Não volta ao branco.

São **duas trocas de filamento**: azul → branco → azul. O m foi colocado
num prato próprio para não introduzir branco nas primeiras camadas azuis.
O prato do 7 também é monocromático.

`Interface shells` permanece ativo para terminar o branco sob as letras.
No corpo azul oculto, `top_shell_layers=0` e `top_shell_thickness=0` retiram
apenas o acabamento desse corpo; as quatro camadas de fundo continuam
sólidas. O acabamento das janelas está num corpo azul local de 0,20 mm.
**Não aplicar essas definições de topo zero ao objeto completo, ao branco
ou às outras peças.** São uma opção específica desta construção.

Torre de priming ativa; purga no preenchimento e suportes desativada. Perfis
completos Generic PLA A1, 220 °C no bico e limite volumétrico de 8 mm³/s;
adequar às bobinas reais. Não se aplicou um fluxo não calibrado nem ironing.
Três paredes/15% Gyroid na casa, acabamento branco sem reduzir a uma parede;
base conserva quatro paredes e 20% Gyroid. O acabamento ainda pode mostrar
linhas de impressão ou marcas de fluxo: esta preparação não garante superfície
lisa nem resolve por si só problemas de calibração.

| Prato | Conteúdo | Estimativa | Material incl. purga/torre | Trocas |
|---|---|---:|---:|---:|
| 1 | Casa UNIDA - azul branco frase azul | 1 h 29 min | 24.93 g | 2 |
| 2 | Base azul - encaixes V2 | 2 h 08 min | 40.98 g | 0 |
| 3 | m branco original para colar | 0 h 08 min | 0.25 g | 0 |
| 4 | 7 ciano original para colar | 0 h 08 min | 0.17 g | 0 |
| **Total** | | **3 h 53 min** | **66.33 g** | **2** |

Estimativas Bambu Studio 02.08.02.61, não tempos/pesos medidos. Se já tens
base e letras V2, imprime apenas o **prato 1**. O acabamento local das janelas
acrescentou cerca de 20 segundos ao ensaio sem acabamento azul dedicado.

## Montagem e validação

Apresentar a casa na base a seco, a direito na ranhura inclinada; não forçar
peças empenadas nem usar a cola para corrigir um encaixe apertado. Para m/7,
testar sem cola e aplicar uma pequena quantidade nos reservatórios interiores.
O contorno original das letras e a folga nominal de 0,20 mm por lado mantêm-se.

Verificados: malhas fechadas, um único volume conectado na casa combinada,
sem colisões entre materiais/componentes, 43 posições de entrada na base,
envelope original de encaixe, altura montada e identidade dos três STL V2
reutilizados. Projeto exportado, reaberto e quatro pratos fatiados sem avisos
de impressão ou suportes. O G-code confirma as três fases, as duas trocas,
o acabamento azul limitado às quatro janelas e a última camada branca acabada.

**Ainda sem ensaio físico desta casa unida.** A janela tem um fundo azul mais
fino e um rebaixo mais profundo; confirmar aspeto, opacidade e encaixe na
primeira impressão. Não imprimir a placa de fundo azul V2 além desta casa.

## Conteúdo e reprodução

3MF editável, sete STL, imagem CAD e pratos, relatórios e script opcional
`M7CasaV4.py + geometry.json`. O script cria o conjunto montado no Fusion;
não foi executado no Fusion neste ambiente e não é um F3D validado.
Geradores dependem dos auxiliares/dados existentes no checkout Build.

```sh
python fusion/tools/generate_m7_house_v4.py
python fusion/tools/build_m7_house_v4_3mf.py
python fusion/tools/build_m7_house_v4_3mf.py --package-only
```
