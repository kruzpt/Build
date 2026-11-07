# Gallardo + TOMAS V3 — bico de 0,4 mm e suportes Tree Slim

Novo projeto para **Bambu Lab A1 com bico de 0,4 mm**, com a geometria ligada
da V2. Mantém as dimensões e as duas leituras: Gallardo de lado e TOMAS de cima,
na posição de apresentação. No prato, a peça já está deitada sobre um lado.

## Utilização

1. Abrir `gallardo-tomas-v3-A1-04-PLA-suportes.3mf` como **projeto** no Bambu Studio.
2. Confirmar que a impressora tem um bico físico de **0,4 mm** e que o perfil
   selecionado é **Bambu Lab A1 0.4 nozzle**.
3. O projeto usa um só filamento **PLA preto**, identificado como posição 1.
   Mapear esse filamento para o rolo correspondente no AMS ou para a alimentação
   externa. A posição 1 no projeto não obriga a colocar fisicamente o preto no
   primeiro compartimento do AMS.
4. Fatiar mantendo a orientação e os suportes já ativados. Não é necessário
   pintar os suportes manualmente.
5. Deixar arrefecer e remover os ramos por pequenas secções. Apoiar os traços do
   carro ao retirar as pontas; não puxar toda a árvore usando a peça como alavanca.

O 3MF é editável, inclui perfis completos e não contém percursos antigos em
cache. Não foi enviada uma impressão para qualquer máquina.

**Estimativa nativa final:** aproximadamente **8 h 19 min e 33,3 g de PLA**,
incluindo os suportes.

## O que mudou

| Configuração | V3 |
| --- | --- |
| Máquina / bico | Bambu Lab A1 / 0,4 mm |
| Material | Bambu PLA Basic @BBL A1, preto |
| Camadas / primeira camada | 0,10 / 0,20 mm |
| Paredes | 4, geradas com Arachne |
| Largura mínima configurada no Arachne | 65% do diâmetro do bico |
| Preenchimento | 20% Gyroid |
| Paredes exteriores / interiores | 30 / 50 mm/s |
| Suportes | Árvore automática, **Tree Slim**, só a partir do prato |
| Interface superior | **2 camadas**, espaçamento de **0,45 mm** |
| Folga entre suporte e peça | **0,20 mm em Z**, **0,40 mm lateralmente** |
| Brim / torre de purga | Desativados |

Os perfis de máquina, processo e filamento são os perfis oficiais completos de
0,4 mm, resolvidos a partir dos recursos instalados do Bambu Studio. Não foi
feita apenas uma troca do número do diâmetro no projeto de 0,2 mm.
O processo parte do perfil `0.12mm High Quality @BBL A1`, com camada ajustada
para 0,10 mm e os valores específicos registados em `process-overrides.json`.

O Arachne adapta a largura dos percursos aos traços finos. Um bico de 0,4 mm
continua a ter menor resolução lateral do que um de 0,2 mm; não se promete
reproduzir cada pormenor mínimo com o mesmo acabamento.

## Remoção dos suportes

Em relação à V2 com suporte normal Snug, esta configuração usa ramos em árvore,
mais folga lateral, menos camadas de interface e interface mais espaçada. O
objetivo é facilitar o acesso e a separação dos apoios, mantendo os necessários
para os trechos que começam no ar.

Isto não garante remoção sem marcas: os contactos usam o mesmo PLA da peça e
os traços do carro são delicados. A configuração foi validada geometricamente
e por fatiamento; **a remoção física ainda não foi testada**.
Na comparação efetuada, os suportes em árvore não foram os mais económicos em
material. A seleção privilegia a remoção; os valores estão em
`support-comparison.json` e a estimativa final em `validation.json`.

## O que se passava na tentativa original

O ficheiro enviado já tinha a profundidade e a orientação adequadas. O texto
era constituído por letras sobrepostas; fundi-las numa união geométrica antes
da interseção evita cascas internas sobrepostas nessa operação. Mesmo com essa
união, o recorte deixava dois pequenos detalhes do carro soltos. Na V2, o
reforço do traço das letras ligou esses detalhes ao corpo principal.

A fragmentação extensa da captura anterior não foi reproduzida a partir do
ficheiro guardado antes do Boolean. Além disso, numa camada isolada podem ver-se
troços separados, que se ligam noutras alturas; isso não demonstra que a peça
completa esteja separada. Para este efeito continua a usar-se **Interseção**
entre o nome extrudido e o carro, depois de unir as sobreposições das letras.

## Verificação e reprodução

A V3 conserva a geometria da V2: um único corpo fechado de cerca de
150 × 30 × 37,3 mm na apresentação e 150 × 37,3 × 30 mm na impressão.
`validation.json` contém o hash do 3MF, dimensões, perfis, estimativas nativas,
verificação dos percursos, filamento usado e ausência de avisos de impressão.
`gallardo-tomas-v3-04-suportes.png` mostra camadas reais do G-code, com apoios a azul.

No checkout do repositório, com os ficheiros V2 e numpy, trimesh, manifold3d e Pillow:

```sh
python fusion/tools/build_gallardo_tomas_v3_04.py \
  --bambu-bin /caminho/bambu-studio \
  --profiles /caminho/resources/profiles/BBL \
  --work-dir /caminho/temporario
```

Modelo base de **Dava**, licença **Standard Digital File License** identificada
no original. A autoria e a licença foram conservadas nos metadados do 3MF.
