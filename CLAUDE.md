# CLAUDE.md: titulo-infinito

Mod de Minecraft (NeoForge 1.21.1, só cliente) que troca o logo da tela de título por **MINECRAFT com INFINITO
embaixo**, nas cores do Avaritia, para o modpack **MC:INFINITO** (a instância do Prism que antes se chamava
"Horizonte Infinito"; a pasta no disco continua `instances\Horizonte Infinito`). Pedido pelo Felipe em 17/10/2026.
**Repositório público** (escolha dele). O `CLAUDE.md` da raiz vale aqui também; o `README.md` explica o mod para ele.

## Decisões dele

- O visual segue o print do "Minecraft Mini Series" que ele mandou: MINECRAFT original em cima, a segunda palavra
  menor, centralizada, com metade da barra de cima escondida atrás do MINECRAFT.
- **O INFINITO é 3D de verdade, renderizado fora do jogo** ("faz o 3D e depois renderiza a imagem para não pesar
  no jogo"). A primeira tentativa, que recortava letras do logo vanilla e colava, ficou errada: o logo tem
  perspectiva, e letra tirada de uma posição fica com a lateral virada para o lado errado em outra.
- A animação também é pré-renderizada (48 quadros); o mod só troca a imagem. Nada de shader.
- Ele gostou das cores da primeira versão (arco-íris do bloco de infinito, lateral cósmica com estrelas); o extra
  que ele aprovou foram as estrelas piscando. O editor de arrastar com o mouse ficou de fora (não pedido).
- **Não abrir o jogo por conta própria**: ele respondeu "não abre" para o teste no `runClient` em 17/10/2026.

## Como funciona

- `ferramentas/render_infinito.py`: o 3D. Câmera calibrada medindo o logo vanilla do 1.21.1 (ponto de fuga da
  profundidade em (528, -1470) e das verticais em (528, 838), em coordenadas do minecraft.png de 1024); as letras
  são blocos deitados numa grade (traço de 3 colunas, 1 de espaço, 10 meias-linhas), a fonte foi tirada do próprio
  logo "desentortado" para a planta. Cada pixel lança um raio: topo = face colorida, frente = faixa cósmica,
  paredes dos lados = preto, como no vanilla. `--conferir <jar>` renderiza o MINECRAFT com a mesma câmera e compara
  com o original (98,6% de silhueta igual em 17/10/2026; a diferença são as rachaduras de pedra, não modeladas).
  Sem argumento, grava os quadros e o `infinito.json` no mod; `--previa <jar>` também faz PNG e WebP animado em
  `ferramentas/saida` (fora do git). Leva ~1 min.
- `assets/titulo_infinito/infinito.json`: onde o INFINITO fica em relação ao logo (unidades do minecraft.png, 4 por
  pixel de interface) e o tamanho dos quadros. Gerado pela ferramenta; não editar à mão.
- `mixin/LogoRendererMixin`: entra no começo do `renderLogo(GuiGraphics, int, float, int)` e desenha tudo
  (`cliente/DesenhoDoTitulo`). O MINECRAFT é a textura do próprio jogo (não vai no jar). O "Java Edition" sai,
  porque cairia em cima do INFINITO. Se o desenho falhar, ele registra no log uma vez e devolve o logo vanilla.
- `mixin/SplashRendererMixin`: o texto amarelo acompanha posição e escala do logo.
- `Config`: `config/titulo_infinito-client.toml` (posicaoX, posicaoY, escala, animar, segundosPorVolta), com tela
  no botão Config da lista de mods. Posição e escala só valem na tela de título; nos créditos o logo fica no lugar
  vanilla.
- `logica/` (sem Minecraft, com testes): `Layout` (onde o logo e o splash vão) e `Animacao` (qual quadro e quanto
  misturar com o seguinte).

## Como compilar e instalar

```powershell
python ferramentas\render_infinito.py      # só se mudar o 3D ou as cores
.\gradlew.bat build                        # testes + jar em build\libs
```

Instalar: copiar o jar de `build\libs` para `%APPDATA%\PrismLauncher\instances\Horizonte Infinito\minecraft\mods`.
Base de build copiada da `bancada-minecraft` (Gradle, NeoForge 21.1.252, Parchment).

## Armadilhas

- **Outros mods mexem no mesmo método:** o Aether (logo e splash) e o Aquamirae (logo) usam `@WrapOperation` no
  `blit` de dentro do `renderLogo`. O mod cancela o método antes, então os deles aplicam sem erro e não rodam (o
  menu do Aether está desligado no pack: `cumulus_menus-client.toml`, "Active Menu" = minecraft).
- No GUI Scale automático dele (6 em 3440 x 1440, 573 x 240 de interface) o logo termina na linha ~103 e o
  primeiro botão começa na 108. Aumentar a escala pela config faz o logo encostar nos botões.
- Mudou `TOPO_Y`/`BASE_Y` ou a câmera na ferramenta? Os quadros e o `infinito.json` mudam juntos; rodar a
  ferramenta antes do build.
- Script de edição com barra invertida não vai por heredoc no Bash (comeu a barra duas vezes aqui).
