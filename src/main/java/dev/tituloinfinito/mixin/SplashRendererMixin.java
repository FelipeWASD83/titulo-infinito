package dev.tituloinfinito.mixin;

import dev.tituloinfinito.cliente.DesenhoDoTitulo;
import dev.tituloinfinito.logica.Layout;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.LogoRenderer;
import net.minecraft.client.gui.components.SplashRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** O texto amarelo anda e cresce junto com o logo quando a posição ou a escala mudam na config. */
@Mixin(SplashRenderer.class)
public abstract class SplashRendererMixin {
    @Unique
    private boolean tituloInfinito$empurrou;

    @Inject(method = "render", at = @At("HEAD"))
    private void tituloInfinito$antes(GuiGraphics g, int larguraTela, Font fonte, int cor, CallbackInfo ci) {
        tituloInfinito$empurrou = false;
        if (!DesenhoDoTitulo.naTelaDeTitulo()) {
            return;
        }
        Layout l = DesenhoDoTitulo.layoutAtual(larguraTela, LogoRenderer.DEFAULT_HEIGHT_OFFSET);
        float vanillaX = larguraTela / 2f + 123f, vanillaY = 69f;
        g.pose().pushPose();
        tituloInfinito$empurrou = true;
        g.pose().translate(l.splashX(), l.splashY(), 0);
        g.pose().scale((float) l.escala(), (float) l.escala(), 1f);
        g.pose().translate(-vanillaX, -vanillaY, 0);
    }

    @Inject(method = "render", at = @At("RETURN"))
    private void tituloInfinito$depois(GuiGraphics g, int larguraTela, Font fonte, int cor, CallbackInfo ci) {
        if (tituloInfinito$empurrou) {
            g.pose().popPose();
            tituloInfinito$empurrou = false;
        }
    }
}
