# Gallardo + TOMAS V4 — orientação do nome e suportes explícitos

O nome foi rodado **180° em relação ao carro**. Vendo o carro de lado, com a
frente para a direita, e inclinando a peça para observar o topo mantendo a
mesma esquerda/direita, passa a ler-se **TOMAS direito**. A imagem
`gallardo-tomas-v4-orientacao.png` usa o mesmo lado de observação nas duas vistas;
a vista superior não foi rodada separadamente para facilitar a leitura.

## Abrir o projeto

Abrir `gallardo-tomas-v4-A1-04-texto-direito-suportes-ON.3mf` como **projeto**,
carregando as configurações incluídas. O processo selecionado deve chamar-se:

**Gallardo TOMAS V4 - 0.10mm A1 0.4 - Tree Slim ON**

- Impressora: **Bambu Lab A1, bico físico de 0,4 mm**.
- Camadas: **0,10 mm**, primeira camada **0,20 mm**.
- PLA preto, uma só cor; confirmar o mapeamento do rolo no AMS ou alimentação externa.
- **Suportes ativados no processo global e também no objeto**.
- Árvore automática **Tree Slim**, só a partir do prato.
- Interface de 2 camadas, espaçamento de 0,45 mm, folga Z de 0,20 mm e lateral de 0,40 mm.
- Sem brim; orientação de impressão deitada sobre um lado, já definida no ficheiro.

O STL incluído contém apenas a geometria. Para conservar as configurações de
suporte e máquina, utilizar o **3MF como projeto**.

Estimativa nativa: **8 h 08 min e 32,8 g de PLA**, incluindo os suportes.

## Sobre os suportes do V3

No V3 publicado, o campo global `enable_support` estava guardado como `1` e o
fatiamento nativo produziu percursos de suporte. Não foi possível reproduzir o
estado desativado que o utilizador observou na sua interface; a causa desse
estado não está estabelecida.

Esta versão usa um nome de processo próprio, declara as diferenças face ao
perfil de sistema e guarda a ativação também como configuração do objeto.
A validação exige que o fatiador volte a exportar o mesmo processo, mantenha
os dois campos de ativação e produza material de suporte no G-code.
Isto verifica o ficheiro e o motor de fatiamento, não a interface no computador
do utilizador.

## Geometria e remoção dos apoios

A rotação muda os cruzamentos entre letras e traços do carro. Uma ligação
discreta, de 1,2 mm de diâmetro, junto à soleira inferior liga o novo pequeno
detalhe que ficava separado. A ligação é limitada pelo volume das letras,
conservando o contorno do nome visto de cima. O resultado continua a ser um
único corpo fechado, com cerca de 150 × 30 × 37,3 mm na apresentação.

Os suportes usam a configuração de remoção da V3. Deixar arrefecer e retirar
os ramos por pequenas secções, apoiando os traços finos do carro. O contacto
entre PLA e PLA pode deixar marcas; a remoção física ainda não foi testada.

## Validação e reprodução

`validation.json` regista dimensões, rotação, reforço local, hashes, estado dos
suportes em ambos os níveis, conservação desse estado após exportação nativa,
percursos reais e estimativas do fatiador. As imagens são projeções das malhas
ou percursos do G-code; não são fotografias de uma impressão física.

No checkout do repositório, com numpy, trimesh, manifold3d e Pillow:

```sh
python fusion/tools/build_gallardo_tomas_v4.py \
  --source /caminho/sharegallardo-straight-sill-v1.3mf \
  --bambu-bin /caminho/bambu-studio \
  --work-dir /caminho/temporario
```

É necessário o ficheiro anterior à interseção enviado pelo utilizador, não
incluído neste pacote. O script reutiliza os perfis completos da V3 e preserva
a autoria de **Dava** e a licença **Standard Digital File License** do modelo
base. Nenhuma impressão foi iniciada numa máquina física.
