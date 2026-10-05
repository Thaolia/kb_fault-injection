#!/usr/bin/env bash
# Régénère les 23 schémas PNG dans assets/schemas/ (dossier parent) depuis src/.
# Dépendances : python3 + schemdraw + matplotlib + numpy + scipy ; graphviz (dot).
# Le recoupement ngspice du doc 09 est SÉPARÉ (check_09_crowbar_spice.py) : c'est un
# test, pas un générateur, et il exige le binaire `ngspice`.
# Surcharge de l'interpréteur : PYTHON=/chemin/vers/python ./generate.sh
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$(cd "$SRC/.." && pwd)"
PY="${PYTHON:-python3}"

echo "[1/4] schemdraw -> b_crowbar, a_loadswitch, c_trigger, e_palier2_agw"
"$PY" "$SRC/gen_schemas.py"

echo "[2/4] graphviz  -> 00_overview, d_interfaces, 06_emfi_block, 06_faultycat_integ, 07_bat32_bench(_raiden), 08_nrf52820_bench"
dot -Tpng -Gdpi=150 "$SRC/overview.dot"        -o "$OUT/00_overview.png"
dot -Tpng -Gdpi=150 "$SRC/interfaces.dot"      -o "$OUT/d_interfaces.png"
dot -Tpng -Gdpi=150 "$SRC/emfi_block.dot"      -o "$OUT/06_emfi_block.png"
dot -Tpng -Gdpi=150 "$SRC/faultycat_integ.dot" -o "$OUT/06_faultycat_integ.png"
dot -Tpng -Gdpi=150 "$SRC/bat32_bench.dot"        -o "$OUT/07_bat32_bench.png"
dot -Tpng -Gdpi=150 "$SRC/bat32_bench_raiden.dot" -o "$OUT/07_bat32_bench_raiden.png"
dot -Tpng -Gdpi=150 "$SRC/nrf52820_bench.dot"    -o "$OUT/08_nrf52820_bench.png"


echo "[3/4] gen_09_banc      -> 09_variante_a/b/c, 09_consoles (doc 09)"
"$PY" "$SRC/gen_09_banc.py"

echo "[4/4] gen_09_crowbar_*  -> 09_crowbar_* (4) + 09_courbe_* (4) (doc 09)"
"$PY" "$SRC/gen_09_crowbar_schemas.py"
"$PY" "$SRC/gen_09_crowbar_courbes.py"

echo "OK — 23 PNG écrits dans $OUT"
echo
echo "⚠ Recoupement ngspice des figures 09_courbe_* — NON lancé ici :"
echo "    python3 $SRC/check_09_crowbar_spice.py   # doit sortir en 0 ; exige ngspice"
