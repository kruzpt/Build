# Universo do Saber V10 — superfície superior sem ironing

Esta versão mantém **exatamente a geometria da V9** e cria um novo perfil de
impressão para melhorar a superfície superior sem recorrer a ironing. O projeto
continua destinado à Bambu Lab A1, bico de 0,4 mm, PLA e AMS Lite.

Abra o [3MF de dois pratos](../../downloads/universo-saber-suporte-v10-topo-sem-ironing-A1-AMS-2-pratos.3mf)
como **projeto** no Bambu Studio. O [esquema dos pratos](../../designs/universo-saber-suporte-v10-topo-sem-ironing-pratos.png)
permite confirmar a disposição antes de voltar a fatiar.

## Perfil V10

| Parâmetro | Valor |
| --- | ---: |
| Altura de camada | 0,20 mm |
| Ironing | **desativado em todas as peças** |
| Uma parede nas superfícies superiores | **todas as superfícies de topo** |
| Camadas superiores gerais | **8 / 1,6 mm** |
| Camadas superiores da base azul | **9 / 1,8 mm** |
| Padrão da superfície | Monotonic line |
| Velocidade da superfície superior | **20 mm/s** |
| Aceleração da superfície superior | **800 mm/s²** |
| Preenchimento sólido interno | **45 mm/s** |
| Parede exterior / interior | 35 / 70 mm/s |
| Paredes gerais / base | 3 / 4 |
| Enchimento da base | 35% gyroid |
| Brim / suportes | desativados |

## Razão das escolhas

Sem ironing, a qualidade depende sobretudo de uma cobertura sólida bem apoiada,
fluxo correto e percursos consistentes. Oito camadas a 0,20 mm criam 1,6 mm de
cobertura geral; a base conserva as nove camadas e 35% gyroid da V9, porque essa
revisão respondia a marcas do enchimento visíveis na peça física.

A superfície a 20 mm/s e 800 mm/s² reduz variações de pressão e vibração na
última camada. O sólido interno fica a 45 mm/s para formar uma fundação mais
regular antes da superfície visível. `Monotonic line` mantém as linhas na mesma
ordem visual. A opção de uma parede no topo dá mais área contínua ao preenchimento
superior; as paredes estruturais inferiores continuam com os valores normais.

Estas escolhas não substituem a calibração do filamento. Se o fluxo estiver
alto, aparecem sulcos e acumulação; se estiver baixo, ficam intervalos entre
linhas. No Bambu Studio, selecione os perfis calibrados das bobinas branca e
azul antes de fatiar.

## Estado da verificação

- O arquivo 3MF abre como ZIP válido e todas as configurações acima foram
  confirmadas diretamente no projeto.
- Os conteúdos `3D/` têm os mesmos SHA-256 da V9; a geometria não mudou.
- As substituições por objeto que reativavam ironing ou anulavam a parede única
  no topo foram removidas.
- O Bambu Studio não está instalado neste ambiente cloud; por isso esta sessão
  **não** confirmou os percursos, o tempo ou o consumo da V10.
- O acabamento ainda requer impressão física. Rever a pré-visualização de
  percursos e confirmar que não existe a funcionalidade `Ironing` antes de
  imprimir.

O [relatório](validation.json) guarda o SHA-256 e as verificações efetuadas. O
[script](../tools/refine_universo_stand_v10_no_ironing_3mf.py) recria o projeto
a partir da V9 sem alterar a geometria.
