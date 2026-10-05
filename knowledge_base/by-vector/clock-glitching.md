# Clock glitching

> Mécanisme partagé avec le voltage glitching : [`../cross-cutting/fault-models-mechanisms.md`](../cross-cutting/fault-models-mechanisms.md).

## 1. Précondition — la vraie limite du vecteur

Le clock et le voltage glitching produisent des fautes **identiques** au niveau du
mécanisme [corpus, SoK 2025 §3.1] — la différence est **l'accessibilité** du signal à
perturber, pas le mécanisme.

- **Une PLL interne bloque le clock glitch.** [corpus, TCHES 2024, p. 176] : *« les
  variations rapides de l'horloge de référence ne traversent pas une PLL »* → contre-mesure
  quasi totale.
- **Le clock glitch externe exige une horloge externe accessible.** [corpus, *Peak Clock*,
  ASHES'19, p. 92-93] : un exemple n'est attaquable que parce que sa PLL est sourcée par un
  signal externe de 4 MHz. Si le firmware démarre sur un oscillateur RC interne et fait
  tourner la PLL dessus, **il n'existe aucun nœud d'horloge externe à manipuler** — passer
  au voltage glitch ou à l'EMFI.

**Règle de décision générale** : le clock glitch n'est exploitable que si l'on peut forcer le
boot sur une horloge externe (cristal, injection sur la broche d'oscillateur, bootloader ROM
qui l'utilise par défaut). Sinon → voltage glitch / EMFI uniquement.

## 2. Technique 1 — burst de sur-cadencement de PLL

[corpus, *Peak Clock*, ASHES'19] : pas une impulsion courte mais un **burst haute fréquence
soutenu sur l'entrée d'horloge**, pour forcer la PLL à se sur-cadencer.

- Exemple documenté : nominal 48 MHz (PLL ×12 depuis 4 MHz externe) ; burst de ~100 µs amène
  le cœur à ~110 MHz ; fenêtre de succès ~119–134 µs (flanc de discrimination 2 µs) ; crash
  au-delà de ~138 µs.
- **Instruction shadowing** : le burst couvrant des dizaines d'instructions, ce sont les
  **branchements** qui échouent en premier.
- Autre exemple à PLL rapide : burst de 500 ns suffit.

## 3. Technique 2 — glitch de période, sur MCU à horloge externe fournie

[corpus, Korak & Höfler, deck FDTC 2014] — au lieu d'un burst soutenu, insérer **une période
raccourcie** `TGlitch` dans l'horloge (`T | TGlitch | T−TGlitch`) sur des MCU dont
l'attaquant contrôle l'horloge d'attaque :

- Horloge de travail 24 MHz (T ≈ 42 ns) ; `TGlitch` balayé 5–18 ns ; fautes reproductibles sur
  [6,0 ; 20,0] ns ; alimentation 3,3 V. ⚠️ **L'architecture du générateur n'est pas publiée** :
  le deck ne montre qu'une boîte noire « Fault Board » reliée à la cible par *supply voltage /
  clock signal / trigger / reset* (sl. 14) — aucune résolution ni topologie de générateur n'y
  est imprimée. Ne pas lui prêter le montage DCM+MUX du deck compagnon sur le chauffage.
- ★ **L'underpowering élargit la fenêtre de glitch** (Cortex-M0) : en abaissant `UGlitch` de
  1,5 V à 1,0 V, la plage de `TGlitch` productive passe de quelques dixièmes de ns à ~3 ns
  (fetch) et ~7,7 ns (execute) *(lues sur graphe, non imprimées)*. ⚠️ L'axe élargi est la
  fenêtre du glitch d'**horloge** — analogue de mécanisme, pas un transfert de chiffres vers
  le voltage glitching.
- **Cartographie par étage de pipeline** obtenue avec cette technique : voir
  [`../cross-cutting/fault-models-mechanisms.md`](../cross-cutting/fault-models-mechanisms.md)
  §6 (skip au fetch, corruption à l'execute, decode intact).
- ⚠️ **Portée limitée** : la Fault Board de cette expérience fournit à la cible **l'horloge
  ET l'alimentation** — précondition inhabituelle pour une cible réelle bootant sur RC
  interne. Aucun taux de succès n'est publié, et le vecteur reste le clock glitch,
  l'underpowering n'y étant qu'un **sensibilisateur combiné**, jamais un vecteur autonome.

## 4. L'effet du chauffage — attesté sur clock glitching, transposable au voltage

Le deck compagnon *Clock Glitch Attacks in the Presence of Heating* (mêmes auteurs) mesure un
**déplacement de seuil identique en ns absolues à 10 et 20 MHz** — signature d'un effet sur
le délai de propagation, donc générique. Détail complet et réserves (le seuil se déplace,
il ne s'élargit pas systématiquement) :
[`../cross-cutting/campaign-instrumentation-metrics.md`](../cross-cutting/campaign-instrumentation-metrics.md) §3.

## 5. Régimes FPGA-internes / simulés — non transposables tels quels

Plusieurs papiers caractérisent le clock glitch **à l'intérieur** d'un FPGA (logique
combinatoire, pas un MCU externe attaqué depuis l'extérieur) — utiles pour la physique, pas
pour dimensionner un banc :

| Source | Régime | Résultat | Portée |
|---|---|---|---|
| Endo (2011) | FPGA Virtex-II, générateur compteur+2 DLL+MUX | résolution 0,17 ns (min. phase-shift DCM) | FPGA-interne |
| Ning (simul., 2018) | AES FPGA, modèle setup-violation | pas de réduction de période 0,02 ns | simulation |
| Surya (iSES'20) | S-box ASCON FPGA, clock glitch local émulant l'EMFI | fenêtre productive [4,1 ; 5,4] ns | FPGA-interne |
| Sneaky Glitch (2024) | FPGA 7-Series, générateur furtif (3 MMCM + 5 BUFGCTRL) | **résolution de commande 14,8 ps ≠ largeur visible 531 ps** | FPGA-interne, mais leçon générale |
| Marotta (COSADE'24) | Artix-7 + SPICE, modèle **énergie-seuil** | pont conceptuel clock↔voltage (« pas assez d'énergie à la bascule ») | modèle, pas un chiffre de banc |

★ **Leçon générale extraite de Sneaky Glitch, valable pour tout étage de sortie physique** :
la **résolution de commande n'est pas la largeur d'impulsion réalisable**. Sur une carte
réelle avec câbles et capacité d'entrée de la cible, le plancher de largeur est fixé par
l'étage de sortie (MOSFET/driver/parasites), pas par le contrôleur de timing — voir
[`../cross-cutting/parameter-search-methodology.md`](../cross-cutting/parameter-search-methodology.md).

## 6. Quand préférer le clock glitch

- La cible **boote sur une horloge externe accessible** (cristal visible, OSC_IN exposé).
- On dispose déjà d'un contrôle de la ligne d'horloge (banc de test, Fault Board dédiée) —
  dans ce cas la précision temporelle atteignable est excellente (cartographie par étage de
  pipeline très nette).
- Sinon : voltage glitching ([`voltage-glitching.md`](voltage-glitching.md)) ou EMFI
  ([`emfi.md`](emfi.md)).
