# M7 — teste do fundo laranja V1

Projeto de diagnóstico pedido após o fundo da placa multicolor apresentar
rugosidade. Imprime **apenas o fundo laranja**, sem árvore, estrela, letras,
corpo do tijolo ou qualquer outro relevo.

## O que imprimir

Abrir **m7-tijolo-teste-laranja-v1-A1-PLA-1-prato.3mf como projeto**.
Um prato e uma peça: **46,4 × 66,4 × 0,60 mm**, três camadas de 0,20 mm.
A1, bico de 0,4 mm, PEI texturado, mesmo laranja usado na placa V7.

- Estimativa Bambu Studio 02.08.02.61: **18 minutos / 2.31 g**.
- **Zero trocas de cor, sem torre, sem brim e sem suportes.**
- Só o filamento lógico **1 laranja** é usado. Os perfis das outras cores
  permanecem no ficheiro original herdado, mas não imprimem neste teste.
- Abrir como projeto e preservar orientação/escala/definições. Não acrescentar
  os STL dos relevos a este prato.

## Condições conservadas da V7

Malha da placa e definições da sua parte preservadas, incluindo posição
no prato e orientação. Material, espessura, temperatura de 220 °C, fluxo 0,98,
três paredes, topo Monotonic line a 25 mm/s, aceleração exterior de 1000 mm/s²,
primeira camada e arrefecimento são os da V7. Não é uma calibração nova nem
uma tentativa de corrigir o fluxo: é um teste da placa nas condições anteriores.

Foram retirados os relevos e o corpo; a torre foi desligada porque já não há
trocas de cor. O projeto completo continua disponível separadamente como V7.
A retirada dos relevos pode afetar classificações/percurso do fatiador, por
isso não se afirma que cada deslocação seja byte a byte a mesma impressão.

## Avaliar

1. Imprimir com a mesma bobina laranja, o mesmo bico e o mesmo prato usados
   na impressão que ficou rugosa. Manter as opções de calibração de envio
   iguais às usadas nessa impressão, para não misturar mudanças no teste.
2. Deixar arrefecer. **Fotografar o topo ainda no prato**, com luz de lado,
   antes de levantar a placa. Assim distinguimos marcas de impressão de uma
   deformação causada ao retirar uma peça de apenas 0,60 mm.
3. Observar o centro, os cantos e se existem ondas ou cristas sentidas ao toque.
4. Retirar com cuidado, sem dobrar, e verificar se está plana.

Se o laranja já sair rugoso aqui, a causa não depende da impressão dos relevos
ou das trocas de cor: investigar a deposição destas três camadas. Se sair liso,
o passo seguinte é observar o que muda durante as fases multicolor; isso não
prova automaticamente que a purga seja a causa. Não repetir ainda a placa
multicolor completa antes de avaliar o resultado.

## Verificação e ficheiros

Ficheiro exportado/reaberto/fatiado com um único objeto e uma única parte
imprimível, dimensões confirmadas e três camadas apenas no filamento 1.
Sem avisos de impressão, suportes, brim ou percursos de prime tower; zero
trocas confirmadas. Estimativas não são medidas físicas e **o teste ainda
não foi impresso neste ambiente**.

3MF editável, relatório, imagem do prato e script de reprodução. O script
depende do projeto V7 e auxiliares no checkout Build; não inicia uma impressão
nem controla o Fusion. Não foram gerados novos STL porque a placa mantém
a malha original da V6/V7.

```sh
python fusion/tools/build_m7_orange_test_v1.py
python fusion/tools/build_m7_orange_test_v1.py --package-only
```
