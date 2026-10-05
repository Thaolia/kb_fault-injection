#!/usr/bin/env python3
"""Courbes théoriques du crowbar de la variante B (09 §4).

Quatre figures dans assets/schemas/ :
  09_courbe_grille      V_GS(t) pour les quatre pilotages de grille
  09_courbe_rail_rdamp  V_VDD(t) et le courant de maille, balayage de R_damp
  09_courbe_cresid      sensibilité à C_résid : descente et remontée vs le plafond TPW
  09_courbe_width       WIDTH réglé → largeur livrée → profondeur atteinte

⚠ MODÈLE THÉORIQUE. L_boucle et C_résid sont des HYPOTHÈSES : elles se mesurent au
premier tir (09 §3.3bis règle 2, et §4.7 étape 2.5). R_pad ≈ 50 Ω est une estimation
[reco], jamais lue au datasheet RP2350 — les conclusions tiennent pour toute valeur
entre 30 et 80 Ω.

Le modèle est recoupé indépendamment par ngspice : voir check_09_crowbar_spice.py.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

SORTIE = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- le banc ----
VS = 3.3          # source
RSERIE = 4.3      # résistance série du 09 §3.3
RWIRE = 0.02      # résistance des fils de la maille de drain
CYCLE = 1 / 150e6  # 6,67 ns — un cycle PIO du raiden-pico

# ------------------------------------------------------ AO3400A, datasheet ----
CISS = 630e-12    # AOS Rev 3.1
RG_INT = 3.0      # résistance de grille interne, typ
VTH = 0.65        # V_GS(th) min à 25 °C

# R_DS(on) en fonction de V_GS. Le datasheet ne donne que trois points (10 / 4,5 /
# 2,5 V, colonne typ) ; la zone sous-seuil est une extrapolation [reco] — elle ne
# change pas le plancher, seulement la forme des toutes premières nanosecondes.
_VGS_PTS = np.array([VTH, 1.0, 1.5, 2.0, 2.5, 3.3, 4.5, 10.0])
_RON_PTS = np.array([1e3, 2.0, 0.20, 0.045, 0.024, 0.021, 0.019, 0.018])

# --------------------------------------------------- RP2350, côté pilotage ----
RPAD_12MA = 50.0   # [reco] — mesuré à l'étape 2 de la mise en route
RPAD_4MA = 150.0   # [reco] — le défaut de reset du pad, si la force n'est pas réglée
RDRV = 2.0         # driver dédié type UCC27511 / TC4427
E9_LEAK = 120e-6   # erratum RP2350-E9 : fuite d'un pad en mode entrée


ROFF = 1e5   # « ouvert » : 20 000 fois R_série, mais assez bas pour que L/R reste
             # intégrable. Une valeur idéale (1e9) rend la maille infiniment raide
             # et fait ramer le solveur sur la phase où le MOSFET ne conduit pas.


def ron(vgs):
    """R_DS(on) vu par la maille, en ohms. Quasi ouvert sous le seuil."""
    return np.where(vgs <= VTH, ROFF, np.minimum(np.interp(vgs, _VGS_PTS, _RON_PTS), ROFF))


def grille(t, rsortie=RPAD_12MA, rpd=None, vsrc=VS):
    """V_GS(t) : charge de C_iss à travers l'impédance de sortie + R_g interne.

    Un pull-down rpd forme un diviseur avec rsortie : il abaisse l'asymptote ET
    accélère la charge (résistance équivalente plus faible).
    """
    if rpd is None:
        vinf, req = vsrc, rsortie + RG_INT
    else:
        vinf = vsrc * rpd / (rpd + rsortie)
        req = rsortie * rpd / (rsortie + rpd) + RG_INT
    return vinf * (1.0 - np.exp(-np.asarray(t) / (req * CISS)))


def simule(rdamp=0.0, cresid=1e-6, lboucle=150e-9, largeur=2e-6,
           rsortie=RPAD_12MA, rpd=None, apres=0.0, npts=4000):
    """Intègre la maille RLC pendant le tir, puis la remontée analytique.

    Pendant le tir : maille série (L_boucle, R_on(t) + R_damp + R_fils, C_résid),
    réalimentée par la source à travers R_série depuis le réservoir.
    Après le tir : le transistor est ouvert, la remontée est un simple R_série·C.
    L'overshoot de relâche (l'énergie de L_boucle) n'est PAS modélisé — en vrai il
    est écrêté par l'avalanche du MOSFET (BV_DSS 30 V) et c'est un second vecteur
    de faute, distinct (09 §8 règle 5).
    """
    def f(t, y):
        v, i = y
        r = float(ron(grille(t, rsortie, rpd))) + rdamp + RWIRE
        return [((VS - v) / RSERIE - i) / cresid, (v - r * i) / lboucle]

    # LSODA : la maille est raide tant que le MOSFET n'est pas passant (L/R très
    # petit). Un solveur explicite y prend des pas de l'ordre de 1e-16 s.
    s = solve_ivp(f, [0.0, largeur], [VS, 0.0], method="LSODA",
                  max_step=2e-9, rtol=1e-7, atol=1e-10)
    t, v, i = s.t, s.y[0], s.y[1]

    if apres > 0.0:
        tau = RSERIE * cresid
        t2 = largeur + np.linspace(0.0, apres, npts)
        v2 = VS - (VS - v[-1]) * np.exp(-(t2 - largeur) / tau)
        t = np.concatenate([t, t2])
        v = np.concatenate([v, v2])
        i = np.concatenate([i, np.zeros_like(t2)])
    return t, v, i


def _note(fig, texte):
    fig.text(0.5, 0.012, texte, ha="center", va="bottom", fontsize=8.2,
             color="#8a5a00",
             bbox=dict(boxstyle="round,pad=0.42", fc="#fff8e6", ec="#e0c070", lw=0.8))


def _style():
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.grid": True, "grid.alpha": 0.28, "grid.linestyle": ":",
        "axes.spines.top": False, "axes.spines.right": False,
        "font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10.5,
        "legend.frameon": True, "legend.framealpha": 0.92, "legend.fontsize": 9.5,
    })


# ============================================================ figure 1 =======
def figure_grille():
    t = np.linspace(0, 300e-9, 3000)
    cas = [
        ("GPIO 12 mA — la carte  (R_pad ≈ 50 Ω)", dict(rsortie=RPAD_12MA), "#1f5f8b", "-", 2.4),
        ("GPIO 4 mA — si la force n'est pas réglée", dict(rsortie=RPAD_4MA), "#7f8c8d", "--", 1.8),
        ("GPIO 12 mA + pull-down 100 Ω", dict(rsortie=RPAD_12MA, rpd=100.0), "#c0392b", "-.", 2.0),
        ("driver dédié (R_out ≈ 2 Ω) + pull-down 100 Ω", dict(rsortie=RDRV, rpd=100.0),
         "#27632a", "-", 2.0),
    ]
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    for nom, kw, c, ls, lw in cas:
        v = grille(t, **kw)
        ax.plot(t * 1e9, v, color=c, ls=ls, lw=lw, label=nom)

    ax.axhline(VTH, color="#c0392b", lw=1.1, ls=":")
    ax.text(298, VTH + 0.05, "V_GS(th) min = 0,65 V  →  le MOSFET commence à conduire",
            ha="right", va="bottom", fontsize=9, color="#c0392b")
    ax.axhline(2.5, color="#333333", lw=1.1, ls=":")
    ax.text(298, 2.55, "2,5 V  →  R_DS(on) = 24 mΩ, conduction établie",
            ha="right", va="bottom", fontsize=9, color="#333333")

    v12 = grille(t, RPAD_12MA)
    for seuil, txt in ((VTH, "7 ns"), (2.5, "47 ns")):
        k = int(np.argmax(v12 >= seuil))
        ax.plot(t[k] * 1e9, seuil, "o", color="#1f5f8b", ms=6, zorder=5)
        ax.annotate(txt, (t[k] * 1e9, seuil), textcoords="offset points", xytext=(8, -14),
                    fontsize=9, color="#1f5f8b", fontweight="bold")

    ax.axvspan(0, 15 * CYCLE * 1e9, color="#c0392b", alpha=0.07)
    ax.text(15 * CYCLE * 1e9 / 2, 0.12, "WIDTH < 15 cycles :\nconduction partielle",
            ha="center", va="bottom", fontsize=8.6, color="#c0392b")

    ax.set_xlabel("temps depuis le front sur GP11  [ns]")
    ax.set_ylabel("$V_{GS}$  [V]")
    ax.set_title("Figure 1 — montée de grille de l'AO3400A selon le pilotage\n"
                 "$C_{iss}$ = 630 pF · $R_g$ interne = 3 Ω  (datasheet AOS Rev 3.1)")
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 3.5)
    ax.legend(loc="center right")
    _note(fig, "Modèle théorique. R_pad ≈ 50 Ω est une estimation [reco] : les conclusions "
               "tiennent pour toute valeur entre 30 et 80 Ω, et l'étape 2 de la mise en route la mesure.")
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    fig.savefig(SORTIE / "09_courbe_grille.png", dpi=170)
    plt.close(fig)
    print("  09_courbe_grille.png")
    return {nom: grille(np.array([300e-9]), **kw)[0] for nom, kw, *_ in cas}


# ============================================================ figure 2 =======
def figure_rail():
    largeur = 6e-6
    cas = [(0.0, "#c0392b", "-"), (0.22, "#e08214", "--"), (0.47, "#1f5f8b", "-"),
           (1.0, "#27632a", "-.")]
    fig, (ax, axi) = plt.subplots(2, 1, figsize=(9.8, 7.4), sharex=True,
                                  gridspec_kw=dict(height_ratios=[2.15, 1]))
    resume = {}
    for rd, c, ls in cas:
        t, v, i = simule(rdamp=rd, largeur=largeur, apres=3.0e-6)
        lw = 2.6 if rd == 0.47 else 1.9
        ax.plot(t * 1e6, v, color=c, ls=ls, lw=lw,
                label=f"$R_{{damp}}$ = {rd:.2f} Ω   →   $V_{{min}}$ = {v.min():+.2f} V")
        axi.plot(t * 1e6, i, color=c, ls=ls, lw=lw,
                 label=f"{rd:.2f} Ω : crête {np.abs(i).max():.1f} A")
        r_tot = float(ron(np.array(VS))) + rd + RWIRE
        resume[rd] = (v.min(), np.abs(i).max(), VS * r_tot / (RSERIE + r_tot))

    ax.axhline(1.37, color="#8e44ad", lw=1.2, ls=":")
    ax.text(0.06, 1.44, "V_PDR = 1,37 V — sous ce niveau, le cœur décroche", fontsize=9,
            color="#8e44ad")
    ax.axhline(0.0, color="#555555", lw=1.0)
    ax.axhspan(-0.3, -0.7, color="#e08214", alpha=0.13)
    ax.axhline(-0.3, color="#e08214", lw=1.2, ls="--")
    ax.text(8.9, -0.27, "−0,3 V : maximum absolu d'une E/S RP2350 (GP26/GP27 !)",
            fontsize=9, color="#e08214", ha="right", va="bottom")
    ax.axhline(-0.7, color="#c0392b", lw=1.2, ls="--")
    ax.text(8.9, -0.68, "−0,7 V : les diodes ESD de la cible écrêtent ici",
            fontsize=9, color="#c0392b", ha="right", va="bottom")
    ax.axvline(largeur * 1e6, color="#999999", lw=1.0, ls=":")
    ax.text(largeur * 1e6 + 0.08, 3.05, "relâche", fontsize=9, color="#666666")

    ax.set_ylabel("nœud VDD  [V]")
    ax.set_title("Figure 2 — effondrement du rail, balayage de la résistance d'amortissement\n"
                 "tir de 6 µs · $C_{résid}$ = 1 µF · $L_{boucle}$ = 150 nH (≈10 cm de boucle)")
    ax.legend(loc="lower right")
    ax.set_ylim(-2.9, 3.6)

    axi.set_xlabel("temps  [µs]")
    axi.set_ylabel("courant de maille  [A]")
    axi.legend(loc="lower right", ncol=2)
    axi.text(0.06, 9.0, "★ la crête réelle vient de la maille LC (I ≈ V/Z0),\n"
                        "pas des 0,77 A du régime établi à travers les 4,3 Ω",
             fontsize=9, color="#c0392b", va="top")
    _note(fig, "Modèle théorique. L'overshoot de relâche n'est pas tracé : il est écrêté par "
               "l'avalanche du MOSFET (BV_DSS 30 V) et constitue un second vecteur de faute (09 §8 règle 5).")
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    fig.savefig(SORTIE / "09_courbe_rail_rdamp.png", dpi=170)
    plt.close(fig)
    print("  09_courbe_rail_rdamp.png")
    return resume


# ============================================================ figure 3 =======
def figure_cresid():
    largeur = 2e-6
    cas = [(100e-9, "#27632a", "-"), (1e-6, "#1f5f8b", "-"), (10e-6, "#c0392b", "--")]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 5.2))
    resume = {}
    for c, col, ls in cas:
        t, v, _ = simule(rdamp=0.47, cresid=c, largeur=largeur, apres=600e-6)
        lab = f"$C_{{résid}}$ = {c*1e6:g} µF"
        a.plot(t * 1e9, v, color=col, ls=ls, lw=2.1, label=lab)
        b.semilogx(np.maximum((t - largeur) * 1e6, 1e-3), v, color=col, ls=ls, lw=2.1,
                   label=f"{lab} — 3τ = {3*RSERIE*c*1e6:.0f} µs")
        resume[c] = (v.min(), 3 * RSERIE * c)

    a.axhline(1.37, color="#8e44ad", lw=1.1, ls=":")
    a.text(3, 1.44, "V_PDR 1,37 V", fontsize=9, color="#8e44ad")
    a.axhline(0.0, color="#555555", lw=0.9)
    a.axhline(-0.3, color="#e08214", lw=1.1, ls="--")
    a.text(895, -0.27, "−0,3 V : max absolu E/S RP2350", fontsize=8.6, color="#e08214",
           ha="right", va="bottom")
    a.text(430, -0.95,
           "★ $R_{damp}$ = 0,47 Ω ne suffit plus à 0,1 µF :\n"
           "$Z_0$ = √(L/C) monte à 1,22 Ω, donc la valeur\n"
           "d'amortissement DOIT suivre $C_{résid}$",
           fontsize=9, color="#c0392b", ha="center", va="top")
    a.set_ylim(-1.9, 3.6)
    a.set_xlim(0, 900)
    a.set_xlabel("temps depuis le front  [ns]")
    a.set_ylabel("nœud VDD  [V]")
    a.set_title("(a) descente — $R_{damp}$ = 0,47 Ω")
    a.legend(loc="upper right")

    b.axvline(300, color="#c0392b", lw=1.6, ls="--")
    b.text(320, 2.3, "TPW = 300 µs\nau-delà, on fait un POR,\npas une faute", fontsize=9,
           color="#c0392b", va="top")
    b.set_xlim(0.1, 600)
    b.set_xlabel("temps depuis la relâche  [µs]")
    b.set_ylabel("nœud VDD  [V]")
    b.set_title("(b) remontée en $R_{série}$ · $C_{résid}$")
    b.legend(loc="lower right")

    fig.suptitle("Figure 3 — combien de découplage faut-il retirer de la carte cible ?",
                 fontsize=12.5)
    _note(fig, "Modèle théorique. C_résid se DÉDUIT de la mesure : τ_remontée / R_série "
               "(09 §3.3bis règle 2). Tant qu'elle n'est pas faite, ces trois courbes bornent le problème.")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    fig.savefig(SORTIE / "09_courbe_cresid.png", dpi=170)
    plt.close(fig)
    print("  09_courbe_cresid.png")
    return resume


# ============================================================ figure 4 =======
def largeur_livree(width_regle):
    """Cycles réellement passés à l'état haut. Vérifié à la source.

    src/glitch.c:376-378 retranche 5 au-dessus de 5 (`if (w > 5) w -= 5;`).
    src/glitch.pio:92-104 tient le pad haut pendant `mov x, isr` (1) +
    `set pins, 1` (1) + `jmp x--` exécuté W+1 fois, soit W + 3 cycles.

    D'où : w ≤ 5 → w + 3 ;  w > 5 → w − 2. La correction n'est PAS monotone —
    WIDTH 6…9 livrent moins que WIDTH 5, et WIDTH 10 l'égale exactement.
    """
    charge = width_regle - 5 if width_regle > 5 else width_regle
    return charge + 3


def figure_width():
    """Deux échelles différentes : l'artefact firmware est à 10 cycles, la
    profondeur utile se joue à 100–600. Les superposer noierait l'un des deux."""
    w_a = np.arange(0, 41)
    livrees = np.array([largeur_livree(int(w)) for w in w_a])

    w_b = np.unique(np.round(np.logspace(0, np.log10(600), 55)).astype(int))
    livrees_b = np.array([largeur_livree(int(w)) for w in w_b])
    profondeurs = np.array([simule(rdamp=0.47, largeur=max(n, 1) * CYCLE)[1].min()
                            for n in livrees_b])

    fig, (a, b) = plt.subplots(2, 1, figsize=(9.8, 7.6))

    a.step(w_a, livrees, where="mid", color="#1f5f8b", lw=2.2, label="livré par le firmware")
    a.plot(w_a, w_a, color="#999999", lw=1.3, ls=":", label="ce qu'on croit régler")
    a.axvspan(6, 10, color="#c0392b", alpha=0.13)
    a.annotate("WIDTH 6…9 livre STRICTEMENT moins que WIDTH 5,\net WIDTH 10 ne fait que l'égaler\n(la correction −5 n'est pas monotone)",
               xy=(8, largeur_livree(8)), xytext=(12.5, 31), fontsize=9.2, color="#c0392b",
               arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.4))
    a.set_xlabel("WIDTH réglé  [cycles]")
    a.set_ylabel("cycles réellement livrés")
    a.set_title("(a) l'artefact du firmware — src/glitch.c:376-378, `if (w > 5) w -= 5;`\n"
                "puis le programme PIO ajoute 3 cycles fixes", fontsize=11)
    a.set_xlim(0, 40)
    a.legend(loc="upper left")

    b.semilogx(w_b, profondeurs, color="#1f5f8b", lw=2.3)
    b.axvspan(1, 15, color="#c0392b", alpha=0.11)
    ymin, ymax = profondeurs.min(), profondeurs.max()
    b.text(3.6, ymin + 0.62 * (ymax - ymin),
           "grille pas encore chargée :\nconduction partielle", ha="center", fontsize=9.2,
           color="#c0392b")
    b.axvline(20, color="#27632a", lw=1.9, ls="--")
    b.text(23, ymin + 0.78 * (ymax - ymin),
           "★ commencer les balayages ici\n(WIDTH ≥ 20 cycles ≈ 133 ns)",
           fontsize=9.5, color="#27632a")
    b.axhline(1.37, color="#8e44ad", lw=1.2, ls=":")
    k = int(np.argmax(profondeurs <= 1.37))
    b.text(w_b[-1], 1.44, "V_PDR 1,37 V — atteint vers "
           f"{w_b[k]} cycles ≈ {w_b[k]*CYCLE*1e9:.0f} ns", fontsize=9, color="#8e44ad",
           ha="right", va="bottom")
    b.set_xlabel("WIDTH réglé  [cycles, échelle log]")
    b.set_ylabel("plancher atteint  [V]")
    b.set_title("(b) la profondeur, elle, se joue bien plus loin", fontsize=11)

    fig.suptitle("Figure 4 — de la valeur réglée à la profondeur obtenue  "
                 "(1 cycle = 6,67 ns)", fontsize=12.5)
    _note(fig, "Modèle théorique, C_résid = 1 µF et L_boucle = 150 nH. DEUX plafonds se cumulent "
               "sous ~20 cycles : la charge de grille (33 ns) et l'artefact de correction du firmware.")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    fig.savefig(SORTIE / "09_courbe_width.png", dpi=170)
    plt.close(fig)
    print("  09_courbe_width.png")
    return w_b, livrees_b, profondeurs


