# Aquelá V6 — ponta exterior do olho em cinzento

[Lobo V6 — 3MF para Bambu A1 / AMS](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v6-LOBO-A1-04-AMS-4-cores.3mf?raw=true) · [Comparação do olho V5/V6](../../designs/anilha-aquela-v6-olho-comparacao-CAD.png) · [Conjunto montado](../../designs/anilha-aquela-v6-montada-CAD.png) · [Pacote completo](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v6-pacote.zip?raw=true)

O triângulo preto que prolongava o olho pequeno em direção ao focinho passa a cinzento. A pupila mantém-se preta, com uma linha fina junto ao branco. O novo cinzento termina a Z = 3,80 mm, à altura do restante pelo cinzento, sobre apoio a Z = 3,32 mm. O nariz, o branco dos olhos e a expressão restante mantêm a geometria anterior.

Esta é uma alteração local à V5. Mantêm-se o conjunto visível de **52 × 55 mm**, a frente de aproximadamente **46,13 × 55 × 4,88 mm**, as letras brancas com 1,44 mm sem contorno nem apoio preto e a passagem do lenço de **25 × 18 mm**.

## O que imprimir

- Abrir o **lobo V6** como projeto no Bambu Studio. Filamentos: **1 preto, 2 cinzento, 3 castanho e 4 branco**.
- Usar os [acessórios V5](https://github.com/kruzpt/Build/blob/main/downloads/anilha-aquela-v5-ACESSORIOS-A1-04-AMS-2-pratos.3mf?raw=true): prato 1 anilha, prato 2 folhas. Filamentos: 1 castanho, 2 verde e 3 preto.
- Se as folhas V5 e a anilha já estão impressas, **só é necessário imprimir a nova frente**. O pacote inclui os acessórios V5 sem alterações.

Não imprimir os STL de cada cor separadamente: são volumes de uma montagem multicolor. O branco e o castanho da frente são reutilizados dos STL V5; os nomes dos ficheiros refletem essa reutilização. O STL monocor V6 inclui a frente completa.

Perfil Bambu A1 com bico de 0,4 mm e AMS Lite, PLA, camadas de 0,12 mm e primeira camada de 0,20 mm. Sem suportes nem brim. Perfil Generic PLA de partida, sem nova calibração dos rolos. Estimativa para a frente: cerca de **2 h 10 min**, 6,89 g na peça e 16,46 g incluindo purga e torre.

## Verificação

- Malhas fechadas, volumes de cor sem interseções significativas e correção limitada à zona exterior do olho.
- Branco, castanho, folhas, anilha e projeto dos acessórios reutilizados com os mesmos SHA-256.
- Lobo V6 exportado, reaberto e fatiado no Bambu Studio 02.09.01.70, sem avisos.
- Percursos verificados para as 12 camadas brancas das letras, ausência de cinzento na tabuleta e ausência de preto sob as letras ou no centro escondido das folhas.
- Cinzento efetivamente extrudido na ponta do olho em quatro camadas; sem percursos pretos no interior dessa zona acima do apoio.
- Validação dos acessórios reutilizada da V5, pois o projeto é idêntico; não foi repetida a sua impressão nem o seu fatiamento.

Relatórios em `geometry.json`, `bambu-validation-lobo.json`, `bambu-validation-acessorios.json` e `toolpath-review.json`. A comparação visual é renderizada dos sólidos CAD exportados. **Ainda não existe teste físico da V6.**

As instruções de colagem continuam as da [V5](../AnilhaAquelaV5/README.md): centros e bases da frente e das folhas alinhados; anilha centrada no verso, com bordo inferior a 7,8 mm da base das folhas. Os scripts requerem o checkout completo do repositório e as dependências das versões anteriores.
