# Clínica Essencial — compacto V5, base invertida e prato de amostra

Projeto final preparado para **Bambu Lab A1, AMS Lite, bico de 0,4 mm**, PLA e
PLA Silk dourado, camada de 0,16 mm. Não foi enviado para uma impressora.

A base tem traseira e laterais direitas, cantos de raio 8 mm e um único recorte
frontal central, suave e simétrico, de 8 mm de profundidade. **Topo plano** e
altura constante de 9,60 mm: não tem a onda em altura da V3 nem o contorno
orgânico da V4. As imagens CAD são da geometria real; a fotografia conceptual
anterior não é uma garantia do acabamento físico.

## Dimensões propostas e compatibilidade

| Parâmetro | Valor | Origem |
|---|---|---|
| Conjunto montado | 200 × 70 × 200 mm | Projeto compacto aprovado |
| Base | 200 × 70 × 9,60 mm | Proposta V5 |
| Dourado em toda a face inferior montada | 0,96 mm, seis camadas | Mantido por escolha do utilizador |
| Ranhuras: espessura / profundidade | 3,60 / 6,40 mm | Encaixes preservados da V4 |
| Línguas: espessura / comprimento de inserção | 3,20 / 6,20 mm | Projeto, a testar fisicamente |
| Largura das línguas branca / verde | 128,15 / 146,46 mm | Geometria V4 preservada |
| Folgas nominais | 0,20 mm por lado; 0,20 mm no fundo | Propostas, não medidas num exemplar |
| Campo QR / passo do módulo | 58,58 mm / 1,302 mm | Geometria preservada |

**Frente e fundo V4 são compatíveis com esta base.** A base V3 já impressa
não recebe estas placas compactas nos mesmos encaixes. As versões anteriores
mantêm-se no repositório. Frente, grafismo, raposa limpa e fundo nervurado não
foram redesenhados nesta versão.

## Abrir e imprimir

Abrir **essencial-compacto-v5-azeitona-A1-AMS-4-pratos.3mf como projeto**.
As orientações e os corpos de cor já estão preparados. **Não virar novamente
base/amostra, nem separar os corpos coloridos.** Selecionar os perfis adequados
às bobinas reais e voltar a fatiar se alterar material, prato ou configurações.

Slots: **1 branco, 2 verde-azeitona, 3 dourado, 4 preto**. O perfil fornecido é
Generic PLA nos três PLA normais e Generic PLA Silk no dourado, com os valores
completos oficiais da A1; limite volumétrico 8 e 5 mm³/s respetivamente. Cor
verde `#737648` apenas para visualização. Prime tower ativa; sem purga no
preenchimento. A amostra e a base têm uma troca verde → dourado cada.

| Prato | Conteúdo | Estimativa | Material incl. torre/purga | Trocas |
|---|---|---:|---:|---:|
| 1 | Frente branca, dourado e QR pretos | 4 h 50 min | 93.42 g | 3 |
| 2 | Fundo verde nervurado | 5 h 15 min | 105.09 g | 0 |
| 3 | Base invertida + friso dourado | 4 h 26 min | 71.14 g | 1 |
| 4 | AMOSTRA: canto real + ranhuras + duas linguetas | 1 h 36 min | 23.17 g | 1 |

O conjunto (pratos 1–3) estima **14 h 31 min / 269.65 g**.
A amostra é adicional. Valores do fatiamento Bambu Studio 02.08.02.61, não
medições físicas; pequenas diferenças no Bambu Studio local são possíveis.

## Começar pelo prato 4 — amostra

1. Imprimir **apenas o prato 4** no mesmo prato e filamento previstos para a
   base. Inclui um recorte real de 70 × 50 mm do canto frontal esquerdo,
   os finais das duas ranhuras e duas linguetas verdes independentes.
2. Deixar arrefecer e retirar. A face que estava contra o prato é o futuro
   topo visível; virar a amostra para colocar o dourado por baixo.
3. Avaliar a textura dessa face, a união verde/dourado e a costura lateral.
   No PEI texturado haverá textura, não um polimento. Prato limpo é essencial.
