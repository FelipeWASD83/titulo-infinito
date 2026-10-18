package dev.tituloinfinito;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.client.gui.ConfigurationScreen;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

/** Só cliente: o mod só muda o desenho do logo da tela de título. */
@Mod(value = TituloInfinitoMod.ID, dist = Dist.CLIENT)
public final class TituloInfinitoMod {
    public static final String ID = "titulo_infinito";

    public TituloInfinitoMod(ModContainer mod) {
        mod.registerConfig(ModConfig.Type.CLIENT, Config.SPEC);
        // botão "Config" na lista de mods, com a tela de opções pronta do NeoForge
        mod.registerExtensionPoint(IConfigScreenFactory.class, ConfigurationScreen::new);
    }
}
