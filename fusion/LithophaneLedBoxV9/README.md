# Caixa para litofania — V9, LED oculto e USB na tampa

Esta versão substitui a V8. O utilizador esclareceu que **a porta USB-C aponta para a traseira da placa LED**. Por isso a placa fica **dentro** da caixa, encostada à face interna da tampa opaca, como previsto no conceito aprovado. A tampa tem uma pequena janela **fechada, na sua face traseira**, alinhada com a porta. O corpo não tem abertura lateral. O cliente vê PLA e a entrada USB-C, sem ver a placa LED.

## Peças

- `corpo.stl`: 178 × 142 × 24,94 mm; frente no prato. Litofania 160 × 124 × 3 mm inserida por trás e colada apenas na margem escondida. Aro separado eliminado.
- `tampa_opaca.stl`: 171,6 × 135,6 × 2,4 mm; encaixa no rebaixo traseiro de 172 × 136 × 2,5 mm. Colar só no perímetro depois de testar o LED e a ficha.

A janela para a USB mede **12 × 18 mm**, centrada provisoriamente a **76 mm à direita do centro da tampa**. A porta da placa mede 8,88 × 3,04 mm. A orientação da janela deixa a dimensão maior paralela à largura da porta, que está no meio da extremidade curta da placa. Se a posição exata da porta na placa diferir da foto, ajustar `usb_center_x`/`usb_center_y` em `litho_box.scad` e voltar a exportar a tampa. Não há rasgo até à borda.

A distância calculada entre o verso da litofania e a face luminosa do LED é de cerca de 15 mm para a espessura medida de 2,04 mm. A fixação do LED à tampa pode ser feita por pequenos pontos de fita na face traseira da placa, fora da tomada; confirmar a superfície real antes da colagem.

As duas malhas STL foram exportadas de `litho_box.scad` com OpenSCAD e verificadas como fechadas. **A ficha do cabo ainda não foi medida ou testada no recorte.** Não colar a tampa antes dessa prova. A litofania pessoal original não é redistribuída.
