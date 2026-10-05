#!/usr/bin/env python3
"""Schémas de la carte crowbar de la variante B (09 §4), rendus avec schemdraw.

Quatre sorties dans assets/schemas/ :
  09_crowbar_carte          — le montage complet, valeurs portées
  09_crowbar_grille_gpio    — la maille de grille pilotée par un GPIO nu
  09_crowbar_grille_driver  — la même avec driver dédié (où les 100 Ω sont justes)
  09_crowbar_maille_rlc     — la maille de décharge, dont sortent les figures 2 et 3

Valeurs : AO3400A (19 mΩ, C_iss 630 pF, V_GS(th) 0,65 V — datasheet AOS Rev 3.1),
R_pd 1 kΩ borné par l'erratum RP2350-E9, R_damp 0,47 Ω, R_adc 1 kΩ.

Deux contraintes de tracé apprises à l'usage :
  * le placement automatique des étiquettes de schemdraw les superpose dès qu'une
    branche porte plus d'une ligne de légende ⇒ tout est posé à la main ;
  * AnalogNFet sort sa grille à DROITE (+0,92) et .reverse() déplace les ancres sans
    déplacer le tracé ⇒ on garde l'orientation par défaut et on met la maille de
    grille à droite du transistor.
"""
from pathlib import Path

import schemdraw
import schemdraw.elements as elm

SORTIE = Path(__file__).resolve().parents[1]

ROUGE = "#c0392b"   # ce que la variante B ajoute
BLEU = "#1f5f8b"    # le raiden-pico
GRIS = "#6f6f6f"    # commentaire neutre


def _config():
    schemdraw.config(unit=1.8, fontsize=11, lw=1.9)


def _ecrire(d, nom):
    for ext in ("svg", "png"):
        d.save(str(SORTIE / f"{nom}.{ext}"), dpi=200)
    print(f"  {nom}.svg + .png")


def _titre(d, x, y, titre, sous_titre=None):
    d += elm.Label().at((x, y)).label(titre, fontsize=13.5)
    if sous_titre:
        d += elm.Label().at((x, y - 0.62)).label(sous_titre, fontsize=9.5, color=GRIS)


def _broche(d, xy, texte, cote="right", couleur=BLEU):
    """Étiquette de broche : point ouvert + texte, sans cadre qui déborde."""
    d += elm.Dot(open=True).at(xy).color(couleur)
    dx = 0.34 if cote == "right" else -0.34
    d += elm.Label().at((xy[0] + dx, xy[1])).label(
        texte, fontsize=10.5, color=couleur,
        halign="left" if cote == "right" else "right")


