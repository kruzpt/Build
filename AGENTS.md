# Entrega de ficheiros deste projeto

O utilizador pediu que os ficheiros sejam acessíveis no GitHub. Links locais
`/workspace/...` não funcionaram na aplicação e não bastam como entrega.

- Use o checkout existente; não crie um worktree sem pedido explícito.
- Guarde scripts Fusion em `fusion/`, imagens e desenhos em `designs/`,
  e pacotes de download em `downloads/`.
- Preserve os ficheiros anteriores. Nomeie novas versões de desenhos de forma
  explícita e atualize os ZIPs quando os respetivos scripts mudarem.
- Para este projeto, o utilizador autorizou enviar futuros ficheiros produzidos
  para o repositório `kruzpt/Build`. Depois de validar os ficheiros, faça commit
  apenas do trabalho relevante e envie para `main` sem force push. Verifique
  primeiro alterações remotas e preserve alterações de outros autores.
- Não envie segredos, credenciais, caches ou ficheiros temporários.
- Confirme o sucesso do push e que o commit está na referência remota antes
  de afirmar que um ficheiro está disponível no GitHub.
- Na entrega, forneça links `https://github.com/kruzpt/Build/blob/main/...`.
  Para download direto, pode usar a mesma página com `?raw=true`; não dependa
  exclusivamente de links locais do ambiente.
- Se o envio falhar, explique o bloqueio e não afirme que foi publicado.

Este fluxo de entrega não autoriza alterações sem relação com o pedido atual.

# Preferências de impressão

- Por indicação do utilizador, não ativar brim por defeito nos novos projetos.
  Reservá-lo para casos concretos que precisem de mais adesão e explicar a razão.

# Fluxo de aprovação de novas peças

- Por indicação explícita do utilizador, apresentar primeiro uma imagem de
  conceito ou um plano da peça, com medidas propostas e pontos por confirmar.
- Aguardar a aprovação desse aspeto/plano antes de preparar e entregar o
  projeto final de modelação ou os ficheiros de impressão STL/3MF.
- Uma geometria auxiliar usada para gerar a prévia é um rascunho de conceito;
  não a apresentar nem publicar como projeto final aprovado.
- Depois da aprovação visual, avançar com a modelação final, configurações,
  verificação e entrega. A aprovação do conceito não equivale a teste físico.

# Perfis de filamento reutilizáveis

- O utilizador quer perfis guardáveis na biblioteca do Bambu Studio, disponíveis
  entre projetos. Consultar `fusion/FilamentLibraryA1/` e reutilizar os perfis
  calibrados compatíveis em vez de criar nomes com sufixos de cada projeto.
- O laranja calibrado para A1 / bico 0,4 mm está em
  `downloads/sunlu-pla-plus-laranja-0931-A1-04.json`. Não assumir que a calibração
  se transfere para outro bico. Distinguir um ficheiro importável de um perfil
  efetivamente instalado na biblioteca do computador do utilizador.
