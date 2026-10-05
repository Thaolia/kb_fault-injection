# Sources des schémas (`assets/schemas/src/`)

Scripts de génération des **23 PNG** de [`../`](../) (embarqués dans
[`../../../docs/05_SCHEMAS_ELECTRONIQUES.md`](../../../docs/05_SCHEMAS_ELECTRONIQUES.md),
[`../../../docs/06_EMI_INJECTOR_EMFI.md`](../../../docs/06_EMI_INJECTOR_EMFI.md),
[`../../../docs/07_BAT32G135_FAULTYCAT.md`](../../../docs/07_BAT32G135_FAULTYCAT.md),
[`../../../docs/08_NRF52820_APPROTECT.md`](../../../docs/08_NRF52820_APPROTECT.md) et
[`../../../docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md`](../../../docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md)).
Trois chaînes d'outils : **schemdraw** (circuits composant-niveau), **graphviz** (diagrammes bloc)
et **matplotlib + scipy** (courbes de simulation du doc 09).

> ⚠ **Le préfixe numérique est celui du DOCUMENT qui embarque la figure, pas une série continue.**
> `07_*` = cible BAT32G135 · `08_*` = cible nRF52820 · `09_*` = banc FaultyCat+raiden. Un renommage
> global `08_ → 09_` casserait `08_nrf52820_bench.png` : toujours renommer par liste explicite.

## Fichiers → PNG produit

| Source | Outil | PNG généré (dans `../`) |
|---|---|---|
| `gen_schemas.py` → `fig_b` | schemdraw | `b_crowbar.png` |
| `gen_schemas.py` → `fig_a` | schemdraw | `a_loadswitch.png` |
| `gen_schemas.py` → `fig_c` | schemdraw | `c_trigger.png` |
| `gen_schemas.py` → `fig_e` | schemdraw | `e_palier2_agw.png` |
| `overview.dot` | graphviz `dot` | `00_overview.png` |
| `interfaces.dot` | graphviz `dot` | `d_interfaces.png` |
| `emfi_block.dot` | graphviz `dot` | `06_emfi_block.png` (module EMFI, doc `06`) |
| `faultycat_integ.dot` | graphviz `dot` | `06_faultycat_integ.png` (intégration FaultyCat, doc `06`) |
| `bat32_bench.dot` | graphviz `dot` | `07_bat32_bench.png` (banc BAT32G135 à 3 outils, doc `07`) |
| `bat32_bench_raiden.dot` | graphviz `dot` | `07_bat32_bench_raiden.png` (variante raiden-pico, doc `07`) |

`gen_schemas.py` écrit ses PNG dans le **dossier parent** (`assets/schemas/`), calculé relativement
au script — pas de chemin absolu à modifier.

## Dépendances

- **Python 3** + **schemdraw** : `pip install schemdraw` (tire `matplotlib`).
- **graphviz** (binaire `dot`) : `apt install graphviz` (ou équivalent).
- **numpy + scipy** : `pip install numpy scipy` — requis par `gen_09_crowbar_courbes.py`.
- **ngspice** (binaire) : `apt install ngspice` — requis par `check_09_crowbar_spice.py` **seul**.
  ⚠ On appelle **`ngspice -b`, jamais PySpice** : PySpice 1.5 refuse ngspice 47
  (« Unsupported Ngspice version ») et réclame `libngspice.so`, absente des paquets courants.

## ⚠ Statut de provenance des figures du doc 09

★ **Les quatre `09_courbe_*` sont un MODÈLE, pas une mesure.** `gen_09_crowbar_courbes.py` le dit
en tête : `L_boucle` et `C_résid` sont des **hypothèses**, et `R_pad ≈ 50 Ω` une estimation `[reco]`
jamais lue au datasheet RP2350. Elles **bornent** le problème et donnent l'ordre de grandeur ;
seules les mesures du doc 09 §4.7 les remplacent. Les citer `[reco]`, **jamais `[fait]`**.

`check_09_crowbar_spice.py` recoupe ce modèle par une netlist **ngspice indépendante** (interrupteur
idéal 19 mΩ contre `R_on(V_GS(t))` intégré par `scipy.solve_ivp`) et **sort en code 1 dès qu'un
écart dépasse 10 %**. C'est un **test**, à lancer séparément de `generate.sh` :

```bash
python3 assets/schemas/src/check_09_crowbar_spice.py   # doit sortir en 0
```

⚠ *Concorder n'est pas être juste* : l'accord des deux solveurs valide leur cohérence, pas la
justesse des hypothèses.
- Police **DejaVu Sans** (accents corrects dans les labels graphviz).

## Régénérer

```bash
# tout (recommandé)
./generate.sh

# avec un interpréteur Python précis (ex. venv contenant schemdraw)
PYTHON=/chemin/venv/bin/python ./generate.sh

# manuellement
python3 gen_schemas.py                                   # -> 4 PNG schemdraw
dot -Tpng -Gdpi=150 overview.dot   -o ../00_overview.png
dot -Tpng -Gdpi=150 interfaces.dot -o ../d_interfaces.png
```

## Après régénération

- **Inspecter visuellement** chaque PNG (schemdraw peut faire chevaucher labels/symboles si on
  change l'espacement) avant de committer. ⚠️ **Ce n'est pas une précaution théorique** : une
  régénération sous **schemdraw 0.23** a produit deux régressions réelles, corrigées depuis dans
  `gen_schemas.py` —
  ① **légendes de bas de figure rognées** par la bounding box serrée ⇒ `margin=0.9` est désormais
  passé à `d.config()` de chaque figure, **ne pas le retirer** ;
  ② **label `Q1 AO3400A` recouvrant le MOSFET** dans `b_crowbar` ⇒ posé avec `halign='left'` et
  dégagé sur la droite. Trois chevauchements mineurs (TLV3501/opamp, C1/Vref, Vdac/boîte DAC) ont
  été corrigés dans la foulée.
- **Le rendu dépend de la version de schemdraw** : deux versions différentes ne produisent pas des
  PNG identiques à l'octet près. Une régénération « pour rien » réécrit donc les 4 fichiers
  schemdraw — inspecter avant de conclure que rien n'a bougé.
- Les docs référencent ces PNG par chemin relatif : ne pas renommer les fichiers de sortie.
- ⚠ **`docs/07` est un document volontairement autonome / exportable.** Les deux PNG `07_*` y sont un
  **complément** : chaque schéma y est **aussi** rendu en ASCII dans le corps du texte, pour que le
  document reste complet une fois exporté hors du dépôt. **Ne pas supprimer les schémas ASCII de
  `docs/07` au motif que les PNG existent.**
