package dev.tituloinfinito.mixin;

import dev.tituloinfinito.cliente.DesenhoDoTitulo;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.LogoRenderer;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Troca o desenho do logo inteiro (o "Java Edition" sai, porque cairia em cima do INFINITO). */
@Mixin(LogoRenderer.class)
public abstract class LogoRendererMixin {
    @Shadow
    @Final
    private boolean showEasterEgg;

    @Shadow
    @Final
    private boolean keepLogoThroughFade;

    @Inject(method = "renderLogo(Lnet/minecraft/client/gui/GuiGraphics;IFI)V", at = @At("HEAD"), cancellable = true)
    private void tituloInfinito$desenhar(GuiGraphics g, int larguraTela, float transparencia, int topo, CallbackInfo ci) {
        if (DesenhoDoTitulo.desenhar(g, larguraTela, keepLogoThroughFade ? 1f : transparencia, topo, showEasterEgg)) {
            ci.cancel();
        }
    }
}
