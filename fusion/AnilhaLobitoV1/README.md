# Anilha de lenço — lobito V1, para colar

Primeira interpretação da fotografia fornecida. O rosto tem relevo plano e é
impresso à parte do corpo, com uma guia no verso que entra num rebaixo do corpo.
Esta solução facilita o posicionamento e reduz as trocas de cor. A aparência
exata está nas imagens do CAD; é uma interpretação vetorial, com o rosto mais
plano que a referência, não uma reprodução escultórica da fotografia.

## Medidas

| Elemento | Medida | Origem |
|---|---:|---|
| Passagem oval livre | **25 × 18 mm** | Coruja BRUNA, que o utilizador confirmou funcionar |
| Altura do corpo | **30 mm** | Proposta para o lobito |
| Rebaixo no corpo | **20 × 23 × 1,35 mm** | Guia de colagem |
| Saliência no verso do rosto | **19,6 × 22,6 × 1,20 mm** | Guia de colagem |
| Folga por lado | **0,20 mm** | Proposta de encaixe para colar |
| Espaço no fundo para cola | **0,15 mm** | Diferença de profundidades |
| Espessura da placa do rosto | **2,40 mm** | Antes dos relevos |

A elipse usa o mesmo gerador e 100 segmentos da coruja. Foi também comparada
com o polígono guardado no projeto antigo: diferença simétrica de área inferior
a 0,001 mm², devida ao arredondamento do ficheiro antigo. A abertura é contínua
e tem entradas suavizadas de 1 mm. A coruja tinha uma passagem de 20 mm de altura;
o corpo deste lobito tem 30 mm, pelo que o atrito no lenço precisa de confirmação.

## Projeto Bambu Studio

`anilha-lobito-v1-A1-AMS-2-pratos.3mf`, para **Bambu Lab A1, bico de 0,4 mm**.

1. **Corpo cinzento:** em pé, uma cor, sem suportes ou brim.
2. **Rosto para colar:** deitado, relevos para cima, cinzento/branco/preto,
   com pequenos suportes por baixo do verso, à volta da guia. A guia começa
   na mesa; o resto do verso começa a 1,20 mm, pelo que esses suportes são
   necessários nesta orientação. As marcas ficam no lado de colagem.

Camada de 0,16 mm, primeira de 0,20 mm, três paredes e 15% gyroid. Perímetros
externos 35 mm/s, topo 25 mm/s, aceleração normal 1000 mm/s². Sem brim nas peças.
Torre de preparação ativa no prato multicolor. Os perfis são **Generic PLA**:
escolher os perfis correspondentes aos filamentos reais e voltar a fatiar.
Não foi aplicado o fluxo 0,931 do laranja a estes três materiais.

Validação nativa no **Bambu Studio 02.09.01.70**, sem avisos nos dois pratos:

| Prato | Estimativa | Material com purgas/torre | Trocas de cor |
|---|---:|---:|---:|
| Corpo | ~1 h 24 min | ~13,53 g | 0 |
| Rosto | ~1 h 05 min | ~10,00 g | 8 |
| Total | **~2 h 29 min** | **~23,53 g** | **8** |

As estimativas incluem a preparação calculada pelo fatiador. O estudo inicial
com o rosto curvo e tudo unido exigia 313 trocas de cor. Esse estudo não é o
ficheiro de impressão entregue.

## Colagem

Deixar arrefecer, retirar os suportes do verso e limpar as superfícies de apoio.
Fazer primeiro o encaixe sem cola: o rosto deve assentar no plano frontal do
corpo, com a guia dentro do rebaixo. Aplicar uma pequena quantidade de cola
compatível com PLA no rebaixo; o espaço no fundo é para essa camada fina.
Não é um encaixe de pressão. Confirmar o ajuste antes de imprimir uma série.

## Validação e fontes

Os STLs fechados foram verificados; o rosto forma um conjunto conectado, a guia
cabe no rebaixo e não há interferência geométrica entre corpo e rosto montado.
O furo permanece livre. Essas verificações não substituem uma impressão física.
A colagem, o aperto no lenço e o acabamento ainda não foram testados.

- `geometry.json`: parâmetros, montagem e verificações geométricas.
- `bambu-validation.json`: estimativas, materiais, avisos e hash do 3MF.
- `generate_anilha_lobito_v1.py`: gerador paramétrico de malhas em milímetros.
- `build_anilha_lobito_v1.py`: construção e validação nativa do 3MF.

Os scripts são executados no checkout do repositório, onde estão os módulos
auxiliares; não são scripts executados dentro do Autodesk Fusion. O pacote
inclui os STLs, o 3MF, as imagens e estes registos.
