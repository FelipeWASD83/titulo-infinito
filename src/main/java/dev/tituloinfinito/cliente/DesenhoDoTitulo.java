package dev.tituloinfinito.cliente;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.systems.RenderSystem;
import dev.tituloinfinito.Config;
import dev.tituloinfinito.TituloInfinitoMod;
import dev.tituloinfinito.logica.Animacao;
import dev.tituloinfinito.logica.Layout;
import java.io.Reader;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.LogoRenderer;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Desenha MINECRAFT (a textura do próprio jogo) por cima do INFINITO (quadros renderizados pela ferramenta
 * {@code ferramentas/render_infinito.py}). Nada de 3D aqui: o 3D já veio pronto nas imagens.
 */
public final class DesenhoDoTitulo {
    private static final Logger LOG = LoggerFactory.getLogger(TituloInfinitoMod.ID);
    private static final ResourceLocation INFO = ResourceLocation.fromNamespaceAndPath(TituloInfinitoMod.ID, "infinito.json");

    private static Info info;
    private static boolean carregou;

    private record Info(int x, int y, int largura, int altura, int pxLargura, int pxAltura, ResourceLocation[] quadros) {
    }

    private DesenhoDoTitulo() {
    }

    /** Fora da tela de título (créditos do fim do jogo) o logo fica no lugar e no tamanho do vanilla. */
    public static Layout layoutAtual(int larguraTela, int topoVanilla) {
        if (Minecraft.getInstance().screen instanceof TitleScreen && Config.SPEC.isLoaded()) {
            return Layout.calcular(larguraTela, topoVanilla, Config.ESCALA.get(), Config.POSICAO_X.get(), Config.POSICAO_Y.get());
        }
        return Layout.calcular(larguraTela, topoVanilla, 1.0, 0, 0);
    }

    /** O splash só acompanha o logo do mod; se o mod desistiu, ele volta para o lugar do vanilla. */
    public static boolean naTelaDeTitulo() {
        return !desistiu && Minecraft.getInstance().screen instanceof TitleScreen && Config.SPEC.isLoaded();
    }

    /**
     * Devolve false se não conseguiu desenhar; aí o mixin deixa o vanilla desenhar o logo dele. Depois da
     * primeira falha o mod para de tentar, para não lotar o log nem travar a tela de título.
     */
    public static boolean desenhar(GuiGraphics g, int larguraTela, float alfa, int topoVanilla, boolean minceraft) {
        if (desistiu) {
            return false;
        }
        try {
            desenharSemProteger(g, larguraTela, alfa, topoVanilla, minceraft);
            return true;
        } catch (Throwable t) {
            desistiu = true;
            LOG.error("O logo do MC:INFINITO falhou; a tela de título volta para o logo do Minecraft", t);
            return false;
        }
    }

    private static boolean desistiu;

    private static void desenharSemProteger(GuiGraphics g, int larguraTela, float alfa, int topoVanilla, boolean minceraft) {
        Layout l = layoutAtual(larguraTela, topoVanilla);
        Info i = info();
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        g.pose().pushPose();
        try {
            desenharNaPose(g, l, i, alfa, minceraft);
        } finally {
            g.setColor(1f, 1f, 1f, 1f);
            g.pose().popPose();
            RenderSystem.disableBlend();
        }
    }

    private static void desenharNaPose(GuiGraphics g, Layout l, Info i, float alfa, boolean minceraft) {
        g.pose().translate(l.origemX(), l.origemY(), 0);
        g.pose().scale((float) l.porUnidade(), (float) l.porUnidade(), 1f);
        if (i != null) {
            boolean animar = !Config.SPEC.isLoaded() || Config.ANIMAR.get();
            double segundos = Config.SPEC.isLoaded() ? Config.SEGUNDOS_POR_VOLTA.get() : 6.0;
            Animacao a = Animacao.em(Util.getMillis(), segundos, i.quadros.length, animar);
            g.setColor(1f, 1f, 1f, alfa);
            blitInfinito(g, i, i.quadros[a.atual()]);
            if (a.mistura() > 0.004f) {
                g.setColor(1f, 1f, 1f, alfa * a.mistura());
                blitInfinito(g, i, i.quadros[a.seguinte()]);
            }
        }
        g.setColor(1f, 1f, 1f, alfa);
        // o minecraft.png tem 1024 x 256; o logo ocupa as 176 linhas de cima (256 x 44 de 256 x 64, como no vanilla)
        g.blit(minceraft ? LogoRenderer.EASTER_EGG_LOGO : LogoRenderer.MINECRAFT_LOGO, 0, 0, 1024, 176, 0f, 0f, 256, 44, 256, 64);
    }

    private static void blitInfinito(GuiGraphics g, Info i, ResourceLocation quadro) {
        g.blit(quadro, i.x, i.y, i.largura, i.altura, 0f, 0f, i.pxLargura, i.pxAltura, i.pxLargura, i.pxAltura);
    }

    /** Lê o infinito.json uma vez e já carrega todos os quadros, para a animação não engasgar na primeira volta. */
    private static Info info() {
        if (carregou) {
            return info;
        }
        carregou = true;
        Minecraft mc = Minecraft.getInstance();
        try (Reader r = mc.getResourceManager().getResourceOrThrow(INFO).openAsReader()) {
            JsonObject o = JsonParser.parseReader(r).getAsJsonObject();
            int n = o.get("quadros").getAsInt();
            ResourceLocation[] quadros = new ResourceLocation[n];
            for (int k = 0; k < n; k++) {
                quadros[k] = ResourceLocation.fromNamespaceAndPath(TituloInfinitoMod.ID,
                        String.format("textures/gui/infinito/quadro_%02d.png", k));
                mc.getTextureManager().getTexture(quadros[k]);
            }
            var px = o.getAsJsonArray("pixels");
            info = new Info(o.get("x").getAsInt(), o.get("y").getAsInt(), o.get("largura").getAsInt(),
                    o.get("altura").getAsInt(), px.get(0).getAsInt(), px.get(1).getAsInt(), quadros);
        } catch (Exception e) {
            LOG.error("Não consegui ler os quadros do INFINITO; o título fica só com o MINECRAFT", e);
            info = null;
        }
        return info;
    }
}
