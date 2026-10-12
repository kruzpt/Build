# Projeto Bambu Studio — A1, bico 0,4 mm, PLA, presilha padrão

Abra `grelha-pintos-v3-A1-PLA-13-pratos.3mf` **como projeto** no Bambu Studio,
conservando as definições incorporadas. O ficheiro é editável e contém
geometria, impressora, filamento, parâmetros e pré-visualizações de **13 pratos**.
O projeto foi criado e reaberto com Bambu Studio **2.8.2.61**.

## Pratos

| Prato | Conteúdo | Utilização |
| --- | --- | --- |
| 01 | Duas bordas de amostra | Testar o encaixe |
| 02 | Uma presilha padrão | Testar PLA antes da produção |
| 03–12 | Uma placa universal por prato, dez no total | Piso 2 × 5 |
| 13 | 26 presilhas padrão | Unir as dez placas |

O prato 02 tem uma presilha de teste adicional; não é uma das 26 do prato 13.
Não há variantes suave/firme nem PETG neste projeto. A geometria é exatamente
a da V3, sem alterar dimensões ou ganchos: placa **217,3 × 179,8 × 30 mm**,
aberturas **8 × 8 mm**, redução de **0,2 mm por placa** nas duas direções.

Os STL anteriores e os respetivos scripts Fusion ficam preservados.

## Definições já guardadas

| Definição | Placas e bordas | Presilhas padrão |
| --- | --- | --- |
| Camada | **0,20 mm** | **0,16 mm** |
| Paredes | **3** | **4** |
| Preenchimento | **20% gyroid** | **100% alinhado retilíneo** |
| Camadas superiores / inferiores | 5 / 5 | 6 / 6 |
| Velocidade parede exterior | 60 mm/s | 25 mm/s |
| Velocidade parede interior | 90 mm/s | 40 mm/s |
| Brim | Só exterior, 3 mm, separação 0,15 mm | Sem brim |
| Suportes | Desligados | Desligados |

Gerador de paredes **Arachne** para as barras e paredes finas. Primeira camada
0,20 mm, velocidade exterior 20 mm/s e preenchimento 30 mm/s. Compensação do
pé de elefante de 0,10 mm. Aceleração geral limitada a 3000 mm/s² e exterior
a 1500 mm/s². A geometria já está orientada: placas/bordas com a face de apoio
na mesa e pés para cima; presilhas deitadas de lado.

Perfil oficial **Generic PLA @BBL A1**, com limite de fluxo de 8 mm³/s:
**220 °C no bico e 65 °C na placa Textured PEI**. Confirme que essa placa e
essas temperaturas correspondem à sua bobina e superfície; ajuste o filamento
se necessário e volte a fatiar. Não substitua o perfil por PETG neste projeto.

As definições específicas das presilhas estão **por objeto**. O painel global
pode continuar a mostrar 0,20 mm e 20%; selecione a presilha em **Objetos**
para ver os seus 0,16 mm e 100%. O fatiamento confirmou 40 camadas nas presilhas,
em vez das 32 que resultariam de 0,20 mm.

## Porque esta combinação

As barras de 1,6 mm e muitas paredes dos alojamentos já ficam quase maciças
com estas paredes: reduzir o preenchimento para valores muito baixos pouparia
pouco nessas zonas. Mantive 20% no restante interior, sem afinar a geometria.
As presilhas são pequenas; o preenchimento sólido e as velocidades menores
priorizam a ligação entre filamentos e o acabamento dos ganchos.

**Configurações de impressão não eliminam a menor flexibilidade do PLA.**
A presilha padrão foi inicialmente proposta para PETG; neste projeto usa-se
o mesmo gancho em PLA, conforme pedido. Imprima primeiro os pratos **01 e 02**,
teste inserção e desmontagem sem rachar, e só depois imprima a produção.
A retenção, fadiga e carga reais ainda não foram ensaiadas fisicamente.

## Fatiamento verificado

O ficheiro entregue está **sem G-code pré-calculado**, para continuar editável.
Selecione o filamento correto e use **Fatiar todos os pratos** no Bambu Studio.
Os 13 pratos foram fatiados na validação com o motor oficial, sem avisos de
impressão. Dimensões, posições, ausência de sobreposição e folga à zona
reservada da A1 foram verificadas no 3MF final.

Estimativas desse fatiamento: cerca de **76,4 g por placa**, **8,2 g para as
26 presilhas**, e **5,4 g para os dois pratos de teste**. São estimativas
dependentes da calibração, bobina e definições mantidas. O consumo não foi
medido numa impressão real.

As pré-visualizações são vistas superiores calculadas da geometria realmente
exportada, com a posição dos objetos de cada prato. Não são imagens geradas
por descrição. `validation.json` regista a versão nativa, hash do projeto,
resultados e contagens de camadas.

## Reproduzir o projeto

Os ficheiros `process-overrides.json`, `clip-overrides.json` e
`filament-overrides.json` contêm apenas os ajustes. A impressora e os valores
de base vêm dos perfis oficiais incluídos no Bambu Studio.

Com o ambiente Python de geração e a CLI oficial instalada:

```sh
python fusion/tools/build_pintos_pla_3mf.py \
  --bambu-bin /caminho/bambu-studio \
  --profiles /caminho/resources/profiles/BBL
```

Não precisa desse ambiente para abrir ou imprimir o 3MF. As verificações
de G-code são executadas localmente; o script não envia trabalhos à impressora.