def carte():
    """Le montage complet de la variante B."""
    _config()
    with schemdraw.Drawing(show=False) as d:
        Y, XV, YG = 4.5, 7.4, -0.7

        _broche(d, (0, Y), "3,3 V\nréglable", cote="left", couleur="black")
        d += elm.Line().at((0, Y)).to((1.4, Y))
        d += elm.Dot().at((1.4, Y))
        d += elm.Capacitor().at((1.4, Y)).down().length(1.5)
        d += elm.Ground().at((1.4, Y - 1.5))
        d += elm.Label().at((0.95, Y - 0.75)).label(
            "$C_{res}$\n100 µF\nfaible ESR", fontsize=10, halign="right")
        d += elm.Line().at((1.4, Y)).to((2.9, Y))
        d += elm.Dot().at((2.9, Y))
        d += elm.Capacitor().at((2.9, Y)).down().length(1.5)
        d += elm.Ground().at((2.9, Y - 1.5))
        d += elm.Label().at((3.35, Y - 0.75)).label("100 nF", fontsize=10, halign="left")

        d += elm.Resistor().at((2.9, Y)).right().length(2.1)
        d += elm.Label().at((3.95, Y + 0.80)).label(
            "$R_{série}$  4,3 Ω\n≥0,25 W · non bobinée", fontsize=10)
        d += elm.Line().at((5.0, Y)).to((XV, Y))
        d += elm.Dot(radius=0.13).at((XV, Y))
        d += elm.Line().at((XV, Y)).to((9.8, Y))
        _broche(d, (9.8, Y), "BAT32G135  VDD\nbr. 7 / 9 / 11", couleur="black")

        # prises ADC protégées
        d += elm.Line().at((XV, Y)).to((XV, Y + 3.4))
        for dy, nom in ((1.9, "GP26 · ADC0"), (3.4, "GP27 · ADC1")):
            d += elm.Resistor().at((XV, Y + dy)).right().length(1.8).color(ROUGE)
            d += elm.Label().at((XV + 0.9, Y + dy + 0.55)).label("1 kΩ", fontsize=10, color=ROUGE)
            _broche(d, (XV + 1.8, Y + dy), nom)
        d += elm.Dot().at((XV, Y + 1.9))
        d += elm.Label().at((XV - 0.45, Y + 2.75)).label(
            "protection ADC :\nce nœud plonge sous 0 V\npendant le tir",
            fontsize=9.5, color=ROUGE, halign="right")

        # branche crowbar — MOSFET vertical, grille à droite (orientation native)
        yd = Y - 1.9
        d += elm.Resistor().at((XV, Y)).down().length(1.9).color(ROUGE)
        d += elm.Label().at((XV - 0.42, Y - 0.95)).label(
            "$R_{damp}$\n0,47 Ω · 1 W", fontsize=10, color=ROUGE, halign="right")
        q = elm.AnalogNFet().right().anchor("drain").at((XV, yd))
        d += q
        d += elm.Line().at(q.source).to((XV, YG))
        d += elm.Dot().at((XV, YG))
        d += elm.Ground().at((XV, YG))

        d += elm.Label().at((XV - 0.28, yd)).label("3 = D", fontsize=9.5, color=GRIS, halign="right")
        d += elm.Label().at((XV - 0.28, q.source[1])).label("2 = S", fontsize=9.5, color=GRIS,
                                                            halign="right")
        d += elm.Label().at((q.gate[0] + 0.12, q.gate[1] + 0.42)).label(
            "1 = G", fontsize=9.5, color=GRIS, halign="left")
        d += elm.Label().at((XV - 1.15, yd - 1.05)).label(
            "AO3400A · SOT-23\n30 V · 19 mΩ à 3,3 V\n$V_{GS(th)}$ 0,65 V min\n$I_{DM}$ 30 A pulsé",
            fontsize=10, halign="right")

        # maille de grille, à droite du transistor
        xg = q.gate[0] + 1.5
        d += elm.Line().at(q.gate).to((xg, q.gate[1]))
        d += elm.Dot().at((xg, q.gate[1]))
        d += elm.Resistor().at((xg, q.gate[1])).right().length(1.7)
        d += elm.Label().at((xg + 0.85, q.gate[1] + 0.64)).label("$R_{g}$  0 Ω\n(strap)", fontsize=10)
        _broche(d, (xg + 1.7, q.gate[1]), "GP11\ngrille")
        d += elm.Resistor().at((xg, q.gate[1])).down().toy(YG).color(ROUGE)
        d += elm.Label().at((xg + 0.42, (q.gate[1] + YG) / 2)).label(
            "$R_{pd}$\n1 kΩ", fontsize=10, color=ROUGE, halign="left")
        d += elm.Line().at((xg, YG)).to((XV, YG))

        d += elm.Label().at((0.2, YG - 1.5)).label(
            "$R_{pd}$ est OBLIGATOIRE et se monte ICI, sur la carte MOSFET, entre grille et source :\n"
            "un fil de grille arraché doit laisser la grille au repos. 1 kΩ, pas 10 kΩ —\n"
            "l'erratum RP2350-E9 injecte 120 µA dans un pad repassé en entrée (doc 09 §4.2).",
            fontsize=10, color=ROUGE, halign="left")

        _titre(d, 4.6, Y + 5.5,
               "Variante B — carte crowbar AO3400A pilotée directement par GP11",
               "une seule masse commune à la source, au raiden-pico et à la cible")
        _ecrire(d, "09_crowbar_carte")


