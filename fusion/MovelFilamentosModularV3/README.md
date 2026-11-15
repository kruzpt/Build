# Móvel de filamentos — conector V3, projeto de impressão

**Ficheiro para abrir no Bambu Studio:** `downloads/movel-filamentos-conector-v3-A1-PETG-4-pratos.3mf`. Esta é a entrega de impressão; os STL em `stl/` são apenas intermediários para reconstruir o 3MF e não precisam de ser importados nem impressos separadamente.

## O que mudou

- As duas entradas horizontais são **redondas à vista**. O alívio em ponta da V2 ficou restrito ao interior das tomadas, escondido por uma boca circular de 3 mm. Esta forma procura permitir a impressão vertical sem suportes; validar a qualidade da boca na primeira peça antes de produzir as restantes.
- A anilha redonda da V2 era só um teste de diâmetro. **Não faz parte deste projeto.** O teste agora é o próprio conector do prato 1.
- O furo nominal para cada cabo continua **Ø22,7 mm**; é o diâmetro do furo, não uma medição do cabo.
- Cada conector tem uma passagem vertical contínua e duas tomadas horizontais cegas a 90°. Há um furo de parafuso por cabo. Os cabos podem ter comprimentos diferentes, escolhidos pelo utilizador.

## Pratos do 3MF

| Prato | Conteúdo | Finalidade |
| --- | --- | --- |
| 1 | 1 conector | Verificar os três encaixes e os parafusos com os cabos reais. |
| 2 | 1 pé | Verificar a ponta do poste e o parafuso lateral. |
| 3 | 3 conectores | Completar os quatro cantos do primeiro andar após a prova. |
| 4 | 3 pés | Completar os quatro apoios do chão. |

Para um andar adicional, imprimir quatro conectores; não é necessário repetir os pés. A quantidade de andares e os comprimentos dos cabos não estão embutidos no modelo.

## Perfil e verificação

Projeto preparado para **Bambu A1, bico 0,4 mm, PETG e prato PEI texturado**, com camada de 0,20 mm, cinco paredes, seis camadas sólidas em cima e em baixo, 35% gyroid, sem suportes e sem brim. O perfil do PETG é genérico: adequar temperatura e fluxo ao filamento real. Ambos os objetos estão orientados com a face larga e plana no prato.

Os STL intermediários são malhas fechadas. O 3MF foi reaberto e os quatro pratos foram fatiados digitalmente sem avisos. **O encaixe Ø22,7 mm, a qualidade da boca circular e a resistência com seis rolos ainda não foram validados fisicamente.** Imprimir os pratos 1 e 2 antes dos pratos 3 e 4. Para cabos de 1 m e vários andares, avaliar contraventamento e fixação à parede na montagem.

Com este perfil, a estimativa do fatiador é cerca de **183 g de PETG por conector** e **43 g por pé**. São peças estruturais grandes; a quantidade de material e o tempo de impressão podem ser reduzidos numa revisão posterior depois de testar a resistência necessária.
