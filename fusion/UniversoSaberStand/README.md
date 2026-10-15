# Suporte de telemóvel — Universo do Saber V1

Suporte desmontável de duas peças, preparado para **Bambu Lab A1**, bico de
0,4 mm, PLA e AMS Lite. O desenho mantém apenas branco e azul e reduz as
mudanças de cor.

## Medidas e montagem

- costas brancas: **200 × 80 × 6 mm**;
- base azul: **110 × 80 × 6 mm**, com dois batentes integrados;
- inclinação das costas: **70° em relação à mesa**;
- área útil acima do apoio: **171,6 mm**;
- relevo azul: **0,8 mm**;
- ranhura nominal: **6,30 mm** para uma peça de 6,00 mm;
- abertura central para cabo e acesso à porta do telefone.

As duas peças entram lateralmente uma na outra até os centros coincidirem.
O próprio fim das ranhuras determina a posição final. Não force o encaixe.

## Testar primeiro a folga

O comportamento do encaixe depende da calibração do filamento e da primeira
camada. Imprima primeiro uma destas amostras, começando em 0,30 mm:

- `universo-saber-suporte-v1-amostra-encaixe-020.stl` — firme;
- `universo-saber-suporte-v1-amostra-encaixe-030.stl` — valor usado no projeto;
- `universo-saber-suporte-v1-amostra-encaixe-040.stl` — mais livre.

Cada STL contém duas pequenas peças. Rode uma delas 90° e faça o mesmo
movimento lateral previsto para o suporte. A amostra combinada dispõe os
três pares, da esquerda para a direita: 0,20, 0,30 e 0,40 mm.

Se a amostra de 0,30 mm não entrar sem esforço, não imprima ainda o projeto
completo. Pode usar a variante de 0,40 mm como referência para ajustar o
script, ou aplicar compensação XY apenas depois de medir o resultado.

## Projeto Bambu Studio

Abra `universo-saber-suporte-v1-A1-AMS-2-pratos.3mf` **como projeto**:

1. **Prato 1 — costas:** PLA branco + relevo azul; uma mudança de cor.
2. **Prato 2 — base:** apenas PLA azul; sem mudança de cor. Tem suporte normal
   snug, somente na mesa, para o pequeno bisel do pé traseiro.

Perfil incluído: 0,20 mm, três paredes, 15% gyroid, cinco camadas superiores,
quatro inferiores, superfície superior monotónica e brim exterior de 3 mm.
O projeto foi fatiado para A1 com cerca de **82,9 g** e **3 h 42 min** no total.
Com PLA a 13–14 €/kg, o material estimado custa aproximadamente 1,08–1,16 €,
sem incluir purga adicional de arranque, energia nem falhas.

Use prato limpo e confirme que o perfil da impressora continua a ser
`Bambu Lab A1 0.4 nozzle`. O verso das costas e a base imprimem deitados.
Retire cuidadosamente o pequeno suporte da base e apare qualquer ressalto da
primeira camada antes de testar a montagem.

## Fusion 360

Copie a pasta `UniversoSaberStand` para a pasta de scripts do Fusion 360 e
execute `UniversoSaberStand.py` em **Utilities > Scripts and Add-ins**. O
script cria um novo documento com os três componentes do conjunto. A
geometria independente usada nos STL e no 3MF encontra-se em `geometry.json`.

O script passa numa verificação sintática, mas ainda não foi executado numa
instalação real do Fusion 360. O logótipo foi redesenhado a partir da imagem
aprovada e continua a ser uma aproximação, pois não foi fornecido o vetor
original.

## Validação e limites

Foram verificados por cálculo: sólidos fechados, ausência de colisão na
posição final, 42 passos do percurso lateral de montagem, contactos dos dois
pés no plano da mesa e três caixas de telefone até 180 × 90 × 17 mm / 320 g.
A menor margem estática ideal calculada foi 31,6 mm dentro do polígono de
apoio.

Estes cálculos não substituem um protótipo. Ainda não foram testados
fisicamente o encaixe, a aderência dos pés, o esforço de toque no ecrã ou a
resistência à queda. Faça primeiro as amostras e depois uma unidade completa.