# ================================================================ sortie =====
def main():
    _style()
    print(f"Sortie : {SORTIE}")
    figure_grille()
    rail = figure_rail()
    cres = figure_cresid()
    w, livrees, prof = figure_width()

    print("\n--- chiffres clés (à citer dans le 09 §4, pas à réinventer) ---")
    tau_g = (RPAD_12MA + RG_INT) * CISS
    print(f"grille GPIO 12 mA : τ = {tau_g*1e9:.1f} ns · seuil 0,65 V à "
          f"{-tau_g*np.log(1-VTH/VS)*1e9:.1f} ns · 2,5 V à {-tau_g*np.log(1-2.5/VS)*1e9:.1f} ns")
    print(f"pull-down sous E9 : 1 kΩ → {E9_LEAK*1e3:.2f} V ; "
          f"4,7 kΩ → {E9_LEAK*4700:.2f} V ; 8,2 kΩ → {E9_LEAK*8200:.2f} V "
          f"(V_GS(th) min = {VTH} V)")
    print(f"{'R_damp':>8} {'V_min':>9} {'I_crête':>9} {'plancher':>10}")
    for rd, (vmin, imax, vfin) in rail.items():
        print(f"{rd:8.2f} {vmin:>+8.3f} V {imax:>7.2f} A {vfin:>8.3f} V")
    for c, (vmin, t3) in cres.items():
        print(f"C_résid {c*1e6:>5g} µF : V_min = {vmin:+.3f} V · 3τ_remontée = {t3*1e6:.0f} µs"
              f"{'  ⚠ au-delà du TPW de 300 µs' if t3 > 300e-6 else ''}")
    print(f"WIDTH 5 livre {largeur_livree(5)} cycles, WIDTH 6 en livre "
          f"{largeur_livree(6)} → non monotone ; minimum réel {largeur_livree(0)} cycles "
          f"= {largeur_livree(0)*CYCLE*1e9:.0f} ns")


if __name__ == "__main__":
    main()
