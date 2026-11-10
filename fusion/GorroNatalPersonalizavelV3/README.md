# Gorro de Natal personalizável V3

Versão redesenhada a partir do conceito aprovado: copa curva com ponta caída,
recorte junto ao pompom, dobra arqueada e aba branca com cinco lóbulos.

## Instalar a fonte antes de abrir o projeto

O pacote inclui `Lobster-Regular.ttf`, distribuída sob a SIL Open Font License.
No Windows:

1. feche o Bambu Studio;
2. clique com o botão direito em `Lobster-Regular.ttf`;
3. escolha **Instalar para todos os utilizadores**;
4. volte a abrir o Bambu Studio e só depois abra o 3MF;
5. ao editar o volume `Nome ...`, confirme que o campo **Font** mostra
   `Lobster`.

Se o projeto for aberto antes da instalação, o Bambu Studio pode substituir a
fonte por Arial. Nesse caso, instale a fonte, reinicie o programa e selecione
manualmente `Lobster` no campo **Font**.

## Perfis

| Projeto | Guia | Exemplo | Tamanho inicial |
| --- | --- | --- | ---: |
| curto | 3–5 letras | Lia | 15,5 mm |
| médio | 6–8 letras | Tomás | 14,5 mm |
| comprido | 9–11 letras | Alexandre | 10,8 mm |

O tamanho não muda automaticamente. Se o novo nome sair da aba, escolha o
perfil adequado ou ajuste `Size`, mantendo a fonte `Lobster`.

## Impressão

- até 98,5 × 93,1 × 4,6 mm, conforme o nome;
- corpo e nome: extrusor 1, vermelho;
- aba e pompom: extrusor 2, branco;
- furo: 5 mm;
- bico previsto: 0,4 mm;
- sem suportes e sem brim por defeito.

O Bambu Studio 2.9.1.70 reabriu e voltou a guardar o projeto com a fonte
instalada, preservando `font_name="Lobster"`, tamanho e espessura. As malhas e
a montagem são verificadas automaticamente por `verify_bambu_projects.py`.
