#!/usr/bin/env python3
"""Génère les schémas de câblage du document docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md.

Aucune dépendance Python tierce : le script produit du Graphviz et appelle le
binaire `dot`. C'est la même chaîne que celle des schémas du document 07.

    python3 assets/schemas/src/gen_09_banc.py            # -> assets/schemas/*.png
    python3 assets/schemas/src/gen_09_banc.py --format svg

Chaque numéro de broche présent ici est traçable à `drivers/include/board_v2.h`
(FaultyCat) ou à `raiden-pico/include/config.h` (raiden-pico). Ne jamais en
inventer un : le schéma est une source de vérité de câblage, pas une
illustration.
"""

import argparse
import subprocess
import sys
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1]

# Code couleur commun aux quatre schémas.
C_PUISSANCE = "#c00000"  # chemin de glitch / rail d'alimentation
C_TEMPS = "#0070c0"      # chaîne de déclenchement
C_ORACLE = "#207f4c"     # SWD : oracle et dump
C_MASSE = "#808080"      # masse commune
C_DATA = "#7030a0"       # liaisons série / USB

TITRES = {
    "raiden": "#1f4e79",
    "fc": "#7b3f00",
    "dut": "#4a4a4a",
    "alim": "#3f6212",
}


def boite(titre, lignes, couleur):
    """Étiquette HTML d'un boîtier : un titre, puis une ligne par broche.

    `lignes` est une liste de (port, texte). Un port vide donne une ligne de
    commentaire, sans ancre — utile pour les notes internes au boîtier.
    """
    html = [
        '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5">',
        f'<TR><TD BGCOLOR="{couleur}"><FONT COLOR="white" POINT-SIZE="13">'
        f"<B>{titre}</B></FONT></TD></TR>",
    ]
    for port, texte in lignes:
        ancre = f' PORT="{port}"' if port else ""
        fond = "" if port else ' BGCOLOR="#f2f2f2"'
        html.append(f'<TR><TD{ancre}{fond} ALIGN="LEFT">{texte}</TD></TR>')
    html.append("</TABLE>>")
    return "\n".join(html)


ENTETE = """digraph {{
  graph [rankdir=LR, splines=spline, nodesep=0.35, ranksep="0.9 equally",
         newrank=true, compound=true,
         fontname="DejaVu Sans", bgcolor="white", label=<{titre}>,
         labelloc="t", fontsize=17];
  node  [shape=plaintext, fontname="DejaVu Sans", fontsize=11];
  edge  [fontname="DejaVu Sans", fontsize=10, penwidth=1.6];
"""


# --------------------------------------------------------------------------
# Boîtiers réutilisés d'un schéma à l'autre
# --------------------------------------------------------------------------

def dut(note):
    """Boîtier de la cible. `note` diffère selon la variante : le crowbar exige
    une carte modifiee (decouplage retire, pile otee), l'EMFI non."""
    return boite(
        "T310 — BAT32G135 (DUT)",
        [
            ("vdd", "<B>VDD</B> — br. 7 / 9 / 11"),
            ("vss", "<B>VSS</B> — br. 6 / 8 / 10"),
            ("rst", "<B>RESETB</B> — br. 2"),
            ("swclk", "<B>P137 / SWCLK</B> — br. 3 / 5 / 7"),
            ("swdio", "<B>P40 / SWDIO</B> — br. 1 / 1 / 3"),
            ("", note),
        ],
        TITRES["dut"],
    )


DUT_MODIFIE = dut("★ découplage RETIRÉ · pile CR2450 ôtée")
DUT_INTACT = dut("★ carte INTACTE — découplage conservé, pile possible")


def raiden(lignes):
    return boite("raiden-pico (RP2350) — 6,67 ns", lignes, TITRES["raiden"])


def faultycat(sous_titre, lignes):
    return boite(f"FaultyCat v2.2 — {sous_titre}", lignes, TITRES["fc"])


# --------------------------------------------------------------------------
# Schéma 1 — variante A (recommandée)
# --------------------------------------------------------------------------

