package dev.tituloinfinito;

import net.neoforged.neoforge.common.ModConfigSpec;

/**
 * config/titulo_infinito-client.toml. O NeoForge relê o arquivo quando ele muda, e a tela de título lê os valores
 * a cada quadro, então dá para ajustar com o jogo aberto.
 */
public final class Config {
    private static final ModConfigSpec.Builder B = new ModConfigSpec.Builder();

    public static final ModConfigSpec.IntValue POSICAO_X = B
            .comment("Desloca o logo para a direita (positivo) ou para a esquerda (negativo), em pixels da interface.")
            .defineInRange("posicaoX", 0, -2000, 2000);
    public static final ModConfigSpec.IntValue POSICAO_Y = B
            .comment("Desloca o logo para baixo (positivo) ou para cima (negativo), em pixels da interface.")
            .defineInRange("posicaoY", 0, -2000, 2000);
    public static final ModConfigSpec.DoubleValue ESCALA = B
            .comment("Tamanho do logo. 1.0 é a largura do logo original do Minecraft; cresce a partir do topo, no centro.")
            .defineInRange("escala", 1.0, 0.25, 4.0);
    public static final ModConfigSpec.BooleanValue ANIMAR = B
            .comment("Faz as cores do INFINITO correrem e as estrelas piscarem.")
            .define("animar", true);
    public static final ModConfigSpec.DoubleValue SEGUNDOS_POR_VOLTA = B
            .comment("Quantos segundos o arco-íris leva para dar uma volta inteira. Menor = mais rápido.")
            .defineInRange("segundosPorVolta", 6.0, 1.0, 60.0);

    public static final ModConfigSpec SPEC = B.build();

    private Config() {
    }
}
