# Caixa para litofania — correção V8

Esta versão corrige o defeito assinalado pelo utilizador: **o corpo já não tem furo lateral**. A litofania original continua 160 × 124 × 3 mm. As duas peças impressas são [corpo](../../downloads/lithoavos-caixa-led-v8/corpo.stl) e [tampa que suporta o LED](../../downloads/lithoavos-caixa-led-v8/tampa_porta_led.stl). O [modelo paramétrico](litho_box.scad) permite ajustar medidas antes de reexportar.

## Porque mudou a posição do LED

A USB-C está fixa no centro da extremidade curta da placa e entra um cabo na direção do plano da placa. Se a placa ficar completamente dentro de uma caixa com as laterais fechadas, a lateral bloqueia a inserção da ficha. A solução V8 monta a placa **por fora da tampa traseira**, com a face luminosa apontada para a litofania através de uma grande janela na tampa. A traseira da placa fica visível. Uma aba de 2 mm mantém a porta mais atrás do que a parede lateral do corpo, de modo que o cabo se liga pelo exterior sem um furo nessa parede. A tampa tem apenas um recorte local para deixar livre a USB-C.

## Medidas e montagem

| Item | Cota do modelo |
| --- | ---: |
| Corpo exterior | 178 × 142 × 18,4 mm |
| Janela frontal | 156 × 120 mm |
| Alojamento da litofania | 160,4 × 124,4 × 3,4 mm |
| Rebaixo traseiro para a tampa | 172 × 136 × 2,5 mm |
| Tampa | 171,6 × 135,6 mm, base 2,4 mm + aba 2 mm |
| Janela luminosa da tampa | 150 × 114 mm |
| LED previsto | 156 × 120,1 × 2,04 mm |
| Distância verso da litofania → face do LED | ≈ 14,9 mm |

A litofania entra pelas costas e recebe pequenos pontos de cola na margem não visível; assim o aro retentor da V7 foi eliminado. O LED é alinhado e fixado na aba posterior da tampa, apenas na margem não luminosa da sua face. Depois de verificar a iluminação e o acesso à USB, a tampa é colada no rebaixo traseiro. Não há parafusos. A porta da placa mede 8,88 × 3,04 mm, conforme a medição do utilizador.

O tamanho **externo da ficha do cabo** ainda é desconhecido, assim como o comprimento exterior exato da placa (156 mm vem do anúncio). O recorte local da tampa tem 20 mm de largura provisória para a ficha. Antes de colar, testar a ficha real e verificar que as margens usadas para fixar a placa não tapam LEDs. Esta versão é um protótipo CAD imprimível, **sem ensaio físico ou fatiamento validado**.

Os dois STL foram exportados com OpenSCAD, verificados como malhas fechadas e correspondem ao SCAD incluído no pacote. A litofania original, que contém uma fotografia pessoal, não é redistribuída.