def variante_a():
    g = ENTETE.format(
        titre="<B>Variante A</B> — raiden-pico = temps + oracle · "
        "FaultyCat = puissance <BR/>"
        '<FONT POINT-SIZE="11">Le délai fin vit côté raiden (6,67 ns) ; '
        "le FaultyCat ne fournit que la largeur (delay_us = 0)</FONT>"
    )
    g += f"""
  raiden [label={raiden([
      ("gp15", "<B>GP15</B> nRST"),
      ("gp3",  "<B>GP3</B> trigger in"),
      ("gp2",  "<B>GP2</B> sortie glitch"),
      ("gp17", "<B>GP17</B> SWCLK"),
      ("gp18", "<B>GP18</B> SWDIO"),
      ("gp26", "<B>GP26</B> ADC0 — profondeur"),
      ("gp27", "<B>GP27</B> ADC1 — TRACE"),
      ("gp22", "GP22 GLITCH_FIRED (oscillo)"),
      ("gp10", "<B>GP10</B> enable alim (TARGET POWER EXT)"),
      ("v33",  "<B>3V3_OUT</B> br. 36 → la source ci-dessus"),
      ("gnd",  "GND"),
      ("",     "console : USB · pont TCP · Wi-Fi (§7)"),
  ])}];

  fc [label={faultycat("crowbar", [
      ("gp8",   "<B>GP8</B> TRIGGER_IN"),
      ("vref",  "TRIGGER_VREF ⚠ mesurer d'abord"),
      ("crow",  "<B>SORTIE CROWBAR</B> = DRAIN"),
      ("",      "GP16 = la GRILLE, sur le PCB —"),
      ("",      "ne JAMAIS la câbler sur VDD"),
      ("gnd",   "GND"),
  ])}];

  alim [label={boite("Source 3,3 V — le raiden lui-même", [
      ("vout", "<B>sortie 3,3 V</B> de la carte raiden"),
      ("",     "br. 36 sur une Pico 2 / Pico 2 W (RP2350A)"),
      ("",     "✅ tranché 2026-09-07 : c'est bien une Pico 2 W"),
      ("gnd",  "GND"),
      ("",     "plus de Bus Pirate : le réservoir absorbe"),
      ("",     "la crête, le régulateur ne voit qu'une"),
      ("",     "moyenne de quelques µA"),
  ], TITRES["alim"])}];

  sw [shape=box, style="rounded,dashed,filled", fillcolor="#f4f4f4", penwidth=1.2,
      label="interrupteur de charge (OPTIONNEL)\nP-FET côté haut, ≥ 1 A de crête\nenable ← GP10 en TARGET POWER EXT\n→ power-cycle pour sortir d'un blocage"];

  cres [shape=box, style="rounded,filled", fillcolor="#eaf3ea", penwidth=1.2,
        label="C_res 100 µF faible ESR\\n// 100 nF\\n(côté SOURCE)"];
  r43  [shape=box, style="filled", fillcolor="#fdeaea", penwidth=1.2,
        label="4,3 Ω\\n≥ 0,25 W, non bobinée"];
  noeud [shape=ellipse, style="filled", fillcolor="#fff2cc", penwidth=1.6,
         label="nœud VDD cible\\n(rail partagé avec la radio 868 MHz)"];

  dut [label={DUT_MODIFIE}];

  {{ rank=same; alim; cres; }}
  {{ rank=same; raiden; fc; r43; }}
  {{ rank=same; noeud; }}

  // --- alimentation et chemin de puissance --------------------------------
  alim:vout -> sw    [color="{C_PUISSANCE}", label="3,3 V"];
  sw        -> r43   [color="{C_PUISSANCE}", style=dashed];
  cres      -> alim:vout [color="{C_PUISSANCE}", dir=none, style=dashed,
                          label="réservoir"];
  r43       -> noeud [color="{C_PUISSANCE}", label="≈21 mV de chute\\nà 5 mA"];
  noeud     -> dut:vdd [color="{C_PUISSANCE}", penwidth=2.4];
  fc:crow   -> noeud [color="{C_PUISSANCE}", penwidth=2.4,
                      label="court-circuit bref\\n8 ns … 50 µs · crête ≈ 0,77 A"];

  // --- chaîne de déclenchement --------------------------------------------
  raiden:gp15 -> dut:rst [color="{C_TEMPS}", label="reset (actif bas)"];
  raiden:gp15 -> raiden:gp3 [color="{C_TEMPS}", style=dashed,
                             label="fil court, SANS résistance", constraint=false];
  raiden:gp2  -> fc:gp8 [color="{C_TEMPS}", penwidth=2.2, constraint=false,
                         label="front après PAUSE\\n(n × 6,67 ns)"];

  // --- oracle SWD ----------------------------------------------------------
  raiden:gp17 -> dut:swclk [color="{C_ORACLE}", label="100 Ω"];
  raiden:gp18 -> dut:swdio [color="{C_ORACLE}", dir=both, label="100 Ω"];

  // --- mesure --------------------------------------------------------------
  noeud -> raiden:gp26 [color="#b06000", style=dotted, constraint=false,
                        label="profondeur / VMIN"];
  noeud -> raiden:gp27 [color="#b06000", style=dotted, constraint=false,
                        label="TRACE — pré-campagne\\nseulement (§3.4)"];

  // --- alimentation pilotée par le raiden -----------------------------------
  raiden:gp10 -> sw [color="{C_TEMPS}", style=dashed, constraint=false,
                     label="power-cycle"];

  // --- masse ---------------------------------------------------------------
  raiden:gnd -> dut:vss [color="{C_MASSE}", style=bold, constraint=false];
  fc:gnd     -> dut:vss [color="{C_MASSE}", style=bold, constraint=false];
  alim:gnd   -> dut:vss [color="{C_MASSE}", style=bold,
                         label="UNE SEULE MASSE"];
}}
"""
    return g


