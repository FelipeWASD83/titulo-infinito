package dev.tituloinfinito.logica;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class LayoutTest {
    @Test
    void escalaUmSemDeslocamentoEOLugarDoVanilla() {
        // tela de 573 de largura (3440 x 1440 na escala 6): o vanilla põe o logo em x = 573/2 - 128
        Layout l = Layout.calcular(573, 30, 1.0, 0, 0);
        assertEquals(573 / 2.0 - 128, l.origemX(), 1e-9);
        assertEquals(30, l.origemY(), 1e-9);
        assertEquals(0.25, l.porUnidade(), 1e-9);
    }

    @Test
    void splashNoLugarDoVanillaComEscalaUm() {
        Layout l = Layout.calcular(573, 30, 1.0, 0, 0);
        assertEquals(573 / 2.0 + 123, l.splashX(), 1e-9);
        assertEquals(69, l.splashY(), 1e-9);
    }

    @Test
    void escalaCresceAPartirDoCentroDoTopo() {
        Layout l = Layout.calcular(600, 30, 2.0, 0, 0);
        double centro = l.origemX() + 1024 * l.porUnidade() / 2;
        assertEquals(300, centro, 1e-9);
        assertEquals(30, l.origemY(), 1e-9);
    }

    @Test
    void splashAcompanhaDeslocamentoEEscala() {
        Layout l = Layout.calcular(600, 30, 1.5, 10, -5);
        assertEquals(l.origemX() + 251 * 1.5, l.splashX(), 1e-9);
        assertEquals(25 + 39 * 1.5, l.splashY(), 1e-9);
    }
}