4. Introduzir cada lingueta a direito numa ranhura, sem cola. Deve entrar e
   sair com pressão manual moderada, sem arquear ou forçar a amostra.
5. Confirmar que as entradas estão limpas e que o fundo da ranhura não impede
   a entrada. As pequenas pontes interiores são feitas sobre 3,60 mm; se houver
   fios soltos ou descaimento que prejudiquem a folga, corrigir antes da base.
6. Só depois imprimir o prato 3. A amostra avalia o acabamento e a folga local;
   não reproduz o empeno de uma placa comprida nem toda a estabilidade final.

A amostra usa verde para as linguetas para não acrescentar trocas. Verifica
sobretudo a geometria/processo do verde: o encaixe da frente branca precisa
igualmente de montagem a seco, pois bobinas diferentes podem contrair de
forma diferente. Não aplicar cola até verificar o conjunto e os QR.

## Orientação e acabamento da base

A face verde visível encosta ao prato. As ranhuras ficam abertas para baixo
durante a impressão e fecham com pontes internas a Z=6,56 mm. Verde nas
primeiras **54 camadas**, até Z=8,64; dourado só nas últimas **seis**, até 9,60.
O dourado cobre a face inferior toda, preservando uma só troca de cor.

Base e amostra: três paredes, 15% Gyroid, paredes exteriores a 35 mm/s,
aceleração exterior 1000 mm/s², cinco camadas inferiores (0,80 mm) e cinco
superiores (mínimo 0,80 mm). Interfaces de material ativas; pontes a 20 mm/s.
Sem suportes e sem brim nestas peças para preservar o bordo em contacto com
o prato. A adesão da base grande tem de ser observada no exemplar real.

A costura está em **Front no fatiador**: como a base está invertida e sem
rotação XY, esse lado corresponde à **traseira da base montada**. É uma
preferência de localização, não uma garantia de que a costura desaparece ou
que um sulco por fluxo/retração ficará resolvido. Não ativar orientação
automática sem rever a montagem e a localização da costura.

## Frente, QR e verificações

Frente preservada: branco termina a Z=3,68 mm; preto/dourado ocupam apenas
as duas camadas finais, 3,84 e 4,00 mm. Três trocas confirmadas no G-code.

Instagram: https://www.instagram.com/clinicaessencial_setubal/

Google: https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg

As secções STL dos dois QR descodificam. A amostragem da grelha conhecida
nos percursos pretos não tem módulos divergentes e descodifica ambos.
O raster bruto do Instagram não descodificou automaticamente; isto continua
a ser verificação geométrica, **não leitura com telemóvel**. Testar fisicamente
ambos os QR no primeiro conjunto, antes de entregar ao cliente.

Verificados: STL estanques, dimensões, montagem sem colisões em 124 posições,
ficheiro 3MF reaberto e quatro pratos fatiados sem avisos nem suportes,
orientação invertida, uma troca na base/amostra e pontes interiores a 20 mm/s.
Margem estática aproximada do centro de gravidade: 27.2 mm,
não um ensaio de empurrão. Sem ensaio físico desta versão.

## Conteúdo do pacote

- 3MF de quatro pratos e onze STL: seis componentes na posição de modelação,
  duas versões invertidas da base/friso e três peças de amostra.
- Para imprimir, preferir o 3MF. Os STL `base-verde-invertido` e
  `friso-dourado-invertido` devem manter coordenadas relativas se forem importados.
- Imagens CAD, vista superior, pratos, primeira camada real e relatórios JSON.
- Script opcional `EssencialCompactoV5.py` com `geometry.json`: cria o conjunto
  montado no Fusion; não foi executado no Fusion neste ambiente. Não é um F3D
  validado e não inclui a amostra como parte do expositor.
- Geradores/verificadores dependem dos auxiliares do repositório Build.

```sh
python fusion/tools/generate_essencial_compacto_v5.py
python fusion/tools/build_essencial_compacto_v5_3mf.py
python fusion/tools/verify_essencial_compacto_v5_qr.py
python fusion/tools/verify_essencial_compacto_v5_base.py
python fusion/tools/build_essencial_compacto_v5_3mf.py --package-only
```