# --------------------------------------------------------------------------
# Schéma 2 — variante B (raiden seul)
# --------------------------------------------------------------------------

def variante_b():
    g = ENTETE.format(
        titre="<B>Variante B</B> — raiden-pico seul, MOSFET externe<BR/>"
        '<FONT POINT-SIZE="11">Un seul appareil dans la boucle de tir : '
        "à souder si la cadence tombe sous ~10 tirs/s</FONT>"
    )
    g += f"""
  raiden [label={raiden([
      ("gp15", "<B>GP15</B> nRST"),
      ("gp3",  "<B>GP3</B> trigger in"),
      ("gp11", "<B>GP11</B> grille crowbar (mode EXT)"),
      ("gp10", "GP10 enable alimentation (mode EXT)"),
      ("gp17", "<B>GP17</B> SWCLK"),
      ("gp18", "<B>GP18</B> SWDIO"),
      ("gp26", "<B>GP26</B> ADC0 — profondeur"),
      ("gnd",  "GND"),
  ])}];

  fet [shape=box, style="filled", fillcolor="#fdeaea", penwidth=1.4,
       label="carte MOSFET externe — AO3400A (SOT-23)\\n\
grille br.1 · source br.2 · drain br.3\\n\
R_pd 1 kΩ grille→source, AU RAS du FET (E9)\\n\
R_damp ≈ √(L/C_résid) en série avec le drain\\n\
schéma détaillé et valeurs : 09 §4.1"];

  src [shape=box, style="rounded,filled", fillcolor="#eaf3ea", penwidth=1.2,
       label="raiden 3V3_OUT (br. 36)\\n+ C_res 100 µF, puis R série\\n(identique à A — plus de Bus Pirate)"];

  noeud [shape=ellipse, style="filled", fillcolor="#fff2cc", penwidth=1.6,
         label="nœud VDD cible"];

  dut [label={DUT_MODIFIE}];

  fc [label={faultycat("hors du chemin de tir", [
      ("", "pont UART console (§7)"),
      ("", "puis EMFI (variante C)"),
  ])}];

  {{ rank=same; src; raiden; fc; }}
  {{ rank=same; fet; }}
  {{ rank=same; noeud; }}

  src -> noeud [color="{C_PUISSANCE}"];
  noeud -> dut:vdd [color="{C_PUISSANCE}", penwidth=2.4];
  fet -> noeud [color="{C_PUISSANCE}", penwidth=2.4, label="court-circuit bref"];
  raiden:gp11 -> fet [color="{C_TEMPS}", penwidth=2.2,
                      label="même moteur PIO que GP2\\nWIDTH/GAP/COUNT · 6,67 ns"];
  raiden:gp10 -> src [color="{C_TEMPS}", style=dashed, label="enable (power-cycle)"];
  raiden:gp15 -> dut:rst [color="{C_TEMPS}", label="reset"];
  raiden:gp15 -> raiden:gp3 [color="{C_TEMPS}", style=dashed, constraint=false,
                             label="fil court"];
  raiden:gp17 -> dut:swclk [color="{C_ORACLE}", label="100 Ω"];
  raiden:gp18 -> dut:swdio [color="{C_ORACLE}", dir=both, label="100 Ω"];
  noeud -> raiden:gp26 [color="#b06000", style=dotted, constraint=false,
                        label="1 kΩ (§4.4)"];
  raiden:gnd -> dut:vss [color="{C_MASSE}", style=bold, label="UNE SEULE MASSE"];
  fc -> raiden [color="{C_DATA}", style=dotted, dir=none,
                label="console UART (§7)"];
}}
"""
    return g


