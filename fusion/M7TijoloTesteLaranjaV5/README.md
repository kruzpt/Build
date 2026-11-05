# M7 — teste laranja V5, uma parede exterior

Ensaio autorizado depois da revisão do processo e do encaixe. Parte do ficheiro
com zero paredes que o utilizador enviou e que tinha boa superfície, com uma
pequena saliência num canto. Contém **apenas a placa lisa**, sem estrela,
árvore, logótipo ou texto.

## Uma única alteração

**Paredes do objeto: 0 → 1.**

Mantém o padrão **Monotonic line**, direção **45°**, fluxo **0,931**, dimensões
**46,4 × 66,4 × 0,60 mm**, três camadas de 0,20 mm e a mesma pintura da costura.
Temperatura, retração, velocidades, acelerações, folgas e todos os parâmetros
de processo e filamento ficam iguais aos do ficheiro recebido.

O ensaio usa uma parede externa para definir o bordo, sem as duas paredes
internas das versões iniciais. Pretende avaliar o acabamento do contorno e o
encaixe a seco, conservando a superfície central que já tinha resultado bem.

**A definição está no objeto.** O perfil global continua a mostrar três paredes,
como no ficheiro recebido. Ao selecionar a peça em **Objects/Objetos**, a
definição de uma parede prevalece. O Gcode foi verificado e contém efetivamente
uma parede exterior por camada e nenhuma parede interior.

## Verificação nativa

Fatiado no **Bambu Studio 02.09.01.70**, para **Bambu Lab A1, bico 0,4 mm**,
sem avisos. A geometria e o restante conteúdo do arquivo estão preservados
byte a byte; no ficheiro de configurações do objeto mudou apenas o valor
do número de paredes.

- Um percurso exterior contínuo por camada, com a pequena abertura da costura.
- Costura na pintura existente, **numa zona reta do bordo**, longe dos cantos.
- Parede externa a 20 mm/s e 500 mm/s² na primeira camada; 50 mm/s e 1000 mm/s²
  nas seguintes. Topo a 25 mm/s e 1000 mm/s².
- Sem brim, suportes, torre ou trocas de cor.
- Estimativa: **17 min 47 s e 2,19 g**, incluindo preparação estimada.
  Aproximadamente quatro segundos e 0,008 g a mais do que a referência.

As zonas de início/fim do enchimento interior continuam a ser escolhidas pelo
fatiador. A costura indicada é a do perímetro exterior, não o ponto de arranque
de todos os movimentos da camada.

## Como comparar

Abrir o V5 como projeto, voltar a fatiar e manter o mesmo filamento e a
calibração dinâmica de fluxo usados nos testes anteriores. Imprimir uma unidade.
Depois de arrefecer, verificar o bordo, a costura e os quatro cantos; experimentar
no rebaixo sem cola e sem forçar. Comparar com a amostra original de zero paredes,
mantendo a orientação identificada.

O resultado físico continua por confirmar. Uma parede torna o contorno mais
definido nos percursos, mas não garante eliminar uma acumulação de plástico.
Este ficheiro é o ensaio da placa lisa; os projetos decorados de produção
permanecem separados.

## Reprodução

O relatório `bambu-validation.json` regista o hash, a mudança de âmbito do objeto,
as posições da costura, velocidades reais pedidas no Gcode e as estimativas.
O script `fusion/tools/build_m7_orange_test_v5.py` recebe `--source` com o 3MF
original do utilizador e `--bambu-bin` com o executável Bambu Studio 2.9.1.70.
Requer os módulos auxiliares disponíveis no checkout do repositório.
