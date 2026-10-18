# MC:INFINITO: logo do título (mod de Minecraft)

Troca o logo da tela de título do Minecraft por **MINECRAFT com INFINITO embaixo**. O INFINITO é um modelo 3D na
mesma fonte do logo original, visto de baixo como a segunda linha do logo do Minecraft Mini Series (a espessura em
cima, encostada no MINECRAFT, e a face embaixo), pintado com o arco-íris do bloco de infinito do Avaritia e com a
espessura cósmica cheia de estrelas. As cores correm pelas letras e as estrelas piscam. Feito para o modpack
MC:INFINITO (Minecraft 1.21.1, NeoForge). Só roda no cliente: não precisa estar no servidor.

## Ajustar posição, tamanho e animação

Na tela de título, abra **Mods**, escolha **MC:INFINITO** e clique em **Config**. Ou edite
`config/titulo_infinito-client.toml` com o jogo aberto: ele relê o arquivo sozinho.

- **Posição horizontal / vertical:** desloca o logo, em pixels da interface (positivo vai para a direita e para baixo).
- **Tamanho:** 1.0 é a largura do logo original. Cresce a partir do topo, no centro. Acima de 1.0 o INFINITO pode
  encostar nos botões.
- **Animar as cores:** liga e desliga o movimento.
- **Segundos por volta:** quanto o arco-íris demora para dar uma volta inteira (padrão 6).

O texto amarelo que pula ao lado do logo acompanha a posição e o tamanho.

## Instalar

Copie `titulo_infinito-neoforge-1.21.1-<versão>.jar` (em `build/libs` depois de compilar) para a pasta `mods` da
instância. Compilar: `.\gradlew.bat build` na pasta do projeto.

## Mudar o desenho

O 3D e as cores saem de `ferramentas/render_infinito.py` (Python com numpy e Pillow). Rode
`python ferramentas\render_infinito.py` e depois compile de novo. Com `--previa` seguido do caminho do jar do
Minecraft 1.21.1, ele também salva uma prévia (imagem e animação) em `ferramentas/saida`.
