"""Modela o INFINITO em blocos 3D na mesma fonte e na mesma câmera do logo do Minecraft 1.21.1 e renderiza
os quadros da animação que o mod desenha.

Uso:
    python ferramentas/render_infinito.py                      # gera os quadros no mod
    python ferramentas/render_infinito.py --conferir <jar>     # renderiza o MINECRAFT e compara com o vanilla
    python ferramentas/render_infinito.py --previa <jar>       # prévia (PNG e WebP animado) em ferramentas/saida

<jar> é o client do 1.21.1 (no Prism: libraries/com/mojang/minecraft/1.21.1/minecraft-1.21.1-client.jar).

Coordenadas "do logo": as do minecraft.png vanilla de 1024 x 256 (o jogo desenha 256 x 44 pixels de GUI a partir
das 176 linhas de cima, então 4 unidades do logo = 1 pixel de GUI).

A geometria: as letras são blocos deitados, vistos de cima e de frente por uma câmera inclinada. A face clara é o
topo, a faixa de baixo é a frente e as paredes dos lados ficam pretas (como no logo vanilla). A câmera foi
calibrada medindo o logo vanilla: o ponto de fuga da profundidade fica em (528, -1470) e o das verticais em
(528, 838), por isso as letras da esquerda e da direita inclinam para lados opostos.
"""
import argparse
import colorsys
import io
import json
import math
import random
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
SAIDA_MOD = RAIZ / "src/main/resources/assets/titulo_infinito/textures/gui/infinito"
SAIDA_INFO = RAIZ / "src/main/resources/assets/titulo_infinito/infinito.json"
SAIDA_RASCUNHO = RAIZ / "ferramentas/saida"

class Camera:
    """Câmera inclinada para baixo, definida pelos dois pontos de fuga na vertical que passa por cx: o horizonte
    (para onde vai a profundidade) e o nadir (para onde vão as verticais), em coordenadas do logo."""

    def __init__(self, cx, cy, y_horizonte, y_nadir):
        self.cx, self.cy = cx, cy
        self.foco = math.sqrt((cy - y_horizonte) * (y_nadir - cy))
        incl = math.atan((cy - y_horizonte) / self.foco)
        self.sen, self.cos = math.sin(incl), math.cos(incl)


# --- câmera calibrada no logo vanilla (coordenadas do logo) ---
CAM_LOGO = Camera(528.0, 64.0, -1470.0, 838.0)
ALTURA = 100.0                      # câmera acima do topo das letras (unidade do mundo)
Z_PERTO, Z_LONGE = 62.3588, 78.9094  # profundidade das 10 meias-linhas do MINECRAFT
ESPESSURA = 7.95                    # altura dos blocos
UNID = 1.57465                      # largura de uma coluna da fonte
X0_MINECRAFT = -56.05
DZ = (Z_LONGE - Z_PERTO) / 10       # profundidade de uma meia-linha

# --- a fonte do logo, tirada do minecraft.png (10 meias-linhas; a linha 0 é a do fundo) ---
FONTE = {
    "M": ["###....###", "###....###", "####..####", "####..####", "##########",
          "##########", "###.##.###", "###.##.###", "###....###", "###....###"],
    "I": ["###"] * 10,
    "N": ["###..###", "###..###", "####.###", "####.###", "########",
          "###.####", "###.####", "###..###", "###..###", "###..###"],
    "E": ["#######", "#######", "###....", "###....", "#######",
          "#######", "###....", "###....", "#######", "#######"],
    "C": ["#######", "#######", "###....", "###....", "###....",
          "###....", "###....", "###....", "#######", "#######"],
    "R": ["#######", "#######", "###.###", "###.###", "######.",
          "#######", "###.###", "###.###", "###.###", "###.###"],
    "A": ["#######", "#######", "##.#.##", "###.###", "##...##",
          "##.#.##", "#######", "###.###", "###.###", "###.###"],
    "F": ["#######", "#######", "###....", "###....", "#######",
          "#######", "###....", "###....", "###....", "###...."],
    "T": ["#######", "#######", "..###..", "..###..", "..###..",
          "..###..", "..###..", "..###..", "..###..", "..###.."],
    # O no mesmo desenho do R e do A: bloco de 7 com o furo de uma coluna
    "O": ["#######", "#######", "###.###", "###.###", "###.###",
          "###.###", "###.###", "###.###", "#######", "#######"],
}

