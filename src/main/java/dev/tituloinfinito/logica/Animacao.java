package dev.tituloinfinito.logica;

/**
 * Qual quadro do INFINITO desenhar agora. Os quadros fecham uma volta (o último emenda no primeiro); entre dois
 * quadros o mod desenha o seguinte por cima com a transparência {@code mistura}, para a cor andar sem degrau.
 */
public record Animacao(int atual, int seguinte, float mistura) {
    public static Animacao em(long milissegundos, double segundosPorVolta, int quadros, boolean animar) {
        if (!animar || quadros <= 1 || segundosPorVolta <= 0) {
            return new Animacao(0, 0, 0f);
        }
        double volta = segundosPorVolta * 1000.0;
        double posicao = (milissegundos % (long) Math.max(1, Math.round(volta))) / volta * quadros;
        int atual = (int) Math.floor(posicao) % quadros;
        return new Animacao(atual, (atual + 1) % quadros, (float) (posicao - Math.floor(posicao)));
    }
}