def grille_gpio():
    """La maille de grille pilotée par un GPIO nu — le modèle de la figure 1."""
    _config()
    with schemdraw.Drawing(show=False) as d:
        Y, YG = 3.0, 0.9
        _broche(d, (0, Y), "GP11\n0 ↔ 3,3 V", cote="left")
        d += elm.Resistor().at((0, Y)).right().length(2.2).color(GRIS)
        d += elm.Label().at((1.1, Y + 0.74)).label(
            "$R_{pad}$ ≈ 50 Ω\n[reco]", fontsize=10, color=GRIS)
        d += elm.Dot().at((2.2, Y))
        d += elm.Resistor().at((2.2, Y)).right().length(2.0)
        d += elm.Label().at((3.2, Y + 0.74)).label("$R_{g}$ interne\n3 Ω", fontsize=10)
        d += elm.Dot().at((4.2, Y))
        d += elm.Label().at((4.55, Y + 0.32)).label("grille", fontsize=10, halign="left")
        d += elm.Capacitor().at((4.2, Y)).down().toy(YG)
        d += elm.Label().at((4.62, (Y + YG) / 2)).label("$C_{iss}$\n630 pF", fontsize=10, halign="left")
        d += elm.Resistor().at((2.2, Y)).down().toy(YG).color(ROUGE)
        d += elm.Label().at((1.78, (Y + YG) / 2)).label(
            "$R_{pd}$\n1 kΩ", fontsize=10, color=ROUGE, halign="right")
        d += elm.Line().at((2.2, YG)).to((4.2, YG))
        d += elm.Ground().at((3.2, YG))

        d += elm.Label().at((5.9, Y - 0.15)).label(
            "τ = ($R_{pad}$ + $R_{g}$) · $C_{iss}$ ≈ 33 ns\n"
            "$V_{GS(th)}$ = 0,65 V franchi à 7 ns\n"
            "$V_{GS}$ = 2,5 V atteint à 47 ns\n"
            "⇒ ne pas balayer WIDTH sous ~15 cycles\n\n$R_{pad}$ est une estimation [reco], jamais lue au\ndatasheet RP2350 : les conclusions tiennent pour\ntoute valeur entre 30 et 80 Ω.",
            fontsize=10.5, halign="left")
        d += elm.Label().at((0.0, YG - 2.0)).label(
            "Pourquoi 1 kΩ et pas la valeur réflexe de 10 kΩ :\n"
            "hors firmware (bootrom, BOOTSEL, reflash, fil arraché) GP11 est une ENTRÉE,\n"
            "et l'erratum RP2350-E9 y injecte jusqu'à 120 µA.\n"
            "      120 µA × 1 kΩ    = 0,12 V    ✓  bien sous $V_{GS(th)}$ min = 0,65 V\n"
            "      120 µA × 8,2 kΩ = 0,98 V    ✗  le « workaround E9 » vise $V_{IL}$, pas une grille",
            fontsize=10, halign="left", color=ROUGE)
        _titre(d, 3.4, Y + 2.6,
               "Maille de grille — pilotage par GPIO nu (RP2350, 12 mA)",
               "c'est ce circuit que trace la figure 1")
        _ecrire(d, "09_crowbar_grille_gpio")


def grille_driver():
    """La variante driver dédié — là où un pull-down de 100 Ω est la bonne valeur."""
    _config()
    with schemdraw.Drawing(show=False) as d:
        XF, YD, YG = 4.0, 3.4, 0.4

        # le driver EN PREMIER : tout élément hérite de la direction courante du
        # dessin, et un Ic posé après un composant .down() se retrouve retourné.
        u = elm.Ic(pins=[elm.IcPin(name="OUT", side="top"),
                         elm.IcPin(name="IN", side="left"),
                         elm.IcPin(name="GND", side="bottom"),
                         elm.IcPin(name="VDD", side="right")],
                   edgepadW=0.5, edgepadH=0.5).right().at((8.9, -1.4))
        d += u
        d += elm.Line().at(u.IN).left().length(1.0)
        _broche(d, (u.IN[0] - 1.0, u.IN[1]), "GP11", cote="left")
        d += elm.Ground().at(u.GND)
        d += elm.Vdd().at(u.VDD).label("3,3 – 5 V", fontsize=10)
        d += elm.Label().at((u.center[0] - 1.55, u.center[1] - 1.35)).label(
            "UCC27511 · TC4427\n$R_{out}$ ≈ 2 Ω", fontsize=10, halign="right")

        q = elm.AnalogNFet().right().anchor("drain").at((XF, YD))
        d += q
        d += elm.Line().at(q.drain).up().length(1.1)
        _broche(d, (XF, YD + 1.1), "nœud VDD", couleur="black")
        d += elm.Line().at(q.source).to((XF, YG))
        d += elm.Dot().at((XF, YG))
        d += elm.Ground().at((XF, YG))
        d += elm.Label().at((XF - 0.32, q.center[1])).label("AO3400A", fontsize=10, halign="right")

        xg = q.gate[0] + 1.5
        d += elm.Line().at(q.gate).to((xg, q.gate[1]))
        d += elm.Dot().at((xg, q.gate[1]))
        d += elm.Resistor().at((xg, q.gate[1])).down().toy(YG).color(ROUGE)
        d += elm.Label().at((xg - 0.42, (q.gate[1] + YG) / 2)).label(
            "100 Ω", fontsize=10, color=ROUGE, halign="right")
        d += elm.Line().at((xg, YG)).to((XF, YG))

        # OUT remonte puis rejoint le nœud de grille, sans traverser le transistor
        d += elm.Line().at(u.OUT).to((u.OUT[0], q.gate[1]))
        d += elm.Line().at((u.OUT[0], q.gate[1])).to((xg, q.gate[1]))

        d += elm.Label().at((0.0, YG - 4.3)).label(
            "ICI 100 Ω est la BONNE valeur : $R_{out}$ ≈ 2 Ω ⇒ τ ≈ 1,6 ns, et 33 mA de charge\n"
            "statique ne gênent pas un driver prévu pour l\'ampère.\n\n"
            "Derrière un GPIO nu (≈50 Ω), la même résistance forme un diviseur : $V_{GS}$ plafonne\n"
            "à 2,2 V et le pad débite 23 mA alors qu\'il est donné pour 12. D\'où le 1 kΩ de la carte.",
            fontsize=10, halign="left", color=ROUGE)
        _titre(d, 5.0, YD + 2.4,
               "Variante driver dédié — la voie d\'évolution, pas la carte de départ",
               "seul montage où le pull-down de 100 Ω vu ailleurs est justifié")
        _ecrire(d, "09_crowbar_grille_driver")


