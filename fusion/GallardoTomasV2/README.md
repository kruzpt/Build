# Gallardo + TOMAS V2 — projeto de impressão

Peça única com duas leituras: **TOMAS visto de cima** e **Gallardo visto de
lado**, na posição de apresentação. O projeto de impressão já a coloca
deitada sobre um lado, para reduzir suportes e pontes.

## Abrir e imprimir

1. Abrir `gallardo-tomas-v2-A1-02-PLA.3mf` como **projeto** no Bambu Studio.
2. Usar **Bambu Lab A1 com bico de 0,2 mm**, conforme o ficheiro fornecido.
   O projeto está configurado para PLA preto, posição de filamento **3**.
   Confirmar o respetivo rolo no mapeamento de filamentos antes de imprimir.
3. Manter a orientação e os suportes definidos e fatiar o prato.
4. Depois de imprimir, deixar arrefecer. Retirar os suportes por pequenas
   secções, apoiando os traços finos do carro; evitar puxar todo o suporte de
   uma vez ou usar as letras como alavanca.

O 3MF é editável e contém os perfis completos, sem percursos antigos em cache.
O STL incluído conserva a orientação de impressão, mas não contém os perfis.
Não foi enviada nenhuma tarefa para uma impressora física.

**Estimativa do fatiador:** cerca de **12 h 20 min** e **28,1 g de PLA**, já com
os suportes. O tempo corresponde ao bico de 0,2 mm e às configurações de detalhe.

## Geometria

| Parâmetro | Valor |
| --- | --- |
| Dimensões na posição de apresentação | 150 × 30 × 37,3 mm |
| Dimensões na posição de impressão | 150 × 37,3 × 30 mm |
| Componentes finais | 1 sólido ligado e fechado |
| Nome | TOMAS, a partir do texto fornecido |
| Reforço do texto | Expansão do contorno em 1,6 mm, seguida de ajuste para 150 × 30 mm |
| Construção | União efetiva das letras, seguida da interseção com o carro |
| Limpeza numérica | Tolerância de 0,001 mm; remoção da pequena inclinação da origem |

O reforço liga os dois detalhes que se separavam na primeira simulação, sem
adicionar uma placa de fundo. Conservam-se as duas projeções pretendidas,
verificadas numericamente em relação aos contornos normalizados.
O contorno é o Gallardo com a aba inferior já removida na versão anterior.

## Configuração

- A1, bico **0,2 mm**, PLA, prato Textured PEI.
- Camada e primeira camada de **0,10 mm**.
- **4 paredes**, **20% Gyroid**.
- Paredes exteriores a 30 mm/s; interiores a 50 mm/s; topo a 25 mm/s.
- Velocidades em balanço limitadas também no perfil do PLA ativo, para que
  os valores herdados do filamento não acelerem essas zonas.
- Suportes normais automáticos **Snug**, com três camadas de interface superior,
  espaçamento da interface de 0,30 mm, folga Z de 0,20 mm e folga lateral de
  0,35 mm. São do mesmo PLA e podem deixar marcas nas faces de contacto.
- **Sem brim** e sem torre de purga; impressão de uma só cor.

As temperaturas, o fluxo e os restantes perfis de material provêm do projeto
enviado. Os perfis inativos permanecem no projeto; só o PLA preto da posição 3
é utilizado.

## Verificação

`validation.json` regista o hash do projeto, geometria, configurações e
estimativas devolvidas pelo Bambu Studio. Foram verificados:

- Malha fechada, orientação consistente e um único componente, incluindo
  exportação e reabertura do STL binário.
- Dimensões e posição dentro do prato.
- Manutenção das projeções do carro e do nome.
- Fatiamento nativo, avisos do prato, alturas de camada, suporte efetivamente
  gerado, ausência de brim, filamento utilizado e velocidade exterior real.

Foram comparadas as posições vertical e deitada para ambos os lados. A posição
escolhida consumiu menos suporte e tempo nas configurações comparadas. As
estimativas dessa comparação estão em `orientation-comparison.json`; a
estimativa definitiva após limitar as velocidades em balanço está em
`validation.json`.

As imagens `gallardo-tomas-v2-vistas.png` e `gallardo-tomas-v2-suportes.png`
mostram, respetivamente, as projeções do modelo e percursos do G-code validado.
Numa camada isolada é normal ver segmentos separados: ligam-se noutras alturas
para formar a peça completa. Esses segmentos da prévia não significam, por si
só, que o modelo tenha corpos soltos.
Não foi realizado teste físico: a resistência dos traços finos, a adesão ao
prato e o acabamento após remover suportes dependem da impressão real.

## Reproduzir

No checkout do repositório, com numpy, trimesh, manifold3d e Pillow instalados:

```sh
python fusion/tools/build_gallardo_tomas_v2.py \
  --source /caminho/sharegallardo-straight-sill-v1.3mf \
  --bambu-bin /caminho/bambu-studio \
  --work-dir /caminho/temporario
```

É necessário o 3MF enviado pelo utilizador, não incluído no pacote. O código
gera a geometria, configura o projeto e exige uma verificação nativa concluída.
O Bambu Studio disponível para validação é a versão 2.8.2.61, usando a opção
de compatibilidade com o ficheiro de origem 2.9.1.70.

Modelo base de **Dava**, com a licença **Standard Digital File License**
identificada no ficheiro original. A identificação e licença do autor foram
conservadas no 3MF; a variante acrescenta o nome, reforços e preparação descritos.
