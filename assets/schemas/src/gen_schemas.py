# -*- coding: utf-8 -*-
"""Génère les schémas électroniques du glitcher RP2350 en PNG (schemdraw).

Sortie : les PNG sont écrits dans le dossier parent (assets/schemas/).
Dépendance : schemdraw (pip install schemdraw), qui tire matplotlib.
Usage : python gen_schemas.py

Note (schemdraw 0.23) : `margin` sur d.config() est indispensable — sans lui les légendes
de bas de figure (elm.Label placés sous le circuit) sont rognées par la bbox serrée.
Les labels posés près d'un composant doivent utiliser halign= pour ne pas le recouvrir.
Toujours INSPECTER VISUELLEMENT les 4 PNG après régénération (cf. README.md).
"""
import os
import traceback
import schemdraw
import schemdraw.elements as elm

# Dossier parent du script = assets/schemas/  → les PNG y sont écrits.
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DPI = 200
BLUE = '#1a5fb4'
GREY = '#666666'
results = []

def run(name, fn):
    try:
        fn()
        results.append(f'{name} OK')
    except Exception as e:
        results.append(f'{name} FAIL: {e}')
        traceback.print_exc()

# ---------- Fig B : Crowbar (Palier 1) ----------
def fig_b():
    with schemdraw.Drawing(file=f"{OUT}/b_crowbar.png", dpi=DPI, show=False) as d:
        d.config(unit=2.6, fontsize=13, margin=0.9)
        d += elm.Label().label('Bloc B — Crowbar (Palier 1)').color(BLUE).at((2.5, 2.6))
        d += elm.Dot(open=True).label('Vin\n(3V3 commuté)', 'left')
        d += elm.Resistor().right().label('Rs 10–100 Ω *')
        A = elm.Dot().label('rail', 'top')
        d += A
        d += elm.Line().right().length(1.6)
        d += elm.RBox(w=2.2, h=1.4).right().label('STM32\ncible').fill('#eaf3ff')
        # branche crowbar vers le bas
        d += elm.Line().down().at(A.center).length(1.5)
        Q = elm.NFet().anchor('drain')
        d += Q
        d += elm.Ground().at(Q.source)
        d += elm.Label().label('Q1  AO3400A\n(N-ch, défaut)', halign='left').at((Q.center.x + 1.1, Q.center.y)).color(GREY)
        # grille -> driver (à gauche, dégagé)
        d += elm.Line().left().at(Q.gate).length(1.4)
        drv = elm.RBox(w=2.0, h=1.1).left().label('ADP3623\ngate driver').fill('#fff3e0')
        d += drv
        d += elm.Line().left().length(0.7)
        d += elm.Dot(open=True).label('GP2\nGLITCH_OUT', 'left')
        d += elm.Label().label('+ TVS clamp rail↔GND · point de mesure < 10 mm · découplage cible minimal').at((2, -3.9)).color(GREY)
        d += elm.Label().label('boucle driver→grille→MOSFET→GND : la plus courte possible (plancher de largeur)').at((2, -4.4)).color(GREY)

# ---------- Fig A : Load switch high-side ----------
def fig_a():
    with schemdraw.Drawing(file=f"{OUT}/a_loadswitch.png", dpi=DPI, show=False) as d:
        d.config(unit=2.4, fontsize=13, margin=0.9)
        d += elm.Label().label('Bloc A — Load switch high-side (power-cycle)').color(BLUE).at((2.3, 1.9))
        d += elm.Dot(open=True).label('+3V3_TGT', 'left')
        d += elm.Line().right().length(0.6)
        ls = elm.RBox(w=2.4, h=1.4).right().label('TPS22918\nload switch').fill('#e8eaf6')
        d += ls
        d += elm.Line().right().length(0.7)
        d += elm.Dot(open=True).label('Vin →\n(vers Bloc B)', 'right')
        # commande ON depuis le bas de la boîte
        d += elm.Line().down().at((ls.center.x, ls.center.y - 0.7)).length(1.0)
        d += elm.Dot(open=True).label('GP3  LOADSW_EN (ON)', 'left')
        d += elm.Label().label('actif haut = cible alimentée · délai POR 1,5–4,5 ms avant re-trigger').at((2.3, -2.4)).color(GREY)

# ---------- Fig C : Trigger (comparateur) ----------
def fig_c():
    with schemdraw.Drawing(file=f"{OUT}/c_trigger.png", dpi=DPI, show=False) as d:
        d.config(unit=2.0, fontsize=13, margin=0.9)
        d += elm.Label().label('Bloc C — Entrée trigger (comparateur rapide)').color(BLUE).at((2, 2.2))
        d += elm.Dot(open=True).label('SMA_TRIG\n(I/O · NRST · ext.)', 'left')
        d += elm.Resistor().right().label('R1 1k')
        P = elm.Dot()
        d += P
        d += elm.Line().right().length(0.4)
        cmp = elm.Opamp().anchor('in1')
        d += cmp
        d += elm.Label().label('TLV3501\ncomparateur').at((cmp.center.x + 0.5, cmp.center.y + 1.8)).color(GREY)
        d += elm.Line().left().at(cmp.in2).length(0.5)
        d += elm.Dot(open=True).label('Vref (seuil)', 'left')
        d += elm.Capacitor().down().at(P.center).label('C1', 'right')
        d += elm.Ground()
        d += elm.Line().right().at(cmp.out).length(0.4)
        d += elm.Resistor().right().label('Rs 100Ω')
        d += elm.Dot(open=True).label('GP4\nTRIG_IN (PIO)', 'right')

# ---------- Fig E : Palier 2 AGW ----------
def fig_e():
    with schemdraw.Drawing(file=f"{OUT}/e_palier2_agw.png", dpi=DPI, show=False) as d:
        d.config(unit=1.4, fontsize=12, margin=0.9)
        d += elm.Label().label("Bloc E — Palier 2 : forme d'onde arbitraire (AGW, Bozzato)").color(BLUE).at((5, 1.9))
        d += elm.Dot(open=True).label('SPI0\nGP17/18/19', 'left')
        d += elm.Line().right().length(0.4)
        d += elm.RBox(w=1.9, h=1.3).right().label('DAC\n≥ 12 bits').fill('#e8f5e9')
        d += elm.Line().right().length(0.4).label('Vdac', 'bottom')
        d += elm.RBox(w=2.1, h=1.3).right().label('THS3062\nétage 1').fill('#fff3e0')
        d += elm.Line().right().length(0.25)
        d += elm.RBox(w=2.1, h=1.3).right().label('THS3062\nétage 2').fill('#fff3e0')
        d += elm.Line().right().length(0.4)
        d += elm.RBox(w=1.7, h=1.3).right().label('relais\nreed').fill('#e3f2fd')
        d += elm.Line().right().length(0.5)
        d += elm.Dot(open=True).label('→ VDD_cible\n(via J-RAIL)', 'right')
        d += elm.Label().label('coupure : GP12 REED_EN   ·   ±10 V · 6 MHz · 145 mA · alim continue de la cible').at((5, -1.6)).color(GREY)

if __name__ == '__main__':
    run('b_crowbar', fig_b)
    run('a_loadswitch', fig_a)
    run('c_trigger', fig_c)
    run('e_palier2', fig_e)
    print("\n".join(results))
