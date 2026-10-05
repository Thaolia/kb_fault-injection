#!/usr/bin/env python3
"""Recoupement indépendant du modèle de gen_09_crowbar_courbes.py par ngspice.

Le modèle Python (scipy.solve_ivp) fait varier R_on avec V_GS(t) ; ngspice utilise
un interrupteur idéal à 19 mΩ qui se ferme à l'instant où V_GS franchit le seuil.
Deux formulations, deux solveurs, deux codes indépendants : si les deux tombent sur
les mêmes V_min et I_crête, le résultat n'est plus un artefact d'intégration.

Sort en code 1 dès qu'un écart dépasse la tolérance — c'est ce qui transforme les
courbes en résultat vérifié plutôt qu'en jolie image.

⚠ On appelle le binaire `ngspice -b`, PAS PySpice : PySpice 1.5 refuse ngspice 47
(« Unsupported Ngspice version 47 ») et exige libngspice.so, absente du système.
"""
import re
import subprocess
import sys

import numpy as np

import gen_09_crowbar_courbes as cc

TOLERANCE = 0.10          # 10 % — l'écart de modélisation attendu est de 1 à 3 %
R_DAMPS = (0.0, 0.22, 0.47, 1.0)
LARGEUR = 6e-6
CRESID = 1e-6
LBOUCLE = 150e-9
T_SEUIL = 7.3e-9          # instant où V_GS franchit V_GS(th) — cf. figure 1


def netlist(rdamp):
    """Même maille que cc.simule() : source → R_série → nœud → L → R_damp → switch."""
    return "\n".join([
        f"* crowbar variante B, R_damp = {rdamp} ohm",
        f"Vs 1 0 DC {cc.VS}",
        f"Rs 1 2 {cc.RSERIE}",
        "Cres 1 0 100u IC=" + str(cc.VS),
        f"Cnode 2 0 {CRESID} IC={cc.VS}",
        f"Lb 2 3 {LBOUCLE}",
        f"Rw 3 3b {cc.RWIRE}",
        f"Rd 3b 4 {max(rdamp, 1e-6)}",
        "Sw 4 0 5 0 SWMOD",
        f"Vg 5 0 PULSE(0 1 {T_SEUIL} 0.1n 0.1n {LARGEUR} 1)",
        "* R_on figé à la valeur datasheet typique à 3,3 V ; c'est LA différence",
        "* de modélisation avec le Python, qui la fait monter avec V_GS(t).",
        f".model SWMOD SW(Ron=0.019 Roff={cc.ROFF:g} Vt=0.5)",
        f".tran 1n {LARGEUR}  uic",
        ".control",
        "run",
        "print vecmin(v(2))",
        "print vecmax(abs(i(Lb)))",
        ".endc",
        ".end",
        "",
    ])


def lance_ngspice(rdamp):
    p = subprocess.run(["ngspice", "-b", "/dev/stdin"], input=netlist(rdamp),
                       capture_output=True, text=True, timeout=120)
    # on vise les vecteurs par leur nom : l'en-tête de ngspice contient d'autres
    # « = <nombre> » en fin de ligne (TNOM, TEMP) qui pollueraient une regex large.
    def lire(motif):
        m = re.search(motif + r"\s*=\s*([-+0-9.eE]+)", p.stdout, re.I)
        if not m:
            raise RuntimeError(f"ngspice : {motif} introuvable pour R_damp={rdamp}\n"
                               f"{p.stdout[-800:]}\n{p.stderr[-400:]}")
        return float(m.group(1))

    return lire(r"vecmin\(v\(2\)\)"), lire(r"vecmax\(abs\(i\(lb\)\)\)")


def main():
    try:
        subprocess.run(["ngspice", "-v"], capture_output=True, timeout=20)
    except FileNotFoundError:
        print("ngspice absent — recoupement impossible. `apt install ngspice`.")
        return 2

    print(f"Recoupement scipy ↔ ngspice — tolérance {TOLERANCE:.0%}\n")
    entete = f"{'R_damp':>7} | {'V_min scipy':>12} {'ngspice':>10} {'écart':>7}" \
             f" | {'I_crête scipy':>14} {'ngspice':>10} {'écart':>7}"
    print(entete)
    print("-" * len(entete))

    echecs = []
    for rd in R_DAMPS:
        _, v, i = cc.simule(rdamp=rd, cresid=CRESID, lboucle=LBOUCLE, largeur=LARGEUR)
        v_py, i_py = float(v.min()), float(np.abs(i).max())
        v_ng, i_ng = lance_ngspice(rd)

        # écart relatif rapporté à l'amplitude du signal (V_S), pas à V_min : à
        # 0,47 Ω, V_min vaut 0,17 V et un écart de 5 mV ferait 3 % d'un côté et
        # 30 % de l'autre. L'échelle physique du problème, c'est 3,3 V.
        e_v = abs(v_py - v_ng) / cc.VS
        e_i = abs(i_py - i_ng) / max(abs(i_py), abs(i_ng), 1e-9)
        drapeau = "  ✗" if (e_v > TOLERANCE or e_i > TOLERANCE) else ""
        if drapeau:
            echecs.append(rd)
        print(f"{rd:7.2f} | {v_py:>+11.3f} V {v_ng:>+9.3f} V {e_v:>6.1%}"
              f" | {i_py:>13.2f} A {i_ng:>9.2f} A {e_i:>6.1%}{drapeau}")

    print()
    if echecs:
        print(f"ÉCHEC : écart > {TOLERANCE:.0%} pour R_damp = "
              f"{', '.join(f'{r} Ω' for r in echecs)}")
        print("Les courbes du 09 §4 ne sont PAS validées — ne pas les publier en l'état.")
        return 1
    print("Les deux modèles concordent. Les figures 2 à 4 reposent sur un résultat recoupé.")
    print("⚠ Concorder n'est pas être juste : L_boucle et C_résid restent des hypothèses,")
    print("  et seules les mesures de l'étape 2.5 de la mise en route les remplaceront.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
