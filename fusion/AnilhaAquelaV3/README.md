# Aquelá V3 — nervuras e contornos pretos nas folhas

Esta revisão acrescenta os riscos escuros pedidos nas folhas: nervuras,
separação entre folhas, ramos laterais e contorno exterior. Os contornos
foram recuperados da referência aprovada e adaptados ao bico de 0,4 mm.
O lobo, a tabuleta, o nome **Aquelá** e a anilha mantêm os ficheiros V2
aprovados, sem alterações. Os hashes estão registados em `geometry.json`.

- [Ver as folhas novas — geometria real](../../designs/anilha-aquela-v3-folhas-CAD.png).
- [Ver o conjunto montado](../../designs/anilha-aquela-v3-montada-CAD.png).
- [Ver os percursos gerados pelo Bambu Studio](../../designs/anilha-aquela-v3-folhas-percursos.png).
- [Descarregar acessórios V3 — 3MF para A1 / AMS](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v3-ACESSORIOS-A1-04-AMS-2-pratos.3mf?raw=true).
- [Descarregar o pacote V3 com o lobo aprovado e acessórios novos](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v3-pacote.zip?raw=true).

## Peça e montagem

As folhas continuam a ser **uma única peça física**, agora impressa com
dois volumes de cor: verde e preto. Não imprimir nem colar as nervuras
separadamente; abrir o 3MF como projeto e manter os volumes alinhados.

| Propriedade | Valor |
| --- | --- |
| Dimensões das folhas | 62 × 48 × 2,96 mm |
| Contorno preto nominal | 0,48 mm |
| Base verde contínua | 1,52 mm |
| Altura da zona central para colagem | 2,00 mm |
| Altura do preto nas folhas expostas | 2,72 mm |
| Altura do verde nas folhas expostas | 2,96 mm |

As nervuras ficam ligeiramente rebaixadas, com 0,24 mm de diferença para o
verde nas folhas expostas. Sob o lobo, ambas as cores terminam no mesmo plano,
conservando a face de colagem. A anilha cola atrás das folhas e o lobo à
frente, com os centros e as bases do lobo/folhas alinhados, como na V2.

## Impressão

O projeto de acessórios tem dois pratos:

1. **Anilha castanha:** uma cor, modelo aprovado V2.
2. **Folhas com nervuras:** verde + preto, num só objeto.

Mapeamento do projeto: filamento 1 castanho, 2 verde, 3 preto. A1 com bico
0,4 mm, camada 0,12 mm e primeira camada 0,20 mm; sem suportes nem brim.
O prato das folhas usa torre de purga para as trocas verde/preto. Perfis
Generic PLA; não é uma nova calibração dos rolos do utilizador.

O lobo continua no projeto
`anilha-aquela-v2-LOBO-A1-04-AMS-4-cores.3mf`, incluído no pacote V3 exatamente
como foi aprovado. O conjunto mantém três peças físicas para colar.

Estimativa das **folhas** no Bambu Studio 2.9.1.70: cerca de **1 h 20 min**, **5,0 g
na peça** e **8,8 g incluindo purgas/torre**, com dez trocas de filamento.

## Verificação

Malhas fechadas, folhas ligadas a uma base contínua, volumes verde/preto
sem interseção volumétrica, sem colisões com o lobo na montagem. Geometria,
cores e transformações comparadas entre STL e 3MF. Exportação, reabertura
e fatiamento nativos concluídos sem avisos de impressão. Os percursos
confirmam a extrusão preta, os dois materiais do prato das folhas e a
ausência de suportes/brim. Resultado em `bambu-validation.json`.

Não foi feito teste físico de impressão ou colagem. As imagens CAD e de
percursos mostram o modelo e o fatiamento, não uma impressão fotografada.

## Reprodução

Na raiz do repositório, com as dependências usadas na V2:

```sh
python fusion/tools/generate_anilha_aquela_v3.py
python fusion/tools/build_anilha_aquela_v3_3mf.py --bambu-bin /caminho/bin/bambu-studio --work-dir /tmp/aquela-v3
```
