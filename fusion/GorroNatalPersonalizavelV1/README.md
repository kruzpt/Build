# Gorro de Natal personalizável V1

Enfeite plano de duas cores para pendurar na árvore, com ponta branca, base em
neve e nome manuscrito. Mede aproximadamente 85 × 92 mm, tem verso plano e foi
desenhado para imprimir deitado sem suportes.

## Três perfis de texto

| Perfil | Letras previstas | Exemplo | Tamanho nominal |
| --- | ---: | --- | ---: |
| `curto` | 3–5 | Lia | 20,0 mm |
| `medio` | 6–8 | Tomás | 16,0 mm |
| `comprido` | 9–11 | Alexandre | 12,5 mm |

Os intervalos são guias: letras manuscritas não têm todas a mesma largura. Antes
de exportar um nome novo, confirme que fica dentro da área branca.

## Personalizar

Abra `GorroNatalPersonalizavelV1.scad` no OpenSCAD e altere apenas:

```scad
perfil = "medio";
nome = "Tomás";
```

Escolha `curto`, `medio` ou `comprido`, carregue em **F6** e exporte o STL. A
fonte usada é `Z003`, uma letra manuscrita disponível no ambiente de construção.
Se for substituída no computador do utilizador, as métricas podem mudar.

O ficheiro também permite exportar separadamente `corpo`, `branco` e `nome`
através da variável `parte`. Os 3MF de exemplo já contêm esses três objetos
alinhados e com as cores atribuídas.

## Limite da edição no fatiador

O texto dos 3MF fornecidos é geometria e não um campo de texto nativo do Bambu
Studio. Pode ser redimensionado como objeto, mas para escrever outro nome é
necessário regenerar o STL no OpenSCAD ou usar a ferramenta **Text shape** do
Bambu Studio e centrá-la manualmente. O Bambu Studio não ajusta automaticamente
o tamanho de um nome novo.

## Construção

- base vermelha: 3,0 mm;
- dobra vermelha discreta: +0,5 mm;
- detalhes brancos: +0,8 mm;
- nome vermelho: +0,8 mm sobre o branco;
- furo: 5,0 mm;
- brim: desativado por defeito;
- impressão: face plana na mesa, sem suportes.

Para regenerar os três exemplos:

```bash
cd /workspace/Build
/workspace/.venvs/Build/bin/python fusion/GorroNatalPersonalizavelV1/build_gorro_natal.py
```

Os STL foram verificados como malhas fechadas e os 3MF como arquivos legíveis.
Ainda falta abrir e fatiar os projetos no Bambu Studio real e fazer o primeiro
teste físico antes de confirmar acabamento, resistência da argola ou perfil de
impressão.
