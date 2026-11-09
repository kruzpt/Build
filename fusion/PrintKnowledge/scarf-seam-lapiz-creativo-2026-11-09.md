# Costura Scarf — transição gradual no fecho dos perímetros

**Registado:** 09/11/2026.

**Link enviado:** https://www.facebook.com/share/r/1FJpAKKamg/

**Vídeo identificado:** https://www.facebook.com/reel/2411461002996429/

**Autor identificado na página pública:** Jose Fillol Levia; marca/página
Lápiz Creativo 3D apresentada no vídeo. É uma fonte diferente do Clube das
ferramentas e da UpLike Digital.

## Observado no vídeo

Revisão visual do vídeo público de aproximadamente 76 segundos. O autor mostra
uma costura vertical num organizador cilíndrico, explica o início/fim dos
perímetros e apresenta a opção Scarf no Bambu Studio. A interface mostra
Bambu Lab P1S, bico de 0,4 mm, processo Standard de 0,20 mm e Generic PLA.
Não equivale a um ensaio com a nossa A1 ou o nosso laranja calibrado.

Na janela do filamento, em modo avançado, são apresentados:

| Campo | Antes | Após a alteração mostrada, cerca de 52–54 s |
| --- | --- | --- |
| Scarf seam type | None / Ninguno | Contour / Contorno |
| Scarf start height | 10% | 10% |
| Scarf slope gap | 15% | **2**, sem símbolo % |
| Scarf length | 10 mm | 10 mm |

Outros valores visíveis: primeira camada de bico a 220 °C, cama PEI texturizada
a 55 °C e velocidade volumétrica máxima de 12 mm³/s. São condições mostradas,
não valores a copiar para os nossos perfis.

No final o autor apresenta peças cilíndricas e reivindica menor visibilidade
da costura. A gravação não constitui uma comparação controlada com o mesmo
filamento nem fornece uma medição de melhoria nas nossas peças.

## Significado e unidades confirmados

Referência consultada no código oficial do Bambu Studio:
https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp

- `filament_scarf_seam_type`: `none`, `external` (Contour), `all` (Contour and hole).
- `filament_scarf_height`: altura inicial em mm ou percentagem da altura de camada.
- `filament_scarf_gap`: encurtamento de fecho em mm ou percentagem do diâmetro do bico.
- `filament_scarf_length`: comprimento da transição em mm.
- `override_filament_scarf_seam_setting`: permite ao processo substituir as
  definições de Scarf do filamento; verificar antes de concluir que o material
  controla o resultado.

**Atenção ao valor do vídeo:** no campo mm/%, escrever `2` significa **2 mm**,
enquanto `2%` significa 0,008 mm num bico de 0,4 mm. Os 15% existentes no nosso
perfil correspondem a 0,06 mm. Não converter silenciosamente o valor mostrado
em 2%, nem recomendar copiar 2 mm sem inspecionar os percursos e o resultado.

A técnica distribui o início/fim do perímetro numa transição gradual e pode
disfarçar a marca. Não elimina as linhas horizontais nem os degraus de uma
superfície curva. Desativar a visualização de Seams na prévia apenas esconde
os marcadores; não muda a impressão.

## Comparação com os ficheiros existentes

Consulta em 09/11/2026:

| Campo | Laranja calibrado A1 / 0,4 e Gallardo V4 laranja |
| --- | --- |
| `filament_scarf_seam_type` | `none` |
| `filament_scarf_height` | `10%` |
| `filament_scarf_gap` | `15%` |
| `filament_scarf_length` | `10` |

No projeto do Gallardo: `override_filament_scarf_seam_setting=0`,
`seam_slope_type=none`, `seam_position=aligned`,
`seam_slope_conditional=1`, `scarf_angle_threshold=155` e
`apply_scarf_seam_on_circles=1`. Existem condições adicionais de aplicação;
ativar uma opção não prova que todos os contornos receberão Scarf.

## Aplicação proposta e comparação inicial

O primeiro candidato é o **corpo redondo da anilha/lobito**, onde a costura
vertical pode ser visível. O benefício nas linhas do topo curvo é limitado:
essas dependem sobretudo da geometria, orientação e altura de camada.
Nos detalhes estreitos do Gallardo ou nos relevos da árvore/estrela, não
assumir benefício sem confirmar comprimentos e percursos. A estratégia de
preenchimento em linhas que resolveu a árvore mantém-se uma aprendizagem
separada.

Proposta de comparação: dois pequenos cilindros iguais, com as mesmas
dimensões, orientação e filamento, um com Scarf desligada e outro com Contour,
altura inicial 10%, comprimento 10 mm e **folga existente de 15% preservada**.
Isto testa primeiro a ativação da técnica, sem acumular a alteração para 2 mm.
Usar as restantes definições do laranja calibrado, incluindo fluxo 0,931,
temperatura 220 °C e limite volumétrico de 8 mm³/s, se esse for o material
escolhido. Não acrescentar simultaneamente a experiência de ventilação a 25%
ou a de engomagem. Sem brim por defeito.

Antes de imprimir: apresentar o plano da amostra conforme a preferência do
utilizador, verificar a aplicação efetiva da Scarf no fatiamento/G-code e
manter o perfil aprovado distinguível de uma variante experimental. Avaliar
visibilidade da costura, pequenos vazios, textura e resistência local.
Para uma peça que contém água, validar também fugas; esta opção não garante
estanqueidade.

**Estado:** vídeo e parâmetros revistos visualmente, semântica/unidades
consultadas no código e perfis existentes comparados. Referência guardada;
nenhum perfil alterado, nova amostra modelada/fatiada ou teste físico nosso
realizado nesta revisão.
