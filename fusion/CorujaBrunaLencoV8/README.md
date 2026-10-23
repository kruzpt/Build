# Lenço V8 — dobras e moldura em relevo como no original

Esta versão recupera os painéis interiores e as duas bandas do nó do lenço
original da coruja V6. Mantém o verde nas bordas e pontas, como pedido,
e o castanho apenas no centro. A V7 tinha uma superfície verde plana;
na V8 as dobras são definidas pela geometria.

- Moldura/contorno verde elevado a Z=1,20 mm.
- Painéis interiores verdes rebaixados a Z=0,90 mm: profundidade 0,30 mm,
  traçados a partir das áreas verdes do lenço original.
- Nó castanho com base contínua entre Z=1,20 e 1,40 mm e duas bandas
  sobrepostas até Z=1,60 mm; vale central de 0,20 mm e pequenos degraus
  nas arestas superiores. O fundo do vale continua castanho.
- Dimensões: **15,97 × 10,37 mm**, espessura até **1,60 mm** no nó.
  O nó fica 0,20 mm mais alto do que na V7; o contorno de encaixe e verso
  plano mantêm as dimensões da V6. Não requer alterar a coruja.
- Não há castanho nem preto nas pontas. As diferenças de verde na imagem
  CAD representam iluminação das faces; é um único filamento verde.

## Imprimir

Abrir **anilha-coruja-bruna-lenco-v8-A1-bico-0.2-2-cores.3mf** como projeto
no Bambu Studio. Está configurado para **Bambu A1, bico 0,2 mm, camadas
0,10 mm**, verso plano contra o prato, sem suportes. Primeiro filamento:
verde. Segundo: castanho. As duas cores são uma única peça impressa em
conjunto; colar apenas o lenço completo na coruja, testando a posição antes.

O verde termina a 1,20 mm e o castanho ocupa apenas as quatro últimas
camadas. **Uma única troca de cor**, confirmada no fatiamento nativo.
Estimativa: **26 min 20 s**, **0,94 g incluindo torre/purga**; aproximadamente
0,14 g na peça. Valores para uma unidade, sujeitos aos perfis de filamento.

## Validação e ficheiros

STL estanques, montagem unida, cores sem sobreposição volumétrica, contorno
de encaixe preservado, exportação/reabertura/fatiamento no Bambu Studio
02.08.02.61, 16 camadas de 0,10 mm, uma troca de cor, sem suportes nem avisos.
**Ainda não foi impresso fisicamente.** Ver `bambu-validation.json` para
estimativas e hash do projeto entregue, e `geometry.json` para dimensões.

O pacote contém apenas o lenço: 3MF, STL de duas cores, STL monocor, GLB,
imagens CAD e scripts. Os STL coloridos são corpos de uma montagem com
coordenadas comuns, não peças para colar individualmente.

Para reproduzir no repositório com os módulos auxiliares existentes e Python
com numpy, OpenCV, Pillow, trimesh e manifold3d:

```sh
python fusion/tools/generate_coruja_lenco_v8.py
python fusion/tools/build_coruja_lenco_v8_3mf.py
```