# --------------------------------------------------------------------------
# Schéma 3 — variante C (EMFI, positionnement manuel)
# --------------------------------------------------------------------------

def variante_c():
    g = ENTETE.format(
        titre="<B>Variante C</B> — EMFI, positionnement manuel<BR/>"
        '<FONT POINT-SIZE="11">Ni découplage à retirer, ni rail à toucher : '
        "la carte peut rester intacte</FONT>"
    )
    g += f"""
  raiden [label={raiden([
      ("gp15", "<B>GP15</B> nRST"),
      ("gp3",  "<B>GP3</B> trigger in"),
      ("gp2",  "<B>GP2</B> sortie glitch"),
      ("gp17", "<B>GP17</B> SWCLK"),
      ("gp18", "<B>GP18</B> SWDIO"),
      ("gnd",  "GND"),
  ])}];

  fc [label={faultycat("EMFI ~250 V", [
      ("gp8",  "<B>GP8</B> TRIGGER_IN"),
      ("sma",  "<B>sortie SMA</B> ← GP14 HVPULSE"),
      ("",     "GP20 PWM flyback · GP18 CHARGED"),
      ("",     "⚠ bouclier plastique OBLIGATOIRE"),
      ("",     "auto-désarmement 60 s · charge 100 ms"),
      ("gnd",  "GND"),
  ])}];

  sonde [shape=box, style="filled", fillcolor="#fdeaea", penwidth=1.4,
         label="sonde EMFI\\nIMMOBILISÉE sur le boîtier\\n5 positions : centre + 4 quadrants"];

  dut [label={DUT_INTACT}];

  pile [shape=box, style="rounded,filled", fillcolor="#eaf3ea",
        label="alimentation normale\\n(pile CR2450, ou raiden 3V3_OUT br. 36)\\naucune modification de la carte"];

  {{ rank=same; raiden; fc; pile; }}
  {{ rank=same; sonde; }}

  raiden:gp15 -> dut:rst [color="{C_TEMPS}", label="reset"];
  raiden:gp15 -> raiden:gp3 [color="{C_TEMPS}", style=dashed, constraint=false,
                             label="fil court"];
  raiden:gp2 -> fc:gp8 [color="{C_TEMPS}", penwidth=2.2,
                        label="front après PAUSE"];
  fc:sma -> sonde [color="{C_PUISSANCE}", penwidth=2.6, label="~250 V"];
  sonde -> dut [color="{C_PUISSANCE}", penwidth=2.6, style=dashed,
                label="couplage magnétique\\nlargeur en µs"];
  raiden:gp17 -> dut:swclk [color="{C_ORACLE}", label="100 Ω"];
  raiden:gp18 -> dut:swdio [color="{C_ORACLE}", dir=both, label="100 Ω"];
  pile -> dut:vdd [color="{C_PUISSANCE}", style=dashed];
  raiden:gnd -> dut:vss [color="{C_MASSE}", style=bold, label="UNE SEULE MASSE"];
  fc:gnd -> dut:vss [color="{C_MASSE}", style=bold, constraint=false];
}}
"""
    return g


# --------------------------------------------------------------------------
# Schéma 4 — le pont UART console
# --------------------------------------------------------------------------

