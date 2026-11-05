# M7 — teste laranja V2: percursos dos cantos

Variante de diagnóstico feita a partir do 3MF calibrado enviado pelo utilizador
em 05/11/2026. Contém apenas o fundo laranja de **46,4 × 66,4 × 0,60 mm**;
não contém os relevos da placa decorativa nem o corpo do tijolo.

## O que a análise confirmou

O ficheiro recebido guardou corretamente o fluxo laranja **0,931**, o fluxo
dourado **0,9702**, a sobreposição de **10%**, as **três paredes**, a scarf
desligada e a costura pintada. Não foi encontrado um multiplicador adicional
de fluxo. O utilizador confirmou que imprimiu com a calibração dinâmica ativa.

A análise foi feita com **Bambu Studio 02.09.01.70**, a mesma versão do ficheiro.
O arquivo recebido não continha Gcode da impressão física; os percursos foram
gerados novamente, sem mudar a orientação ou a posição da peça.

O topo original começa no canto inferior direito do prato com uma diagonal de
**0,484 mm**. As linhas crescem progressivamente e voltam a encurtar no canto
oposto. Esse padrão é compatível com os cantos que aparecem piores nas fotos,
admitindo a mesma orientação. Não demonstra, por si só, a causa física.

As paredes internas continuam perto de 98 mm/s e 6000 mm/s² no Gcode; o topo
já usa 25 mm/s e 1000 mm/s². Não foram alteradas essas velocidades ou acelerações
neste ensaio, para manter a comparação concentrada nos percursos.

## Duas alterações

| Definição | Referência do utilizador | V2 |
|---|---:|---:|
| Direção de enchimento — Infill direction | 45° | **0°** |
| Velocidade de preenchimento de lacunas — Gap infill | 250 mm/s configurados | **25 mm/s** |

O ângulo 0° gera 168 linhas de topo de **43,937 mm**, em vez das diagonais
progressivamente curtas. O fatiador também cria duas faixas de preenchimento
de lacunas junto dos bordos. Sem a segunda alteração, essas faixas seriam
impressas a cerca de 128 mm/s efetivos. Ambas ficaram verificadas a **25 mm/s**.

Todos os restantes parâmetros foram conservados. Os ficheiros de geometria,
a pintura da costura, a posição e as configurações de objeto/peça estão
preservados byte a byte. Os percursos das paredes também ficaram iguais.
Sem brim, suportes ou prime tower; sem trocas de cor.

**O ângulo de enchimento também roda os percursos das camadas anteriores.**
Este é um ensaio dirigido aos percursos; não isola exclusivamente a última camada
nem garante que os cantos fiquem resolvidos.

## Utilização

Abra o novo 3MF como projeto e volte a fatiar. Mantenha o mesmo laranja, o fluxo
0,931 e a calibração dinâmica que já estavam a ser usados. Para comparar,
imprima apenas esta unidade e observe os quatro cantos antes de retirar a peça
do prato, depois de arrefecer. Não é necessário repetir os testes de fluxo.

Estimativa nativa: **17 min 37 s e 2,19 g**, incluindo o tempo de preparação
estimado pelo fatiador. A quantidade de material praticamente não muda em
relação ao ficheiro recebido. A impressão física desta variante ainda não foi
realizada. Não foram alterados os projetos de produção do tijolo ou da clínica.

## Ficheiros e reprodução

- Projeto: `downloads/m7-tijolo-teste-laranja-v2-cantos-A1-PLA-1-prato.3mf`.
- Comparação dos percursos: `designs/m7-tijolo-teste-laranja-v2-cantos-percursos.png`.
- Relatório nativo e hashes: `bambu-validation.json` nesta pasta.
- Script: `fusion/tools/build_m7_orange_test_v2.py`.

Para reproduzir, use Python com Pillow, a versão indicada do Bambu Studio e o
3MF original enviado pelo utilizador:

```text
python fusion/tools/build_m7_orange_test_v2.py --source /caminho/original.3mf --bambu-bin /caminho/bambu-studio --work-dir /tmp/m7-laranja-v2
```
