package dev.tituloinfinito.logica;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class AnimacaoTest {
    @Test
    void desligadaFicaNoPrimeiroQuadro() {
        Animacao a = Animacao.em(123456, 6, 48, false);
        assertEquals(0, a.atual());
        assertEquals(0f, a.mistura());
    }

    @Test
    void meioDoQuadroMisturaMetade() {
        // 6 s e 48 quadros: 125 ms por quadro
        Animacao a = Animacao.em(125 * 3 + 62, 6, 48, true);
        assertEquals(3, a.atual());
        assertEquals(4, a.seguinte());
        assertEquals(0.496f, a.mistura(), 0.001f);
    }

    @Test
    void ultimoQuadroEmendaNoPrimeiro() {
        Animacao a = Animacao.em(5999, 6, 48, true);
        assertEquals(47, a.atual());
        assertEquals(0, a.seguinte());
    }

    @Test
    void voltaSeRepete() {
        Animacao a = Animacao.em(6000L * 1000 + 250, 6, 48, true);
        assertEquals(2, a.atual());
    }
}
