# Diagnóstico do Gallardo / TOMAS

Análise do ficheiro fornecido `sharegallardo-straight-sill-v1.3mf`.
Este trabalho produz apenas uma imagem de diagnóstico e dados de análise;
não altera nem entrega um novo projeto de impressão.

- O ficheiro contém dois objetos antes da operação booleana: carro e texto.
- O carro mede 150 × 30 × 37,30 mm; o texto mede 150,40 × 30 × 37,30 mm.
  Os volumes coincidem em profundidade e altura e partilham o mesmo eixo longo.
  O carro é lido de lado e TOMAS de cima: a orientação é adequada ao efeito.
- O texto usa Courier New sem negrito e contém cinco cascas fechadas que se
  sobrepõem. Uma união geométrica dessas cascas produz um único sólido ligado.
- A interseção desse sólido com o carro, simulada com Manifold3D, contém um
  corpo principal de 9708,61 mm³ e dois fragmentos de 6,03 e 4,36 mm³.
  As zonas dos fragmentos estão assinaladas a vermelho na imagem.
- Isto não reproduz a fragmentação extensa da captura anterior. O ficheiro
  anterior à operação não permite determinar qual foi a operação ou a vista
  usada nessa captura. A simulação não usa o Boolean nativo do Bambu Studio.
- O passo seguinte proposto é fundir as sobreposições das letras antes da
  interseção e rever as ligações nos detalhes marcados. Uma fonte de traço mais
  cheio pode melhorar a resistência, mas a ligação final precisa de nova
  verificação; engrossar por si só não garante a eliminação dos fragmentos.

## Reprodução

É necessário o ficheiro enviado pelo utilizador, não incluído neste relatório.
Dependências: numpy, trimesh, manifold3d e Pillow.

```sh
python fusion/tools/review_gallardo_tomas.py /caminho/sharegallardo-straight-sill-v1.3mf
```

As projeções representam as malhas efetivas com a mesma escala. A direção de
observação da vista de cima foi rodada 180° apenas para facilitar a leitura do
nome; a geometria não foi alterada. Não foi efetuado teste físico nem fatiamento.

O modelo base conserva a autoria de Dava e a licença Standard Digital File
License identificadas no projeto original. Este relatório publica apenas os
dados de diagnóstico, projeções e código de análise.
