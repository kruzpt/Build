# Universo do Saber V11 — perfil anti-empeno

Esta versão mantém exatamente a geometria e o acabamento superior sem ironing
da V10. Altera apenas o processo para combater o levantamento observado nos
cantos das peças grandes.

Abra o [3MF V11 de dois pratos](../../downloads/universo-saber-suporte-v11-anti-empeno-A1-AMS-2-pratos.3mf)
como projeto no Bambu Studio. A temperatura do bico não foi alterada: antes de
fatiar, selecione o perfil calibrado de cada bobina.

## Parâmetros anti-empeno

| Parâmetro | V11 |
| --- | ---: |
| Placa PEI texturada, primeira camada | 60 °C |
| Placa PEI texturada, restantes | 60 °C |
| Brim exterior | 5 mm |
| Separação do brim | 0,15 mm |
| Parede / enchimento da primeira camada | 15 / 25 mm/s |
| Aceleração da primeira camada | 400 mm/s² |
| Ventoinha de peça desligada | primeiras 4 camadas |
| Ventoinha plena | camada 8 |
| Intervalo da ventoinha | 50–70% |
| Ventoinha auxiliar | desligada |
| Ironing | desligado |

O projeto conserva as oito camadas superiores, padrão monotonic line, superfície
a 20 mm/s e uma parede nas superfícies de topo da V10. A base mantém nove
camadas superiores e 35% gyroid.

## Utilização

Limpe a placa com água morna e detergente antes do teste. Não aplique cola numa
PEI texturada limpa sem necessidade. Retire o brim apenas depois de a placa
arrefecer. Se os cantos ainda levantarem, não aumente automaticamente a mesa:
verifique correntes de ar, placa deformada e contacto real da primeira camada.

O 3MF foi reaberto e fatiado no Bambu Studio sem avisos. O G-code de validação
confirmou mesa a 60 °C, brim e ausência de ironing. O resultado físico ainda
precisa de uma impressão de teste.