def consoles():
    g = ENTETE.format(
        titre="<B>Les chemins de console du raiden-pico</B> — et leur statut réel<BR/>"
        '<FONT POINT-SIZE="11">Vert = mesuré sur le banc · '
        "Orange = code écrit, non exercé · Rouge = pas écrit</FONT>"
    )
    g += f"""
  poste [label={boite("Poste de travail", [
      ("scripts", "<B>scripts/</B> — serial_for_url() accepte"),
      ("",        "/dev/ttyACM0  ET  socket://hôte:port"),
      ("pty",     "<B>raiden_bridge.py pty</B> → /tmp/raiden"),
      ("",        "201 ko/s vs 49 o/s en socket:// direct"),
  ], "#404040")}];

  banc [label={boite("Hôte du banc", [
      ("usb",   "<B>/dev/ttyACM0</B> — USB CDC natif"),
      ("serve", "<B>raiden_bridge.py serve</B> → TCP :5000"),
      ("",      "ni socat ni sudo"),
      ("cdc3",  "CDC3 du FaultyCat (« Target UART »)"),
  ], "#404040")}];

  raiden [label={raiden([
      ("usb",  "<B>USB CDC</B> — v0.13, la seule voie réelle"),
      ("uart", "GP0/GP1 UART0 — exige <B>v0.14</B> (§7.2)"),
      ("wifi", "<B>CLI TCP Wi-Fi</B> — Pico 2 W"),
      ("",     "net_cli.c : associe + sections silencieuses"),
      ("",     "PAS de serveur TCP : rien n'écoute encore"),
  ])}];

  fc [label={faultycat("pont uart_passthrough", [
      ("cdc", "CDC2 : uart enter · CDC3 : les données"),
      ("ch",  "CH0=GP0 TX / CH1=GP1 RX, pompé à 1 ms"),
  ])}];

  {{ rank=same; poste; }}
  {{ rank=same; banc; fc; }}
  {{ rank=same; raiden; }}

  // 1. USB natif — mesuré, c'est le chemin du dump
  raiden:usb -> banc:usb [color="#207f4c", penwidth=2.6, dir=both,
                          label="1 · USB natif — MESURÉ\\ndump 64 Ko en 26 s, md5 6f37bd86…"];

  // 2. Pont TCP côté banc — mesuré, mêmes md5 et même durée
  banc:serve -> poste:scripts [color="#207f4c", penwidth=2.4, dir=both,
                               label="2 · socket://banc:5000 — MESURÉ\\nmêmes md5, mêmes 26 s"];
  poste:pty -> poste:scripts [color="#207f4c", style=dashed, constraint=false,
                              label="pty : in_waiting réel (TIOCINQ)"];

  // 3. Wi-Fi — non écrit
  raiden:wifi -> poste:scripts [color="#c00000", style=dotted, penwidth=2.0,
                                label="3 · CLI TCP Wi-Fi — À ÉCRIRE\\ncmake -DBOARD=pico2w -DWIFI_SSID=…\\net il faut un Pico 2 W"];

  // 4. Pont UART FaultyCat — code prêt d'un côté seulement
  raiden:uart -> fc:ch [color="#b06000", style=dashed, penwidth=2.0,
                        label="4 · UART — INERTE\\ntant que v0.14 n'est pas posée"];
  fc:cdc -> banc:cdc3 [color="#b06000", style=dashed, penwidth=2.0];

  note [shape=note, style=filled, fillcolor="#fff2cc", fontsize=10,
        label="Discipline temps réel, valable pour TOUTES ces voies :\\nle moteur de glitch PIO est immunisé (front matériel GP15→GP3).\\nCe qui ne l'est pas : VMIN / ADC-gated, et TRACE.\\nNET_QUIET_SECTION couvre déjà power_glitch_once et SWD RACE ;\\nla section TRACE reste à faire (CHANGELOG, Unreleased)."];
  raiden -> note [style=invis];
}}
"""
    return g


SCHEMAS = {
    "09_variante_a_crowbar": variante_a,
    "09_variante_b_raiden_seul": variante_b,
    "09_variante_c_emfi": variante_c,
    "09_consoles": consoles,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--format", default="png", choices=["png", "svg", "pdf"])
    ap.add_argument("--keep-dot", action="store_true",
                    help="conserver les sources .dot à côté des images")
    ap.add_argument("--only", help="ne générer qu'un schéma (nom sans extension)")
    a = ap.parse_args()

    cibles = SCHEMAS if not a.only else {a.only: SCHEMAS[a.only]}
    for nom, fabrique in cibles.items():
        source = fabrique()
        if a.keep_dot:
            (OUT_DIR / "src" / f"{nom}.dot").write_text(source, encoding="utf-8")
        sortie = OUT_DIR / f"{nom}.{a.format}"
        r = subprocess.run(["dot", f"-T{a.format}", "-o", str(sortie)],
                           input=source, text=True, capture_output=True)
        if r.returncode != 0:
            print(f"[ÉCHEC] {nom}\n{r.stderr}", file=sys.stderr)
            return 1
        if r.stderr.strip():
            print(f"[avertissement] {nom}: {r.stderr.strip()}", file=sys.stderr)
        print(f"{sortie}  ({sortie.stat().st_size} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