TOPO, FRENTE, LADO = 1, 2, 3


def grade_da_palavra(palavra):
    colunas = []
    for i, ch in enumerate(palavra):
        if i:
            colunas.append(["."] * 10)
        g = FONTE[ch]
        for c in range(len(g[0])):
            colunas.append([g[r][c] for r in range(10)])
    return np.array([[colunas[c][r] == "#" for c in range(len(colunas))] for r in range(10)])


class Palavra:
    """Uma palavra deitada no plano do topo: canto esquerdo em x_esq, borda de perto em z_perto, escala k."""

    def __init__(self, palavra, x_esq, z_perto, k, espessura=None, de_ponta_cabeca=False):
        self.grade = grade_da_palavra(palavra)
        if de_ponta_cabeca:
            # a imagem vai ser virada de cabeça para baixo depois; a grade vira antes para o texto ler normal
            self.grade = self.grade[::-1]
        self.x_esq, self.z_perto, self.k = x_esq, z_perto, k
        self.ncol = self.grade.shape[1]
        self.espessura = ESPESSURA * k if espessura is None else espessura

    def dentro(self, X, Z):
        col = np.floor((X - self.x_esq) / (self.k * UNID)).astype(int)
        lin = 9 - np.floor((Z - self.z_perto) / (self.k * DZ)).astype(int)
        ok = (col >= 0) & (col < self.ncol) & (lin >= 0) & (lin < 10)
        res = np.zeros(X.shape, bool)
        res[ok] = self.grade[lin[ok], col[ok]]
        return res

    def fonte_xy(self, X, Z):
        """Posição contínua na grade da fonte (coluna, meia-linha)."""
        return (X - self.x_esq) / (self.k * UNID), 10 - (Z - self.z_perto) / (self.k * DZ)


def projetar(X, Y, Z, cam=CAM_LOGO):
    pf = -Y * cam.sen + Z * cam.cos
    pd = -Y * cam.cos - Z * cam.sen
    return cam.cx + cam.foco * X / pf, cam.cy + cam.foco * pd / pf


def z_na_linha(y, Y=-ALTURA, cam=CAM_LOGO):
    k = (y - cam.cy) / cam.foco
    return (-Y * cam.cos + k * Y * cam.sen) / (k * cam.cos + cam.sen)


def x_na_coluna(x, Z, Y=-ALTURA, cam=CAM_LOGO):
    return (x - cam.cx) * (-Y * cam.sen + Z * cam.cos) / cam.foco


