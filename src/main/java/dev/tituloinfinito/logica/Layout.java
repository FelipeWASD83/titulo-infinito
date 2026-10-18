package dev.tituloinfinito.logica;

/**
 * Onde o logo vai na tela. Tudo em "unidades do logo": as do minecraft.png vanilla de 1024 de largura, em que
 * 4 unidades são 1 pixel de interface na escala 1.
 *
 * @param origemX    canto esquerdo do logo na tela (pixels de interface)
 * @param origemY    topo do logo na tela (pixels de interface)
 * @param porUnidade pixels de interface por unidade do logo
 */
public record Layout(double origemX, double origemY, double porUnidade) {
    /** O vanilla desenha o logo com 256 pixels de largura, centralizado. */
    public static final double LARGURA_VANILLA = 256;
    /** Onde o vanilla põe o centro do texto amarelo, em relação ao canto do logo (com o logo em y = 30). */
    public static final double SPLASH_X = 128 + 123, SPLASH_Y = 69 - 30;

    /** escala 1 e deslocamento 0 dão exatamente o lugar do logo vanilla; a escala cresce a partir do topo, no centro. */
    public static Layout calcular(int larguraTela, int topoVanilla, double escala, int deslocX, int deslocY) {
        double origemX = larguraTela / 2.0 - LARGURA_VANILLA / 2 * escala + deslocX;
        double origemY = topoVanilla + deslocY;
        return new Layout(origemX, origemY, escala / 4.0);
    }

    public double escala() {
        return porUnidade * 4.0;
    }

    /** Centro do texto amarelo, acompanhando o logo. */
    public double splashX() {
        return origemX + SPLASH_X * escala();
    }

    public double splashY() {
        return origemY + SPLASH_Y * escala();
    }
}
