# Équipement et paliers de coût — vue transversale

> Détails d'implémentation par vecteur : crowbar/AGW dans
> [`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md), injecteurs EM
> dans [`../by-vector/emfi.md`](../by-vector/emfi.md).

## 1. Coût / succès / contrôle spatial par mécanisme

[corpus, SoK 2025, Tables 1-2, p. 6] :

| Mécanisme | Coût bas | Coût haut | Taux de succès moyen | Contrôle spatial |
|---|---|---|---|---|
| **Clock / Voltage glitching** | **50 $** (PicoGlitcher v2) | 600 $ (ChipWhisperer) | ≈ 1,4 % | aucun (effet global) |
| **EMFI** | 4 000 $ (ChipShouter) | 10 000 $+ | ≈ 2 % | **local** |
| **Laser (LFI)** | 500 $ | 50 000 $+ | ≈ 100 % | **très local** |

Repère de cadrage répété dans plusieurs papiers : *« low cost »* = **< 3 000 $** d'équipement
[corpus, Barenghi *et al.*, cité par Bozzato] ; *« moins de 500 $ d'équipement »* suffit pour
une évaluation professionnelle [corpus, Yuce p. 15].

## 2. Voltage/clock glitching — outils

| Outil | Type | Prix ind. | Note |
|---|---|---|---|
| **PicoGlitcher v2** | RP2040/RP2350, crowbar | ~50 $ | **[corpus, SoK 2025 réf. 81]** |
| **ChipWhisperer-Nano/Lite/Husky** | clock + voltage | ~50 → 600 $+ | **[corpus, SoK 2025 réf. 82]** ; écosystème mûr, scope intégré (Husky) |
| **Faultier** (Hextree) | crowbar, éducatif | bas coût | **[reco]** — positionnement, prix non sourcé |
| Crowbar DIY | MOSFET N + driver de grille | **[reco]** < 10 € en composants (estimation, aucun prix fournisseur vérifié) | topologie **[corpus]** : voir [`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §3 |
| Générateur DDS externe (ex. FeelTech FY3200S) | forme d'onde arbitraire | ~50 $ | **[corpus, Bozzato p. 203-204]** : ±10 V, 2048 pts, 12 bits, 6 MHz |

## 3. EMFI — paliers de tension et outils

| Palier | Tension | Outils | Cible typique |
|---|---|---|---|
| **A** | ~250 V | **[ref]** **FaultyCat** (Electronic Cats, RP2040, ~240 V, open-source) · **[ref]** **PicoEMP** (~133 $, kit Tindie — seul prix EMFI vérifié en boutique) | MCU/SoC (STM32, EFR32, ESP32) |
| **B** | ~500 V | **[ref]** ChipShouter 150–500 V | MCU/SoC durcis |
| **C** | ~1 kV | **SiliconToaster** [corpus] (transfo ×200 + Cockcroft-Walton ×4 + IGBT, USB 5 V → 1,2 kV programmable) | cibles dures (x86, gros boîtier, IHS) |
| pro | — | **ChipShouter** (NAE-CW520) | ~4 000 $ [corpus, SoK], > 1000 imp/s sans refroidissement actif |

**Injecteur EMFI le moins cher de la classe kV attesté par un papier** [corpus, BADFET,
WOOT'17] : **< 350 $** pour 280 A @ 300 V / 54 A @ 1100 V.

**Banc DIY chiffré intermédiaire** [corpus, Toldo, hardwear.io 2023] : ~200 $ platine XY +
~2000 $ pulseur + ~100 $ générateur de délai (~2300 $ total).

**Plancher de coût qualitatif, non chiffré en BOM** [ref, talk Hackfest LeClair 2026] : un
injecteur EMFI peut se construire à partir d'un allumeur piézo + une inductance ferrite
(quelques dollars), sans position répétable ni forme contrôlée — seuil de faisabilité, pas
un point de départ d'ingénierie.

**Modification tierce du PicoEMP** [ref, RECESSIM 2026, non affiliée NewAE] : remplacement du
circuit de charge HT par une alimentation de laboratoire externe programmable →
**500 V à 1 kHz** en continu (contre ~1 impulsion/s stock), ~150-250 $ total, mais garde-fou
de sécurité d'origine dégradé (pas de dissipateur exposé prévu pour cette puissance).

## 4. Générateurs d'impulsions haute tension (palier 1 kV+)

Le switch HT est la vraie difficulté au-delà de ~500 V. Options citées : **strings
d'avalanche transistors** ou **thyristors en mode avalanche** (fronts sub-ns, sorties
1–4 kV) [ref] ; alternative plus simple mais plus lente : **IGBT 1200 V** ou **SCR HT**
[corpus, SiliconToaster].

## 5. Une classe d'injecteur souvent absente des BOM DIY : la chaîne RF continue

[corpus, *Faults in Our Bus*, NDSS 2024] : générateur de signal → générateur de train
d'impulsions → **amplificateur de puissance large bande** → sonde champ proche du commerce.
**Aucune HT, aucun condensateur, aucun IGBT** — et cela suffit à fauter un SoC à 600 MHz+.
Alternative crédible à la décharge capacitive quand une chaîne RF de laboratoire est
disponible. Détail : [`../by-vector/emfi.md`](../by-vector/emfi.md) §4.

## 6. Cibles de calibration de sonde

[ref, NewAE ChipSHOUTER Ballistic Gel (CW521)] — carte à grande puce SRAM conçue pour charger
un motif connu, injecter, relire et **visualiser spatialement** la zone de bits retournés.
Utile pour caractériser une nouvelle pointe EMFI avant de viser une cible réelle,
indépendamment du fournisseur du reste de la chaîne.

## 7. Sécurité (paliers HT, > 250 V)

Voir [`../by-vector/emfi.md`](../by-vector/emfi.md) §8 pour le détail complet (danger létal,
résistance de purge, isolation hipot, interlock, `E = ½·C·V²`). Règle de départ : **rester au
palier A (~250 V) et/ou acheter un outil prêt à l'emploi** (FaultyCat/PicoEMP) avant de
construire un générateur 1 kV maison.

## Bancs sourcés qui ont effectivement cassé une cible

Ces chiffres valent mieux qu'un prix catalogue : ils sont attachés à un **résultat**.

| Banc | Coût imprimé | Vecteur | Cible cassée | Source |
|---|---|---|---|---|
| **chip.fail** — Cmod A7 (~70 $) + MUX PMOD (~1,80 $) + DPS3003 (~20 $) | **≈ 92 $** | voltage | **STM32F2** (Trezor One), nRF52840, ESP32, SAM L11 | [corpus, sl. 63] |
| **chip.fail** — « le glitcher à 5 $ » | **5 $** | voltage | **SAM L11**, *« succès après littéralement 5 minutes »* | [corpus, sl. 114-117] |
| ★ **LimitedResults** — système de glitch maison | ***« less than 5$ »*** | voltage | **nRF52840** — dev-kit **et produit commercial** (souris Logitech G Pro) ; APPROTECT contourné, firmware dumpé | `[ref]` |
| **COSIC** — injecteur EM complet | **≈ 40 €** | **EMFI** | **STM32F411** | [corpus, p. 12] |
| **RHUL** — station laser | **≈ 395 $** : diode **< 40 $** + switch **70 $** + FPGA **35 $** + ★ **microscope Leitz d'occasion ≈ 250 $** | **laser** | AVR / ARM | [corpus, p. 2-3] |
| **GIAnT** + Raspberry Pi 3 | non chiffré (open-design) | voltage | STM8 ×2, 78K0 | [corpus, p. 5] |
| Estimation Kraken | **~75 $** | voltage | **STM32F205** (*seed*) | `[ref]` |
| **NE555** (jrainimo) | quelques € | voltage | **STM8** | `[ref]` |

★ **Trois enseignements qui déplacent les paliers de ce fichier.**

1. **Le coût du glitcher n'est pas le facteur limitant.** Un banc à ~92 $ casse un STM32F2 ; un banc
   à 5 $ casse un SAM L11. Ce qui coûte, c'est **l'instrumentation de mesure** (oscilloscope, alim
   programmable) et le **temps de caractérisation**. ★ **Le cas nRF52 pousse le constat un cran plus
   loin** : un système *« less than 5$ »* n'y casse pas seulement une carte de développement, mais un
   **produit commercial** (souris Logitech G Pro) — l'auteur estime l'attaque reproductible *« in
   less than one day and with less than 500$ equipment »*, ces 500 $ désignant **le banc complet, pas
   le glitcher**. La barrière d'entrée n'est donc ni le prix de l'organe de commutation, ni même
   celui de l'instrumentation, mais **la connaissance du bon instant** — cohérent avec §6 et avec le
   ⚠️ « ce que le prix n'achète pas » ci-dessous.
2. ★ **L'EMFI n'est plus réservé au haut de gamme.** À **≈ 40 €**, l'injecteur COSIC se situe **sous**
   le PicoEMP (**133 $** vérifié) et le FaultyCat, et c'est pourtant le seul banc `[corpus]` ayant
   fauté un **STM32** par voie EM. La fourchette EMFI « 4 000–10 000 $+ » du SoK 2025 décrit le
   **marché commercial**, pas la borne basse technique.
3. ★ **Le palier laser a enfin un détail de composition**, jusqu'ici non sourcé : **≈ 395 $** chez
   RHUL — dont **≈ 250 $ pour la seule optique** (microscope d'occasion), contre ~145 $
   d'électronique. Cela **confirme** la borne basse « 500 $ » du SoK plutôt que de la contredire,
   ⚠️ mais déplace le poste dominant : **sur un banc laser, c'est l'optique qui coûte, pas la
   source**. Détail : [`../by-vector/laser-fi.md`](../by-vector/laser-fi.md) §2.

⚠️ **Ce que le prix n'achète pas** : `[ref]`, Raelize note qu'un outil bas coût *« is often **not able
to sufficiently sweep the glitch parameter search space** »* — mais qu'**une fois les paramètres
connus**, il peut être réglé pour les rejouer. **Découvrir** un espace de paramètres et **rejouer**
une attaque connue n'ont pas le même coût d'entrée.

⚠️ **Résolution du contrôleur — non discriminante** : GIAnT **10 ns**, FPGA chip.fail **10 ns**
(100 MHz), timer STM32F407 de Bozzato **10 ns**. Trois bancs, trois budgets, **la même résolution**.
Le facteur discriminant est l'**étage de sortie** et la **méthode de recherche**, pas le tick.

---

## ★ La composition d'un banc réel — ce qu'aucune table de prix ne dit `[fait]`

> **Provenance : `[fait]`/`[fw]`** — banc BAT32G135 monté et exercé, septembre 2026 (`docs/09`).

Les tables de coût de ce document comparent des **glitchers**. Un banc qui fonctionne en demande
**trois fonctions distinctes**, et le piège est de croire qu'un seul outil les couvre :

| Fonction | Qui la tient | Pourquoi pas un autre |
|---|---|---|
| **Le TEMPS** (trigger → délai → impulsion) | un contrôleur à **PIO déterministe** | un outil terminal (type Bus Pirate) n'est **pas** temps réel : il ne doit **jamais** se trouver dans le chemin de trigger |
| **La PUISSANCE** (le MOSFET, ou la HT) | le glitcher | seul à porter l'organe de commutation |
| ★ **L'ORACLE** (lire la cible pour savoir si ça a marché) | un **debugger séparé** | ⚠ le glitcher bas coût ne sait souvent **pas** le faire |

★★ **Le coût caché : un glitcher bas coût n'est pas forcément un oracle.** Sur le FaultyCat v3, le
sous-shell de debug est **WIP** et le firmware répond `ERR wip` ; ce qui est public est un
**scanner de brochage**, pas un client de debug capable de lire de la mémoire. ⇒ **un troisième
outil est obligatoire** pour l'oracle et le dump. Budgéter un banc sur le seul prix du glitcher
sous-estime donc systématiquement.

★ **Mais deux fonctions peuvent fusionner** : un contrôleur qui tient **à la fois** le temps, le
reset et un SWD éprouvé (cas d'un firmware de glitcher à SWD intégré) ramène le banc à **deux**
outils, et supprime l'alimentation programmable si un **réservoir de 100 µF** absorbe la crête —
le régulateur ne voit alors qu'une moyenne de quelques centaines de µA.
⚠ **Ce qu'on perd en supprimant l'alimentation programmable** : la **tension réglable**, donc la
mesure du plancher d'alimentation de la cible (seuil de brown-out réel). Cette mesure **peut être
différée, pas supprimée** — elle borne le budget de profondeur et donne le point d'underpowering.

⚠ **Coût de latence, pas d'argent** : quand l'oracle est un processus externe relancé à chaque tir
(OpenOCD en sous-processus, ~1–2 s), **c'est lui qui borne la cadence**, pas le glitcher. Une
campagne de 10⁵ tentatives passe alors de ~15 min à **~24 h**. La parade est de garder une session
ouverte et de lui parler par son port de contrôle.