def maille_rlc():
    """La maille de décharge — l'origine du ringing et de $R_{damp}$."""
    _config()
    with schemdraw.Drawing(show=False) as d:
        Y = 4.2
        _broche(d, (0, Y), "$C_{res}$\n3,3 V", cote="left", couleur="black")
        d += elm.Resistor().at((0, Y)).right().length(2.1)
        d += elm.Label().at((1.05, Y + 0.74)).label("$R_{série}$\n4,3 Ω", fontsize=10)
        d += elm.Line().at((2.1, Y)).to((3.2, Y))
        d += elm.Dot(radius=0.13).at((3.2, Y))
        d += elm.Label().at((4.6, Y + 0.52)).label("nœud VDD", fontsize=10, color=GRIS)

        d += elm.Capacitor().at((3.2, Y)).down().length(1.8)
        d += elm.Ground().at((3.2, Y - 1.8))
        d += elm.Label().at((2.78, Y - 0.9)).label(
            "$C_{résid}$\n0,1 – 10 µF\n[hypothèse]", fontsize=10, halign="right")

        d += elm.Line().at((3.2, Y)).to((6.0, Y))
        d += elm.Dot().at((6.0, Y))
        d += elm.Inductor2().at((6.0, Y)).down().length(1.8)
        d += elm.Label().at((5.58, Y - 0.9)).label(
            "$L_{boucle}$\n30 – 150 nH\n[hypothèse]", fontsize=10, halign="right")
        d += elm.Resistor().at((6.0, Y - 1.8)).down().length(1.8).color(ROUGE)
        d += elm.Label().at((5.58, Y - 2.7)).label(
            "$R_{damp}$\n0,47 Ω", fontsize=10, color=ROUGE, halign="right")
        d += elm.Resistor().at((6.0, Y - 3.6)).down().length(1.8)
        d += elm.Label().at((5.42, Y - 4.5)).label(
            "$R_{on}$(t)\n19 mΩ à 3,3 V\nouvert sous 0,65 V", fontsize=10, halign="right")
        d += elm.Ground().at((6.0, Y - 5.4))

        d += elm.Line().at((6.0, Y)).to((8.4, Y))
        d += elm.Dot().at((8.4, Y))
        d += elm.Diode().at((8.4, Y)).down().length(1.8)
        d += elm.Ground().at((8.4, Y - 1.8))
        d += elm.Label().at((8.82, Y - 0.9)).label(
            "ESD cible\nclampe à −0,7 V", fontsize=10, halign="left")
        d += elm.Line().at((8.4, Y)).to((9.4, Y))
        d += elm.Resistor().at((9.4, Y)).right().length(1.8).color(ROUGE)
        d += elm.Label().at((10.3, Y + 0.55)).label("1 kΩ", fontsize=10, color=ROUGE)
        _broche(d, (11.2, Y), "GP26/27")

        d += elm.Label().at((7.3, Y - 3.5)).label(
            "Z0 = √(L / $C_{résid}$) = 0,39 Ω          ζ = $R_{totale}$ / (2 · Z0)\n\n"
            "sans $R_{damp}$  :  ζ = 0,05   ⇒   $V_{min}$ = −2,37 V  ·  8,0 A de crête\n"
            "avec 0,47 Ω   :  ζ ≈ 0,6     ⇒   $V_{min}$ = +0,17 V  ·  4,1 A de crête\n\n"
            "★ $R_{damp}$ ≈ $Z_0$ SUIT $C_{résid}$ : 0,15 Ω à 10 µF · 0,47 Ω à 1 µF · 1,2 Ω à 0,1 µF",
            fontsize=10.5, halign="left", color=ROUGE)
        _titre(d, 5.0, Y + 2.1,
               "Maille de décharge — ce qui fixe vraiment la descente du rail",
               "à 19 mΩ, l'AO3400A ne suit plus le modèle τ = $R_{on}$ · C du 09 §3.3bis")
        _ecrire(d, "09_crowbar_maille_rlc")


if __name__ == "__main__":
    print(f"Sortie : {SORTIE}")
    carte()
    grille_gpio()
    grille_driver()
    maille_rlc()