def lancar_raios(palavra, x0, y0, largura, altura, escala, passos=160, cam=CAM_LOGO):
    """Para cada pixel da janela (em coordenadas do logo), acha a face que o raio acerta."""
    w, h = int(round(largura * escala)), int(round(altura * escala))
    px = x0 + (np.arange(w) + 0.5) / escala
    py = y0 + (np.arange(h) + 0.5) / escala
    A, B = np.meshgrid((px - cam.cx) / cam.foco, (py - cam.cy) / cam.foco)
    dx, dy, dz = A, -cam.sen - B * cam.cos, cam.cos - B * cam.sen
    tipo = np.zeros((h, w), np.uint8)
    X_hit = np.zeros((h, w))
    Z_hit = np.zeros((h, w))
    v_hit = np.zeros((h, w))
    borda = np.zeros((h, w), bool)
    descendo = dy < 0
    t_topo = np.where(descendo, -ALTURA / np.where(descendo, dy, -1), np.inf)
    t_base = np.where(descendo, (-ALTURA - palavra.espessura) / np.where(descendo, dy, -1), np.inf)
    pendente = descendo.copy()
    Xa = Za = None
    for j in range(passos + 1):
        t = t_topo + (t_base - t_topo) * (j / passos)
        X, Z = t * dx, t * dz
        dentro = palavra.dentro(X, Z) & pendente
        if j == 0:
            tipo[dentro] = TOPO
            X_hit[dentro], Z_hit[dentro] = X[dentro], Z[dentro]
            perto = ~palavra.dentro(X, Z - 0.22 * palavra.k)
            borda[dentro & perto] = True
        else:
            pela_frente = dentro & ~palavra.dentro(X, Za)
            tipo[pela_frente] = FRENTE
            tipo[dentro & ~pela_frente] = LADO
            X_hit[dentro], Z_hit[dentro] = X[dentro], Z[dentro]
            Y = t * dy
            v_hit[dentro] = ((-ALTURA - Y) / palavra.espessura)[dentro]
        pendente &= ~dentro
        Xa, Za = X, Z
    return {"tipo": tipo, "X": X_hit, "Z": Z_hit, "v": v_hit, "borda": borda, "py": np.broadcast_to(py[:, None], (h, w))}


def contorno(alfa, raio_px):
    """Contorno preto arredondado em volta de tudo (o logo vanilla tem uns 10 unidades)."""
    img = Image.fromarray((alfa * 255).astype(np.uint8))
    r = max(1, int(round(raio_px)))
    # desfoque + corte: com sigma 0,55 r e corte em 3,4% a borda anda r pixels e os cantos saem arredondados
    borrado = np.array(img.filter(ImageFilter.GaussianBlur(r * 0.55))).astype(float) / 255
    return np.maximum(np.clip((borrado - 0.034) * 40, 0, 1), alfa)


def reduzir(rgba, fator):
    img = Image.fromarray(np.clip(rgba * 255, 0, 255).astype(np.uint8), "RGBA")
    # pré-multiplica para não sujar a borda de preto ao reduzir
    a = np.array(img).astype(float) / 255
    a[..., :3] *= a[..., 3:4]
    pm = Image.fromarray((a * 255).astype(np.uint8), "RGBA")
    pm = pm.resize((img.width // fator, img.height // fator), Image.BOX)
    b = np.array(pm).astype(float) / 255
    alfa = b[..., 3:4]
    b[..., :3] = np.where(alfa > 0, b[..., :3] / np.maximum(alfa, 1e-6), 0)
    return b


# ------------------------------------------------------------------ conferência com o vanilla

def logo_vanilla(jar):
    with zipfile.ZipFile(jar) as z:
        dados = z.read("assets/minecraft/textures/gui/title/minecraft.png")
    return Image.open(io.BytesIO(dados)).convert("RGBA")


def pintar_vanilla(r):
    tipo, py = r["tipo"], r["py"]
    h, w = tipo.shape
    rgba = np.zeros((h, w, 4))
    t = np.clip((py - 9) / 121, 0, 1)
    topo = np.stack([206 - 30 * t, 195 - 30 * t, 190 - 29 * t], -1) / 255
    topo[r["borda"]] = np.array([228, 220, 215]) / 255
    frente = np.stack([61 - 21 * r["v"], 57 - 19 * r["v"], 56 - 19 * r["v"]], -1) / 255
    rgba[tipo == TOPO, :3] = topo[tipo == TOPO]
    rgba[tipo == FRENTE, :3] = frente[tipo == FRENTE]
    rgba[..., 3] = (tipo > 0)
    return rgba


def conferir(jar):
    SS = 3
    p = Palavra("MINECRAFT", X0_MINECRAFT, Z_PERTO, 1.0)
    r = lancar_raios(p, 0, 0, 1024, 176, SS)
    rgba = pintar_vanilla(r)
    a = contorno(rgba[..., 3], 10 * SS)
    rgba[..., 3] = a
    final = reduzir(rgba, SS)
    van = np.array(logo_vanilla(jar).crop((0, 0, 1024, 176))).astype(float) / 255
    meu = final[..., 3] > 0.5
    ref = van[..., 3] > 0.5
    iou = (meu & ref).sum() / (meu | ref).sum()
    lum_ref = (van[..., :3] @ [.3, .59, .11]) * van[..., 3]
    lum_meu = (final[..., :3] @ [.3, .59, .11]) * final[..., 3]
    topo_ref, topo_meu = lum_ref > 0.55, lum_meu > 0.55
    iou_topo = (topo_ref & topo_meu).sum() / (topo_ref | topo_meu).sum()
    print(f"silhueta IoU {iou:.3f} | face de cima IoU {iou_topo:.3f}")
    SAIDA_RASCUNHO.mkdir(parents=True, exist_ok=True)
    comp = np.zeros((176 * 2 + 8, 1024, 3))
    comp[:176] = van[..., :3] * van[..., 3:4] + (1 - van[..., 3:4]) * [1, 0, 1]
    comp[184:] = final[..., :3] * final[..., 3:4] + (1 - final[..., 3:4]) * [1, 0, 1]
    Image.fromarray((comp * 255).astype(np.uint8)).save(SAIDA_RASCUNHO / "conferencia.png")
    dif = np.zeros((176, 1024, 3))
    dif[..., 0] = ref & ~meu
    dif[..., 1] = meu & ~ref
    dif[..., 2] = topo_ref ^ topo_meu
    Image.fromarray((dif * 255).astype(np.uint8)).save(SAIDA_RASCUNHO / "diferenca.png")


# ------------------------------------------------------------------ INFINITO

PALAVRA = "INFINITO"
QUADROS = 48
ESCALA_SAIDA = 1.5     # pixels por unidade do logo: 1536 px para os 256 de GUI, 6 px por pixel de GUI no PC dele
SS = 3                 # superamostragem
# Como no print de referência, a segunda linha é vista DE BAIXO: a face grande é a de baixo do bloco e afunila para
# baixo, e a espessura aparece em cima, encostada no MINECRAFT. Isso é a mesma cena espelhada: renderiza vista de
# cima com a câmera do logo e vira a imagem em torno de ESPELHO_Y.
# Medidas da referência, na escala do logo (face do MINECRAFT = 121): letras a ~81% da largura das de cima (o
# INFINITO tem 53 colunas da fonte, então ~600 de largura), espessura ~38 e face ~68, bem mais achatada que a de
# cima: a palavra é vista mais de raspão. A espessura começa logo abaixo da faixa do MINECRAFT.
LARGURA_ALVO = 0.81 * 1024 * 53 / 71 - 18
ESPESSURA_TOPO_Y, FACE_PERTO_Y, FACE_LONGE_Y = 166.0, 206.0, 274.0
CONTORNO = 8.0
ESPELHO_Y = None   # calculado em montar_infinito


def espelhar_y(y):
    return 2 * ESPELHO_Y - y


def _buscar(f, lo, hi, alvo, crescente):
    for _ in range(80):
        meio = (lo + hi) / 2
        if (f(meio) < alvo) == crescente:
            lo = meio
        else:
            hi = meio
    return (lo + hi) / 2


# Na referência a segunda linha tem perspectiva mais forte que a primeira: o ponto de fuga da face fica a ~850 da
# borda de perto (no MINECRAFT fica a ~1500). Com a câmera do logo não dá para ter essa inclinação, essa largura e
# essa face achatada ao mesmo tempo, então o INFINITO tem câmera própria, calibrada pelas três medidas.
DIST_FUGA = 850.0
CAM_INF = None     # calculada em montar_infinito


def montar_infinito():
    global ESPELHO_Y, CAM_INF
    ncol = grade_da_palavra(PALAVRA).shape[1]
    altura_face = FACE_LONGE_Y - FACE_PERTO_Y
    y_horizonte = CAM_LOGO.cy - 1534.0
    y_perto = y_horizonte + DIST_FUGA      # na imagem ainda sem virar; a câmera fica centrada nessa linha

    def montar(y_nadir):
        cam = Camera(CAM_LOGO.cx, y_perto, y_horizonte, y_nadir)
        z = z_na_linha(y_perto, cam=cam)
        # escala do bloco que dá a largura pedida na borda de perto, a essa distância
        k = LARGURA_ALVO * (ALTURA * cam.sen + z * cam.cos) / (cam.foco * ncol * UNID)
        face = y_perto - projetar(0, -ALTURA, z + 10 * k * DZ, cam)[1]
        return cam, z, k, face

    # nadir mais longe = câmera mais de raspão = face mais baixa para a mesma largura
    y_nadir = _buscar(lambda yn: montar(yn)[3], y_perto + 50, y_perto + 20000, altura_face, crescente=False)
    CAM_INF, z_perto, k, _ = montar(y_nadir)
    ESPELHO_Y = (FACE_PERTO_Y + y_perto) / 2
    x_meio = x_na_coluna(512, z_perto, cam=CAM_INF)
    alvo = espelhar_y(ESPESSURA_TOPO_Y)
    espessura = _buscar(lambda t: projetar(x_meio, -ALTURA - t, z_perto, CAM_INF)[1], 0.0, 5000.0, alvo, crescente=True)
    largura = ncol * k * UNID
    return Palavra(PALAVRA, x_meio - largura / 2, z_perto, k, espessura=espessura, de_ponta_cabeca=True)


def janela(p, raio, cam=CAM_LOGO):
    """Retângulo (em unidades do logo) que contém a palavra com contorno, arredondado para a grade de saída."""
    xs, ys = [], []
    for X in (p.x_esq, p.x_esq + p.ncol * p.k * UNID):
        for Z in (p.z_perto, p.z_perto + 10 * p.k * DZ):
            for Y in (-ALTURA, -ALTURA - p.espessura):
                x, y = projetar(X, Y, Z, cam)
                xs.append(x)
                ys.append(y)
    m = raio + 3
    x0, y0 = math.floor(min(xs) - m), math.floor(min(ys) - m)
    x1, y1 = math.ceil(max(xs) + m), math.ceil(max(ys) + m)
    return x0, y0, x1 - x0, y1 - y0


def rachaduras(p):
    """Rachaduras finas no topo, como as do logo, desenhadas na grade da fonte (a perspectiva vem de graça)."""
    R = 24
    h, w = 10 * R, p.ncol * R
    escura = Image.new("L", (w, h))
    clara = Image.new("L", (w, h))
    from PIL import ImageDraw
    de, dc = ImageDraw.Draw(escura), ImageDraw.Draw(clara)
    rnd = random.Random(11)
    grade = p.grade
    col = 0
    for i, ch in enumerate(PALAVRA):
        larg = len(FONTE[ch][0])
        for _ in range(3 if larg > 3 else 2):
            # um "L": anda na horizontal numa divisa de meia-linha e desce um pouco
            r = rnd.choice((2, 4, 6, 8))
            c0 = col + rnd.randint(0, max(0, larg - 2))
            c1 = min(col + larg, c0 + rnd.randint(1, 3))
            if not grade[r - 1, c0] or not grade[min(r, 9), c0]:
                continue
            y = r * R
            pts = [(c0 * R + 4, y), (c1 * R - 4, y), (c1 * R - 4, y + rnd.choice((R // 2, R)))]
            de.line(pts, fill=255, width=3)
            dc.line([(x, yy + 3) for x, yy in pts], fill=255, width=2)
        col += larg + 1
    cheia = np.kron(grade, np.ones((R, R))) > 0
    margem = np.array(Image.fromarray((cheia * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(9))) > 0
    e = np.array(escura) / 255 * margem
    c = np.array(clara) / 255 * margem * (1 - e)
    return e, c, R


def cor_arco_iris(t, fase, profundidade):
    """t: posição ao longo da palavra (0 a 1); profundidade: 0 no fundo da letra, 1 na borda de perto."""
    matiz = (0.98 - t * 1.13 - fase) % 1.0
    sat = 0.52 + 0.24 * profundidade
    val = 1.0 - 0.10 * profundidade
    h6 = matiz * 6
    i = np.floor(h6).astype(int) % 6
    f = h6 - np.floor(h6)
    pp, q, tt = val * (1 - sat), val * (1 - sat * f), val * (1 - sat * (1 - f))
    r = np.choose(i, [val, q, pp, pp, tt, val])
    g = np.choose(i, [tt, val, val, q, pp, pp])
    b = np.choose(i, [pp, pp, tt, val, val, q])
    rgb = np.stack([r, g, b], -1)
    brilho = ((1 - profundidade) ** 2 * 0.25)[..., None]   # luz branca no fundo da letra
    return rgb + (1 - rgb) * brilho


def renderizar_quadros(previa_jar=None):
    p = montar_infinito()
    raio = CONTORNO
    x0, y0, lw, lh = janela(p, raio, CAM_INF)
    escala = ESCALA_SAIDA * SS
    r = lancar_raios(p, x0, y0, lw, lh, escala, cam=CAM_INF)
    # vira de cabeça para baixo: a janela passa a começar no espelho do que era o fim dela
    r = {chave: np.flipud(valor) for chave, valor in r.items()}
    y0 = int(round(espelhar_y(y0 + lh)))
    print(f"INFINITO: escala {p.k:.3f}, espessura {p.espessura:.2f}, janela do logo x={x0} y={y0} {lw}x{lh}")
    tipo = r["tipo"]
    fx, fy = p.fonte_xy(r["X"], r["Z"])
    t = np.clip(fx / p.ncol, 0, 1)
    prof = np.clip(fy / 10, 0, 1)
    racha_e, racha_c, RR = rachaduras(p)
    ix = np.clip((fx * RR).astype(int), 0, racha_e.shape[1] - 1)
    iy = np.clip((fy * RR).astype(int), 0, racha_e.shape[0] - 1)
    e = np.where(tipo == TOPO, racha_e[iy, ix], 0)[..., None]
    c = np.where(tipo == TOPO, racha_c[iy, ix], 0)[..., None]
    alfa = contorno((tipo > 0).astype(float), raio * escala)
    topo, frente = tipo == TOPO, tipo == FRENTE
    borda = r["borda"][..., None]
    v = r["v"][..., None]
    fundo_cosmico = np.array([0.25, 0.10, 0.45]) * (1 - v) + np.array([0.06, 0.03, 0.16]) * v

    # estrelas: lugares fixos na frente cósmica; cada uma pisca num ritmo que fecha o ciclo da animação
    rnd = random.Random(7)
    fh, fw = int(lh * ESCALA_SAIDA), int(lw * ESCALA_SAIDA)
    frente_final = np.array(Image.fromarray((frente * 255).astype(np.uint8)).resize((fw, fh), Image.BOX)) > 230
    fr = np.array(Image.fromarray((frente_final * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))) > 0
    ys, xs = np.nonzero(fr)
    estrelas = []
    for _ in range(max(6, len(ys) // 260)):
        k = rnd.randrange(len(ys))
        estrelas.append((xs[k], ys[k], rnd.choice((1, 1, 2, 2, 3)), rnd.random(), rnd.choice((1, 2, 3))))

    SAIDA_MOD.mkdir(parents=True, exist_ok=True)
    for velho in list(SAIDA_MOD.glob("quadro_*.png")) + list(SAIDA_MOD.glob("quadro_*.png.mcmeta")):
        velho.unlink()
    quadros = []
    for n in range(QUADROS):
        fase = n / QUADROS
        cor = cor_arco_iris(t, fase, prof)
        cor = np.where(borda, cor + (1 - cor) * 0.8, cor)   # quina clara entre a espessura e a face, como no print
        cor = cor * (1 - 0.38 * e) + (1 - cor) * 0.4 * c
        tinta = cor_arco_iris(t, fase, np.full_like(t, 0.5))
        cosmico = fundo_cosmico + 0.12 * tinta
        rgba = np.zeros(tipo.shape + (4,))
        rgba[topo, :3] = cor[topo]
        rgba[frente, :3] = cosmico[frente]
        rgba[..., 3] = alfa
        final = reduzir(rgba, SS)
        brilhos = np.zeros(final.shape[:2])
        for (sx, sy, tam, fase_e, freq) in estrelas:
            b = 0.55 + 0.45 * math.sin(2 * math.pi * (freq * fase + fase_e))
            for d in range(-tam, tam + 1):
                f = b * (1 - abs(d) / (tam + 1)) ** 0.7
                for yy, xx in ((sy + d, sx), (sy, sx + d)):
                    if 0 <= yy < fh and 0 <= xx < fw and frente_final[yy, xx]:
                        brilhos[yy, xx] = max(brilhos[yy, xx], f)
        final[..., :3] += (1 - final[..., :3]) * brilhos[..., None]
        img = Image.fromarray(np.clip(final * 255, 0, 255).astype(np.uint8), "RGBA")
        img.save(SAIDA_MOD / f"quadro_{n:02d}.png", optimize=True)
        # filtro suave, como o minecraft.png vanilla, para o logo não serrilhar fora da escala 1
        (SAIDA_MOD / f"quadro_{n:02d}.png.mcmeta").write_text('{"texture": {"blur": true}}\n', encoding="utf-8")
        quadros.append(img)
    SAIDA_INFO.write_text(json.dumps({
        "x": x0, "y": y0, "largura": lw, "altura": lh,
        "pixels": [fw, fh], "quadros": QUADROS,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"{QUADROS} quadros de {fw}x{fh} em {SAIDA_MOD}")
    if previa_jar:
        previa(previa_jar, quadros, x0, y0)


def previa(jar, quadros, x0, y0):
    """MINECRAFT vanilla por cima do INFINITO, do jeito que o mod desenha, num fundo parecido com o do jogo."""
    van = logo_vanilla(jar).crop((0, 0, 1024, 176))
    S = ESCALA_SAIDA
    van = van.resize((int(1024 * S), int(176 * S)), Image.LANCZOS)
    larg = int(1024 * S) + 80
    alt = int(max(176, y0 + quadros[0].height / S) * S) + 60
    with zipfile.ZipFile(jar) as z:
        pano = Image.open(io.BytesIO(z.read("assets/minecraft/textures/gui/title/background/panorama_0.png"))).convert("RGBA")
    esc = max(larg / pano.width, alt / pano.height)
    pano = pano.resize((int(pano.width * esc) + 1, int(pano.height * esc) + 1)).crop((0, 0, larg, alt))
    pano = pano.filter(ImageFilter.GaussianBlur(8))
    telas = []
    for q in quadros:
        tela = pano.copy()
        tela.alpha_composite(q, (40 + int(x0 * S), 30 + int(y0 * S)))
        tela.alpha_composite(van, (40, 30))
        telas.append(tela.convert("RGB"))
    SAIDA_RASCUNHO.mkdir(parents=True, exist_ok=True)
    telas[0].save(SAIDA_RASCUNHO / "previa.png")
    telas[0].save(SAIDA_RASCUNHO / "previa.webp", save_all=True, append_images=telas[1:],
                  duration=int(6000 / len(telas)), loop=0, quality=90)
    print("prévia em", SAIDA_RASCUNHO)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--conferir", metavar="JAR")
    ap.add_argument("--previa", metavar="JAR")
    a = ap.parse_args()
    if a.conferir:
        conferir(a.conferir)
    else:
        renderizar_quadros(a.previa)
